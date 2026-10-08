#!/usr/bin/env python3
"""Distinct exact native47-row and new analytic-scale parameter families."""
import argparse, concurrent.futures,hashlib,importlib.util,json,os,time
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def native():
 base=ROOT/"work/scout/snapshots/pr40-43f59ff53359/research";certificate=json.loads((base/"copied-both-reversed/certificate.json").read_text());source=base/"copied-reversed/balanced_assembly.py"
 spec=importlib.util.spec_from_file_location("native_assembly",source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 a=F(783777693,20000000000000);tested=passed=0;failed=Counter();best=None;winners=[]
 for bj in range(1,100):
  beta=F(bj,200)
  for power in range(10,310):
   h=F(1,2**power);q=a*(1-2*h);eps=(1-h)/(1+q);kappa=eps*q*(1-h)
   tested+=1
   try:
    r=m.assembly(certificate["finite_bridge"],a,kappa,beta=beta,h=h)
    passed+=1
    if best is None or kappa>best:best=kappa;winners=[dict(beta=str(beta),h=str(h),kappa=str(kappa),slacks={k:str(v) for k,v in r["constraints"].items()})]
   except m.InvalidAssembly as e:
    text=str(e);reason=text.split("'",2)[1] if "'" in text else text;failed[reason]+=1
 return dict(kind="native47_parameter_family",tested=tested,passed=passed,failed=dict(failed),best_arithmetic_kappa=str(best),best=winners,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),source_head="43f59ff533598762cbc43a5e14af2bbbc76fabbd",scope="changed beta/backoff families; native finite proofs remain conditional inputs")
def analytic():
 eps=F(999999,1000000);kappa=F(78376985522307,2000000000000000000);tested=passed=0;fail=Counter();best=None;front=[]
 for bj in range(33,129):
  B=F(bj,16)
  for tj in range(128,449,2):
   theta=F(tj,16)
   for pj in range(160,513,2):
    precision=F(pj,16);tested+=1
    gaps=dict(native_gaussian=precision-2-theta,inverse_chirp=theta-(8+2*B),contraction=precision-1-theta,phase_halo=(theta-2*B-1)/2,sparse_sort=eps*(B-2)-kappa,phase_lu=1-kappa-eps*(3-B),metadata=eps*precision-4,forward_chirp=theta-7)
    # The inverse chirp equality needs a separately chosen small constant;
    # native Gaussian equality needs a sufficiently large digit constant; all other exponent comparisons are strict.
    bad=[name for name,v in gaps.items() if v<0 or (v==0 and name not in ("inverse_chirp","native_gaussian"))]
    if bad:fail[bad[0]]+=1;continue
    passed+=1
    if best is None or precision<best:best=precision;front=[dict(delta_degree=str(B),theta_degree=str(theta),precision_degree=str(precision),gaps={k:str(v) for k,v in gaps.items()})]
    elif precision==best and len(front)<20:front.append(dict(delta_degree=str(B),theta_degree=str(theta),precision_degree=str(precision)))
 return dict(kind="analytic_scale_parameter_family",tested=tested,passed=passed,first_failed_inequality=dict(fail),minimum_grid_precision_degree=str(best),grid_minimizers=front,scope="exact finite rational parameter grid, not an all-size machine certificate")
def worker(name):
 began=time.time();print(json.dumps(dict(event="start",family=name,pid=os.getpid())),flush=True);r=native() if name=="native47" else analytic();r["elapsed_seconds"]=time.time()-began;return r
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 protocol=dict(question="Does the lower precision grid survive the inherited u^2*theta>=Q premise?",pid=os.getpid(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),supersedes="20261008T1420Z analytic grid was scoped and omitted this inherited comparison; preserve its evidence",unchanged_control="d^18 precision,d^-16 mismatch,d^-4 phase width satisfies new exponent comparison at equality, with separately chosen digit constant")
 (a.output/"protocol.json").write_text(json.dumps(protocol,indent=2)+"\n")
 print(json.dumps(dict(event="start",pid=os.getpid(),family="analytic_native_gaussian_repair")),flush=True)
 r=analytic();r["pid"]=os.getpid();r["source_sha256"]=protocol["source_sha256"]
 (a.output/"analytic.json").write_text(json.dumps(r,indent=2)+"\n")
 print(json.dumps(dict(event="done",tested=r["tested"],passed=r["passed"],minimum_grid_precision_degree=r["minimum_grid_precision_degree"])),flush=True)
