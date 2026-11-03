"""Single-tool local stdio MCP transport; no provider calls. Session identity is operator-bound."""
import argparse
from pathlib import Path
import json
import sys
import socket
import os

from .bootstrap_broker import Broker

SCHEMA = {'type': 'object', 'properties': {
    'action': {'type': 'string', 'enum': ['status','inventory','examples','run','submit','evaluate','result','seal']},
    'code': {'type': 'string'}, 'names': {'type': 'array', 'items': {'type': 'string'}},
    'indices': {'type': 'array', 'items': {'type': 'integer'}},
    'parent_id': {'type': ['string','null']}, 'patch_id': {'type': ['string','null']},
    'rationale': {'type': 'string'}, 'job_id': {'type': 'string'}},
    'required': ['action'], 'additionalProperties': False}
HELP = '''Bounded direct-weight laboratory. status: remaining resources and own patches. inventory: editable Gold
layer tensors and hashes. examples(indices, at most four): dev prompts. run(code,names): numpy Python in isolated
sandbox, exporting up to eight named Gold tensors. Helpers: NAMES, SHAPES, gold(name), load(name), save(name,array),
reset(), saved(); numpy imported as np. Gold tensors are float32 views, proposals rounded to BF16 at submission.
/work is persistent private scratch; /gold is read-only. No network, torch, gradients or other host paths.
submit(parent_id=null,rationale): validate files saved by save(), create a patch owned by this session. All saved
files define proposed absolute tensor values; reset() between unrelated proposals. Child patch must have your own
parent_id. evaluate(patch_id): enqueue one full frozen dev pass. result(job_id): fetch only per-cell dev metrics
and resource counts; poll after doing useful analysis. seal(patch_id): irreversible final submission; null means
failure. No further edits/evaluations after sealing. No select/test/transfer access. Never simulate target tasks or
perform unmetered inference. Only operator evaluator runs the small model.'''


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--session',required=True); ap.add_argument('--root',required=True); ap.add_argument('--socket')
    a=ap.parse_args(); broker=Broker(a.session,a.root)
    incoming, outgoing = sys.stdin, sys.stdout
    if a.socket:
        address = Path(a.socket).resolve()
        address.parent.mkdir(parents=True, exist_ok=True)
        os.chdir(address.parent)
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        listener.bind(address.name)
        address.chmod(0o600)
        listener.listen(1)
        connection, _ = listener.accept()
        incoming = connection.makefile('r')
        outgoing = connection.makefile('w')
    for line in incoming:
        msg = None
        try:
            msg=json.loads(line)
            if 'id' not in msg:
                continue
            method=msg.get('method')
            if method=='initialize':
                result={'protocolVersion':msg['params']['protocolVersion'], 'capabilities':{'tools':{}},
                        'serverInfo':{'name':'weight-space-bootstrap','version':'1'}}
            elif method=='tools/list':
                result={'tools':[{'name':'lab','description':HELP,'inputSchema':SCHEMA}]}
            elif method=='tools/call':
                if msg['params']['name']!='lab':
                    raise ValueError('unknown tool')
                try:
                    payload=broker.call(msg['params']['arguments'])
                    result={'content':[{'type':'text','text':json.dumps(payload,allow_nan=False)}]}
                except Exception as ex:
                    result={'isError':True,'content':[{'type':'text','text':f'{type(ex).__name__}: request refused; inspect status or revise permitted arguments'}]}
            elif method=='ping':
                result={}
            else:
                raise ValueError('unsupported method')
            reply={'jsonrpc':'2.0','id':msg['id'],'result':result}
        except Exception:
            reply={'jsonrpc':'2.0','id':msg.get('id') if isinstance(msg,dict) else None,
                   'error':{'code':-32602,'message':'Invalid request'}}
        print(json.dumps(reply),file=outgoing,flush=True)


if __name__=='__main__':
    main()
