#!/usr/bin/env python3
"""Independent conservative scalar bills and fixed-profile limit for fd25adb.

Apache-2.0; prepared for RaD with OpenAI GPT-6.1 Sol assistance.
Only independently authored assembly arithmetic and stdlib are imported.
Finite signed identity, local-ring prime presentations and reflected geometry
remain separate gates. This is a negative supplier assessment, not a new record.
"""
import argparse
from collections import Counter
import copy
from fractions import Fraction as F
import json
from math import prod
from pathlib import Path
import subprocess
import sys

from review_balanced_unified import (BAD, OLD, ceil, complete_profile, digest,
    encode, exact_match, histogram, integer, moment, need, pinned_bytes, thresholds)
from review_rebuilt168_ceiling import native_assembly

CONFIG = "032d797e7c41572c2f8b1559fe48407b91040daa542b09ee03529765677ce890"
HEAD = "fd25adb7fbaa12ee761d02c733c54d1d2a7687ee"
PUBLIC = F(40557,62500000)
COARSE, ATOM, COMPLEX = F(6549403,10**10), F(654536791,10**12), F(6493335,10**10)
BETA, ETA, ZETA = F(1,10**9), F(1,10**8), F(1,10**10)


def components(row, expected):
    profile = complete_profile(row, expected, component=True)
    h,v,R,physical,pairs,loss = (integer(row[k],k) for k in
        ("h","v","R","physical_R","pairs","loss"))
    sinks=integer(row.get("sinks",0),"sinks")
    need(physical == R-pairs-sinks and profile["W"] == 2*v+physical,
         "Physical alias/sink role stock")
    need(profile["m"] == 3*h and profile["m"]*profile["W"]-profile["mass"]
         == row["deficit_per_vertex"] == 2*v-3*loss,"Complete telescoping deficit")
    return profile


def bridge(physical,scalar,cp,*,widened):
    h,v,R,c,q,M = (integer(scalar[k],k,1) for k in
        ("h","v","R","c","q","total_M_operations"))
    need((h,v,R,c,q,M,scalar["matched"]) == (22,1320,13606,20686,3157,32972,10237),
         "Actual fd25adb scalar inventory")
    need(R == c+q-scalar["matched"] == physical["R"],"Virtual scalar roles")
    m=cp["m"]; half=m//2
    V=(1<<(m-1+(half-1)**2))*prod((1<<(2*i))-1 for i in range(1,half))
    W,s,N=V*cp["W"],V*cp["mass"],V*v
    base=4*(c+v)+10*v+4*h*v+4*h*h+8*h+8+2*h+8*R*v*(M+16)+32*v
    target_shears=2*physical["sinks"]*7
    D=target_shears+M
    need(3*(q-physical["sinks"]+M)<1<<18,"Conservative signed half-read envelope")
    digits=2*D+3 if widened else 0
    primitives=4*D if widened else 0
    local=base+8*R*v*digits+primitives
    logical=3*V*local+8*W+4*N+8*m*R*V
    router=64*(m+1)**3*(logical+1)*(W+1)**2
    E=64*(W+m+router+1)**3
    literal=2*router*W*W+8*s+4*W+4+32*m
    B=s+E; C0=32*m*B*B
    degree=1
    while m**degree<=2*cp["maxchild"]**degree:degree+=1
    coefficient=degree*W.bit_length()+9909+252
    A=(1-ATOM)*COARSE+ATOM*OLD
    result=dict(V=V,W=W,s=s,N=N,m=m,maxchild=cp["maxchild"],
        physical_roles=physical["physical_R"],scalar_roles=R,reuse_pairs=physical["pairs"],
        sinks=physical["sinks"],base_local_scalar=base,additional_event_bound=D,
        additional_target_shears=target_shears,additional_readout_digits=digits,
        additional_primitive_bill=primitives,readout_digit_bound=M+16+digits,
        local_scalar=local,logical_scalar=logical,router=router,E=E,literal=literal,
        B=B,C0=C0,C1=1,strict_literal_gap=E-literal,
        induction_gap=2*B*(m-cp["maxchild"])-s-E,guard_gap=C0-2*B-18,
        halving_degree=degree,wire_bits=W.bit_length(),complex_coefficient=degree*W.bit_length(),
        old_coarse_reserve=9909,old_leaf_reserve=252,row_coefficient=coefficient,
        row_degree=70000,row_gap=F(70000)-F(51*coefficient,25),suffix_slope=280000,
        ordinary_saving=A,atom=ATOM,coarse=COARSE,old=OLD,adapter_gap=ATOM-A,
        internal_row_gap=1-A-ATOM,fixed_odd_divisor=3)
    need(all(result[k]>0 for k in ("strict_literal_gap","induction_gap","guard_gap",
        "row_gap","adapter_gap","internal_row_gap")),"Full conservative paid bridge")
    return result


