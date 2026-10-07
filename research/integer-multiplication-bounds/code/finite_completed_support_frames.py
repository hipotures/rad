#!/usr/bin/env python3
"""Complete support envelopes using coordinates unused by descendant targets.

V* is the complement of all descendant excluded-pair endpoints. It contains
the formal source union. E(C,V*) is positive, nests toward parent gates, and
keeps all output targets orthogonal. At inputs V* equals the source triple.
No alternating target-kernel direction is added by this family.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys
from unittest.mock import patch

import finite_target_frames as original
import finite_selected_target_frames as selected
from finite_fast_target_frames import included,incident_table


def labels(circuit,selected_pairs):
    assert not selected_pairs, "Use --pair-mode none for support completion"
    h=circuit.h
    pairs=tuple(combinations(range(h),2))
    ids={pair:index for index,pair in enumerate(pairs)}
    table=incident_table(pairs)
    omitted={node:0 for node in circuit.active}
    for (common,target),node in circuit.outputs.items():
        omitted[node]|=1<<ids[tuple(vertex for vertex in target if vertex!=common)]
    for node in sorted(circuit.active,reverse=True):
        if circuit.args[node]:
            for child in circuit.args[node]:omitted[child]|=omitted[node]
    frames={}
    intern={}
    enlarged=extra=maximum_extra=0
    for node in sorted(circuit.active):
        core=circuit.core[node]
        edges=omitted[node]
        incident=0
        for index,byte in enumerate(edges.to_bytes((edges.bit_length()+7)//8,"little")):
            incident|=table[index][byte]
        vertices=((1<<h)-1)&~incident
        assert not core&incident
        assert not circuit.union[node]&~vertices
        delta=(vertices&~circuit.union[node]).bit_count()
        enlarged+=bool(delta)
        extra+=delta
        maximum_extra=max(maximum_extra,delta)
        components=tuple((1<<vertex,0) for vertex in original.bits(vertices&~core))
        frame=original.TargetSpace(h,core,components)
        frames[node]=intern.setdefault((core,vertices),frame)
        if core.bit_count()==3:assert not components
        if circuit.args[node]:
            assert all(included(frames[child],frame) for child in circuit.args[node])
    for triple,node in circuit.variables.items():
        assert frames[node].core==sum(1<<vertex for vertex in triple)
        assert frames[node].dimension==1 and frames[node].basis==((1,0,0,0),)
    pairings=0
    for (common,target),node in circuit.outputs.items():
        frame=frames[node]
        assert frame.core&(1<<common)
        for column in frame.basis:
            assert sum(original.coordinate(frame,column,vertex) for vertex in target)==column[0]
            pairings+=1
    return frames,{"unique_rational_frames":len(intern),"completed_nodes":enlarged,
                   "sum_added_coordinates":extra,"maximum_added_coordinates":maximum_extra,
                   "source_triple_lines_checked":len(circuit.inputs),
                   "physical_target_pairings_checked":pairings,"all_original_edges_nested":True,
                   "frame_family":"E(C,V*) with V* avoiding every descendant excluded-pair endpoint",
                   "nondegeneracy":"Positive common-core total-sum support envelope"}


def main():
    with patch.object(original,"included",included),patch.object(selected,"included",included),patch.object(selected,"labels",labels):
        selected.main()
    output=Path(sys.argv[sys.argv.index("--output")+1])
    result=json.loads(output.read_text())
    for name in (Path(__file__).name,"finite_fast_target_frames.py"):
        result["source_sha256"][name]=sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
    result["frame_generator_override"]="Positive coordinate support completion from descendant targets"
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")


if __name__=="__main__":
    main()
