# Independent review of the converged physical placement

The forward finite construction and exact conditional certificate were
independently checked on 2026-10-09, 07:43--07:54 UTC. The proposed final
conditional saving is `296187231/500000000000 = 0.000592374462`. It is a
placement change on the unchanged PR #161 scalar construction, not a new
scalar DAG or a parameter-only adjustment. Promotion to
`ACCEPTED_CONDITIONAL` additionally needs the separate signed/reflected
geometry receipt and the coordinator's compatibility assessment. This lane
does not decide the live public comparison or publication status.

The upstream predecessor is eumemic's PR #161 at
`d14e29157bc905be1ced0776dd893d0714013f3a`. Its final kappa is
`5878747/10000000000`. The converged placement changes 6,030 frames against
that public physical placement and has 12,827 overrides against its full
backward-intersection frames. Candidate frame SHA-256 is
`f02a59311c667316b1f2e21916cebf71c58f79fbfbd3a126a24743d1d7ff016a`.
The initial 6,027-frame candidate remains a distinct discovery attempt.

## Independent method and evidence

The reviewer imports no candidate Python for its geometry or arithmetic.
Its own signed integer-support propagation reconstructs every DAG value,
root support and operation value. Its own binary elimination reconstructs
all 19,055 full backward intersections, including carrier matching and
root caps. It checks every value containment, role chain, pair handoff and
the old-value reads in the actual literal execution order. In particular,
the 2,970 late deadlines are distinct; the reviewer nevertheless uses the
literal pair insertion order instead of inferring chronology from ranks.

The forward audit checked 32,426 signed operations, 85,340 spliced chain
edges and 330 signed Hadamard blocks. The destructive original-source
`K` itinerary is reconstructed for each eight-port cube, including its
common parity frame, destination cap, full-frame endpoint and exact inverse.
Every charged local, source, target, residual-gauge and shared-center term
is recounted. The complete result is:

| Quantity | Independently recomputed value |
|---|---:|
| Parent dimension | 66 |
| Width per vertex | 15,681 |
| Physical dirty slots | 13,041 |
| Alias pairs / late reads | 2,970 / 2,970 |
| Child occurrences | 228,306 |
| Rank mass | 1,033,626 |
| Rank deficit | 1,320 |
| Largest child | 20 |

The final forward audit took 4.34 seconds. It verified all 61 source
fingerprints from the retained PR #161 certificate. Graph, full witness,
signed selection, pairs and complex record match the
[immutable input pins](configs/immutable-scalar-inputs.json).
The assembly lane's independently regenerated graph, witness and selection
were subsequently compared byte for byte to these same inputs; all match.
Its physical profile has identical JSON content to the reviewed discovery
profile, although JSON field ordering changes its byte hash.

The exact scalar audit was freshly rerun in 1.90 seconds. Integer adjoint
propagation checks all 1,742,400 source/output coefficients and all
17,214,120 arbitrary-dirty/output coefficients, rather than infer exactness
from agreement at several primes. Every cleanup event equals the signed
inverse of its corresponding mutation. This proves the local scalar
operator and dirty restoration; its inverse/bank-renaming argument does
not by itself certify complemented geometric frames.

Independent rational arithmetic checks the complete binary and complex
histograms, full rare-class binary fallback, full finite-group order,
expanded scalar work, routing, semantic precision guard, row stock,
all 47 strict assembly constraints and all seven final margins. It uses
40 positive atanh terms, a degree-nine exponential polynomial, explicit
tails and outward rational rounding on a `2^-180` grid. It reads no saved
moment endpoint or verification flag to establish acceptance.

| Exact quantity | Value or rigorous lower bound |
|---|---:|
| Coarse binary saving | `5936323/10000000000` |
| Effective ordinary binary saving | `1482692819/2500000000000` |
| Accepted complex saving | `74320127/125000000000` |
| Binary gap including full fallback | `> 6.66981963256853e-11` |
| Complex complete moment gap | `> 1.3465976499253738e-12` |
| Next complex grid excess at `b + 10^-12` | `> 8.002097645739117e-13` |
| Final conditional kappa | `296187231/500000000000` |