def root_bracket(profile,points,rare=False):
    lo,hi=(F(point,10**12) for point in points)
    lower,upper=moment(profile,lo,rare),moment(profile,hi,rare)
    need(lower["upper"]<1<upper["lower"],"Full moment root separation")
    return dict(lower=lo,upper=hi,accepted_moment=lower,rejected_moment=upper)


def events(rows):
    inventories=[]
    P=(1<<61)-1; half=(P+1)//2
    for direction in ("forward_events","reflected_events"):
        inventory=Counter()
        for event in rows[direction]:
            need(isinstance(event,list) and event,"Literal event encoding")
            kind=event[0];inventory[kind]+=1
            if kind in ("op","inj","ysh","kd"):
                need(event[3] in (-1,1),"Nonunit literal elementary operation")
            if kind == "yw":
                need(event[3] in (half,P-half),"Nonhalf additional pivot shear")
        inventories.append(dict(inventory))
    need(inventories[0] == inventories[1] == dict(centre=22,inj=2640,kd=1320,
        ktr=660,op=65714,read=16657,ysh=588,yw=115),"Complete two-orientation event count")
    stars=rows["sink_map"]
    need(len(stars)==42 and all(len(z["T"])==8 and z["c"] in z["T"]
        and z["coeff"] in ("1/2","-1/2") for z in stars),"Actual unit target stars")
    targets=[t for z in stars for t in z["T"]]
    need(len(targets)==len(set(targets)) and sum(len(z["writes"]) for z in stars)==115,
         "Disjoint target stars and literal half-writes")
    primitive=65714+2640+588+2*115
    need(primitive<=4*(20686+1320) and 3*(3157-42+115)<1<<15,
         "Actual primitive and signed half-read envelope")
    return dict(actual_event_inventory=inventories[0],effective_half_reads=3230,
                actual_primitive_bill=primitive)


def source_constraints(saved,assembly):
    aliases=dict(a_positive="bit_positive",a_below_b="complex_above_bit",
        b_below_one_over32="complex_below_one_over32",phase_leaf_above_bit="leaf_saving_above_bit")
    margins=dict(prefix="balanced_prefix",movement="coordinate_movement",compact="compact_phase_layer",
        bulk="bulk_exposure",Gaussian="Gaussian_arithmetic",scalar="scalar_work",dimension="dimension")
    need(len(saved["strict_constraints"])==47 and len(saved["margins"])==7,"Public full 47+7 inventory")
    for name,value in assembly["slacks"].items():
        key=margins[name[:-12]]+"_above_kappa" if name.endswith("_above_kappa") else aliases.get(name,name)
        need(F(saved["strict_constraints"][key])==value,"Named public constraint "+name)
    for name,value in assembly["margins"].items():
        need(F(saved["margins"][margins[name]])==value,"Named public margin "+name)


