#!/usr/bin/env python3
"""Independent exact bills, 47+7 and ceiling on actually rebuilt PR168 rows.

Apache-2.0; prepared for RaD with OpenAI GPT-6.1 Sol assistance.
Only our earlier independent interval/type helpers and stdlib are imported.
No candidate or predecessor checker is imported. This is a fixed-profile
negative ceiling, not acceptance of a new frame word or an all-size theorem.
The paid layout equations retain the PR23/29, James Chang PR34, RaD,
Rohan Arun PR100/103, icekylinx/eumemic PR161/168 and PR141/163 lineage.
"""

import argparse
from collections import Counter
import copy
from fractions import Fraction as F
import json
from math import prod
from pathlib import Path
import sys

from review_balanced_unified import (BAD, OLD, complete_profile, digest,
    encode, exact_match, histogram, moment, need, pinned_bytes, thresholds)


def profile_rows(bit, physical):
    bp=complete_profile(bit,(72,25772,1853648,60))
    cp=complete_profile(physical,(66,14841,978186,20),component=True)
    H=Counter()
    for r,n in histogram(bit["selected_rank_histogram"],"bit gauges").items():H[3*r]+=n
    for field in ("remaining_internal_histogram","source_data_histogram","target_data_histogram"):
        for r,n in histogram(bit[field],field).items():H[r]+=3*n
    H[2]+=2*bit["v"];H.pop(0,None)
    need(dict(H)==bp["hist"],"Rebuilt binary component histogram")
    need((bit["h"],bit["v"],bit["R"],bit["loss"])==(24,1760,22252,528)
         and bp["m"]*bp["W"]-bp["mass"]==2*bit["v"]-3*bit["loss"]==1936,
         "Native binary stock and telescoping")
    need(F(2*bp["m"]**3,1<<80)<BAD and
         bp["mass"]+BAD*32*bp["m"]**2*bp["edges"]<bp["m"]*bp["W"],"Full rare-class envelope")
    return bp,cp


def native_bridge(physical,scalar,cp,coarse,atom):
    h,v,R,c,q,M=(scalar[k] for k in ("h","v","R","c","q","total_M_operations"))
    need((h,v,R,c,q,M)==(22,1320,15171,18395,4477,32246),"Actual native complex scalar graph")
    need(R==c+q-scalar["matched"] and scalar["matched"]==7701,"Native scalar inventory")
    need(physical["R"]==R and physical["physical_R"]==12201 and physical["pairs"]==2970
         and physical["late_pairs"]==2970 and R-physical["pairs"]==physical["physical_R"],
         "Native physical reuse/compensation")
    need(cp["m"]==3*h and cp["W"]==2*v+physical["physical_R"]
         and cp["m"]*cp["W"]-cp["mass"]==2*v-3*scalar["loss"]==1320,
         "Native complex dimension and deficit")
    need(3*q<1<<15,"Dirty readout binary expansion")
    m=cp["m"];half=m//2
    V=(1<<(m-1+(half-1)**2))*prod((1<<(2*i))-1 for i in range(1,half))
    W,s,N=V*cp["W"],V*cp["mass"],V*v
    L=4*(c+v)+10*v+4*h*v+4*h*h+8*h+8+2*h+8*R*v*(M+16)+32*v
    K=3*V*L+8*W+4*N+8*m*R*V
    G=64*(m+1)**3*(K+1)*(W+1)**2
    E=64*(W+m+G+1)**3
    literal=2*G*W*W+8*s+4*W+4+32*m
    B=s+E;C0=32*m*B*B;d=1
    while m**d<=2*cp["maxchild"]**d:d+=1
    coefficient=d*W.bit_length()+9909+252
    A=(1-atom)*coarse+atom*OLD
    result=dict(V=V,W=W,s=s,N=N,m=m,maxchild=cp["maxchild"],physical_roles=physical["physical_R"],
        scalar_roles=R,reuse_pairs=physical["pairs"],local_scalar=L,logical_scalar=K,router=G,
        E=E,literal=literal,B=B,C0=C0,C1=1,strict_literal_gap=E-literal,
        induction_gap=2*B*(m-cp["maxchild"])-s-E,guard_gap=C0-2*B-18,
        halving_degree=d,wire_bits=W.bit_length(),complex_coefficient=d*W.bit_length(),
        old_coarse_reserve=9909,old_leaf_reserve=252,row_coefficient=coefficient,row_degree=70000,
        row_gap=F(70000)-F(51*coefficient,25),suffix_slope=280000,ordinary_saving=A,
        atom=atom,coarse=coarse,old=OLD,adapter_gap=atom-A,internal_row_gap=1-A-atom,fixed_odd_divisor=3)
    need(all(result[k]>0 for k in ("strict_literal_gap","induction_gap","guard_gap","row_gap",
                                   "adapter_gap","internal_row_gap")),"Native full bills or atom toll")
    return result


