# Exact fixed-dimensional nonlinear permutation words

Status: **CONSTRUCTIVE BOOLEAN WORD** and **EXACT FINITE PAYLOAD CERTIFICATE**.
Every supplied permutation of h data bits has a literal NOT/CNOT/Toffoli word
with one additional dirty bit restored for both initial values. This gives
fixed-h nonlinear address components. It does not give an efficient growing-h
field-order router: the general gate bound below is exponential in h.

## Restored dirty-bit controlled gates

To toggle target t under k positive controls, let g be a distinct borrowed
bit with arbitrary initial value. For k<=2 use the actual NOT, CNOT or
Toffoli gate. For k>=3 split the controls into disjoint sets A and B with
`r=ceil(k/2)` controls in A. Define complete subwords

```text
L: g ^= product(A),
R: t ^= g*product(B).
```

Execute `L R L R`. The two R toggles cancel the initial g contribution and
leave exactly `t ^= product(A)*product(B)`. The two L toggles restore g.
Compile L recursively, borrowing t; compile R recursively, borrowing one
control from A. Each subword restores every borrowed value before the next
subword, so the Boolean commutator argument remains exact. No clean bit is
introduced, and k decreases in both recursive calls.

With T(k) actual Toffoli gates, the balanced recurrence is
`T(k)=2*T(r)+2*T(k-r+1)` with `T(2)=1`, hence `T(k)=O(k^2)`.
For example k=3,4,5 use exactly 4,10,16 Toffoli gates. Negative controls are
conjugated by actual NOT gates, which are also counted.

## Arbitrary permutation compiler

An adjacent transposition of two h-bit addresses differing in bit t is a
toggle of t under the specified pattern of all other h-1 bits. The preceding
controlled word implements it with restored g. For arbitrary u,v, take a
Gray path `w0=u,...,wm=v`, flipping each differing bit once. Execute its
adjacent swaps forward and then all but the last backward. This swaps only
u and v and returns every intermediate address.

Decompose a permutation into disjoint cycles. A cycle
`c0->c1->...->cl->c0` is implemented chronologically by
`(c0,c1),(c0,c2),...,(c0,cl)`. At most `2^h-1` transpositions suffice.
Each path has at most h edges and each controlled edge costs `O(h^2)`
gates plus its NOT conjugations. Therefore

```text
G_h = O(2^h*h^3)
```

is an explicit sufficient bound. Its constants are acceptable only when h
is fixed. Compiling one permutation separately for every growing selected
width does not inherit a constant-pass native bill.

The [standalone compiler](../../code/obstructions/borrowed_bit_permutation_words.py)
emits only tuples of one, two or three bit indices. It never substitutes a
many-controlled toggle as one primitive. The retained whole-word hashes and
source let another executor regenerate every gate.

## Conditional native composition and complete shape

Suppose an independently established packed gate contract acts on f selected
columns of distinct complete address slots of width `(f+1)K`, including its
exceptional-record repair. Supply h data slots and one complete borrowed
slot. The compiled logical bit g in every column is the selected bit of that
last slot. Every Toffoli uses three distinct slots; for h>=3 there is also
a fourth distinct complete slot for a restored routing companion.
All unused bits, the companion and the entire borrowed slot must return
exactly, for arbitrary complete address values and payloads.

If the paid per-gate contract is

```text
B = O(V(((f+1)K)^tau+1) + M*A^3 + delta*M*A*(R+A)),
V=M*R, A=ceil(log2(2V)),
```

then the complete compiled word costs `O(G_h*B)`. Under the separately
proved guard/long-record hypotheses and fixed h, this can have the desired
local sublinear-in-address-width order. NOT and CNOT stages, slot movement,
all exceptional payloads and numerical-field preservation remain paid.
The present compiler verifies Boolean composition, not those native gates.

For this f-of-(f+1)-chunk layout, native NOT and CNOT must use the guarded
all-f Boolean-control specialization `c=1` or `c=x`. The old routine acting
on all f+1 selected positions would also toggle the preprocessed guard bit
and would implement the wrong word. The extra chunk supplies carry guards;
its selected bit is outside the compiled logical target and must return.

The h+1 slots are address coordinates within one physical payload stream;
they are not new free scalar banks. Nevertheless, an additional complete
slot needs a real location. Extra padding changes M and V. If its selected
bits belong to the parent's required C target, their own C operations or
recursive child calls must also be charged. Borrowing unselected guard bits
at a different offset is another routing interface and is not established
by this same-offset word. A declared shape cannot waive any of these costs.

Thus the [earlier prefix-affine obstruction](singer-prefix-routing-boundary.md)
does not exclude these fixed-h nonlinear words. They implement the tested
Singer permutations exactly, but the [whole field-cyclic reduction](../synthesis/finite-field-cyclic-core.md)
still needs an efficient growing-dimensional router, kernel arithmetic,
transposes, precision and an improving recurrence. This certificate closes
none of those global obligations by itself.

## Finite evidence and reproduction

Four workers tested h=3,4,5. At each h they compiled multiplicative field
ordering with zero-first and zero-last conventions, a deterministically
shuffled arbitrary permutation and a single transposition. Primitive
polynomials are 11,19,37 in binary integer notation, the same small supplied
fields used in the earlier exact cyclic-core record. Their full nonzero
cycles are rechecked here; no uniform primitive-polynomial generator is
asserted.

All 448 complete address columns, both initial dirty-bit values, literal
reverse words and 1,792 complete four-field payload records agree exactly.
Omitting the last actual gate changes the target in every case. Borrowed-bit
temporary changes are observed at h=4/5 and fully restored. Separate k=3,4,5
controlled-word tests enumerate every control, target and dirty-bit value.
The zero-last Singer words use 58,312,2,082 total gates at h=3,4,5,
respectively; the counts include all NOT conjugations and actual Toffoli
subwords, and make no optimality claim.

[The retained run](../../runs/20261009T035601Z-borrowed-bit-permutations/report.md)
contains full counts, hashes, protocols and unchanged outputs. Standard
Python, from the repository root:

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/borrowed_bit_permutation_words.py --workers 1 --bounded
```

Omit `--bounded` and use `--workers 4 --output <fresh-directory>` for all
retained dimensions. List scatter and measured Python runtime are exact
reference verification, not a native tape implementation or exponent proof.
