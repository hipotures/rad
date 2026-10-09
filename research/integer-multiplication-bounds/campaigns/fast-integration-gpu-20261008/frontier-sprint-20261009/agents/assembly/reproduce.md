# Reproduce the frozen placement assembly

Prerequisites: Python 3 with the standard library. Recovering missing predecessor
files additionally requires an already authenticated GitHub CLI. No numerical
package, machine-specific path, installed research package or model is required.
Run without Python `-O`. Library thread pools were bounded to one in the recorded
runs; the finite regeneration is sequential because its stages depend on each
other. Source acquisition uses at most four read workers.

The frame witness is owned by the placement lane. Its SHA-256 is
`f02a59311c667316b1f2e21916cebf71c58f79fbfbd3a126a24743d1d7ff016a`.
Use the preserved `frames.json` of `live161-components-converged`; an archived
gzip copy must be decompressed intact before use. This document does not claim
that ignored live files exist in a new Git clone.

From any directory, replace the following paths with the paths to the retrieved
assembly files and the frozen frame witness. All outputs must be fresh paths.

```bash
python3 /path/to/assembly/code/fetch_pinned_source.py \
  --pin /path/to/assembly/configs/placement-pin.json \
  --output /path/to/disposable/predecessor-source --workers 4

python3 /path/to/assembly/code/certify_placement.py \
  --source /path/to/disposable/predecessor-source \
  --frames /path/to/frozen/frames.json \
  --pin /path/to/assembly/configs/placement-pin.json \
  --output /path/to/disposable/fresh-certificate

python3 /path/to/assembly/code/check_negative_controls.py \
  --output /path/to/disposable/fresh-negative-controls.json
```

The source recovery helper reads only 28 allowlisted files (1,027,490 bytes)
from `eumemic/integer-mult-bounds` at
`d14e29157bc905be1ced0776dd893d0714013f3a`; it verifies every SHA-256 before
the certifier imports code. A source pin is a reconstruction identity, not
evidence of independent mathematical review. Apache-2.0 licenses and all source
notices are included among the recovered files.

The certifier reconstructs the signed complex DAG from its pinned module
sources, carrier matching and exact gauge selection. It then reads the frozen
changed frames, reconstructs all role/target chains and compensated aliases,
and executes the forward signed dirty replay. It separately regenerates the
unchanged bit graph, frames, word and profile from the retained pair module and
carrier arcs, and runs its independent exact-integer checker. The complete
fresh histograms feed the exact supplier and finite bridge calculations.

Expected result: `PASS finite suppliers and 47+7` with
`kappa=296187231/500000000000`. The complex accepted grid point is
`74320127/125000000000`, and its successor by `1/10^12` is rigorously rejected.
The bit coarse saving is `5936323/10^10`; its full fallback moment contracts.
The row coefficient is 12,320 and its reserved degree is 70,000. The 13 cheap
entry-point/strict-assembly controls must all be rejected.

Recorded coverage: the complete certifier was run against the immutable source
snapshot and again against a clean export containing only the 28 pinned files.
Their supplier, bridge and assembly mathematics are exactly equal. The source
recovery helper was separately run against GitHub and all bytes match the clean
export's manifest. These are local tests; no upstream PR was created.

Independent forward, exact signed scalar, reflected geometry, paid-incidence
and arithmetic review commands belong to the baseline and geometry lanes. Run
those checkers as specified in their reproduction files before accepting a new
modified witness. The broader upstream suite and scoped Lean checks are also
separate gates. Finite replay and exact arithmetic do not prove the inherited
all-size analytic, uniform-recursion, semantic-grid or tape contracts.

## Independent balanced composition review

The newer reviewer imports only the standard library. Restore all seven
finite inputs and all 75 predecessor source files at the relative paths in
`agents/transfer/configs/unified-first.json` under one disposable sprint root.
The source pins identify PR161 and the immutable mathematical PR163 snapshot;
each file is checked before arithmetic. Preserve the author certificate at
`work/transfer/20261009T0820-unified-first/receipt.json`. Its SHA-256 is
`21112e3b9a63ca1ded2c3542c3987ab51ddcded6c8d1a3763228ce5ba803e639`.
Complete archived receipts are evidence, not replacements for their finite
inputs. The source/input inventory and recovery classification are retained
in the artifact manifest.

Source recovery alone was also exercised through the authenticated GitHub
CLI using read-only contents requests at the exact revisions:

```bash
python3 /path/to/assembly/code/fetch_review_sources.py \
  --config /path/to/transfer/configs/unified-first.json \
  --output /path/to/fresh-restored-sprint --workers 4
```

This places the 75 files at their pinned relative paths. Restore the separate
seven finite inputs before running the independent reviewer; the recovery
helper does not substitute source histories for changed frame witnesses.

From any working directory, run:

```bash
python3 /path/to/assembly/code/review_balanced_unified.py \
  --sprint /path/to/restored-sprint \
  --config /path/to/restored-sprint/agents/transfer/configs/unified-first.json \
  --certificate /path/to/restored-sprint/work/transfer/20261009T0820-unified-first/receipt.json \
  --output /path/to/fresh-independent-review.json
```

