import sys,json,datetime
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from producer_search import initialize
from point_order_search import evaluate
work=Path(sys.argv[3]);initialize(sys.argv[2],work,work/'builds/moment_match_positive')
configs=json.loads(Path(sys.argv[4]).read_text());done=[]
for c in configs:
 if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime(2026,10,8,14,26,6,tzinfo=datetime.timezone.utc):break
 r=evaluate(c);done.append(r);Path(sys.argv[5]).write_text(json.dumps({'rows':done,'tested':len(done),'planned':len(configs)},indent=2)+'\n');print(json.dumps({k:r.get(k) for k in ('case_id','status','R','seconds','pid')}),flush=True)
