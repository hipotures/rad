#!/usr/bin/env python3
"""Bind the supplemental body-generator closure without changing 86/24.

Apache-2.0; prepared for RaD with OpenAI GPT-6.1 Sol assistance.
This verifies bytes and complete declared producer provenance. It does not
execute the finite construction or replace independent geometry/identity gates.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

from review_balanced_unified import digest, need, pinned_bytes


def main():
    need(not sys.flags.optimize,"Assertion-disabled Python is unsupported")
    if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(0)
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sprint",type=Path,default=Path(__file__).resolve().parents[3])
    p.add_argument("--config",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args();need(not args.output.exists(),"Fresh recovery identity required")
    config=json.loads(args.config.read_bytes())
    raw={name:pinned_bytes(args.sprint,pin) for name,pin in config["files"].items()}
    for name,pin in config["files"].items():need(len(raw[name])==pin["bytes"],"Byte count "+name)
    original=json.loads(raw["arithmetic_config"])
    producer=json.loads(raw["body_regeneration"])
    protocol=json.loads(raw["body_protocol"])
    need(len(original["sources"])==86 and len(original["inputs"])==24,"Original identity changed")
    need(producer["source_head"]==protocol["source_head"]==config["source_head"],"Body source revision")
    need(producer["input_pins"]==protocol["input_pins"] and
         producer["source_pins"]==protocol["source_pins"],"Body producer provenance changed")
    need(producer["driver_sha256"]==sha256(raw["body_driver"]).hexdigest(),"Actual body generator omitted")
    records=list(original["sources"].values())+list(original["inputs"].values())
    for name,expected in producer["source_pins"].items():
        need(any(pin["path"].endswith("/"+name) and pin["sha256"]==expected for pin in records),
             "Body generator source missing: "+name)
    for name,expected in producer["input_pins"].items():
        need(any(pin["path"].endswith("/"+name) and pin["sha256"]==expected["sha256"]
            and pin["bytes"]==expected["bytes"] for pin in records),"Body generator output missing: "+name)
    result=dict(status="PASS_SUPPLEMENTAL_SINK_BODY_GENERATOR_RECOVERY_BINDING",
        source_head=config["source_head"],files=config["files"],original_source_records=86,
        original_input_records=24,additional_source_records=1,additional_input_records=1,
        body_generator_sha256=producer["driver_sha256"],checked_body_sources=len(producer["source_pins"]),
        checked_body_outputs=len(producer["input_pins"]),checker_sha256=digest(Path(__file__)),
        scope="Supplemental body-driver and regeneration-receipt binding closes source recovery for those native inputs. The unchanged 86/24 arithmetic identity is retained separately. The original body protocol lacked its driver hash, but its separately saved regeneration receipt pins the actual driver and has identical complete source/input pins. No finite identity, local-ring or reflected geometry gate is re-executed here.")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("PASS supplemental sink recovery: unchanged 86/24 plus one body driver and one producer receipt")


if __name__=="__main__":main()
