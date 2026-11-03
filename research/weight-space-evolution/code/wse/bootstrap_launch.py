"""Prepare/run fresh local Codex parents using existing ChatGPT login; no separate service credential.

Operator entrypoint. Logs are private execution payloads until reviewed and archived. Never archive the homes
folder: it contains the existing login's private credential copy, not research evidence.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

from .bootstrap_prepare import TOPIC, verify, prepare_views
from .bootstrap_broker import Broker


CAMPAIGN = '20261103T-phaseD-bootstrap-execution'


def prepare(sid, root):
    cfg = json.loads((TOPIC / 'configs/phaseD_bootstrap/budget.json').read_text())
    if cfg['status'] != 'AUTHORIZED_EXISTING_CODEX_SESSIONS':
        raise RuntimeError('existing-session execution not authorized')
    verify()
    prepare_views()
    Broker(sid, root)
    home = root / 'homes' / sid
    home.mkdir(parents=True, exist_ok=True, mode=0o700)
    original = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    source = original / 'auth.json'
    # Never print credential values. Refuse absent login and avoid any credential creation flow.
    if not source.is_file():
        raise RuntimeError('existing local ChatGPT login unavailable')
    auth = json.loads(source.read_text())
    if auth.get('auth_mode') != 'chatgpt':
        raise RuntimeError('requires the existing ChatGPT login; other credential modes refused')
    target = home / 'auth.json'
    if not target.exists():
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as f:
            json.dump(auth, f)
    text = (TOPIC / 'configs/phaseD_bootstrap/codex_tools.toml').read_text()
    instructions = home / 'instructions.md'
    instructions.write_text('Use only the lab tool to conduct the bounded research. Do not request other tools or access host files.\n')
    # Top-level settings must precede the TOML feature table.
    text = 'model_instructions_file = ' + json.dumps('/codex-home/instructions.md') + '\n' + text
    text += '\n[mcp_servers.lab]\ncommand = "/usr/bin/python3"\n'
    text += 'args = ["-I", "/transport/proxy.py", "/transport/lab.sock"]\n'
    text += 'startup_timeout_sec = 60\ntool_timeout_sec = 300\n'
    text += '[mcp_servers.lab.tools.lab]\napproval_mode = "approve"\n'
    (home / 'config.toml').write_text(text)
    return home


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--session',required=True)
    ap.add_argument('--root',default=str(TOPIC/'work/phaseD-bootstrap/execution'))
    ap.add_argument('--probe',action='store_true')
    a=ap.parse_args(); root=Path(a.root).resolve()
    root.relative_to(TOPIC/'work')
    home=prepare(a.session,root)
    logs=root/'logs';logs.mkdir(exist_ok=True)
    suffix='probe' if a.probe else 'parent'
    out=logs/f'{a.session}-{suffix}.jsonl'; err=logs/f'{a.session}-{suffix}.stderr.log'
    if out.exists():
        raise RuntimeError('refusing to overwrite previous session log; use resume after inspecting live state')
    if a.probe:
        prompt='Call lab status once, then state the exact tools available to you. Do not perform editing or evaluation.'
    else:
        prompt=(TOPIC/f'configs/phaseD_bootstrap/{a.session}.md').read_text()
        prompt+='''\nExecute the experiment now using only lab. Start with inventory and dev examples. Submit real bounded
numerical patches, request dev evaluation and use per-cell feedback to refine. Do not stop after a plan. Use useful
analysis between result polls. Respect the 30 dev-pass and 200 sandbox budgets, and seal your best candidate even
if the dev result is negative. Your final report must distinguish reduced harm from useful repair. No assigned
specialty: optimize broad editing ability while preserving per-family evidence. You have no activation hooks;
form hypotheses from tensor statistics and measured dev effects. Never fit parameters using gradients or an
optimizer. Use at most 12 development evaluations in an initial exploration; only use the rest if informative.
Gold views and saved proposals use absolute tensor values; use reset() to avoid carrying stale edits. Before
sealing, wait for every submitted evaluation to finish. A result poll may take about a minute; do not conclude
failure from a pending response. Keep exact numerical recipes in your run code and final report.\n'''
    import time
    from .bootstrap_isolation import command
    cwd=root/a.session/'conversation';cwd.mkdir(parents=True,exist_ok=True)
    address=root/'sockets'/a.session/'lab.sock'
    server_log=(logs/f'{a.session}-{suffix}-broker.log').open('x')
    server=subprocess.Popen([str(TOPIC/'work/envs/wse/bin/python'),'-m','wse.bootstrap_mcp',
         '--session',a.session,'--root',str(root),'--socket',str(address)],
         env=dict(os.environ,PYTHONPATH=str(TOPIC/'code')),cwd=TOPIC,stdout=server_log,stderr=server_log)
    try:
        for _ in range(100):
            if address.exists():break
            if server.poll() is not None:raise RuntimeError('broker server failed before readiness')
            time.sleep(0.1)
        if not address.exists():raise RuntimeError('broker socket not ready')
        prefix=command(home,cwd,address)
        # Exercise the actual outer mount namespace before any parent request.
        check='import os,json; print(json.dumps({"topic_invisible":not os.path.exists('+repr(str(TOPIC))+'),"only_socket_transport":os.path.exists("/transport/lab.sock")}))'
        checked=subprocess.check_output(prefix+['/usr/bin/python3','-I','-c',check],text=True)
        checks=json.loads(checked)
        if not all(checks.values()):raise RuntimeError('outer namespace isolation failed')
        (logs/f'{a.session}-{suffix}-isolation.json').write_text(json.dumps(checks))
        cmd=prefix+['/opt/codex/bin/codex','exec','--skip-git-repo-check','--json','--cd','/conversation','-']
        with out.open('x') as f, err.open('x') as e:
            proc=subprocess.run(cmd,input=prompt,text=True,stdout=f,stderr=e,cwd=TOPIC,timeout=15000)
    finally:
        server.terminate()
        try:server.wait(timeout=10)
        except subprocess.TimeoutExpired:server.kill();server.wait()
        server_log.close()
        if address.exists():address.unlink()
    print(json.dumps({'session':a.session,'mode':suffix,'returncode':proc.returncode,'log':str(out.relative_to(TOPIC))}))
    raise SystemExit(proc.returncode)


if __name__=='__main__':
    main()
