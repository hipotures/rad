# Two address orders do not supply these complete scan boundaries

Status: **EXACT FINITE CHANNEL-SPACE CERTIFICATES**. These negatives concern
additive scan sums in the specified two orderings, not products of scans,
arbitrary streaming algorithms or a native multiplication exponent.

The [one-order classification](weighted-scan-intertwiner-structure.md)
leaves only three midpoint channels at f>=4. This experiment lifts that
restriction. For a specified permutation P, define
`L'=L_D+P*L_D*P^-1`, and solve the entire `Q(i)` space of X with
`X in L'` and `C_f*X in L'`. The matrix P changes actual rows and columns;
it is not a free reinterpretation of address metadata.

Four order maps are retained: full bit reversal, binary Gray code
`a xor (a>>1)`, one swap of the lowest/highest orbit bits, and one CNOT
from the lowest bit to the highest. Bit reversal and the endpoint swap
are axis permutations and commute with the tensor C_f. Gray and this
CNOT generally do not. Every map is checked as a literal bijection.

The solver removes dependencies from the two scan-space bases, forms
all entries of `C_f X=Y` with independent X/Y coefficients, and solves
the complete linear system exactly. Projection of a null vector to X
is injective because the chosen Y basis is independent. Each projected
basis vector is cleared to primitive Gaussian integers and independently
tested for membership of both operators in the sum space.

| f | Order | Exact channel dimension | Largest tested scalar rank | Six-bank source-stack lower / upper rank |
| --- | --- | ---: | ---: | --- |
| 3 | Bit reversal | 26 | 8 | 8 / 8 |
| 3 | Gray | 25 | 4 | 8 / 8 |
| 3 | Endpoint swap | 26 | 8 | 8 / 8 |
| 3 | Endpoint CNOT | 27 | 8 | 8 / 8 |
| 4 | Bit reversal | 37 | 4 | 13 / 13 |
| 4 | Gray | 39 | 4 | 14 / 15 |
| 4 | Endpoint swap | 37 | 4 | 13 / 13 |
| 4 | Endpoint CNOT | 37 | 4 | 12 / 12 |

The upper bounds concern the whole complete channel space. After removing
row-constant and column-constant parts, every remaining matrix's rows lie
in one fixed space of dimension r. A vertical six-bank source column
therefore has rank at most `1+r+6`: one shared constant functional, the
fixed r residual functionals, and six arbitrary column-constant
functionals. The four f4 values of r are 6, 8, 6 and 5. At D16 all
four upper bounds are strictly below sixteen. In the common missing-line
quotient, such a source column cannot belong to an invertible input
boundary, even if every other source column is unrestricted.

The tested ranks are witnesses, not exhaustive maximization claims. In
particular, the Gray lower witness fourteen does not prove its upper
bound fifteen is attained. The small f3 full-rank scalar witnesses are
not fast native operators. The largest tested bit-reversal and endpoint
swap witness has determinant norm `67108864000000`; its odd factor
precludes a Gaussian-dyadic inverse for that witness. The endpoint-CNOT
witness also has an odd determinant factor. No search over all dyadic
invertible channels was completed or claimed.

## Route and time scope

Full bit reversal has midpoint crossing rank D/4, demonstrating that
the earlier fixed-cut-rank premise can be lifted by a permutation. A
formal axis rename still supplies no fixed-tape runtime. Naively,
full reversal takes Theta(f) specified-digit swaps and Gray takes
Theta(f) specified-digit CNOTs. Their cost cannot be imported from a
fixed-h per-column bulk wrapper. A separate functional-mask/guard
construction is under independent investigation.

The endpoint variants instead use one specified-digit gate, independent
of f, and test whether a potentially cheaper order already suffices.
They still require actual native routing, complete records, all control
and endpoint guards. Their f4 algebraic capacity fails before these
unpaid costs matter. Per-address scan weights and a native inverse
factorization remain additional obligations in any positive case.

## Failed control, repair and reproduction

The first run aborted on a test-control assertion: it required bit
reversal to have midpoint rank greater than two already at f3. Its
actual rank is D/4=2 at f3. The repair checks that exact D/4 identity
instead; the underlying channel equations are unchanged. The failed
source SHA is `c2848f2abd97bfa2b4364a666a1acab1942950d0623559501bda72466cf6aca2`.
[The recovery patch](../../code/synthesis/patches/two-order-cut-control-repair.patch)
reverses the repaired source to those exact bytes, and a bounded import
of the recovered source reproduces the original assertion. The first
run has no complete certificate; its preserved receipt states this.

- [Failed first control](../../runs/20261009T043932Z-synthesis-two-order-scan-attempt/)
- [Complete repaired two-order run](../../runs/20261009T044143Z-synthesis-two-order-scan-repair/)
- [Complete single-bit order run](../../runs/20261009T044336Z-synthesis-constant-bit-scan/)

The repaired two-order source is
[two_order_scan_channels.py](../../code/synthesis/two_order_scan_channels.py),
SHA `1fa8acee9498c536cab6c671dfe0327401d64b28f376db4af6c67cb80ab1f71d`.
The endpoint wrapper is
[constant_bit_scan_channels.py](../../code/synthesis/constant_bit_scan_channels.py),
SHA `6e573ed9b92d3d4f23c7be0c4a47667f0c9a40c3ffc64073cc4a9a41db52f07b`.
Both read the unchanged exact arithmetic source pinned by the preceding
one-order run. The wrapper changes only the process-local order-table
API; full class and source-capacity checks remain in the engine.

Each complete run uses four workers and standard-library Python, at
most 6.693 seconds per case. Full compact certificates and protocols
remain unchanged; their durable persistence receipts pin every source
and original hash. Dense channel matrices are deterministically
regenerated and hashed, not claimed to be retained as dumps.

From the topic root, use fresh outputs:

```sh
python3 -B code/synthesis/two_order_scan_channels.py --workers 4 \
  --output work/reproduce/<fresh>-two-order-scan/results
python3 -B code/synthesis/constant_bit_scan_channels.py --workers 4 \
  --output work/reproduce/<fresh>-constant-bit-scan/results
```

A bounded wrapper may call `probe((3,'bit_reverse'))` or
`probe((3,'end_swap'))` without generating output. The f4 complete
channel solves are reproduction workloads. A changed product of scans,
hierarchical state, or different number of complete banks needs fresh
capacity analysis; none is excluded by these eight finite cases.
