import pathlib,json,time,datetime,os,threading,subprocess
from progress import update
C=pathlib.Path(__file__).resolve().parents[1]
INPUT_PARENT=pathlib.Path(os.environ.get('RAD_INPUT_CAMPAIGNS',json.loads((C/'configs/storage.json').read_text())['input_campaign_parent']))
P0=INPUT_PARENT/'golden-swap-phase0-20261006T185015Z';P1=INPUT_PARENT/'golden-swap-phase1-20261006T200037Z'
W=pathlib.Path(os.environ.get('RAD_WORK_ROOT',json.loads((C/'configs/storage.json').read_text())['work_root']))
SOURCE=W/'repos/runtime';BUILD=W/'builds/runtime'
def load(p):return json.loads(pathlib.Path(p).read_text())
def save(p,x):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp.'+str(os.getpid())+'.'+str(threading.get_ident()));tmp.write_text(json.dumps(x,indent=2)+'\n');os.replace(tmp,p)
def progress(step,message,**kw):update(step,kw.pop('status','RUNNING'),message,**kw)
def ledger(message,**kw):
 x=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),message=message,**kw)
 with (C/'attempt-ledger.jsonl').open('a') as f:f.write(json.dumps(x)+'\n')
def no_gpu():assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True,timeout=8).strip(),'GPU conflict'
class Heartbeat:
 def __init__(self,label,step):self.label=label;self.step=step;self.stop=threading.Event()
 def __enter__(self):
  def worker():
   while not self.stop.wait(25):progress(self.step,'HEARTBEAT '+self.label,eta='unknown')
  self.thread=threading.Thread(target=worker,daemon=True);self.thread.start();return self
 def __exit__(self,*_):self.stop.set();self.thread.join(2)
