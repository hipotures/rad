# Follow-up circuit screens

This report separates exact finite map/frame checks from exploratory count
screens. No new multiplication theorem depends on the rejected mixed-source
graphs or on the count-only ground sweep.

## Ground-size screen

The 186-case sweep covered even ground sizes 40 through 100, point orders
`natural`, `paired`, and `gap`, and direct-recursion thresholds 2 and 4. It
checked every local pair-exclusion map and counted the global support interner
before removing unused nodes. These counts give conservative role upper
bounds; they are not claims of a globally minimum circuit at each size. Each
row records an exact rational `eta`, a proved logarithm enclosure, the
downstream complex-saving and guard checks, and the supported saving under
the pinned downstream recipe.

The best screen value is h=50 with paired order, followed by h=52. Selected
counts and admissible bit parameters are:

| h | Order | Threshold | Screen R | Admissible a, approximately |
|---:|---|---:|---:|---:|
| 40 | paired | 2 | 243960 | 7.7858e-10 |
| 46 | paired | 2 | 380006 | 2.8108e-9 |
| 48 | paired | 2 | 433872 | 2.9955e-9 |
| 50 | paired | 2 or 4 | 494250 | 3.0508e-9 |
| 52 | paired | 2 | 557804 | 3.0394e-9 |
| 54 | paired | 2 | 628398 | 2.9684e-9 |
| 60 | paired | 2 | 871860 | 2.6247e-9 |
| 80 | paired | 2 | 2124720 | 1.4729e-9 |
| 100 | paired | 2 | 4219100 | 8.4016e-10 |

The h=50 paired circuit has a complete certificate recorded separately in
[the aligned-pairing report](finite-aligned-pairing.md). A fresh complete
h=52/threshold-2 check confirmed 491504 additions, 66300 partial outputs,
557804 roles, exact global output maps, and both frame directions. Its witness
is [the h52 certificate](../runs/20261007T230300Z-finite-ground52-recheck/results/certificate.json).
The first h52 attempt failed to save its output because its destination
directory was absent; it was superseded by that fresh run and is not counted
as a retained certificate.

The sweep took 743.8768 seconds. Its complete external rows are
`derived/finite/ground40-100.jsonl` under the campaign work root; the compact
screen summary is [here](../runs/20261007T224510Z-finite-ground-scan/results/summary.json).
These scores use the pinned downstream recipe, so later improvements to
finite frames or downstream transforms should rescore the same exact rows.

## Greedy pair-star factoring

The aligned h=50 graph uses 216000 additions in its fixed-pair star groups.
Greedily replacing the most frequent input pair did not improve three sample
groups under any of four tie rules (`canonical`, `large`, `small`, `random`).
The full canonical screen covered all 1225 fixed pairs and reproduced every
original group count exactly. This is evidence against this particular
greedy factoring rule, rather than a lower bound on all star circuits.

The complete external result is `derived/finite/star-all-canonical.json`.
The four `star-samples-*.json` files preserve the smaller tie comparisons.
The generator is [finite_star_screen.py](../code/finite_star_screen.py).

## Factored two-anchor outputs

For each global pair A={a,a'} and third point b, the mixed-source experiment
combined the old common-a and common-a' partial outputs into a single
exclusion map on inputs `x_{a,u,v}+x_{a',u,v}`. The old common-b output
remained. Whole global support interning included both the old paired graph
and all mixed-source families; unused nodes were removed before counting.
Every resulting whole target was expanded and checked against the exact
intersection-one map.

| Single-exclusion template | Local additions, n=48 | Global additions | Outputs | R | R increase | Degenerate active spans |
|---|---:|---:|---:|---:|---:|---:|
| paired | 3330 | 477394 | 57600 | 534994 | 40744 | 1950 |
| balanced | 2974 | 494598 | 57600 | 552198 | 57948 | 400 |

The balanced template uses fewer additions locally but loses more global
sharing. Neither candidate meets the original raw-source-span frame
conditions, and both increase the actual pre-reuse role count. They are
rejected as proposed multiplication improvements.

The positive/indefinite/degenerate mixed-span criterion is proved and checked
in [the mixed-pair span report](finite-mixed-pair-spans.md). The exact whole-map
results are [paired](../runs/20261007T225510Z-finite-mixed-outputs/results/paired.json)
and [balanced](../runs/20261007T230010Z-finite-mixed-balanced/results/certificate.json).
The generator is [finite_mixed_circuit_screen.py](../code/finite_mixed_circuit_screen.py).
The mixed-source lemma may still be useful for a circuit with fewer roles or
for a different nondegenerate frame family; these two failed graphs do not
exclude such constructions.

## Recovery

All paths above extend the existing topic. The campaign work root is
`/srv/ai/work/rad/integer-multiplication-bounds/20261007T222521Z`; external
rows are deterministic outputs of the retained scripts and their recorded
commands/seeds. The immutable reference is
`repos/upstream-reference` at
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`. The coordinating agent owns
the shared manifests and publication of completed external text evidence.
