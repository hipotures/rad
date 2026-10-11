#!/usr/bin/env python3
"""Why #501 stops at `apply-frame-map` (job 5 post-hoc diagnosis, seconds).

#501's code/apply_retime.py requires sha256(canonical JSON of the freshly built #484 gauge80-kernel42
FULL-WORD) == RETIME-FRAMES.json.gz's `source_word_json_sha256`, with canonical = json.dumps(sort_keys=True,
separators=(',', ':')). This script recomputes that hash for every FULL-WORD of that word under the job 5
run (built independently inside the #484, #496, #497, #500, #501 and #502 replays), compares the portable
CANONICAL-WORD hash those builds record, and tests whether last-bit float differences in the word's three
`report` floats (±K ulps each) could explain the pin.

usage: job5_pr501_word_check.py --run <job5 run> --out <json> [--ulps 8]
"""
import argparse
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path


def canon_sha(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--run', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--ulps', type=int, default=8)
    a = ap.parse_args()
    run = Path(a.run)
    tree = next((run / 'trees').glob('pr-501-*')) / 'research/r489-pooled-retimed-complex'
    pin = json.loads(gzip.decompress((tree / 'data/RETIME-FRAMES.json.gz').read_bytes()))['source_word_json_sha256']
    prov = json.loads((tree / 'provenance/RETIME-FROZEN.json').read_text())
    builds = []
    for p in sorted((run / 'out').glob('**/gauge80-kernel42/split-centres/FULL-WORD.json.gz')):
        w = json.loads(gzip.decompress(p.read_bytes()))
        steps = p.parent.parent / 'STEPS.json'
        cw = json.loads(steps.read_text()).get('canonical_word_sha256') if steps.exists() else None
        builds.append(dict(path=str(p.relative_to(run)), full_word_canonical_sha256=canon_sha(w),
                           gz_file_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                           recorded_canonical_word_sha256=cw))
    # #484-pipeline builds record their CANONICAL-WORD hash in STEPS.json; a word without it (#502's own retimed
    # variant, also named gauge80-kernel42) is listed separately and not counted as a build of #484's word.
    other = [b for b in builds if b['recorded_canonical_word_sha256'] is None]
    builds = [b for b in builds if b['recorded_canonical_word_sha256'] is not None]
    w = json.loads(gzip.decompress((run / builds[0]['path']).read_bytes()))
    keys = ['baseline_b', 'complex_coarse_float', 'gain_percent_float']
    base = [w['report'][k] for k in keys]

    def step(x, n):
        for _ in range(abs(n)):
            x = math.nextafter(x, math.inf if n > 0 else -math.inf)
        return x
    hits, tried = [], 0
    for d in itertools.product(range(-a.ulps, a.ulps + 1), repeat=len(keys)):
        for k, b, n in zip(keys, base, d):
            w['report'][k] = step(b, n)
        tried += 1
        if canon_sha(w) == pin:
            hits.append(list(d))
    distinct = sorted({b['full_word_canonical_sha256'] for b in builds})
    res = dict(pinned_source_word_json_sha256=pin,
               author_provenance=dict(source_word=prov.get('source_word'), source_word_sha256=prov.get('source_word_sha256')),
               builds=builds, other_words_with_this_name=other, distinct_full_word_hashes=distinct,
               distinct_recorded_canonical_word_hashes=sorted({b['recorded_canonical_word_sha256'] for b in builds}),
               pin_matches_any_build=pin in distinct,
               float_ulp_test=dict(fields=keys, ulps=a.ulps, combinations=tried, matches=hits))
    Path(a.out).write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k not in ('builds', 'other_words_with_this_name')}, indent=1))
    print(len(builds), 'builds of #484 gauge80-kernel42;', len(other), 'other word(s) with this name')


if __name__ == '__main__':
    main()
