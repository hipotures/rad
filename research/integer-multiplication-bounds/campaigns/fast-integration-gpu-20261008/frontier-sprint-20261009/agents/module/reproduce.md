# Reproduce the bounded structural module batch

Run from the sprint directory unless an absolute path is supplied. Tested
environment: Linux, CPython 3.14, standard library only. Assertions must
remain enabled. Each job uses at most four processes and one library thread;
no GPU framework is required. Originals and execution material stay in
ignored or external storage. Use fresh destinations; scripts refuse
overwrites.

## Recover immutable upstream sources

The original sources are downloadable with the GitHub CLI. The frontier
lane's archive manifests record the original archive byte sizes, hashes and
safe extraction. A new archive can have a different container root; do not
assume the original extracted directory name. The helper strips and checks
the single root, rejects links/unsafe paths and applies the tar data filter.

```bash
mkdir -p work/inputs work/repos work/receipts
python3 code/fetch_snapshot.py eumemic/integer-mult-bounds fd25adb7fbaa12ee761d02c733c54d1d2a7687ee module-source-fd25adb
python3 code/fetch_snapshot.py chafreaky/integer-mult-bounds 7518fed2688baf25c7c32bae32674f3334b517da module-plan-7518fed
```

The generator and native regeneration script verify the actual required
source/module hashes. The PR165 constructor path is
`research/paired-cube-plateau-162/references/pr162/make_plan.py`, SHA256
`29a4548855513bb51b08c4cfe10a3ce717fdb837d24769c16f5b71a7b7a681dc`.
Other authored checker dependencies are retained in the sprint's baseline,
signed and placement lanes and pinned in `input-manifest.json` and the run
protocols.

## Fresh complete reconstruction

The executable wrapper regenerates a new native control export, generates
the four exact candidate inputs, rebuilds each whole graph/matching/word/
gauge/alias/frame/sink context, performs all finite checks and encloses the
finite roots rationally. It enables the repaired carrier-seed validation
from the start; it does not intentionally recreate the historical failed
batch.

```bash
bash agents/module/code/reproduce.sh \
  work/repos/module-source-fd25adb \
  work/repos/module-plan-7518fed \
  work/module/fresh-reproduction 4
```

Expected finite outcomes are in `results/structural-module-batch.json`:
control W 13,894 / 42 sinks; edge and long-diagonal W 14,224 / 42 sinks;
balanced triple W 14,008 / 74 sinks. The strict root intervals should agree
with the report. All four must reject the two required complex savings.
Changes in unrelated source/checker versions require a new run rather than
replacement of retained results.

What was exercised here: actual exact generation of all four inputs, the
initial full four-worker construction (three completions and one seed
failure), the separate one-worker repaired all-long construction, strict
rational enclosures for all four full paid profiles, source pin readback,
three invalid positive-module controls and Python/shell syntax checks.
The convenience wrapper's complete new four-case invocation was not rerun
after these checks; its component construction paths were exercised as
described. No all-size or analytic-composition path was exercised for these
negative candidates.

## Inspect or recover complete retained evidence

```bash
python3 ../../../../../tools/archive_workspace.py verify-text \
  --destination agents/module/evidence/structural-module-20261009T1045Z
gzip -dc agents/module/evidence/structural-module-20261009T1045Z/structural-summary-20261009T1035Z/summary.json.gz
```

The archive manifest provides every original and compressed SHA256 and byte
size. Extract into a fresh destination with ordinary `gzip -dc`; never
overwrite an original or earlier run. The initial carrier rejection is in
the archived `structural-batch-20261009T1025Z.log`. To recreate the initial
driver exactly for a historical diagnostic, start from the original signed
driver at SHA256 `ac1ff39e4af5a507a42f74442a663b024ed704f538cdb814cb1f472c506a1998`
and apply `code/evaluator-adaptation.patch`; the final driver additionally
applies `code/seed-revalidation.patch`. The original failure is preserved
as evidence, not treated as a valid finite result.
