#!/usr/bin/env python3
"""Profile-conditional exact ceiling and paid target for a new public claim.

Apache-2.0; prepared with OpenAI GPT-6.1 Sol assistance for RaD.
Imports only our independent arithmetic helper and the standard library.
This is a negative scope result, not finite acceptance of discovery frames.
"""

import argparse
from fractions import Fraction as F
import json
from pathlib import Path
import sys

from review_balanced_unified import (BAD, BETA, ETA, OLD, WEAKENING,
    complete_profile, digest, encode, moment, need)


def above_grid(value, denominator):
    scaled = value*denominator
    return F(scaled.numerator//scaled.denominator+1, denominator)


def main():
    need(not sys.flags.optimize, "Assertion-disabled Python is unsupported")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bit-profile", type=Path, required=True)
    p.add_argument("--bit-frames", type=Path, required=True)
    p.add_argument("--complex-profile", type=Path, required=True)
    p.add_argument("--complex-frames", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--public-kappa", default="297136180212477/500000000000000000")
    args = p.parse_args()
    need(not args.output.exists(), "Fresh result identity required")
    bp = complete_profile(json.loads(args.bit_profile.read_text()), (72,26888,1934000,60))
    cp = complete_profile(json.loads(args.complex_profile.read_text()),
                          (66,15681,1033626,20), component=True)
    a0 = F(59503737587021, 10**17)
    a0_upper = a0+F(1,10**18)
    b = F(594608516, 10**12)
    b_upper = b+F(1,10**12)
    bm, bn = moment(bp,a0,True), moment(bp,a0_upper,True)
    cm, cn = moment(cp,b), moment(cp,b_upper)
    need(bm["upper"] < 1 < bn["lower"] and cm["upper"] < 1 < cn["lower"],
         "Profile-conditional characteristic endpoints not separated")
    need(F(2*bp["m"]**3,1<<80)<BAD and
         bp["mass"]+BAD*32*bp["m"]**2*bp["edges"]<bp["m"]*bp["W"],
         "Full fallback prime/rank envelope changed")
    public = F(args.public_kappa)
    need(0 < public < F(1,32), "Public target domain")
    # A(theta)=a0-theta*(a0-OLD); theta>A(theta) gives
    # theta>a0/(1+a0-OLD). Supremum A is that strict boundary.
    atom_infimum = a0/(1+a0-OLD)
    atom_upper = a0_upper/(1+a0_upper-OLD)
    theta = above_grid(atom_infimum,10**24)
    ordinary = (1-theta)*a0+theta*OLD
    need(ordinary<theta<1-ordinary, "Optimized atom does not pay both tolls")
    supplier_upper = min(atom_upper,b_upper)
    need(supplier_upper == b_upper, "This frozen profile pair is no longer complex-limited")
    ceiling = supplier_upper/(1+supplier_upper)
    need(ceiling < public, "This profile pair has not been excluded at the new target")
    optimistic_required = public/(1-public)
    retained_a_required = public/((1-2*ETA)*(1-ETA-public))
    retained_b_required = (retained_a_required+WEAKENING)/(1-BETA)
    grid_required = above_grid(retained_b_required,10**12)
    fixed_atom_ordinary = F(999,1000)*a0+F(1,1000)*OLD
    out = dict(status="PROFILE_CONDITIONAL_CEILING_BELOW_OBSERVED_CLAIM",
        scope="Exact arithmetic on supplied changed profiles; finite independent bit/F2/dual-Gram and complex reflection checks are prerequisites for any acceptance",
        input_pins={name:dict(path=str(getattr(args,name)),sha256=digest(getattr(args,name)))
                    for name in ("bit_profile","bit_frames","complex_profile","complex_frames")},
        bit=bp, complex=cp, coarse_bit_saving=a0, coarse_bit_upper=a0_upper,
        complex_saving=b, complex_upper=b_upper,
        intervals=dict(bit=bm,bit_upper=bn,complex=cm,complex_upper=cn),
        atom_infimum=atom_infimum, atom_chosen=theta, ordinary_saving=ordinary,
        optimistic_ordinary_upper=atom_upper, fixed_atom_ordinary=fixed_atom_ordinary,
        limiting_supplier="complex", optimistic_supplier_upper=supplier_upper,
        balanced_ceiling=ceiling, public_kappa=public, shortfall=public-ceiling,
        optimistic_bit_complex_requirement=optimistic_required,
        retained_a_requirement=retained_a_required, retained_b_requirement=retained_b_required,
        sufficient_complex_12_grid=grid_required,
        proof="The characteristic is strictly increasing; rejected endpoints bound the saving. The paid atom gives A<alpha/(1+alpha-OLD). Balanced g=(1-eta)q/(1+q)<a/(1+a), with a<=min(A,b). Hence kappa<min(A_upper,b_upper)/(1+min(A_upper,b_upper)).",
        all_size_hypotheses="Same conditional ordinary wrapper, uniform local-ring compiler, completed complex tensor, paid balanced/router/bulk and analytic tape contracts",
        own_source_sha256=digest(Path(__file__)),
        interval_helper_sha256=digest(Path(__file__).with_name("review_balanced_unified.py")))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(encode(out),indent=2,sort_keys=True)+"\n")
    print("Profile-conditional ceiling="+str(ceiling)+" < public="+str(public))
    print("Exact shortfall="+str(public-ceiling)+"; retained sufficient complex grid="+str(grid_required))


if __name__ == "__main__":
    main()
