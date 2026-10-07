"""Common append-only actual-ID capture outside the unmodified native engine.

Two cheap /proc snapshots delimit decode. No per-token timing or disk I/O.
"""
import hashlib,json,os,pathlib,sys,time
sys.path.insert(0,os.getcwd())
from serve import server
original=server.StrataEngine.generate
counter=0
root=pathlib.Path(sys.argv[sys.argv.index('--config')+1]).parent/'raw'

def snapshot(pid):
 stat=pathlib.Path(f'/proc/{pid}/stat').read_text().split(') ',1)[1].split()
 return {'monotonic':time.monotonic(),'epoch':time.time(),'system_cpu_ticks':list(map(int,pathlib.Path('/proc/stat').read_text().splitlines()[0].split()[1:])),'native_cpu_ticks':int(stat[11])+int(stat[12]),'native_rss_pages':int(stat[21])}

def generate(self,*args,**kwargs):
 global counter
 counter+=1;number=counter;ids=[];first=None;begin=snapshot(self.proc.pid)
 gen=original(self,*args,**kwargs)
 try:
  for t in gen:
   if t is not None:
    if first is None:first=snapshot(self.proc.pid)
    ids.append(t)
   yield t
 finally:
  gen.close();end=snapshot(self.proc.pid)
  incoming=args[0] if args else kwargs['ids']
  raw=json.dumps(incoming,separators=(',',':')).encode()
  p=root/f'output-ids-request{number}.json'
  if p.exists():raise RuntimeError('Refuse overwrite ID evidence')
  p.write_text(json.dumps(ids,separators=(',',':')))
  (root/f'input-ids-request{number}.json').write_bytes(raw)
  (root/f'capture-request{number}.json').write_text(json.dumps({'input_count':len(incoming),'input_ids_sha256':hashlib.sha256(raw).hexdigest(),'output_count':len(ids),'output_ids_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'begin':begin,'first_token':first,'end':end,'native_last':self.last,'native_pid':self.proc.pid},indent=2)+'\n')
server.StrataEngine.generate=generate
if __name__=='__main__':server.main()
