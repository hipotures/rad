# E1: actual alternate complements on the historical PR120 construction

No tested alternate complement improved the complete paid profile. Reversing
pivots changed 2,248 actual selected role subspaces while leaving the full child
histogram identical. Random elementary basis changes produced different legal
complements but fewer retained deferrals and a strictly worse discovery moment.
This is a scoped result for the fixed PR120 greedy order, not a theorem that
complement choices cannot improve the construction.

## Source and scope

Input: CrocSwap/integer-mult-bounds PR120 at
`bfc5466b028923a1f8655602994ea56c70b5c329`, immutable sprint snapshot
`work/repos/pr120-bfc5466`. The evaluator is
`research/deferred-replayed/complex_deferred.py`; it credits Avi Eisenberg,
eumemic, Swapnil Jain, icekylinx, Zhihao Chen and inherited contributors under
Apache-2.0. This lane substitutes only `sat_nonsingular_part`. The scalar DAG,
carrier matching, placement priority, binary supplier, stopping policy and
assembly remain unchanged. The report's complete 14-page text was read before
implementation, including its existing-integration warning and publication
boundaries.

The original evaluator freshly reconstructs scalar outputs, carrier/frame
chains, target containment and nesting, arbitrary dirty restoration for two
modular forward replays, and all paid child multiplicities. A separate XOR
elimination routine checks that each extracted space lies inside its candidate,
its Gram rank equals its dimension, and its dimension equals the original Gram
rank. Radical dimensions are discarded. The unchanged control exactly matches
the pinned complete profile.

## Experiment and measurements

The first batch ran four processes, with numerical library pools set to one.
Each process used approximately 952 MiB peak RSS and 55.6–57.7 seconds. The
second mixed seed used one process and 54.9 seconds. Python was 3.14.4; the
harness uses only its standard library. Replay seeds are inherited 1 and 2;
complement seeds are given below. A small exhaustive check covers every
3-dimensional degenerate subspace of GF(2)^4 (seven spaces), and independently
checks all three extraction policies on each.

All variants retain m=576, W=124,390,992, rank mass=71,647,349,312,
deficit=1,862,080, and maximum child=574. The common trial is the historical
complex saving b=109140237/10^12. Moments use Decimal precision 70 and are
screening values, not rigorous rational enclosures.

| Policy | Seed | Changed selected roles | Deferred roles | Delta H(b) versus control |
|---|---:|---:|---:|---:|
| Unchanged control | 20261009 | 0 | 4560 | 0 |
| Reverse pivots | 20261009 | 2248 | 4560 | 0, identical complete histogram |
| Sparse pivots | 20261009 | 2248 | 4560 | 0, same assignment as reverse pivots |
| Mixed basis | 20261009 | 2250 | 4071 | +1.5880694258836707e-8 |
| Mixed basis | 20261010 | 2215 | 4054 | +1.64250385964355e-8 |

The control has H(b)=0.9999999999997621838890942153020196. The first
three policies form only two distinct physical constructions: sparse and
reverse pivots converge to identical selected frames. The additional mixed
seed was therefore run to provide three genuinely distinct legal alternatives
to the control. All profile multiplicities and common-trial values at b,
0.00012, and 0.0005622769 are retained in the result JSON. No rounded profile
score is labelled final kappa.

## Interpretation and limits

The equal-profile changed frames demonstrate why changing exact complements is
not sufficient by itself. Under this fixed selection order, the reverse/sparse
policy keeps every selected dimension and complete paid multiplicity unchanged.
The mixed choices alter future intersections adversely. Their lower deferred
counts and worse complete moments agree here; neither count alone was used to
rank the variants.

Status remains `DISCOVERY`: this lane has not independently replayed the
complemented reflected word, enclosed moments rationally, or rerun all 47
assembly constraints and seven margins. Those expensive promotion gates are
not warranted for a historical candidate that does not improve its own
control, much less the refreshed paired-cube public frontier. The original
source's all-size transfer hypotheses remain assumptions.

PR160/161 use general Clifford physical subspaces rather than PR120's
nondegenerate-projector complement interface. A literal copy of the old
extractor is not a compatible optimization of that model. The relevant next
experiment changes actual intermediate physical subspaces inside their legal
lower/upper bounds and recomputes complete paid chains.

## Reproduction and recovery

Run from the sprint directory after obtaining the exact immutable source
snapshot through the coordinator's input manifest. Do not use a current branch
head in place of the source pin. Outputs must use fresh directories.

```bash
python3 agents/complements/code/check_small_complements.py \
  --source work/repos/pr120-bfc5466 \
  --output agents/complements/results/small-exact-prototype.json
python3 agents/complements/code/screen_complements.py \
  --source work/repos/pr120-bfc5466 \
  --output work/complements/reproduction-first \
  --summary work/complements/reproduction-first-summary.json
python3 agents/complements/code/screen_complements.py \
  --source work/repos/pr120-bfc5466 --seed 20261010 \
  --output work/complements/reproduction-second \
  --summary work/complements/reproduction-second-summary.json
```

The final command reruns four policies for convenience; only `mixed_basis` was
needed and measured in the original second batch. Each run records script,
source, DAG, word and profile SHA-256 values. Full original word exports are
about 36.8 MB each and remain in ignored `work/complements/`; they are
reproducible from the pinned downloadable source and retained harness.
`results/construction-identities.json` records exact paths, sizes and hashes.
The compact profiles, source code and conclusions are durable. Raw exported
words are not represented as files present in a Git clone.
