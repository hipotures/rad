#!/usr/bin/env python3
"""Portable source-only region-build override for lifetime/word policies.

Install before capturing compiler.build or compiler.compile_. The returned
callable recreates exact retained budget assignments from public source;
no selected output DAG/word is read. Candidate matrices/moments remain a
separate gate because lifetime, row and reclamation choices change the word.
"""
from pathlib import Path
import joint_region_search_v3 as region


def install(source,work,configuration):
    config=dict(configuration)
    assert set(config)=={'h','policy','rank_delta','sweeps','limit'}
    assert config['h']in(23,25)and config['policy']in('baseline','rank-first','largest','sparse','late')
    region.initialize(Path(source),Path(work))
    def build(h):
        assert h==config['h']
        return region.build_regions(h,config)
    region.COMPILER.build=build
    return build
