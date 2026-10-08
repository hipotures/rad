#!/usr/bin/env python3
"""New finite cyclic inverse families; each result is written on completion."""
import argparse, concurrent.futures, hashlib, importlib.util, json, os, time
from pathlib import Path
CASES=[(191,192,160),(211,223,160),(251,256,180),(283,284,180),(331,337,200),(383,384,200),(443,448,220),(509,514,220)]
def job(case):
 s,t,digits=case
 spec=importlib.util.spec_from_file_location("locality",Path(__file__).resolve().parents[1]/"agents/inverse/code/global_locality_controls.py")
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 began=time.time();print(json.dumps(dict(event="start",pid=os.getpid(),s=s,t=t,digits=digits)),flush=True)
 try:
  r=m.cyclic_numeric(s,t,digits);r["status"]="passed"
 except Exception as e:
  r=dict(s=s,t=t,decimal_digits=digits,status="failed",error=type(e).__name__+": "+str(e))
 r["worker_pid"]=os.getpid();r["wall_seconds"]=time.time()-began
 return r
def main():
 a=argparse.ArgumentParser();a.add_argument("--workers",type=int,default=4);a.add_argument("--output",type=Path,required=True);z=a.parse_args();z.output.mkdir(parents=True,exist_ok=False)
 protocol=dict(cases=CASES,workers=z.workers,root_pid=os.getpid(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),dependency="agents/inverse/code/global_locality_controls.py",scope="distinct Gaussian cyclic lengths, phase spacings, precisions and complete basis solves")
 (z.output/"protocol.json").write_text(json.dumps(protocol,indent=2)+"\n")
 with concurrent.futures.ProcessPoolExecutor(max_workers=z.workers) as pool:
  pending={pool.submit(job,c):c for c in CASES}
  for future in concurrent.futures.as_completed(pending):
   r=future.result();(z.output/("s%d-t%d.json"%(r["s"],r["t"]))).write_text(json.dumps(r,indent=2)+"\n");print(json.dumps(dict(event="completed",s=r["s"],t=r["t"],status=r["status"],seconds=r["wall_seconds"])),flush=True)
if __name__=="__main__":main()
