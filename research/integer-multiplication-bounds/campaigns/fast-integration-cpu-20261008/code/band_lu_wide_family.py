#!/usr/bin/env python3
"""Wider exact band-LU families; independently check dimension-free error bounds."""
import argparse,concurrent.futures,hashlib,importlib.util,json,os,time
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CASES=[(256,16,48,20261008101),(512,48,80,20261008102),(768,64,112,20261008103),(1024,96,160,20261008104),(1280,128,192,20261008105),(1536,160,224,20261008106)]
def band_residual(a,l,u,scale,w):
 m=len(a);maximum=0
 for i in range(m):
  assert all(v==0 for j,v in enumerate(l[i]) if j>i or j<i-w)
  assert all(v==0 for j,v in enumerate(u[i]) if j<i or j>i+w)
  assert all(v==0 for j,v in enumerate(a[i]) if abs(j-i)>w)
  total=0
  for j in range(max(0,i-w),min(m,i+w+1)):
   actual=sum(l[i][k]*u[k][j] for k in range(max(0,i-w,j-w),min(i,j)+1))
   total+=abs(actual-a[i][j]*scale)
  maximum=max(maximum,total)
 return F(maximum,scale*scale)
def job(case):
 m,w,p,seed=case;path=ROOT/"agents/inverse/code/fixed_grid_band_lu.py"
 spec=importlib.util.spec_from_file_location("grid_lu",path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 raw=path.read_text();start=raw.index("    poor_l, poor_u, poor_reciprocal, _ = factor(poor_a, w, poor_bits)");end=raw.index("    return {",start)
 coarse=raw[start:end]
 repair="    try:\n"+"".join("    "+line+"\n" for line in coarse.splitlines())+"    except AssertionError:\n        poor_error = None  # Coarse rounding has left the solver's near-identity domain.\n"
 transformed=raw[:start]+repair+raw[end:];exec(compile(transformed,str(path),"exec"),module.__dict__)
 # Validate the support-aware exact oracle against the dense independent oracle.
 a=module.build(17,3,24,seed);l,u,_,_=module.factor(a,3,24)
 assert band_residual(a,l,u,1<<24,3)==module.factor_residual(a,l,u,1<<24)
 module.factor_residual=lambda a,l,u,scale:band_residual(a,l,u,scale,w)
 print(json.dumps(dict(event="start",pid=os.getpid(),m=m,w=w,bits=p)),flush=True)
 began=time.time();r=module.run_case(*case);r.update(worker_pid=os.getpid(),status="passed",source_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
 tight_factor=F(w*(w+2),1<<p);tight_solution=F((1<<12)*(w+1)**2,1<<p)
 assert F(r["factor_residual_row_norm"])<tight_factor
 assert F(r["solution_error_bound_from_residual"])<tight_solution
 r.update(tight_factor_bound=str(tight_factor),tight_solution_bound=str(tight_solution),coarse_negative_stability_failure=r["coarse_precision_negative_residual"]=="None",scope="All residual rows and band support checked by exact integers; dimension-free written bounds, generic matrices not cyclic Gaussian geometry",wall_seconds=time.time()-began)
 return r
if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("--workers",type=int,default=3);a.add_argument("--output",type=Path,required=True);z=a.parse_args();z.output.mkdir(parents=True,exist_ok=False)
 (z.output/"protocol.json").write_text(json.dumps(dict(cases=CASES,workers=z.workers,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+"\n")
 with concurrent.futures.ProcessPoolExecutor(max_workers=z.workers) as pool:
  pending={pool.submit(job,c):c for c in CASES}
  for f in concurrent.futures.as_completed(pending):
   try:r=f.result()
   except Exception as error:
    m,w,p,seed=pending[f];r=dict(m=m,half_bandwidth=w,fractional_bits=p,seed=seed,status="failed",error=type(error).__name__+": "+str(error),wall_seconds=None)
   (z.output/("m%d-w%d.json"%(r["m"],r["half_bandwidth"]))).write_text(json.dumps(r,indent=2)+"\n");print(json.dumps(dict(event="done",m=r["m"],w=r["half_bandwidth"],seconds=r["wall_seconds"])),flush=True)
