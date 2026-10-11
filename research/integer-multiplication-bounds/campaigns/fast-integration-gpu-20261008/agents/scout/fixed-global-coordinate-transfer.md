# Fixed global address-coordinate transfer

The selected improvement applies one global permutation to an already compiled
matrix-weighted word. It preserves the scalar graph, carrier choices, paid
roles, literal XORs, physical events and output dispatch. The new physical
source labels are derived from this permutation. Scalar compilation continues
to use the original input order and matching certificate.

Let `order[i]` be the old coordinate occupying new position `i`, and let
`P[i, order[i]]=1`. The parent scalar-to-address labeling is `Q`. The new
labeling is exactly `inverse(order) composed with Q`. For the selected h25
word, `order=[3,1,0,2,4,...,24]`; the parent exchanges coordinates 22 and 23,
and the new labeling starts `[2,1,3,0]` while preserving that exchange.

For every actual integer frame matrix B, the new frame matrix is PB. Both
H0=I−J/9 and Lβ=I−βJ commute with P. Therefore BᵀH0B is unchanged and the
actual rational projector becomes PΠP⁻¹. Containment, positive Gram forms,
idempotence and every physical source/sink condition are covariant. The
constructor checks this column identity for every frame, then an independently
authored full-word checker reconstructs all scalar source supports, sinks,
both complete dirty role orientations and the actual transition multiset.
A second implementation permutes the parent binary directly; its bytes must
equal the independently reconstructed binary.

The ordered northeast profile is recomputed. A permutation can change its
contiguous child widths even though its rank and source weights are invariant.
Full rational CRT for the selected h25 word at β=−1/15 gives local moment
909405.8346570414, compared with 909405.8459796387 for the identity address
order at the common screening saving 257/5,000,000. These numerical local
moments alone do not certify an exponent.

All lexical source triples and singleton centers are relabeled bijectively.
The complete Cartesian family of 4,073,300 source pairs is consequently the
same normalized DATA family after its pair labels are permuted. Coordinate
products are permuted together with source membership, and every original
triple appears once. This statement uses the complete independently checked
DATA certificate at β23=1/15 and β25=−1/15; it does not reuse a certificate
from β25=7/207. Source, center, sink, scalar and stock interfaces are separately
checked against the actual transformed word. W=136,283,234 and total rank
mass 78,361,012,650 are unchanged. All copied centers and cleanup remain paid.

The remaining all-size analytic, routing, precision, fixed-tape and rational
address compiler assumptions are inherited unchanged from the pinned sources.
Finite F2 role restoration and the algebraic array-gauge bridge have their
previous explicit scope; the address realization is conditional. This note
does not promote finite role checks to an unconditional all-size theorem.

Selected reconstruction is executable with
`code/reproduce_fixed_global_coordinate_candidate.py --work <fresh-work>`.
It downloads the public pin with gh when `--source <immutable-snapshot>` is
omitted. It needs Python3, g++, Boost headers, Git and gh; CUDA is unnecessary
for selected-only reproduction. The small fixture and regeneration manifest
under `fixtures/` bind the complete authored closure and parent selected-only
source recovery. `--prepare-only` validates this closure and emits commands.
The public-source parent was already cleanly replayed for both full axes;
the complete coordinate reconstruction and its native profile were executed.
The orchestration wrapper itself has only its preparation path tested.

Avi Eisenberg's PR62 supplies interval strips and core-aware pair assembly;
eumemic's PR57 supplies joint invertible synthesis and paid reclamation.
Alejandro Zarzuelo Urdiales's PR61 refines parameters. Rohan Arun, Chafik
Boukhalfa and every directly inherited predecessor retain their attribution.
Earlier source partition and whole-chain cloning work is credited within its
proved scope. OpenAI Codex assisted the present investigation. Inherited
licenses and disclosures apply.
