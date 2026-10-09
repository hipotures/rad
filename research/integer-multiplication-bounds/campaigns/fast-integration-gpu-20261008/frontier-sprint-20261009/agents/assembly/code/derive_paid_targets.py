#!/usr/bin/env python3
"""Exact paid-interface requirements for a pinned public final kappa.

Apache-2.0; prepared for RaD with OpenAI GPT-6.1 Sol assistance.
This derives necessary supplier targets, not a new finite construction.
"""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True
if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(0)


def need(test,message):
    if not test:raise ValueError(message)


def encode(value):
    if isinstance(value,F):return str(value)
    if isinstance(value,dict):return {k:encode(v) for k,v in value.items()}
    return value


def main():
    need(not sys.flags.optimize,"Assertion-disabled Python is unsupported")
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--certificate",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--ratio",default="101/100")
    p.add_argument("--eta",default="1/100000000")
    p.add_argument("--beta",default="1/1000000000")
    p.add_argument("--weakening",default="1/10000000000")
    p.add_argument("--grid",type=int,default=10**12)
    args=p.parse_args();need(not args.output.exists(),"Fresh target identity required")
    data=args.certificate.read_bytes();claim=F(json.loads(data)["kappa"])
    ratio,eta,beta,weak=(F(getattr(args,k)) for k in ("ratio","eta","beta","weakening"))
    old=F(384599,10**10);need(0<claim<F(1,32) and ratio>=F(101,100),"Claim/relative improvement domain")
    need(0<eta<F(1,8) and 0<beta<1 and weak>0 and args.grid>0,"Paid parameter domain")
    floor=claim*ratio;need(floor<1-eta,"Positive assembly inverse denominator")
    z=floor*args.grid;reported=F(-(-z.numerator//z.denominator),args.grid)

    def above_grid(x):
        y=x*args.grid
        return F(y.numerator//y.denominator+1,args.grid)

    def targets(k):
        a=k/((1-2*eta)*(1-eta-k));b=(a+weak)/(1-beta)
        alpha=a*(1-old)/(1-a)
        points={name:above_grid(value) for name,value in
            (("ordinary",a),("complex",b),("optimized_coarse_bit",alpha))}
        previous=points["complex"]-F(1,args.grid)
        available=(1-beta)*previous-weak;q=available*(1-2*eta)
        previous_g=(1-eta)*q/(1+q)
        need(previous<=b and previous_g<=k,"The preceding complex grid should be insufficient")
        return dict(kappa=k,ordinary_requirement=a,complex_requirement=b,
            optimized_coarse_requirement=alpha,sufficient_1e12_points=points,
            previous_complex_grid=previous,previous_complex_maximum=previous_g,
            previous_complex_shortfall=k-previous_g)

    out=dict(status="EXACT_NECESSARY_PAID_NATIVE_TARGETS",claim=claim,ratio=ratio,
        one_percent_floor=floor,reported_grid_kappa=reported,
        rational_floor_targets=targets(floor),reported_grid_targets=targets(reported),
        parameters=dict(eta=eta,beta=beta,weakening=weak,old_ordinary_saving=old,grid=args.grid),
        input=dict(path=str(args.certificate),sha256=sha256(data).hexdigest()),
        proof="Invert g=(1-eta)a(1-2eta)/(1+a(1-2eta)), enforce a<=(1-beta)b-weakening, and invert the paid atom bound A<alpha/(1+alpha-old). The reported grid rounds the non-strict publication floor upward; supplier grid points must be strictly above their requirements.",
        scope="Pinned comparable claim arithmetic only; finite suppliers, all 47+7, full bills and live frontier remain separate acceptance/publication gates.",
        own_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(encode(out),indent=2,sort_keys=True)+"\n")
    print("Required relative floor="+str(floor)+"; reported grid kappa="+str(reported))
    print("Required supplier grids="+str(encode(out["reported_grid_targets"]["sufficient_1e12_points"])))


if __name__=="__main__":main()
