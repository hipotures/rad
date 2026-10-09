# Fixed-dimensional borrowed-bit permutation words

Four exact workers tested 12 complete permutations at h3/4/5. All 448
address columns, both initial borrowed-bit values, literal reverse gates
and 1,792 four-field payload records match. Omitted physical gates fail.
The controlled-k NOT commutator uses exactly 4/10/16 Toffoli gates at k3/4/5
and restores all controls and arbitrary dirty ancillary values.

The supplied field orderings are exact finite cases. The general compiler
has O(2^h h^3) gates and supplies no efficient growing-h router. Native
composition requires existing complete data, borrowed and companion slots;
extra volume and the additional selected target cannot be omitted.
Whole fixed-kernel arithmetic and a new multiplication exponent remain open.

[Constructive proof and native shape](../../reports/obstructions/borrowed-bit-permutations-and-native-shape.md),
[exact source](../../code/obstructions/borrowed_bit_permutation_words.py),
[protocol](results/protocol.json), [full results](results/summary.json),
[original-byte provenance](persistence.json). Original outputs remain unchanged.
