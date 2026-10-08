#!/usr/bin/env python3
"""Exact complex prefix rounding after rational inverse-vector normalization."""
import argparse, hashlib, json, os, random, time
from pathlib import Path
CASES=[(64,24,4096),(256,48,2048),(1024,96,1024),(4096,128,256),(16384,160,64)]
PHASES=[(3,4),(4,3),(-3,4),(-4,3),(3,-4),(-4,-3),(5,0),(0,5),(-5,0),(0,-5)]
def check(d,p,samples):
 rng=random.Random(20261008+d+p);scale=1<<p;tested=0;maximum_bits=0;began=time.time()
 for trial in range(samples):
  ar,ai,den=1,0,1;br,bi=scale,0
  for j in range(d):
   x,y=PHASES[rng.randrange(len(PHASES))];xr,yi=x*scale//5,y*scale//5
   # Exact product oracle retains arbitrary denominators only in this checker.
   ar,ai=ar*x-ai*y,ar*y+ai*x;den*=5
   # Actual implementation rounds both generated factors and EACH completed prefix.
   br,bi=(br*xr-bi*yi)//scale,(br*yi+bi*xr)//scale
   er=br*den-ar*scale;ei=bi*den-ai*scale
   assert er*er+ei*ei <= (4*(j+1)*den)**2
   maximum_bits=max(maximum_bits,abs(br).bit_length(),abs(bi).bit_length());tested+=1
  assert maximum_bits<=p+3
 # L=(1+1/d^2) is the explicit exact inverse-vector normalization.
 assert (d*d+1)**d < 2*(d*d)**d
 # A merely constant per-axis norm above1 violates that reserve; scope is deliberate.
 weak_norm_exceeds_two=17**d > 2*16**d
 assert weak_norm_exceeds_two
 return dict(d=d,fractional_bits=p,samples=samples,seed=20261008+d+p,prefix_combinations=tested,maximum_stored_component_bits=maximum_bits,status="passed",rigorous_error_envelope="4*j*2^-P for complex prefixes with rounded unit-disk factors",negative_constant_per_axis_norm_exceeds_two=weak_norm_exceeds_two,scope="Exact bounded-precision discriminator, not a full tape multiplier; exact oracle denominators are never retained by the proposed implementation",seconds=time.time()-began)
if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("--output",type=Path,required=True);z=a.parse_args();z.output.mkdir(parents=True,exist_ok=False)
 (z.output/"protocol.json").write_text(json.dumps(dict(pid=os.getpid(),cases=CASES,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+"\n")
 for c in CASES:
  print(json.dumps(dict(event="start",pid=os.getpid(),d=c[0],p=c[1])),flush=True);r=check(*c);(z.output/("d%d-p%d.json"%c[:2])).write_text(json.dumps(r,indent=2)+"\n");print(json.dumps(dict(event="done",d=r["d"],prefix_combinations=r["prefix_combinations"],seconds=r["seconds"])),flush=True)
