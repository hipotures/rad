#!/usr/bin/env python3
"""Independently review the portable normalized fused/lifetime arithmetic.

Apache-2.0; prepared for RaD with OpenAI GPT-6.1 Sol assistance.
This imports only the three explicitly distributed independent assembly
modules and stdlib, never the package author's transfer implementation.
The original 141-source, 24-input scientific closure and independently executed
finite proofs are preserved separately. The public arithmetic subset does
not pretend to rerun that full closure or establish a current record.
"""

import argparse
import copy
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

from review_fused_lifetime import (ATOM, BETA, COARSE, COMPLEX, ETA, KAPPA,
    PUBLIC, PUBLIC_HEAD, WEAKENING, digest, encode, exact_match, full_bill,
    independent_derivation, native_assembly, need, pinned_bytes, profiles,
    verify_author_intervals)

IDENTITY = "dcfddaa8ec464b94fc0b0c31d8c5fac9a86c45e6067fcc478753d11f748c331f"
AUTHOR_CONFIG = "e423b802770cb3477ef83598d2ca00acfddfa2b9843e3ece0a72fb61aace119f"
AUTHOR_RECEIPT = "2f040351c0c1f27b11c7d4eba7734658eb014b57c5c0d7da8d8572ed76ce83ba"
HYPOTHESES = "ebf7ca25618b2f97bd426940ba20b13f4b98399473f264ca9591efa4bec75cba"
FINITE_PREREQUISITES = "00a5d6a0646a85a195a26099311ddeaa51b94e37a30956eb6578db7bd78d12de"
FIELDS = {"bit", "physical", "scalar", "bit_frames", "complex_frames",
          "complex_pairs", "transfer_math.py", "verify_transfer.py"}


def scientific_identity(config):
    science = config["scientific_source_bindings"]
    need(science["author_config_sha256"] == AUTHOR_CONFIG
         and config["author_receipt_sha256"] == AUTHOR_RECEIPT,
         "Original independent scientific identity changed")
    need(len(science["sources"]) == science["source_record_count"] == 141
         and len(science["inputs"]) == science["input_record_count"] == 24,
         "Original complete metadata inventory omitted")
    reduced = {section:{key:{"bytes":pin["bytes"], "sha256":pin["sha256"]}
        for key,pin in science[section].items()} for section in ("sources", "inputs")}
    encoded = json.dumps(reduced,sort_keys=True,separators=(",", ":")).encode()
    need(sha256(encoded).hexdigest() == IDENTITY, "Normalized scientific metadata changed")
    for name, expected in (("inherited_hypotheses", HYPOTHESES),
                           ("finite_prerequisites", FINITE_PREREQUISITES)):
        retained = json.dumps(science[name],sort_keys=True,separators=(",", ":")).encode()
        need(sha256(retained).hexdigest() == expected, "Retained proof boundary changed: "+name)
    return science


def verify(directory, config, author):
    need(set(config["files"]) == FIELDS, "Portable arithmetic file inventory")
    science = scientific_identity(config)
    rows = {}
    for name, pin in config["files"].items():
        data = pinned_bytes(directory, pin)
        need(len(data) == pin["bytes"], "Portable byte count: "+name)
        if name not in ("transfer_math.py", "verify_transfer.py"):
            rows[name] = json.loads(data)
            record = science["inputs"][name]
            need(pin["sha256"] == record["sha256"] and pin["bytes"] == record["bytes"],
                 "Actual public fixture differs from original accepted input: "+name)
    parameters = dict(coarse=COARSE,atom=ATOM,complex_saving=COMPLEX,phase_stop=BETA,
        backoff=ETA,strict_weakening=WEAKENING,kappa=KAPPA,
        bit_next_grid_step=F(1,10**12),complex_next_grid_step=F(1,10**12),
        comparison_public_kappa=PUBLIC,required_publication_ratio=F(101,100),
        comparison_public_head=PUBLIC_HEAD)
    exact_match(config["parameters"], parameters, "Portable parameters")
    exact_match(author["source_inputs"], config, "Portable certificate input metadata")
    need(config["candidate_id"] == science["candidate_id"] == author["candidate_id"]
         == "balanced-lifetime-fused-168-170-20261009", "Candidate identity")
    need(config["inherited_hypotheses"] == science["inherited_hypotheses"]
         and config["finite_prerequisites"] == science["finite_prerequisites"],
         "Portable conditional boundaries changed")
    own = independent_derivation(rows["bit"],rows["physical"],rows["scalar"])
    for actual, name in (("bit_profile","bit_profile"),("complex_profile","complex_profile"),
        ("contaminated_bit_rank","contaminated_bit_rank"),("finite_bridge","bridge"),
        ("assembly","assembly"),("numeric_cutoffs","cutoffs"),("kappa","kappa")):
        exact_match(author[actual], own[name], "Public independent "+actual)
    verify_author_intervals(author,own["independent_intervals"])
    return own, rows


