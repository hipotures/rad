# Actual subspace orientations on coherent fused PR168 plans

Two bounded batches found no additional gain from equal-rank orientation choice.
Each unchanged control and its three genuinely different physical subspace
variants converged to identical final frame bytes and paid histograms after the
same component descent. However, joint equal-frame component descent on the
stronger coherent signed plan produced a native complex saving that passes the
required exact trial `617560360/10^12`. This is a placement gain, not an
orientation-specific gain or a final accepted exponent saving.

## Frozen inputs and compatibility

Both batches use the actual newly fused PR168 signed graph, supported by upstream
source revision `98c115b53742b6613ad630de4d493f37b0119da7` from
<https://github.com/eumemic/integer-mult-bounds>. The graph was constructed by the
signed lane's `screen_pr168_modules.py`: complete positive-first singleton fusion,
fresh matching and extended closure, fresh selected gauges and literal word.
This is not a transplant of PR161 frames or a change only to its certificate.
Graph SHA-256 is
`962228efaa62680a7ed830430a9af5c3fc758ac3b41025e34a37ab086e6fe9aa`;
literal-word SHA-256 is
`365ec31ad80db614ca014ef10b1347eafca9e225db3d93a96ee705e42b026902`.

The first frozen complete state is placement's
`work/placement/pr168-fusion-global-lower-98c115b`, with its original 2,640
physical aliases/deadlines from the fused export. The second state is the signed
lane's stronger `work/signed/fused168-joint-best-20261009T0912Z`, with a new
coherent alias/deadline fit. Each state was copied as a whole into this lane's
ignored context, preserving its graph, witness, literal word, logical record,
selected gauges, physical frames, physical pairs, deadlines and complete profile.
The pair sets were never mixed. All supplied input pins were checked through
`prepare_context.py`; compact manifests retain hashes of the copied files.

The inherited physical model credits eumemic, icekylinx and the contributors
identified by its source under Apache-2.0. New E1 code and analysis were prepared
with GPT-6.1 Sol assistance. General Clifford physical frames are used: no
nondegenerate-projector assumption from the historical PR120 interface is added.

## Discriminator and measurements

The first state has 25 strict-interior singleton intervals and 29 strict-interior
connected equal-frame components. Operation 20865 has local lower/current/upper
ranks 8/9/14 and 63 possible quotient lines. Four two-operation components have
ranks 7/8/10 and seven quotient lines each; the remaining strict intervals have
small one- or two-dimensional quotient selections. The stronger signed state
has no strict-interior singleton interval and exactly four strict-interior
equal-frame components:
`[16510,18551]`, `[16524,18580]`, `[16526,18581]`, `[16542,18593]`.

For every extraction the harness freshly computes the exact incoming/value-span
lower space and the outgoing-frame upper intersection, enumerates all quotient
subspaces up to quotient dimension six and selected dimension two, and checks
the selected actual frame's dimension and containment. The full carrier/pair
chain check runs after every extraction, accounting for preceding changes.
Policies select the unchanged frame, the first alternative, the last alternative
or a seeded random alternative. All four initial physical frame files are
distinct in each batch. Equal-rank changes preserve the entire initial paid
histogram, which is checked explicitly.

All four policies then run identical component endpoint descent, with reverse
traversal on pass two and common trial `617560360/10^12`. Each batch uses four
concurrent processes, with numerical thread pools set to one. Python was 3.14.4;
peak memory was 346–347 MiB per process. No orientation choice is scored by role
count or a local rank surrogate alone.

| Coherent starting state | Policies | Final frame identity | Discovery complex root |
|---|---|---|---:|
| Fixed original aliases, global-lower placement | Control + 3 distinct alternatives across 29 components | All identical, `e277a6a0…` | 0.0006171565860613583 |
| New coherent signed seed31 aliases | Control + 3 distinct alternatives across 4 components | All identical, `7bd852bd…` | 0.0006176612298503512 |

First-batch processes took 11.98–12.66 seconds. The control accepted 265, 91 and
16 moves; the orientation variants accepted 267, 93 and 18 moves, but all final
frames were identical. Second-batch processes took 11.33–11.52 seconds; all
policies accepted 137, 21 and zero moves. The second batch therefore reached
component-descent convergence within its three-pass bound.

The second result's exact final frame SHA-256 is
`7bd852bd6f489fc3d4eaef9f97f6ae6a3d4cc750cea58b0346b2f503562355e9`.
Its complete profile SHA-256 is
`27bc4e03956d8e4f0f0d14ce25e71e2b521a5466d850a30682e795078eec890f`.
The frozen complete bundle is
`work/complements/fused168-component-winner-v1`. It has dimension 66, physical
width 14,843, rank mass 978,318, deficit 1,320, largest child 20 and 12,203 physical
dirty slots. All source, target, local and remaining gauge-tail costs are charged.

## Exact finite and moment evidence

