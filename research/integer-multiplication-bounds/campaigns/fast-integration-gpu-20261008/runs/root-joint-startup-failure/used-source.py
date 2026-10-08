import sys,json,datetime
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
sys.path.insert(0,sys.argv[1])
from producer_search import initialize
from point_order_search import evaluate
work=Path(sys.argv[3]);configs=json.loads(Path(sys.argv[4]).read_text());done=[]
with ProcessPoolExecutor(max_workers=4,initializer=initialize,initargs=(sys.argv[2],work,work/'builds/moment_match_positive')) as pool:
 pending={};it=iter(configs)
 for _ in range(4):
  c=next(it,None)
  if c:pending[pool.submit(evaluate,c)]=c
 while pending:
  f=next(as_completed(pending));pending.pop(f);r=f.result();done.append(r);Path(sys.argv[5]).write_text(json.dumps({'rows':done,'tested':len(done),'planned':len(configs)},indent=2)+'\n');print(json.dumps({k:r.get(k) for k in ('case_id','status','R','seconds','pid')}),flush=True)
  if datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,10,8,14,26,6,tzinfo=datetime.timezone.utc):
   c=next(it,None)
   if c:pending[pool.submit(evaluate,c)]=c