def source_bills(saved,bill,assembly):
    sections={"complex":dict(N=bill["N"],W=bill["W"],s=bill["s"],m=bill["m"],
        maxchild=bill["maxchild"],invocations_per_stage=bill["V"],
        local_group_upper=bill["local_scalar"],logical_group_upper=bill["logical_scalar"],
        scalar_group_upper=bill["router"],finite_group_router_upper=bill["router"],
        original_X_involution_scalar_group_upper=32*1320,halving_degree=bill["halving_degree"],
        wire_bits=bill["wire_bits"],coefficient_bound=26,coefficient_denominator_divides=6,
        auxiliary_banks_after_sharing=1,stages=3),
        "bit_uniform":dict(atom_beta=ATOM,coarse_saving=COARSE,old_atom_saving=OLD,
            ordinary_saving=bill["ordinary_saving"]),
        "rows":dict(coefficient=bill["row_coefficient"],complex_coefficient=bill["complex_coefficient"],
            degree=bill["row_degree"],degree_gap=bill["row_gap"],suffix_slope=bill["suffix_slope"]),
        "semantic":{key:bill[key] for key in ("B","C0","C1","E","fixed_odd_divisor",
            "induction_gap","strict_literal_gap")}}
    sections["semantic"]["literal_charge"]=bill["literal"]
    for section,values in sections.items():
        for key,value in values.items():
            exact_match(saved["finite_bridge"][section][key],value,"Named public bill "+section+"."+key)
    exact_match(saved["finite_bridge"]["conservative_old_coarse_row_reserve"],9909,"Public old row reserve")
    exact_match(saved["finite_bridge"]["ordinary_leaf_row_degree"],252,"Public ordinary leaf reserve")
    parameters=dict(C0=bill["C0"],C1=1,a_bit=assembly["a"],a_complex=assembly["b"],
        actual_bit_saving=bill["ordinary_saving"],alpha_squared_power=assembly["r"],
        **{key:assembly[key] for key in ("beta","c","delta","epsilon","eta","kappa",
            "lambda_","lambda_prime","q","sigma","tau")})
    exact_match(saved["assembly"]["parameters"],parameters,"All public assembly parameters")
    exact_match(saved["assembly"]["recurrence"],dict(internal=assembly["internal"],
        leaf=assembly["leaf"],reservations=1-assembly["c"]),"All public recurrence exponents")
    exact_match(saved["assembly"]["minimum_margin"],assembly["g"],"Public minimum margin")
    exact_match(saved["assembly"]["absorption_gap"],assembly["absorption_gap"],"Public logarithm absorption")