Expected: `PASS: kappa=594087017/1000000000000`, all 47+7, 75 source pins,
seven input pins and 20 rejected controls. The first review and a clean
84-file (14,586,403-byte) export both passed in approximately 0.31 seconds;
all mathematical, hash, interval and control fields match exactly. The
reviewer reconstructs complex component counts and recomputes binary totals
and full moments. Actual independent binary frame/F2/dual-Gram replay belongs
to the baseline lane, and complemented signed complex reflection belongs to
the geometry lane. These gates cannot be replaced by this inexpensive check.

The fixed mathematical comparison to PR163 is strict. A subsequently observed
draft PR165 claim exceeds this first unified value; no record publication
script is justified by this receipt alone. Retained all-size routing,
restoration, analytic, precision and setup contracts remain explicit.

## Profile-conditional ceiling against draft PR165

The negative ceiling assessment uses the immutable batch2 singleton bit
profile and the polished unequal-operation-pair complex profile. It imports
only the independent interval helper above and does not claim finite
acceptance of either new frame set.

```bash
python3 /path/to/assembly/code/assess_balanced_ceiling.py \
  --bit-profile /path/to/batch2/profile.json \
  --bit-frames /path/to/batch2/frames.json \
  --complex-profile /path/to/polished/physical-profile.json \
  --complex-frames /path/to/polished/frames.json \
  --output /path/to/fresh-ceiling-assessment.json
```

Expected exact optimistic balanced ceiling:
`594608517/1000594608517`, below the observed draft PR165 claim. The retained
backoffs require complex saving strictly above approximately
`0.000594625848498`, with sufficient 12-digit grid `594625849/10^12`.
This excludes only the identified profile pair under the paid atom and
balanced formulas. Further frame searches or a different word have their own
identities and are not covered by this ceiling.
# Frozen fused/lifetime composition

Run from the sprint root with Python 3.11+ and the standard library.
Restore the exact upstream revisions and explicit source bytes named in
`agents/transfer/configs/lifetime-fused-168-170.json`, plus the ten
supplemental reviewer/code/proof pins in
`agents/assembly/configs/fused-lifetime-review-binding.json`.
Use GitHub CLI acquisition at the original immutable revisions; never
replace them by a moving pull-request head. The source inventories retain
the PR117 LICENSE/NOTICE/SOURCE/DAG/replayed closure and PR170 notices.
The source-clean test below was exercised from those pinned bytes; it is
not a claim that every upstream acquisition route was retested in this lane.

Frozen bit fixtures and deterministically reconstructed exports are preserved
under `agents/bit/candidates/binary-168-paired-lifetime-p12/`; its reproduction
recipe regenerates all five export bytes and replays the intact archived plan.
The complete coherent complex input is preserved as whole gzip files under
`agents/placement/evidence/pr168-placement-20261009T092200Z/`
`fused168-joint-raise-frozen-20261009T0937Z/`. Restore each file to its
original relative location recorded by the author configuration and verify
the decoded SHA-256/size. All nine complex files and all four bit fixtures
were checked against the original frozen bytes by this lane.
Independent finite receipts and their executed sources are given by the
supplemental binding; their full rerun commands belong to the baseline,
signed and geometry lane reports. Arithmetic and identity binding are not
replacement finite executions.

```bash
python3 agents/assembly/code/review_fused_lifetime.py \
  --config agents/transfer/configs/lifetime-fused-168-170.json \
  --certificate work/transfer/20261009T-lifetime-fused-168-170/receipt.json \
  --output work/assembly/reproduced-fused-arithmetic/review.json

python3 agents/assembly/code/bind_fused_reviews.py \
  --config agents/transfer/configs/lifetime-fused-168-170.json \
  --binding agents/assembly/configs/fused-lifetime-review-binding.json \
  --output work/assembly/reproduced-fused-binding/binding.json

python3 agents/assembly/code/export_fused_acceptance.py \
  --config agents/transfer/configs/lifetime-fused-168-170.json \
  --certificate work/transfer/20261009T-lifetime-fused-168-170/receipt.json \
  --binding agents/assembly/configs/fused-lifetime-review-binding.json \
  --binding-reference work/assembly/20261009T-independent-lifetime-fused/finite-binding.json \
  --destination work/assembly/reproduced-fused-clean-export
```

The third command was tested: 184 files, 30,567,095 bytes, independent
stable mathematical output equal and finite binding byte-identical.
Outputs must have fresh identities. Original complete receipts are retained
in `agents/assembly/evidence/20261009T-fused-lifetime-independent-review/`;
restore the arithmetic review/finite binding to their manifest locations
before replaying the binder. Its supplemental manifest additionally names
six original independent receipts, which are archived by their owning lanes.
Use no source expectations or saved PASS flag to bypass a recomputation.

The later comparable PR168 observation and its source-bound target arithmetic
are retained separately. The accepted frozen coefficient is below the current
one-percent publication floor; these commands do not perform publication.
