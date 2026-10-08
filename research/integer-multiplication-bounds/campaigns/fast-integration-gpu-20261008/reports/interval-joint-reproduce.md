# Reproducing rational interval joint compilation

Prerequisites are authenticated GitHub CLI, Git, Python 3, a C++20 compiler and Boost multiprecision headers. Run from the RaD repository root. Choose a fresh writable external work root; authored code does not require this host's paths.

```bash
campaign=research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008
joint_work=/your/writable/interval-joint-reproduction
python3 "$campaign/code/fetch_interval_joint_sources.py" --work "$joint_work/public"
python3 -B "$campaign/code/reproduce_joint_rational.py" \
  --snapshot "$joint_work/public/snapshots/pr62-ad0f25ff7b23cff7f08ad237c2254e6ecf74257e" \
  --work "$joint_work/rebuilt"
```

Acquisition checks live GitHub metadata, downloads the three pinned public sources automatically, records exact file hashes, and freezes their snapshots. It never substitutes current main or a moving PR57 head for the pinned compiler. The reproduction reconstructs both exact scalar graphs, independently compiles both literal words from source, checks the entire arbitrary dirty basis, reconstructs transitions from operations and events, rebuilds the general rational CRT profiler, derives the two actual local width distributions, recounts scalar/stock charges, assembles the complete recurrence and independently binds it. Expected κ is `2550846181/50000000000000`, roles `27918,36586`, W `137151806`, rank mass `78860441550`, 47 strict constraints and seven positive margins.

The retained complete mixed DATA certificate is re-used after exact source/center/basis compatibility: all 4073300 pairs have nine singletons and widths 21,17,481. Its generator is independently regenerable:

```bash
g++ -O3 -std=c++20 "$campaign/agents/geometry/code/fixed23_negative25_data_pairs.cpp" \
  -o "$joint_work/mixed-data"
"$joint_work/mixed-data" > "$joint_work/mixed-data-full.json"
```

The [mixed DATA proof](../agents/scout/mixed-fixed-negative-data-proof.md) explains the rational incidence upper cuts, complete enumeration, nonvanishing lower witnesses and exact rational recovery of the 22 unlucky cases. Its source/center interface is explicitly checked in `agents/scout/code/audit_source_center_basis_interfaces.py`; the corresponding immutable receipt names every consumed input and hash. The mixed all-pair proof predates the interval graph but its normalized full DATA matrix depends only on the unchanged source family, actual data order and selected coordinate products. It is not a reuse of a different both-negative data histogram.

Complete integer transition audits, selected native profiles, independent Fraction controls and public snapshot hashes are published under `evidence/interval-rational-1854`. Each gzip contains one complete source file. The large public compressed words are downloadable from PR62's pinned commit; transition binaries and native executables are deterministically regenerated. No local-only dependency commit or manual transfer is required.

The original targeted source replay, both full dirty-word checks, both generic native CRT runs, Fraction controls, exact composition, independent per-transition binding and adversarial failure controls were exercised during this checkpoint. The unified reproduction driver is additionally exercised on a fresh external output directory, with its receipt recorded alongside the acceptance evidence. Inherited all-size analytic, physical realization, prime/setup, precision, stock and fixed-tape assumptions are listed in the [proof](interval-joint-rational-proof.md); the reproduction certifies the finite ingredients within that scope.
