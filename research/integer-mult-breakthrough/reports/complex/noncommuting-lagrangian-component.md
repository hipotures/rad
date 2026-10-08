# A noncommuting common frame saves one rank on an exact four-port gate

Status: EXACT FINITE COMPONENT, independently reviewed rank geometry.
This is a local compiler example. No complete multiplication motif,
improved characteristic or exponent has been obtained.

## Question and geometry

The general symmetric quadratic interface still uses commuting
Fourier-diagonal frames. Full fixed-size Clifford frames allow a larger
space. Up to nonrecursive monomial phases and address routing, a frame
can be represented by a Lagrangian subspace in binary symplectic space.
The abstract transition rank between two such subspaces L and M is

    d(L,M)=n-dim(L intersect M)=rank([basis(L);basis(M)])-n.

The [original bounded screen](../../code/complex/lagrangian_phase_screen.py)
enumerates all Lagrangians using symplectic H, S and CNOT generators.
Its graph chart consists of `L(A)={(z,Az)}`, for symmetric binary A.
A common scalar gate is assigned one frame; every incoming and outgoing
role incidence must be counted. An odd number of sampled terminals is
an abstract metric example until actual continuation is supplied.

Primary context is Dehaene and De Moor,
[The Clifford group, stabilizer states, and linear and quadratic operations over GF(2)](https://arxiv.org/abs/quant-ph/0304125v1),
18 April 2003. Theorem 4 decomposes a symplectic map into index changes,
quadratic phases and a partial Hadamard with dimension given by the
mixing-block rank. The paper supplies Clifford algebra, not a fixed-tape
integer-multiplication algorithm. The implementation below is original.

Four workers completed [the first screen](../../runs/20261008T220448Z-complex-lagrangian-screen/):

| n | Terminal count | Cases | Strict full-frame gains | Maximum rank gain |
| --- | ---: | ---: | ---: | ---: |
| 2 | 3 | All 56 graph triples | 0 | 0 |
| 3 | 3 | All 41664 graph triples | 4480 | 1 |
| 3 | 5 | 2048 seeded sets | 100 | 2 |
| 4 | 5 | 512 seeded sets | 62 | 2 |

The counts are finite metric evidence. They do not specify a scalar
algorithm or turn omitted output incidences into zero-cost endpoints.

## Explicit two-role gate with four charged incidences

Use three address coordinates. Write phase-space masks with Z in bits
0..2 and X in bits 3..5. For symmetric A, let
`K_A=H diag(i^q_A) H`, using the canonical Z4 lift with diagonal
coefficients A_ii and off-diagonal coefficients 2A_ij.

The two incoming role frames have matrices

    A0 = [[1,1,0],[1,0,0],[0,0,0]],
    A1 = [[1,1,1],[1,0,1],[1,1,0]].

The two outgoing continuation frames have matrices

    A2 = [[1,1,0],[1,0,0],[0,0,1]],
    A3 = [[0,0,0],[0,1,1],[0,1,1]].

Their upper-triangular binary generator codes are 3,23,35,56, respectively.
Every one of the 64 symmetric graph candidates has total incident rank
at least six. The unique minimum over all 135 Lagrangians has basis

    Lstar = [32,19,10]

and incident ranks `[1,1,1,2]`, totaling five.

Choose a literal Gaussian-dyadic common frame

    F=K_A0 * Htilde_2,   Htilde=S*C*S=(1+i)/2 * [[1,1],[1,-1]].

Htilde acts on address bit 2. The inverse symplectic image of the
computational Z subspace is Lstar; the displayed operator uses no
irrational coefficient. For physical input arrays x,y, apply

    E0=F*K_A0^-1 to x,
    E1=F*K_A1^-1 to y,
    y <- y+x,
    E2=K_A2*F^-1 to x,
    E3=K_A3*F^-1 to y.

In their virtual endpoint coordinates this is exactly the in-place shear
`y <- y+x`, with x retained. Algebraically its physical map is

    diag(K_A2,K_A3) * shear * diag(K_A0^-1,K_A1^-1).

The common frame cancels across the scalar shear because the same linear
operator is applied to both roles. Both inputs and both outputs are paid;
the output frames are explicit continuation conditions. Reversing the
shear and all four transitions restores arbitrary physical arrays exactly.

The [literal checker](../../code/complex/lagrangian_gate_witness.py)
finds an exact normal form for EACH transition:

    affine output routing * unit quadratic chirp *
    (C^tensor rank tensor I) * unit quadratic chirp * input routing.

All coefficient matrices are compared entry by entry with their original
Gaussian rational matrices. All chirp exponents are verified to be Z4
quadratics with even off-diagonal coefficients. The normal forms retain
their affine offsets and basis columns, so routing is not silently free.
Rank-one and rank-two children are strict contractions of a three-slot
parent. Inverse edges use the same rank after the usual paid inverse-C
unit wrappers.

Four workers completed [the component replay](../../runs/20261008T221238Z-complex-lagrangian-gate/).
They cover one and two columns, chunk widths one and two, and both
positions within a two-bit chunk. Four independent Gaussian coefficient
fields pass 3200 forward/reverse output values. The bounded tests also
check all 16 two-role basis inputs, wrong chirps and spectator preservation.
This is exact finite payload evidence. The array adapter is an explicitly
specified finite affine map, not a measured fixed-tape router.

## Independent interpretation and limits

The reversible-synthesis track imports none of this producer and confirms
the unique 5-versus-6 median. It also proves a structural criterion: if
the span of all `Lstar intersect L(A_i)` is transverse to the vertical
Lagrangian, that span extends to a symmetric graph preserving every
intersection. A strict graph-chart gap therefore requires a vertical
direction generated jointly by those intersections. Here the vertical
mask 32 is the sum of intersection directions 25 and 57. See the track's
[independent completion certificate](../synthesis/lagrangian-chart-boundary.md).

This local gain need not survive a whole network. Under the inherited
auxiliary source/sink contract each role runs from frame zero to full,
so the triangle inequality alone already forces at least n total ranks
along its full path. The old monotone side paths attain that bound.
Changing an internal gate can move a cost to another incidence. The
coordinator also proves that an unassisted three-shear two-role signed
exchange remains at cost at least 2n even with full Lagrangian frames.
Helpers, branching or different chronology need a complete audit.

The leverage hypothesis is a network where noncommuting frames remove
costly forced returns or permit scalar sharing excluded by the old chart.
The next test must pay all continuation edges and demonstrate a favorable
whole child distribution. The one-rank component does not establish
that kappa crosses 1e-4.

## Reproduction

```sh
python3 -B research/integer-mult-breakthrough/code/complex/test_lagrangian_phase_interface.py
python3 -B research/integer-mult-breakthrough/code/complex/lagrangian_gate_witness.py \
  --columns 2 --chunk-width 1 --offset 0 --output /tmp/fresh-lagrangian-gate.json
```

Only Python's standard library is required. Output paths must be fresh.