def main():
    need(not sys.flags.optimize,"Assertion-disabled Python is unsupported")
    if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(0)
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sprint",type=Path,default=Path(__file__).resolve().parents[3])
    p.add_argument("--config",type=Path,required=True)
    p.add_argument("--certificate",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args();need(not args.output.exists(),"Fresh review identity required")
    need(digest(args.config)==CONFIG,"Frozen terminal-sink source identity")
    config=json.loads(args.config.read_text());author=json.loads(args.certificate.read_text())
    need(config["source_head"]==HEAD and len(config["sources"])==86 and len(config["inputs"])==24,
         "Complete immutable fd25adb source/input inventory")
    raw={name:pinned_bytes(args.sprint,pin) for name,pin in config["inputs"].items()}
    for section in ("sources","inputs"):
        for name,pin in config[section].items():
            data=pinned_bytes(args.sprint,pin)
            need(len(data)==pin["bytes"],"Pinned byte count "+name)
    rows={name:json.loads(data) for name,data in raw.items()}
    pins=list(config["sources"].values())+list(config["inputs"].values())
    def declared(name,expected):
        need(any(pin["path"].endswith("/"+name) and pin["sha256"]==expected for pin in pins),
             "Declared native source/input absent: "+name)
    for name,value in rows["public_certificate"]["source_sha256"].items():declared(name,value)
    for key in ("native_protocol","body_protocol"):
        protocol=rows[key]
        need(protocol["source_head"]==HEAD,"Fresh native producer head")
        for name,value in protocol["source_pins"].items():declared(name,value)
        for name,pin in protocol["input_pins"].items():declared(name,pin["sha256"])
    exact_match(author["source_pins"],config,"Author source identity")
    need(author["config_sha256"]==CONFIG,"Author config identity")
    bit,physical,scalar=(rows[k] for k in ("bit","physical","scalar"))
    need(rows["native_profile"]==physical,"Actual regenerated complete sink profile")
    graph,word=rows["body_graph"],rows["body_word"]
    need(len(graph["args"])-graph["v"]==scalar["c"] and len(graph["roots"])==scalar["q"]
        and len(word["ops"])==len(word["opcoeff"])==scalar["total_M_operations"]
        and len(rows["body_physical_pairs"])==physical["pairs"]
        and all(isinstance(pair,list) and len(pair)==2 and all(k in (-1,1) for k in pair)
                for pair in word["opcoeff"]),"Actual raw body/root/operation inventory")
    bp=components(bit,(72,21812,1568528,60));cp=components(physical,(66,13894,915684,20))
    need((bit["R"],bit["physical_R"],bit["pairs"],physical["R"],physical["physical_R"],
        physical["pairs"],physical["sinks"])==(20052,18292,1760,13606,11254,2310,42),"Native finite stocks")
    need(F(2*bp["m"]**3,1<<80)<BAD and
         bp["mass"]+BAD*32*bp["m"]**2*bp["edges"]<bp["m"]*bp["W"],"Complete binary fallback envelope")
    for name,value in dict(coarse=COARSE,atom=ATOM,complex_saving=COMPLEX,phase_stop=BETA,
        backoff=ETA,strict_weakening=ZETA,public_kappa=PUBLIC,required_ratio=F(101,100)).items():
        need(F(config[name])==value,"Exact retained supplier/parameter "+name)
    need(F(rows["public_certificate"]["kappa"])==PUBLIC,"Public source coefficient")
    inventory=events(rows)
    br=root_bracket(bp,(654940331,654940332),True)
    cr=root_bracket(cp,(649333576,649333577))
    need(moment(bp,COARSE,True)["upper"]<1 and moment(cp,COMPLEX)["upper"]<1,
         "Pinned source suppliers have full strict moments")
    source=bridge(physical,scalar,cp,widened=False);paid=bridge(physical,scalar,cp,widened=True)
    sa=native_assembly(source,COMPLEX,BETA,ETA,ZETA,PUBLIC)
    pa=native_assembly(paid,COMPLEX,BETA,ETA,ZETA,PUBLIC)
    source_constraints(rows["public_certificate"]["assembly"],sa)
    source_bills(rows["public_certificate"],source,sa)
    own=dict(bit_profile=bp,complex_profile=cp,source_bridge=source,paid_bridge=paid,
        source_assembly=sa,paid_assembly=pa,numeric_cutoffs=thresholds(paid,pa),**inventory)
    for key,value in own.items():exact_match(author[key],value,"Independent sink "+key)
    for name,independent in (("bit_root",br),("complex_root",cr)):
        need(F(author[name]["lower"])==independent["lower"] and
             F(author[name]["upper"])==independent["upper"],"Native bracket endpoints")
        for endpoint in ("accepted_moment","rejected_moment"):
            lo,hi=(F(author[name][endpoint][k]) for k in ("lower","upper"))
            need(lo<=independent[endpoint]["lower"]<=independent[endpoint]["upper"]<=hi,
                 "Author bracket enclosure")
    target=PUBLIC*F(101,100);needed=target/((1-2*ETA)*(1-ETA-target))
    requirements=dict(ideal_ordinary_complex=target/(1-target),ordinary=needed,
        complex=(needed+ZETA)/(1-BETA),optimized_coarse=needed*(1-OLD)/(1-needed))
    target_record=dict(kappa=target,required_ratio=F(101,100),requirements=requirements,
        sufficient_1e12_points={k:F(ceil(v*10**12),10**12) for k,v in requirements.items()})
    exact_match(author["target"],target_record,"Independent fd25adb one-percent requirements")
    ordinary_upper=br["upper"]/(1+br["upper"]-OLD);controlling=min(ordinary_upper,cr["upper"])
    ceiling=controlling/(1+controlling)
    need(ceiling<target,"Every-reserve fixed-profile obstruction")
    for key,value in dict(ordinary_upper=ordinary_upper,complex_upper=cr["upper"],
        controlling_upper=controlling,balanced_upper=ceiling,shortfall=target-ceiling).items():
        exact_match(author["fixed_profile_obstruction"][key],value,"Independent supplier ceiling "+key)
    controls=[]
    def reject(name,call):
        try:call()
        except (ValueError,KeyError,ZeroDivisionError):controls.append(name)
        else:raise ValueError("Negative control accepted: "+name)
    reject("sinks counted as aliases only",lambda:components(dict(physical,sinks=0),(66,13894,915684,20)))
    reject("deleted sinks returned to wire stock",lambda:components(dict(physical,W_per_vertex=13936),(66,13894,915684,20)))
    reject("virtual scalar roles collapsed",lambda:bridge(physical,dict(scalar,R=11254),cp,widened=True))
    reject("one-percent coefficient on fixed suppliers",lambda:native_assembly(paid,COMPLEX,BETA,ETA,ZETA,target))
    reject("paid literal guard omitted",lambda:native_assembly(dict(paid,strict_literal_gap=0),COMPLEX,BETA,ETA,ZETA,PUBLIC))
    reject("public source byte changed",lambda:pinned_bytes(args.sprint,dict(config["inputs"]["physical"],sha256="0"*64)))
    for field,value in (("local_scalar",source["local_scalar"]),("additional_readout_digits",33560),
                        ("readout_digit_bound",32988),("row_coefficient",1)):
        changed=copy.deepcopy(paid);changed[field]=value
        reject("conservative bill omitted "+field,lambda row=changed:exact_match(encode(row),paid,"Mutated paid bill"))
    probe=subprocess.run([sys.executable,"-O",str(Path(__file__).resolve()),"--help"],capture_output=True,text=True)
    need(probe.returncode!=0 and "Assertion-disabled Python" in probe.stderr,"Optimized execution accepted")
    controls.append("assertion-disabled execution")
    output=dict(status="PASS_INDEPENDENT_CONDITIONAL_SINK_BILLS_AND_FIXED_PROFILE_LIMIT",
        source_head=HEAD,config_sha256=CONFIG,author_receipt_sha256=digest(args.certificate),
        checker_sha256=digest(Path(__file__)),source_records=86,input_records=24,
        **own,independent_bit_root=br,independent_complex_root=cr,target=target_record,
        fixed_profile_ceiling=ceiling,target_shortfall=target-ceiling,rejected_controls=controls,
        PUBLICATION_READY=False,
        scalar_scope="Unit target shears add at most one numerator bit. Additive half-shears require a common dyadic refinement and add at most two cleared-numerator bits. The bound pays 2D+3 extra digits and 4D primitives while retaining every base charge. Extra operations introduce no odd denominator beyond the retained factor 3. Exact incoming-grid operations, projectors and child returns remain inherited contracts.",
        review_boundary="Raw events, component counts, full moments/fallback, scalar/precision/router/row bills, named public47+7, widened47+7 and cutoffs are freshly recomputed. Signed all-column identity, finite odd-prime eligibility and literal reflected geometry are separate prerequisites; no saved verdict establishes them here. Source fd25adb comparison is historical and is not a live frontier refresh.")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(encode(output),sort_keys=True,indent=2)+"\n")
    print("PASS independent conservative sink bills: L="+str(paid["local_scalar"])+
          "; 47+7; fixed-profile ceiling "+str(ceiling)+"; "+str(len(controls))+" controls")


if __name__=="__main__":main()
