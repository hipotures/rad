"""Read-only frontend wrapper: retain actual generated IDs, without engine instrumentation.

One append per already-yielded integer token, one write after generator closure.
No per-token timing, synchronous I/O, copying activations or mathematical changes.
Both members of every new comparison use this same wrapper.
"""
import hashlib, json, os, pathlib, sys
sys.path.insert(0,os.getcwd())
from serve import server
original=server.StrataEngine.generate
counter=0
def generate(self,*args,**kwargs):
    global counter
    counter+=1;number=counter;ids=[]
    gen=original(self,*args,**kwargs)
    try:
        for t in gen:
            if t is not None:ids.append(t)
            yield t
    finally:
        gen.close()
        prefix=os.environ.get('STRATA_RESEARCH_OUTPUT_IDS')
        if prefix:
            data=json.dumps(ids,separators=(',',':')).encode()
            p=pathlib.Path(prefix+f'-request{number}.json')
            if p.exists():raise RuntimeError('Refuse overwrite output ID evidence')
            p.write_bytes(data)
            incoming=args[0] if args else kwargs['ids']
            raw=json.dumps(incoming,separators=(',',':')).encode()
            pathlib.Path(prefix+f'-input-request{number}.json').write_text(json.dumps({'count':len(incoming),'sha256':hashlib.sha256(raw).hexdigest(),'encoding':'JSON integer array, compact separators, service-rendered actual engine IDs'},indent=2)+'\n')
server.StrataEngine.generate=generate
if __name__=='__main__':server.main()
