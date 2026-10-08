#!/usr/bin/env python3
"""Positive envelopes using only required descendant common coordinates.

A is the set of designated common points of descendant partial outputs,
which lies inside the original source core C. E(A,V) is positive and nested.
A size threshold may retain source-core equalities at smaller pair-star
nodes and drop them at larger nodes; monotone source unions guarantee
that these mixed labels still nest. Sources remain original triple lines.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from unittest.mock import patch

import finite_target_frames as original
import finite_selected_target_frames as selected
from finite_fast_target_frames import included


def labels(circuit,selected_pairs,threshold=0):
    assert not selected_pairs, "Use --pair-mode none for descendant-common envelopes"
    required={node:0 for node in circuit.active}
    for (common,target),node in circuit.outputs.items():required[node]|=1<<common
    for node in sorted(circuit.active,reverse=True):
        if circuit.args[node]:
            for child in circuit.args[node]:required[child]|=required[node]
    frames={}
    intern={}
    relaxed=extra=eligible=0
    for node in sorted(circuit.active):
        source_core=circuit.core[node]
        target_core=required[node]
        assert target_core and not target_core&~source_core
        vertices=circuit.union[node]
        eligible+=target_core!=source_core
        core=target_core if vertices.bit_count()>=threshold else source_core
        relaxed+=core!=source_core
        extra+=source_core.bit_count()-core.bit_count()
        components=tuple((1<<vertex,0) for vertex in original.bits(vertices&~core))
        frame=original.TargetSpace(circuit.h,core,components)
        frames[node]=intern.setdefault((core,vertices),frame)
        if circuit.args[node]:
            assert all(included(frames[child],frame) for child in circuit.args[node])
    for triple,node in circuit.variables.items():
        assert required[node]==circuit.core[node]
        assert frames[node].dimension==1 and frames[node].basis==((1,0,0,0),)
    pairings=0
    for (common,target),node in circuit.outputs.items():
        frame=frames[node]
        assert frame.core&(1<<common)
        for column in frame.basis:
            assert sum(original.coordinate(frame,column,vertex) for vertex in target)==column[0]
            pairings+=1
    return frames,{"unique_rational_frames":len(intern),"eligible_core_relaxations":eligible,
                   "relaxed_nodes":relaxed,"sum_added_dimensions":extra,"threshold":threshold,
                   "source_triple_lines_checked":len(circuit.inputs),
                   "physical_target_pairings_checked":pairings,"all_original_edges_nested":True,
                   "frame_family":"E(K,V), K descendant common points at large unions and source core below threshold",
                   "nondegeneracy":"Positive common-core total-sum support envelope"}


def main():
    parser=argparse.ArgumentParser(add_help=False)
    parser.add_argument("--core-threshold",type=int,default=0)
    own,remaining=parser.parse_known_args()
    sys.argv=[sys.argv[0]]+remaining
    generator=lambda circuit,pairs:labels(circuit,pairs,own.core_threshold)
    with patch.object(original,"included",included),patch.object(selected,"included",included),patch.object(selected,"labels",generator):
        selected.main()
    output=Path(sys.argv[sys.argv.index("--output")+1])
    result=json.loads(output.read_text())
    for name in (Path(__file__).name,"finite_fast_target_frames.py"):
        result["source_sha256"][name]=sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
    result["frame_generator_override"]="Positive envelopes with required descendant common coordinates"
    result["settings"]["core_threshold"]=own.core_threshold
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")


if __name__=="__main__":
    main()
