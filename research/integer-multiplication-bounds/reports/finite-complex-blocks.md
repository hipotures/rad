# Generalized complex contraction blocks

The paired complex D/E circuit was generalized to contraction blocks of
three and four vertices. All six ground-8/ground-12 controls passed exact
disjoint maps, complete physical coefficient reconstruction, unchanged
binary frame/residual/terminal checks, partner-bank matching, and guard
counts. Every ground-8 data and dirty auxiliary basis coordinate also
passed the Gaussian-dyadic identity; each case passed three signed dirty
probes. The six-case cohort took 1.804 seconds.

The larger blocks are worse in this test:

| Ground | Pairs | Blocks of 3 | Blocks of 4 |
| --- | ---: | ---: | ---: |
| 8 | 898 | 917 | 962 |
| 12 | 4,973 | 6,466 | 6,783 |

Counts are actual reversible roles `c+2v`, not additions alone. The sum
association is balanced, seed 109, and the direct base ground is four. No
retained-controller optimization is introduced in this branch. The exact
baseline node identities are preserved when block size is two.

The key correction needed for blocks larger than two is to separate the
weighted polynomial degree `p` from maximum deletion-query size `q`.
Let the touched blocks be those meeting an omitted vertex set. Every
surviving hyperedge has a unique subset `X` of vertices in those blocks;
its other vertices lie in untouched blocks. The coarse all-untouched sum
and the sums indexed by nonempty `X` are disjoint and exhaust the answer.
If `X` meets `r` blocks and contains `s` vertices, its recursive component
has degree at most `p-s` but outside deletion-query size at most `q-r`.
For pairs, `r=s`; with larger blocks they may differ. A naive replacement
of pairs by larger blocks while retaining one parameter omits required
components or requests unavailable deletion tables.

The fresh source
[finite_complex_blocks.py](../code/finite_complex_blocks.py), SHA-256
`3523479d22b1f1c2195228c37555992ea0ae363ffcd29cc81cd748131fabab46`,
implements both parameters and exact source-support interning. Its physical
checker reconstructs every pivot addition and fresh fanout copy with exact
coefficient bitsets, rather than relying only on output dimensions.
The [certificate](../runs/20261008T013240Z-finite-complex-block-small/results/certificate.json)
records exact DAG hashes, all source pins, basis counts and frame evidence;
the [protocol](../runs/20261008T013240Z-finite-complex-block-small/protocol.json)
contains the command and resource/timeout controls.

This is a bounded negative for these uniform blocks on the checked small
grounds. It does not exclude nonuniform contraction choices or altered
sum association. The unchanged binary frame argument is compatible with
any exact monotone D map whose active support meets the existing bound;
each new candidate still needs its full checks and analytic transfer.
