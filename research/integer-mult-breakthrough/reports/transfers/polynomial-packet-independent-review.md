# Independent complete polynomial packet arithmetic review

Status: **READ-ONLY SOURCE AND ANALYTICAL REVIEW** of
[partial_polynomial_product_packets.py](../../code/complex/partial_polynomial_product_packets.py),
SHA256 `b9fff086ff47cf80cdb0073bd9cc62f4d3b62f45236fbaf2794a5bdd529bc0f7`.
The guarded signed-radix arithmetic is accepted. The producer was not
imported or independently run. No native orbit layout, dirty word,
improved multiplier induction or exponent is supplied.

The packet recursion is the three-product signed dyadic bilinear word
on complete Gaussian negacyclic polynomial records. Its source additions,
Gaussian recombination and negacyclic products commute with the scalar
packet identity, so the final grid is s. Comparing to literal C/product/
inverse-C on grid 3s is valid only after the explicitly tested exact
grid alignment. It is not an uncharged native normalization.

For real coefficient lists of length r and magnitude at most L, every
ordinary product coefficient has magnitude at most `r L^2`. The radix
choice `B>2rL^2` ensures a unique balanced representative for every
coefficient, including negative coefficients. Evaluating both inputs at
B, multiplying the complete signed integers and decoding all `2r-1`
digits therefore reconstructs the FULL ordinary product. The zero-tail
check matters for signed encodings. Only afterward does subtracting the
upper degree-r coefficients perform the negacyclic fold. Omitting that
complete decoding or choosing the radix from coefficient precision alone
can corrupt recovery.

A Gaussian leaf uses the three actual real products
`P=ar*br`, `Q=ai*bi`, `S=(ar+ai)*(br+bi)` and returns
`(P-Q,S-P-Q)`. A real-only leaf uses one real product and rejects imaginary
data. Thus the named packet has 3^s polynomial leaves and respectively
`3*3^s` or `3^s` signed integer products. These are algorithm counts,
rather than general bilinear lower bounds.

Each leaf source coefficient sums at most 2^s original coefficients;
the third Gaussian product adds one more bit. Hence its strict balanced
radix has `O(p+s+log r)` bits, and its COMPLETE integer operand has
`Q=O(r*(p+s+log r))` bits. The displayed conservative bound
`r*[2(p+s)+bit_length(r)+4]+2` is sound. It prices a full polynomial
record, rather than one p-bit coefficient. The measured complete operand
lengths are finite producer observations; the all-size cost still needs
a paid multiplier and actual record slicing/movement.

The four full producer cases use nine, nine, 81 and 243 integer products.
Their ordinary balanced coefficient counts are
`9*5+9*9+81*13+243*5=2394`. Their Gaussian endpoint component counts
are `12+40+112+96=260`. These formulas independently reconstruct the
reported counts from the case definitions. They are not an independent
replay of the recorded operand values.

The source explicitly uses ordinary exact Python multiplication as a
finite arithmetic reference; it does not call an improved research
multiplier. Its rejected weak-radix example correctly targets the missing
convolution growth guard. Existing fixed-grid and packet prefix controls
remain separately scoped: this source records product operands and
radix decoding, but does not instrument every physical tape buffer,
arbitrary dirty field or every recursive arithmetic prefix.

For the time comparison, use the
[independent packet envelope](fused-packet-size-envelope.md). The current
native selected width E, packet width s and growing chunk width K are
distinct. A complete polynomial product row can have a different budget
from a native wrapper. Neither a short-record coefficient estimate nor
an assumed same-size improved multiplication oracle can replace this
complete Q-bit ledger.

The dated analytical receipt binds the producer hash and immutable full
run identity. This is internal research review and not formal verification
or an independently reproduced native implementation.
