# Primary-source Walsh model screen

This screen separates published arithmetic or RAM statements from the paid
native Gaussian-dyadic problem. It establishes no new transform or multiplier
bound. The pinned primary PDFs were acquired on 2026-10-09; byte hashes,
immutable ignored paths and recovery URLs are in
[the source receipt](../../configs/synthesis/walsh-literature-screen.json).

[Alman and Rao, arXiv:2211.06459v2](https://arxiv.org/html/2211.06459v2),
14 June 2023, Theorem 1.1 and Sections 2.2/6, give a Walsh arithmetic count
with leading constant 23/24. Their small-block sparse/low-rank decomposition
shares intermediate sums and moves powers of two through recursion. It
demonstrates why cancellation and scaling deserve exploration. The paper
counts field operations and treats arithmetic access permutations separately
from native tape movement. Its stated improvement is a leading constant;
importing a positive logarithmic exponent or a native precision guarantee
would require additional evidence.

[Alman, arXiv:2211.04643v1](https://arxiv.org/html/2211.04643v1),
9 November 2022, Theorem 1.1, analyzes constant-size finite fields in a RAM
bit-operation model with lookup tables, obtaining a log-log saving. Section 3
uses table block length of order `log(D)/log(q)`. In our whole-coefficient
integer core, avoiding wrap requires `log(q)` at least the coefficient bits
plus `log(D)`, so that direct table block is bounded. This is a conditional
model comparison, not an exclusion of bit slicing, another representation,
or paid native lookup algorithms. The paper's conclusion also identifies
data permutation as an implementation obstacle in its word RAM extension.

[Serre and Pueschel, arXiv:1710.08029v1](https://arxiv.org/abs/1710.08029v1),
22 October 2017, characterizes butterfly arrays interleaved with binary
linear address permutations. That declared class does not cover our nonlinear
multiplicative field ordering, arbitrary cancellation circuits, or padded
convolution. It is useful context for stating the exact routing premise,
rather than evidence for a general lower bound.

No claim is made that these are the latest or optimal transforms in every
model. Their dated, pinned statements are the inputs to this screen. A useful
transfer must retain coordinate access, coefficient alphabet/precision,
scaling prefixes, table generation and restoration. The current exact
field-character convolution remains an independently derived finite reduction
with those native obligations open; external novelty is not asserted.
