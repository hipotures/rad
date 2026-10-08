#!/usr/bin/env python3
"""Fresh actual-role position refinements at the newly better cutoff two.

The frozen structured candidate generator and exact direct-envelope
evaluator are reused. Prior association rules0/1 are normalized to their
identical canonical graph before exclusion, so the completed cutoff and
association controls are not evaluated again under different case IDs.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

import finite_singleton_successor as direct
from finite_singleton_structured import structured


def candidates(anchor, prior):
    assert anchor['base'] == 2
    normalized=[]
    for protocol in [prior,*[json.loads((path/'protocol.json').read_text()) for path in direct.EXTRA_RUNS]]:
        for row in protocol['candidate_definitions']:
            if row.get('sum_rule_early',0) in (0,1) and row.get('sum_rule_late',0) in (0,1):
                base=2 if row['base']==3 else row['base']
                normalized.append(dict(candidate_id=direct.queue.identity(row['h'],base,row['positions'])[1]))
    amended=dict(prior,candidate_definitions=[*prior['candidate_definitions'],*normalized])
    rows,excluded=structured(anchor,amended)
    direct.CONFIGURATION.update(cutoff_two_refinement_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        normalized_prior_entries=len(normalized),semantic_exclusion='Local rule1 exactly equals balanced rule0; cutoff3 equals2 on completed h50 recipes; normalize before costly full evaluation',
        refinement_scope='New singleton positions at cutoff2, frozen exact graph/envelope/flow/compiler/target evaluator')
    return rows,excluded


if __name__=='__main__':
    direct.successor=candidates
    if '--target-cases' not in sys.argv:sys.argv.extend(['--target-cases','450'])
    direct.main()