def native_assembly(bill,b,beta,eta,weakening,kappa=None):
    a=min(bill["ordinary_saving"],(1-beta)*b-weakening)
    tau,sigma=1-a,1-b;q=a*(1-2*eta);c=q+eta/4;e=(1-eta)/(1+q)
    lp=1-q;lam=(tau+lp)/2;g=e*q;r=(g+1-e)/2;delta=eta/8
    if kappa is None:
        z=g*10**18;kappa=F(-(-z.numerator//z.denominator)-1,10**18)
    internal=tau+(1-beta)*max(sigma-tau,F(0));leaf=sigma+beta*(1-sigma)
    margins=dict(prefix=1-e,movement=a,compact=g,bulk=a,Gaussian=min(1-e-delta,r-delta),
                 scalar=1-e-delta,dimension=e)
    slacks=dict(a_positive=a,a_below_b=b-a,b_below_one_over32=F(1,32)-b,
        beta_positive=beta,beta_below_one=1-beta,phase_leaf_above_bit=(1-beta)*b-a,
        q_positive=q,q_below_internal=1-internal-q,q_below_leaf=1-leaf-q,
        c_positive=c,c_below_one=1-c,q_below_reservations=c-q,
        lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,lambda_above_internal=lam-internal,
        lambda_prime_above_lambda=lp-lam,compact_leaf=lp-leaf,compact_reservations=lp-(1-c),
        lambda_prime_below_one=q,epsilon_positive=e,epsilon_below_one=1-e,guard_width=1-e,
        K_geometry=1-e*(1+c),K_dominates_log=e*c,record_suffix=1-e,
        phase_local=1-e-delta,phase_boundary=r-delta,gamma_sublinear=1-e-r,
        cell_above_band=e-(1-r)/2,prime_interval_packing=1-e,alpha_positive=r,
        alpha_below_one=1-r,alpha_below_one_fourth=F(1,4)-r,delta_positive=delta,
        delta_below_one_eighth=F(1,8)-delta,short_record_fallback=e-a,small_field_exposure=1-e-g,
        artificial_boundary=8-e+r-delta-g,literal_scalar_guard=bill["strict_literal_gap"],row_product_gap=bill["row_gap"])
    slacks.update({name+"_above_kappa":v-kappa for name,v in margins.items()})
    need(len(slacks)==47 and len(margins)==7 and all(v>0 for v in slacks.values()),"Native 47+7")
    need(min(margins.values())==g and 1-e-g==eta and 1-e-r==eta/2
         and 1-e*(1+c)==eta-e*eta/4,"Native balanced identities")
    return dict(a=a,b=b,beta=beta,eta=eta,weakening=weakening,q=q,c=c,epsilon=e,lambda_=lam,
        lambda_prime=lp,g=g,r=r,delta=delta,kappa=kappa,tau=tau,sigma=sigma,internal=internal,
        leaf=leaf,margins=margins,slacks=slacks,absorption_gap=g-kappa,strict_ceiling=a/(1+a))


def main():
    need(not sys.flags.optimize,"Assertion-disabled Python is unsupported")
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sprint",type=Path,default=Path(__file__).resolve().parents[3])
    p.add_argument("--config",type=Path,required=True)
    p.add_argument("--certificate",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args();need(not args.output.exists(),"Fresh review identity required")
    config=json.loads(args.config.read_text());author=json.loads(args.certificate.read_text())
    need(len(config["sources"]) in (74,79) and len(config["inputs"])==22,"Source168 rebuilt inventory")
    rows={name:json.loads(pinned_bytes(args.sprint,pin)) for name,pin in config["inputs"].items()}
    for pin in config["sources"].values():pinned_bytes(args.sprint,pin)
    exact_match(author["source_pins"],config,"Source pin agreement")
    need(author["config_sha256"]==digest(args.config),"Author config identity")
    for a,b in (("bit","saved_bit"),("physical","saved_physical"),("scalar","saved_scalar")):
        exact_match(rows[a],rows[b],"Actual rebuilt versus saved "+a)
    source=args.sprint/Path(config["inputs"]["saved_bit"]["path"]).parents[3]
    # Every regenerated bit file must equal the immutable source bytes, not
    # merely a saved 'all_available_source_outputs_identical' flag.
    for name in ("frames","graph","kchron","profile","word"):
        pin=config["inputs"]["rebuilt_bit_"+name+"_p12"]
        need(digest(args.sprint/pin["path"])==digest(source/("research/paired-cube-bit/out/"+name+"_p12.json")),
             "Actual fresh bit output differs: "+name)
    protocol=rows["rebuilt_complex_protocol"]
    for name,expected in protocol["source_pins"].items():
        need(digest(source/name)==expected,"Actual regenerated complex source differs: "+name)
    for name,pin in protocol["input_pins"].items():
        folder=Path(config["inputs"]["physical"]["path"]).parent
        need(digest(args.sprint/folder/name)==pin["sha256"],"Actual regenerated complex export differs: "+name)
    bit,physical,scalar=(rows[k] for k in ("bit","physical","scalar"))
    bp,cp=profile_rows(bit,physical)
    blo,bhi=F(610582011,10**12),F(610582012,10**12)
    clo,chi=F(613954254,10**12),F(613954255,10**12)
    intervals=dict(bit_lower=moment(bp,blo,True),bit_upper=moment(bp,bhi,True),
                   complex_lower=moment(cp,clo),complex_upper=moment(cp,chi))
    need(intervals["bit_lower"]["upper"]<1<intervals["bit_upper"]["lower"] and
         intervals["complex_lower"]["upper"]<1<intervals["complex_upper"]["lower"],"Independent root brackets")
    coarse,b,atom,beta,eta,zeta=(F(config[k]) for k in
        ("coarse","complex_saving","atom","phase_stop","backoff","strict_weakening"))
    need(atom==F(1,1000) and beta==F(1,10**9) and eta==F(1,10**8) and zeta==F(1,10**10),"Retained parameters")
    need(moment(bp,coarse,True)["upper"]<1 and moment(cp,b)["upper"]<1,"Public certified suppliers")
    bill=native_bridge(physical,scalar,cp,coarse,atom)
    public=native_assembly(bill,b,beta,eta,zeta,F(config["public_kappa"]))
    exact_match(author["bit_profile"],bp,"Independent bit profile")
    exact_match(author["complex_profile"],cp,"Independent complex profile")
    exact_match(author["bridge"],bill,"Independent native full finite bills")
    exact_match(author["public_assembly"],public,"Independent native public 47+7")
    saved=rows["public_certificate"]
    aliases={"a_positive":"bit_positive","a_below_b":"complex_above_bit",
             "b_below_one_over32":"complex_below_one_over32","phase_leaf_above_bit":"leaf_saving_above_bit"}
    margin_aliases={"prefix":"balanced_prefix","movement":"coordinate_movement","compact":"compact_phase_layer",
                    "bulk":"bulk_exposure","Gaussian":"Gaussian_arithmetic","scalar":"scalar_work","dimension":"dimension"}
    need(len(saved["assembly"]["strict_constraints"])==47,"Saved native complete constraints")
    for name,value in public["slacks"].items():
        if name.endswith("_above_kappa"):
            actual=margin_aliases[name[:-12]]+"_above_kappa"
        else:actual=aliases.get(name,name)
        need(F(saved["assembly"]["strict_constraints"][actual])==value,"Saved native semantic constraint: "+name)
    for name,value in public["margins"].items():
        need(F(saved["assembly"]["margins"][margin_aliases[name]])==value,"Saved native margin: "+name)
    frontier=F(config["comparison_public_kappa"])
    need(F(rows["frontier_claim"]["kappa"])==frontier,"Pinned actual PR169 claim")
    target=F(config["required_ratio"])*frontier
    need(target==F(308330881,500000000000),"One-percent exact target")
    optimistic=target/(1-target)
    needed_a=target/((1-2*eta)*(1-eta-target))
    needed_b=(needed_a+zeta)/(1-beta)
    needed_coarse=needed_a*(1-OLD)/(1-needed_a)
    needed_fixed=(needed_a-atom*OLD)/(1-atom)
    ordinary_upper=bhi/(1+bhi-OLD)
    supplier_upper=min(ordinary_upper,chi)
    ceiling=supplier_upper/(1+supplier_upper)
    need(ordinary_upper<chi and ceiling<target,"Native paid obstruction")
    z=blo/(1+blo-OLD)*10**12
    theta=F(-(-z.numerator//z.denominator),10**12)
    if theta==blo/(1+blo-OLD):theta+=F(1,10**12)
    refined_bill=native_bridge(physical,scalar,cp,blo,theta)
    refined=native_assembly(refined_bill,clo,beta,eta,zeta)
    z=refined["g"]*10**12
    refined["kappa_12_grid"]=F(-(-z.numerator//z.denominator)-1,10**12)
    exact_match(author["refined_bridge"],refined_bill,"Independent refined atom bills")
    exact_match(author["refined_assembly"],refined,"Independent refined 47+7")
    independent_targets=dict(required_ratio=F(config["required_ratio"]),kappa=target,
        comparison_frontier_kappa=frontier,comparison_frontier_head=config["comparison_public_head"],
        ideal_ordinary_and_complex_requirement=optimistic,retained_ordinary_requirement=needed_a,
        retained_complex_requirement=needed_b,optimal_paid_atom_coarse_requirement=needed_coarse,
        fixed_atom_coarse_requirement=needed_fixed,
        sufficient_1e12_points={name:F(-(-(value*10**12).numerator//(value*10**12).denominator),10**12)
            for name,value in (("ordinary",needed_a),("complex",needed_b),("optimized_coarse_bit",needed_coarse),
                               ("fixed_atom_coarse_bit",needed_fixed))})
    exact_match(author["target"],independent_targets,"Independent one-percent native targets")
    obstruction=dict(bit_ordinary_upper=ordinary_upper,complex_upper=chi,controlling_upper=supplier_upper,
        balanced_upper=ceiling,target_shortfall=target-ceiling,limiting_supplier="bit",
        bit_coarse_gap=needed_coarse-bhi,complex_gap=needed_b-chi,
        scope="All parameters in the retained paid balanced family on these exact fixed profiles; no claim that frame or topology changes are impossible.")
    exact_match(author["obstruction"],obstruction,"Independent all-parameter paid obstruction")
    controls=[]
    def reject(name,call):
        try:call()
        except (ValueError,KeyError,ZeroDivisionError):controls.append(name)
        else:raise ValueError("Negative accepted: "+name)
    reject("fixed suppliers promoted to one-percent target",lambda:native_assembly(refined_bill,clo,beta,eta,zeta,target))
    reject("unpaid preceding atom grid",lambda:native_bridge(physical,scalar,cp,blo,theta-F(1,10**12)))
    reject("virtual reserve collapsed",lambda:native_bridge(physical,dict(scalar,R=physical["physical_R"]),cp,coarse,atom))
    reject("literal scalar bill omitted",lambda:native_assembly(dict(bill,strict_literal_gap=0),b,beta,eta,zeta,public["kappa"]))
    reject("saved profile mass corrupted",lambda:profile_rows(dict(bit,rank_per_vertex=1),physical))
    reject("corrupted fresh bit identity",lambda:pinned_bytes(args.sprint,dict(config["inputs"]["bit"],sha256="0"*64)))
    result=dict(status="PASS_INDEPENDENT_REBUILT168_PAID_CEILING_BELOW_ONE_PERCENT_FLOOR",
        bit_profile=bp,complex_profile=cp,intervals=intervals,bridge=bill,public_assembly=public,
        refined_bridge=refined_bill,refined_assembly=refined,target=independent_targets,obstruction=obstruction,
        input_pins=config["inputs"],source_pins=config["sources"],checked_inputs=22,checked_sources=len(config["sources"]),
        author_certificate_sha256=digest(args.certificate),config_sha256=digest(args.config),
        own_source_sha256=digest(Path(__file__)),negative_controls=controls,
        actual_rebuilt_profile_scope="Both rows and scalar input are fresh producer outputs; every field matches saved source and all recorded export bytes and source hashes are verified. Native finite bit/F2/local-ring review remains independently separate; complex reflection has a separate lane receipt.",
        all_size_contracts=config["conditional_prerequisites"])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(encode(result),indent=2,sort_keys=True)+"\n")
    print("PASS independent rebuilt168 ceiling="+str(ceiling)+" < one-percent floor="+str(target))
    print("All"+str(len(config["sources"]))+" sources/22 inputs/full bills/public and refined47+7; "+str(len(controls))+" negative controls")


if __name__=="__main__":main()