Every final variant was freshly checked by the upstream physical compiler:
operation support containment, nested carrier chains and pair handoffs, legal
pair chronology/deadlines, target containment and read order, complete child
histogram, strict child contraction and telescoping deficit. Arbitrary dirty
modular replay passed both seeds and rejected its three signed/read controls.

The frozen second result additionally passed independent binary elimination:
33,568 operation value containments and 85,136 forward carrier/pair edges,
including complemented reverse inclusion and exact reversed transition ranks.
Negative indices, noncanonical bases, invalid value frames and omitted frame
complements were rejected. This is exact geometric incidence arithmetic, with a
scope narrower than the full literal reflected-word audit.

The separate signed-core checker was rerun on the frozen complete bundle,
checking both shear signs with exact integer propagation. In each orientation it
checked 1,742,400 source/output coefficients and 16,107,960 arbitrary-dirty/output
coefficients on 12,203 slots. The literal word has 52,888 read/mutation events and
34,888 exact signed cleanup inverse events. Omitted reads, bad signs, illegal
indices and omitted cleanup were rejected. The inherited expanded local scalar
bill is 5,264,026,273,944; it was not removed from the accounting.

An independent inventory recount and rational interval kernel established:

- `H(617560360/10^12) < 1`, with rigorous gap at least
  `2.20227932894e-7` (rounded down; the exact fraction is in the receipt).
- `H(617661229/10^12) < 1` and `H(617661230/10^12) > 1`, rigorously enclosing
  the native complex root between those adjacent grid points.

These are native complex moment results. Status remains `DISCOVERY` overall:
this lane did not complete the full literal reflected Clifford word audit or
all binary/47-constraint/seven-margin assembly gates. The coordinator selected a
slightly stronger placement continuation, numerical complex root approximately
0.000617664283700077, for the independent full audit. No claim that an upstream
PR exists, or that this lane has accepted final kappa, follows from the checks.

## Reproduction and retained material

Run from the sprint directory after obtaining the exact source revision and
retained fused input bundle through the shared manifests/evidence archive.
Use fresh output paths. `prepare_context.py` creates portable derived input
layouts pointing to the inspected source scripts; it does not rerun the original
module search. The authored fusion generator and exact input pins preserve that
distinct source-transformation provenance.

```bash
python3 agents/placement/code/prepare_context.py \
  --source work/frontier/pr168-98c115b/extracted/eumemic-integer-mult-bounds-98c115b \
  --input work/signed/fused168-joint-best-20261009T0912Z \
  --output work/complements/reproduction-joint-context \
  --source-commit 98c115b53742b6613ad630de4d493f37b0119da7 \
  --source-repository https://github.com/eumemic/integer-mult-bounds
cp work/signed/fused168-joint-best-20261009T0912Z/physical-frames.json \
  work/complements/reproduction-joint-context/start-frames.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
python3 agents/complements/code/screen_fused_orientations.py \
  --context work/complements/reproduction-joint-context \
  --placement-code agents/placement/code/physical_search.py \
  --output work/complements/reproduction-joint-orientations \
  --summary work/complements/reproduction-joint-summary.json --workers 4 --passes 3
python3 agents/complements/code/check_physical_frames.py \
  --source work/complements/reproduction-joint-context/source \
  --export work/complements/reproduction-joint-context/export \
  --placement-code agents/placement/code/physical_search.py \
  --frames work/complements/reproduction-joint-orientations/control/frames.json \
  --output work/complements/reproduction-joint-frame-check.json
python3 agents/complements/code/enclose_fused_candidate.py \
  --profile work/complements/reproduction-joint-orientations/control/profile.json \
  --logical-record work/signed/fused168-joint-best-20261009T0912Z/profile-before.json \
  --interval-code agents/signed/code/interval_moments.py --root-grid 617661229 \
  --output work/complements/reproduction-joint-exact-moments.json
python3 agents/signed/code/check_pr165_signed_control.py \
  --export work/complements/fused168-component-winner-v1 \
  --exact-core agents/baseline/code/exact_aliased_core.py \
  --output work/complements/reproduction-winner-signed-check.json
```

All commands' meaningful computation paths were exercised on pinned inputs. The
two complete batches, own input context transformations, exact frame check,
exact signed-core check and rational moments are retained under `results/`.
`results/pr168-orientation-artifact-manifest.json` records every frozen/context
and attempt JSON's size/hash. Completed raw finite exports belong in the shared
gzip evidence publication path; they remain unchanged in ignored `work/` before
the coordinator archives them. The source snapshots are downloadable, and the
finite exports are reconstructible from retained source transformations and
pins; neither an ignored host path nor a local hash alone is asserted to recover
the raw bytes.

The tested complement policies have diminishing information value: they
repeatedly converge to the same frame assignment. Continue compatible frame
closure/exchanges or genuinely changed carrier matching, preserving complete
coherent bundles and the independent reflected/assembly gates.