The first arithmetic audit took 0.066 seconds. A final 0.210-second audit
also binds every derived assembly parameter and recurrence value, with
deliberate mutation controls for both. It checked all 28 explicit candidate
source pins. Its certificate SHA-256 is
`6ea1a24ef616e6e4a262643505382e5888dfc1d5ac95c441a7fcb403d0f04da6`.
All seven margins exceed kappa strictly; the exact absorption gap is
`2059080576968043308833194189/6257413463983798037833653590500000000000`.
No final saving is obtained by adding independently reported component
improvements.

## Negative controls

Fresh rejection controls cover an illegal negative frame index, a frame
replaced by its bad complement, an omitted selected target, a premature
compensation deadline, two algebraically cancelling unpaid gates, an
incorrect source pin, actual altered source bytes and a histogram mutation
preserving both occurrence count and rank mass. The arithmetic audit also
rejects inconsistent derived parameters and recurrence values. The scalar checker also
rejects an omitted old-value read, a bad signed gate, an illegal literal
index and omitted cleanup. Optimized execution (`python3 -O`) is explicitly
rejected by all three reviewer entry points, with the final checker hashes
recorded. Every mutated case was rejected; optimized executions wrote no
successful receipt.

## Exact reproduction

Run from the sprint directory with Python 3's standard library only. Input
sources remain in the ignored immutable snapshot; the coordinator's
artifact manifest records how to reacquire them. The assembly certifier's
fresh outputs are produced by its documented reproduction command.
Each reviewer output below must be a fresh nonexistent filename.
All three commands were exercised against the assembly lane's fresh exports;
the measured forward/scalar/arithmetic runtimes were 4.30/1.83/0.072 seconds
before the final assembly-binding controls were added. The final arithmetic
entry point was then rerun successfully with those controls.

```bash
python3 agents/baseline/code/independent_physical_frames.py \
  --tree work/repos/pr161-d14e291 \
  --export work/assembly/20261009T-converged-certificate/complex-export \
  --frames work/placement/live161-components-converged/frames.json \
  --profile work/assembly/20261009T-converged-certificate/physical-profile.json \
  --scalar-receipt agents/baseline/configs/immutable-scalar-inputs.json \
  --output work/baseline/fresh-forward.json

python3 agents/baseline/code/exact_aliased_core.py \
  --tree work/repos/pr161-d14e291 \
  --export work/assembly/20261009T-converged-certificate/complex-export \
  --output work/baseline/fresh-scalar.json

python3 agents/baseline/code/independent_arithmetic.py \
  --tree work/repos/pr161-d14e291 \
  --certificate work/assembly/20261009T-converged-certificate/certificate.json \
  --physical work/assembly/20261009T-converged-certificate/physical-profile.json \
  --bit-profile work/assembly/20261009T-converged-certificate/bit-export/profile_p12.json \
  --candidate-frames work/placement/live161-components-converged/frames.json \
  --output work/baseline/fresh-arithmetic.json
```

Authoritative original receipts are retained unchanged in this lane's
ignored `work/baseline/`: `converged-forward-final.json`,
`converged-exact-core-takeover.json`,
`converged-independent-arithmetic-final.json` and
`optimized-mode-controls-final.json`. Complete gzip copies of 39 earlier
receipts/logs and two final hardened receipts are retained under
[the first evidence namespace](evidence/converged-review-20261009T0750/)
and [the final evidence namespace](evidence/converged-review-final-20261009T0754/).
Both manifests were reviewed and `verify-text --check-originals` passed,
including complete CRC/UTF-8/credential/size/SHA-256 checks. Originals were
not changed; the original work files are not present in an ordinary Git
clone. The coordinator owns staging, auditing, committing and pushing these
durable copies.

## Boundaries and attribution

Finite checks do not establish the inherited arbitrary-subspace Clifford
implementation, completed-core sharing/cover, uniform stopped recurrence,
ordinary conversion, exact common odd-grid precision, analytic resampling
or all-size tape/recovery contracts. Those remain explicit hypotheses.
Reflected complementary geometry is the separate geometry reviewer's
responsibility. Full repository tests and the relevant Lean modules have
separate coverage; unrelated formal statements do not prove this candidate.

The inherited paid chronology and equations credit icekylinx, eumemic,
jamesyc, an664, Zhihao Chen, Swapnil Jain and the retained source notices.
The independent arithmetic uses the supplied RaD supplement's rational
enclosure method. Reviewer source and this report were prepared with
OpenAI GPT-6.1 Sol assistance. The lane owns no Git or upstream writes.