def main():
    need(not sys.flags.optimize,"Assertion-disabled Python is unsupported")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--directory",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args = p.parse_args()
    need(not args.output.exists(),"Fresh portable review identity required")
    config_path = args.directory/"transfer-inputs.json"
    author_path = args.directory/"transfer-certificate.json"
    config,author = (json.loads(path.read_text()) for path in (config_path,author_path))
    own, rows = verify(args.directory,config,author)
    controls = []
    def reject(name, call):
        try:
            call()
        except (ValueError,KeyError,ZeroDivisionError):
            controls.append(name)
        else:
            raise ValueError("Negative control accepted: "+name)
    for field,value in (("W",14843),("scalar_roles",12203),("local_scalar",0),("router",0),
        ("C0",1),("old_coarse_reserve",0),("old_leaf_reserve",0),("row_coefficient",1),("row_degree",1)):
        mutation = copy.deepcopy(author["finite_bridge"]);mutation[field] = value
        reject("incorrect full bill "+field,lambda row=mutation:exact_match(row,own["bridge"],"Mutated public bill"))
    for field in ("bit","physical"):
        mutation = copy.deepcopy(rows[field]);mutation["child_histogram"]["1"] += 2;mutation["child_histogram"]["2"] -= 1
        reject("mass-preserving unpaid "+field,lambda row=mutation,key=field:
            profiles(row,rows["physical"]) if key=="bit" else profiles(rows["bit"],row))
    reject("preceding unpaid atom",lambda:full_bill(rows["physical"],rows["scalar"],own["complex_profile"],atom=ATOM-F(1,10**12)))
    reject("next final grid",lambda:native_assembly(own["bridge"],COMPLEX,BETA,ETA,WEAKENING,KAPPA+F(1,10**12)))
    reject("zero complex stop",lambda:native_assembly(own["bridge"],COMPLEX,F(0),ETA,WEAKENING,KAPPA))
    reject("zero paid reserve",lambda:native_assembly(own["bridge"],COMPLEX,BETA,F(0),WEAKENING,KAPPA))
    mutation = copy.deepcopy(author);mutation["bit_moment"]["upper"]="9/10";mutation["bit_moment"]["gap_lower"]="1/10"
    reject("fabricated supplier interval",lambda:verify_author_intervals(mutation,own["independent_intervals"]))
    mutation = copy.deepcopy(config);mutation["scientific_source_bindings"]["source_record_count"] = 140
    reject("original scientific closure shortened",lambda:scientific_identity(mutation))
    for field in ("inherited_hypotheses", "finite_prerequisites"):
        mutation = copy.deepcopy(config)
        mutation[field] = mutation["scientific_source_bindings"][field] = []
        reject("retained boundary omitted "+field,lambda row=mutation:scientific_identity(row))
    reject("public fixture corruption",lambda:pinned_bytes(args.directory,dict(config["files"]["bit_frames"],sha256="0"*64)))
    reject("unsafe public fixture path",lambda:pinned_bytes(args.directory,dict(path="../escape",sha256="0"*64)))
    probe = subprocess.run([sys.executable,"-O",str(Path(__file__).resolve()),"--help"],capture_output=True,text=True)
    need(probe.returncode != 0 and "Assertion-disabled Python" in probe.stderr,"Optimized public review accepted")
    controls.append("assertion-disabled execution")
    output = dict(status="PASS_INDEPENDENT_PORTABLE_ARITHMETIC_HISTORICAL_NONQUALIFYING",
        candidate_id=config["candidate_id"], **own, portable_input_pins=config["files"],
        config_sha256=digest(config_path),certificate_sha256=digest(author_path),
        original_scientific_identity=IDENTITY,original_author_config_sha256=AUTHOR_CONFIG,
        original_author_receipt_sha256=AUTHOR_RECEIPT,checked_public_files=8,
        original_metadata_source_records=141,original_metadata_input_records=24,
        rejected_controls=controls, checker_sha256=digest(Path(__file__)),
        independent_module_sha256={name:digest(Path(__file__).with_name(name)) for name in
            ("review_fused_lifetime.py","review_balanced_unified.py","review_rebuilt168_ceiling.py")},
        PUBLICATION_READY=False,
        scope="Fresh portable full moments and fallback, complete component distribution, full paid bills, 47 strict constraints and seven margins, and cutoffs with eight actual file pins, immutable original metadata and retained hypothesis text. Original 141-source, 24-input byte closure and independent finite executions remain separately preserved scientific evidence; this subset does not rerun them or the live frontier.")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(encode(output),sort_keys=True,indent=2)+"\n")
    print("PASS independent portable arithmetic: "+str(KAPPA)+"; full moments/bills/47+7; "+str(len(controls))+" controls; historical nonqualifying")


if __name__ == "__main__":
    main()
