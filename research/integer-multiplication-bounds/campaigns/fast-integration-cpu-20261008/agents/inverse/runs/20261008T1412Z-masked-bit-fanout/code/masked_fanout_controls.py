#!/usr/bin/env python3
"""Actual ten-rotation controls for repeated-source BIT fanout.

Reimplements the inherited masked F_u identity independently from the
completed RaD report at 6b32837aee0561af85e4efaca21af07b9f2749d2.
Source bits repeat and lie outside the ACTIVE target set. Finite address
checks are not a proof of the inherited fixed-tape cost.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
import time


def program(slots):
    identity = (
        ("rotate", "y", "first", 1),
        ("swap", "t", "b", 0),
        ("rotate", "b", "load_t", 1),
        ("swap", "t", "b", 0),
        ("rotate", "y", "second", 1),
        ("swap", "t", "b", 0),
        ("rotate", "b", "unload_t", -1),
        ("swap", "t", "b", 0),
    )
    return (identity + (("swap", "u", "b", 0),
                        ("rotate", "b", "source", 1),
                        ("swap", "u", "b", 0)) + identity +
            (("swap", "u", "b", 0),
             ("rotate", "b", "source", -1),
             ("swap", "u", "b", 0)))


def execute(state, slots, K, G, sources, inverse=False, rho=0):
    assert len(sources) == slots
    targets = tuple(rho + i*K for i in range(slots))
    assert all(source not in targets for source in sources)
    widths = {"u": slots*G, "t": slots*G, "y": slots*K+rho, "b": slots*G}
    q = dict(zip(("u", "t", "y", "b"), state))
    B = 1 << G
    def digit(field, i):
        return (q[field] >> (i*G)) & (B-1)
    def offset(kind):
        if kind in ("first", "second"):
            return sum((digit("u", i)&1) *
                       (2*digit("t", i) if kind == "first" else 1-2*digit("t", i)) *
                       (1 << targets[i]) for i in range(slots))
        if kind == "source":
            return sum(((q["y"] >> source)&1) << (i*G)
                       for i,source in enumerate(sources))
        return sum((((q["y"] >> targets[i])&1) ^
                    ((digit("u", i)&1) if kind == "unload_t" else 0)) << (i*G)
                   for i in range(slots))
    ops = program(slots)
    for action,target,kind,sign in reversed(ops) if inverse else ops:
        if action == "swap":
            q[target],q[kind] = q[kind],q[target]
        else:
            q[target] = (q[target] + (-sign if inverse else sign)*offset(kind)) % (1 << widths[target])
    return tuple(q[name] for name in ("u", "t", "y", "b"))


def ideal(state, slots, K, sources, rho=0):
    u,t,y,b = state
    return u,t,y ^ sum(((y >> source)&1) << (rho+i*K)
                       for i,source in enumerate(sources)),b


def good(state, slots, K, G, rho=0):
    u,t,y,b = state
    B = 1 << G
    for i in range(slots):
        if ((u >> (i*G))&(B-1)) == B-1 or ((t >> (i*G))&(B-1)) == B-1:
            return False
        guard = ((y >> (rho+i*K))&((1 << K)-1)) >> 1
        if not 2*B <= guard < (1 << (K-1))-2*B:
            return False
    return True


def exhaustive(K, source):
    started = time.monotonic()
    slots,G,rho = 2,1,0
    sources = (source,source)
    widths = (slots*G,slots*G,slots*K,slots*G)
    count = 1 << sum(widths)
    good_count = wrong_bad = 0
    images = set()
    for state in itertools.product(*(range(1 << width) for width in widths)):
        image = execute(state,slots,K,G,sources)
        assert execute(image,slots,K,G,sources,inverse=True) == state
        assert good(image,slots,K,G) == good(state,slots,K,G)
        target = ideal(state,slots,K,sources)
        assert good(target,slots,K,G) == good(state,slots,K,G)
        assert image not in images
        images.add(image)
        if good(state,slots,K,G):
            assert image == target
            good_count += 1
        else:
            wrong_bad += int(image != target)
    assert len(images) == count
    return {"K":K,"source":source,"complete_states":count,"good_states":good_count,
            "wrong_unrepaired_bad_states":wrong_bad,"bijection":True,"explicit_inverse":True,
            "wall_seconds":time.monotonic()-started}


def adversarial(seed, count):
    rng=random.Random(seed)
    tested=good_count=wrong_bad=0
    families=[]
    for slots,G,K,rho,mode in ((4,2,10,0,"one"),(8,3,12,11,"one"),
                               (12,2,10,1,"pairs"),(16,3,12,2,"pairs")):
        widths=(slots*G,slots*G,slots*K+rho,slots*G)
        sources=tuple(rho+1 if mode=="one" else rho+1+(i%2)*K for i in range(slots))
        family_good=family_wrong=0
        B=1 << G
        for trial in range(count):
            state=[rng.randrange(1 << width) for width in widths]
            # Alternate guaranteed-good constructions and dirty-guard boundaries.
            for i in range(slots):
                ut=rng.randrange(B-1) if trial%2==0 else rng.choice((0,B-2,B-1))
                tt=rng.randrange(B-1) if trial%2==0 else rng.choice((0,B-2,B-1))
                state[0]=(state[0]&~((B-1)<<(i*G))) | (ut<<(i*G))
                state[1]=(state[1]&~((B-1)<<(i*G))) | (tt<<(i*G))
                lo,hi=2*B,(1 << (K-1))-2*B
                guard=rng.randrange(lo,hi) if trial%2==0 else rng.choice((lo-1,lo,hi-1,hi))
                word=(guard << 1)|rng.randrange(2)
                shift=rho+i*K
                state[2]=(state[2]&~(((1 << K)-1)<<shift))|(word<<shift)
            state=tuple(state)
            image=execute(state,slots,K,G,sources,rho=rho)
            assert execute(image,slots,K,G,sources,inverse=True,rho=rho)==state
            assert good(image,slots,K,G,rho)==good(state,slots,K,G,rho)
            target=ideal(state,slots,K,sources,rho)
            if good(state,slots,K,G,rho):
                assert image==target
                family_good+=1
            else:
                family_wrong+=int(image!=target)
            tested+=1
        good_count+=family_good;wrong_bad+=family_wrong
        families.append({"slots":slots,"G":G,"K":K,"rho":rho,"source_mode":mode,
                         "good_states":family_good,"wrong_unrepaired_bad_states":family_wrong})
    # Source inside the active set violates the required contract.
    try:
        execute((0,0,0,0),2,5,1,(0,0))
        raise AssertionError("active source was accepted")
    except AssertionError:
        pass
    return {"seed":seed,"states":tested,"good_states":good_count,
            "wrong_unrepaired_bad_states":wrong_bad,"families":families,
            "active_target_source_rejected":True}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True)
    parser.add_argument("--adversarial-per-family",type=int,default=25000)
    args=parser.parse_args();started=time.monotonic()
    results=[]
    for K,source in ((5,2),(6,11)):
        result=exhaustive(K,source);results.append(result)
        print(json.dumps({"exhaustive_completed":result}),flush=True)
    stress=adversarial(2026100842,args.adversarial_per_family)
    result={"run_id":"20261008T1412Z-masked-bit-fanout","status":"PASS",
            "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "inherited_identity":"RaD6b32837a, masked arbitrary-source BIT shear; distinctness removed and explicitly tested",
            "exhaustive":results,"adversarial":stress,"workers":1,"native_threads":1,
            "wall_seconds":time.monotonic()-started}
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status":"PASS","wall_seconds":result["wall_seconds"]}),flush=True)


if __name__=="__main__":
    main()
