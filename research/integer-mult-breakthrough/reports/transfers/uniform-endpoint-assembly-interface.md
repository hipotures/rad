# Uniform endpoint families and a disk-valued assembly interface

Status: **CONDITIONAL NUMERICAL CONTRACT, ANALYTICAL TRANSFER AND EXACT
FINAL-SCAN CONTROLS**. This extends the useful endpoint families of the
[rounding/depth lemma](unitary-rounding-depth-contract.md) and binds a
proposed final numerical interface to the original assembly's error
calculation. No faster native supplier, new characteristic root, or
larger multiplication exponent is claimed.

The original inputs are `original-layers` and `original-assembly` from the
research input manifest. Their source is
[openai/math revision adc7f124](https://github.com/openai/math/tree/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026/build/sections).
The inspected 05-layers.tex has SHA-256
`20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594`;
08-assembly.tex has SHA-256
`763d7945b1e1ec4ebae9b799bcefcc45fa9bae6e2ffad799868a9c3d513dbd4a`.
These primary sources are read-only. The following changes are proposed
interfaces, not modifications or automatic acceptance of their original
all-size hypotheses.

## Endpoint families with a uniform numerical bound

The useful property is a uniform operator-norm bound for every COMPLETE
endpoint actually called by the recursion. If an inverse is called, it
must have its own bound; an inverse never called is not needed by the
error transport argument. Forward contractions therefore also qualify,
provided all live fields and buffers are included. Rectangular zero
embeddings and final projections are contractions. Address-dependent
branch decisions must remain exact and independent of rounded payloads.

For a fixed branching count s and at most J local norm-growing operations
per node, each of norm at most B, suppose all completed child types have
norm at most A0>=1, independently of width and column count. At depth
L, the unresolved-stack argument gives a bound of the form

```text
Gamma <= (B^J A0^(s+1))^(L+1).
```

A harmless extra fixed factor A0 can be included when using prefix/tail
inverses for an interval. Alternatively the two-active-stack decomposition
bounds intervals directly, including rectangular padding maps. With that
fixed enlargement, prefix/tail norms are at most Gamma and interval norms
at most Gamma^2. Thus the logarithmic precision allowance remains
`O(log N+L)` under the same complete injection-count and local-word
contract. This is a sufficient analytic bound, not a cheap circuit.

Several useful nonunit endpoint families meet this condition.

* With W fixed banks, let U_in(e) and U_out(e) be block-diagonal unitary
  address frames, including their exact phases. Let
  `M in GL_W(Z[i,1/2])` be fixed, with dyadic inverse. Then
  `E_e=U_out(e)(M tensor I)U_in(e)^-1` has exactly the norm of M, and its
  inverse has exactly the norm of M^-1. These bounds do not depend on e
  or f. A finite set of such bank matrices and a fixed number of complete
  stages remains uniformly bounded. The address frames can differ
  between banks; their literal implementation and prefixes remain paid.
* An address-operator shear `[[I,0],[c V_e,I]]`, with fixed dyadic c and
  unitary V_e, and its inverse have norm at most `1+|c|`. Unitary frames
  on either side preserve that bound. This covers some noncanonical
  joint/partial-output families without making them canonical C targets.
  It supplies a numerical condition, not an assembly adapter or a
  contracting moment for those targets.
* A similarity `G_e^-1 U_e G_e`, with unitary U_e and a uniform condition
  bound on G_e, qualifies. A SINGLE global Boolean amplitude gate with
  values 2 and 1/2 has condition 4 regardless of the number of bits in its
  Boolean predicate. Its tensor product over f columns instead has
  condition 4^f. A uniform bound cannot be inferred from that tensor
  bound. Exact cancellations may still yield a bounded endpoint, but
  then its actual local prefixes need an independent proof.

This endpoint claim does not hide repeated scaling in a local primitive.
An operator described as one gate but implemented with width-many norm-
growing steps does not meet fixed J. Likewise a `(1+i)^f` gauge cannot
be treated as a fixed B operation. Its literal compensation and buffers
must be bound separately.

Z_e and signed T_e=Z_e diag((-1)^weight) have norm phi^e, where
phi=(1+sqrt(5))/2. Their inverse norms grow similarly. They do not meet
the uniform condition by their ordinary Euclidean endpoint norms. A
different metric would need a coherent proof for the entire word,
including control projectors, frames and conversion back to the actual
coefficient norm. The present contract does not supply that proof.

## A disk interface requires a coefficient-domain premise

Original 05-layers supplies the exact normalized Walsh tensor H followed
by componentwise truncation Q_p. Every row of H has absolute row sum one,
so an input of coefficient modulus at most one has a true output in the
complex unit disk. Q_p then preserves that disk. Its error is below
`sqrt(2)*2^-p`. This coefficient-domain fact is separate from global
Euclidean unitarity of the underlying C primitive: an arbitrary unitary
transform can increase one coefficient's modulus beyond one.

For a proposed approximate normalized layer, assume separately that every
TRUE coefficient z satisfies `|z|<=1`. Suppose its approximate coefficient
w meets the complete absolute bound `|w-z|<=eta`, with

```text
p>=1,    h=2^-p,    0<=eta<=h/8.
```

First truncate both components of w toward zero to grid h. Then choose
the component of larger absolute value, choosing the real component on
a tie, and move it ONE grid unit toward zero if it is nonzero. Let R_p
be that exact final operation. It returns a disk-grid value and satisfies

```text
|R_p(w)-z| < 3h.
```

Here is a rational bound valid even at the smallest permitted p. Write
v=Q_p(w). Truncation does not increase modulus, so `|v|<=1+eta`. If v is
already in the disk, the extra move stays there. Otherwise its largest
component has magnitude a>1/sqrt(2)>1/2. As h<=1/2, subtracting h from
that component decreases squared modulus by

```text
2*a*h-h^2 > h-h^2 >= h/2.
```

The possible squared excess is at most

```text
2*eta+eta^2 <= h/4+h^2/64 <= 33h/128 < h/2.
```

The move therefore reaches the disk. Its error from v is at most h;
truncation changes w by less than sqrt(2)h. Together with eta<=h/8,
the total is strictly below 3h. The selected component is nonnegative
after the magnitude decrement; zero is never moved across zero.

An abstract exact witness shows why ordinary Q_p is insufficient given
only the generic disk target/error contract. For p>=3, put
`z=(1-h^2)+i*h` and `w=1+i*h`. Then z is inside the disk,
`|w-z|=h^2<=h/8`, but Q_p(w)=w is outside. R_p(w)=(1-h)+i*h is inside.
This ideal target uses a finer grid. It is not claimed to be the output
of the original normalized butterfly on its prescribed input domain.

The [exact source](../../code/transfers/disk_safe_rounding.py) passes
four p=3/8/32/128 cases, four complete scalar fields each: 1104 admitted
records and four such negative controls. It also checks the domain/error
premises and final zero-padding targets. A final ideal zero coefficient
with error at most h/8 truncates to exact zero. This does not permit
intermediate correlated scratch erasure.

R_p is implementable by a full scan under the existing fixed-format
stream contract: read the two complete component words, truncate their
magnitudes, compare, decrement, restore signs and write the prescribed
output words. All scalar copies, reads and writes cost O(p) per
coefficient for O(p)-bit words. With complete record payload 2rp,
this costs O(V). The Python controls are arithmetic references, not a
compiled multitape machine. Input/output width conversions and bounded
buffers are part of the stated scan interface.

## Conditional binding to the original assembly sensitivity

The numerical endpoint lemma can make eta<=2^(-p-3) if its actual complete
state has fixed B,J and depth L<=d, and

```text
q >= p+3+ceil(log2 N)+ceil(log2 Gamma)+O(1).
```

In the original shape, log of the complete scalar volume is O(p),
`d=Theta(p^epsilon)` and `dK=O(p)`. Fixed branching permits
`log N=O(log M_max+d+log p)`, even for exponentially many recursive
calls; no polynomial call-count premise is used. Under the explicit
complete-volume and literal-prefix bounds, internal q and signed guards
are still O(p). This requires rebinding actual record widths and native
overhead; numerical feasibility does not prove them.

Using R_p changes the original per-layer coefficient error constant.
It cannot be represented as the old exact-before-Q_p proposition. A
conservative recomputation of original 08-assembly is nevertheless
straightforward. Keep its exact maps, scales, disk-valued resampling,
phase construction, exact products and recovery hypotheses. Replace only
the layer error by `3h`, h=2^-p. With L=log2 T and M=T/r, the following
sufficient error coefficients multiply h:

```text
synthetic transform:      <=3L,
normalized ring product: <=M(9L+2)<=11TL,
twisted complex product: <=11TL+12<=23TL,
chirp transform:         <=23TL+10<=33TL,
source transform:        <=34*2^gamma*TL.
```

Here TL>=1, and the last line uses the eventual original condition
`2*d*p^2<=TL`. Its source and opposite maps are exact contractions.
The disk margins .6/.701/.501/.26 can be replaced by slightly larger
fixed margins, all below one, because these coefficients times h tend
to zero. The two exact scales by S and the input unscaling then give

```text
E_w <=104*2^gamma*T^2*L,
final absolute error <1664*b*2^(-b+gamma)
                     <=1664*b*2^(-3b/4)<1/2 eventually,
```

using the original p=6b, S<=T<2^b, L<b and gamma<=b/4. True final
coefficients are real integers, so unique nearest-integer recovery and
the separately exact address restoration and carry procedure still
follow under those retained assumptions. The extra O(V) final scans do
not change a supplied per-layer O(V d^lambda) bound with lambda>=0.
They do not establish such a bound themselves.

The original whole-assembly exponent ledger is not transplanted to a new
network. This sensitivity calculation shows that a fixed-factor change
in the layer approximation constant is compatible with its recovery
margin. A new native profile must still prove canonical target semantics,
strict paid moments, well-founded stopping, full row stock, all routing,
actual precision and whole-integer assumptions. The frozen complex root
and its target threshold are unaffected by this numerical observation.

## Continuation criterion and reproduction

Use these numerical interfaces when a genuinely cheaper canonical or
changed jointly assembled supplier meets the complete endpoint and
local-word hypotheses. The decisive task is then a literal native word
with its row/volume/time ledger and the actual outer integer inputs and
scales. Do not spend a parameter sweep on the final scalar scan.

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/disk_safe_rounding.py --workers 1 --small
```

Four workers reproduce the full four cases. The only runtime closure is
that authored source and its portable configuration; it uses the Python
standard library. The complete source/seed/protocol and all generated
scalar records are retained in the run. A fresh output path is required
to preserve completed evidence. Independent Q_s product-format recovery
is reviewed [separately](rounded-product-independent-review.md).

Attribution: AI-assisted internal mathematical exploration and exact
finite arithmetic controls; no formal verification or external review.
