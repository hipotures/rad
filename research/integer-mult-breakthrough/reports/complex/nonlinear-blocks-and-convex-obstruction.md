# Right-Toffoli frames are dominated in the tested block interface

Status: **EXACT FINITE FAMILY CERTIFICATES AND A CONDITIONAL LOCAL MOMENT
OBSTRUCTION**. No new multiplier, native router or exponent is claimed.

## Question and interfaces

The full-Clifford component results justify testing frames beyond the Clifford
group. In three selected address bits, take all 135 literal Gaussian-dyadic
Clifford representatives F and replace them by F P, where P is a Toffoli
permutation with each of the three possible targets, or the ordered composition
with targets 0,1,2. Right composition matters: a common left monomial gauge
only permutes or phases the two transition matrices and cannot reduce their
admitted child ranks. The graph endpoints are all 64 symmetric quadratic
frames. Every input and output incidence of a scalar gate is charged.

The [uniform screen](../../code/complex/nonlinear_common_frame_screen.py) admits
an edge only if its complete exact matrix is an address permutation and unit
row/column gauges around one `C^tensor r` child, with spectator blocks fixed.
Address permutations are allowed to be arbitrary finite permutations. This is
an optimistic exact-array interface: their fixed-tape realization is unpaid.
Flat disjoint support blocks must be Walsh character tables after dephasing.
The checker reconstructs every admitted coefficient, and all 8640 plain
Clifford controls reproduce their independent Lagrangian distances.

The [nonuniform extension](../../code/complex/nonuniform_phase_blocks.py) allows
disjoint blocks of different ranks r_b and sizes 2^r_b. Its mean rank

    mu = sum_b 2^r_b r_b / 8

is a volume proxy. It is not a literal child count or a proved recursion.
The extension also reconstructs each admitted matrix exactly.

## Complete finite evidence

Each row below comprises all 135 times 64 actual transition matrices. Each
family was one useful worker in the four-worker runs.

| Family | Uniform admitted edges | Variable-block admitted edges | Uniform single-frame dominated candidates | Variable-block single-frame dominated candidates | Fixed-mixture certified candidates |
| --- | ---: | ---: | ---: | ---: | ---: |
| Toffoli target 0 | 1920 | 2112 | 135 | 87 | 135 |
| Toffoli target 1 | 1920 | 2112 | 135 | 87 | 135 |
| Toffoli target 2 | 1920 | 2112 | 135 | 87 | 135 |
| Ordered three-target composition | 352 | 352 | 135 | 135 | 135 |

Uniform discovery used 4097 seeded four-incidence sets per family. The enlarged
interface sampled admitted sets of the 48 undominated candidates as well as
1025 general sets. Neither produced a gain. These samples motivate the complete
certificates; the final negative does not depend on sample coverage.

The variable-block Toffoli cases add 48 edges with four rank-zero singleton
blocks and one rank-two block (mean one), and 144 edges with two rank-one
blocks and one rank-two block (mean three halves). Other admitted edges are
uniform. Edges with overlapping supports or nonreal dephased coefficients
are outside the interface, rather than assumed expensive by a universal bound.

For example, `F=Htilde_1 P_Toffoli0` admits graph codes 0 through 11, with
means `[1,2,1,2,3,3,3,3,3/2,3/2,3/2,3/2]`. No single Clifford candidate
dominates this vector. The equal mixture of Lagrangians `[4,2,1]` and
`[17,10,4]` does, simultaneously for every admitted code. This demonstrates
why a single-frame screen alone would leave a false promising residue.

The [convex checker](../../code/complex/nonuniform_convex_certificate.py)
examines all 9180 unordered equal-weight pairs of the 135 Clifford frames.
For every nonlinear candidate it finds one fixed pair A,B such that

    mu(c) >= (r_A(c)+r_B(c))/2

for every admitted endpoint c. All comparisons are exact rational/integer
comparisons. The pair cannot change with the terminal or incidence weight.
An empty admitted row has no usable terminal set and is vacuously dominated.

Complete run identities and unchanged producer hashes are in the protocols:

- [Uniform screen](../../runs/20261008T225901Z-complex-nonlinear-frames/protocol.json).
- [Variable-block screen](../../runs/20261008T230900Z-complex-nonuniform-blocks/protocol.json).
- [All fixed-mixture certificates](../../runs/20261008T231408Z-complex-nonuniform-convex/protocol.json).

The result JSON files retain all dominance rows, allowed codes and fixed pair
labels; protocols identify the ignored complete logs. The complete uniform/convex row-level text and logs are published unchanged
in the evidence namespaces recorded in the artifact manifest. The larger
Toffoli convex files have compact readable summaries with exact omission lists.

## Conditional tensor moment implication

For `G^tensor f`, a direct-sum block word has width R=sum_i r_bi and volume
fraction product_i(2^r_bi/8). Under a complete, volume-preserving grouping
interface, the normalized width moment is exactly E[(R/f)^tau]. The bounded
law of large numbers sends this to mu^tau for any fixed positive tau. This
is an analytical limit of the exact block distribution, not an implementation.

For 0<tau<=1, concavity gives

    mu(c)^tau >= ((r_A(c)+r_B(c))/2)^tau
              >= (r_A(c)^tau+r_B(c)^tau)/2.

Sum with any nonnegative incidence weights. The nonlinear local moment is at
least the average cost of the two fixed Clifford choices, hence at least the
better Clifford cost. Thus even ideal routing cannot yield an asymptotic
concave-rank moment gain for these families and these endpoints. Finite-f
moments can lie below their limit; this statement does not discard a finite
architecture on that basis or supply a general circuit lower bound.

The theorem does not cover other nonlinear permutations, nonblock or multi-child
edges, nonunitary frames, nonlinear endpoint frames, or a whole network whose
common choices and continuation frames differ. It also does not replace the
complete child multiplicity ledger needed for a kappa claim.

## Paid routing and precision obligations

Tensor words with differing active rank require paid routing into variable-width
child streams while retaining all fields, spectators and arbitrary dirty bits.
Sorting by total rank does not alone compact selected active coordinates.
Padding to the largest cube can duplicate volume exponentially in f; a full
bit-by-bit radix pass can lose the desired exponent. Neither cost is hidden
in the mean-rank proxy.

A packed Toffoli needs two predecessor controls, its target chunk and an
independent restored guard chunk. That is four complete chunks even though
the algebraic permutation acts on three bits. A specialization of the packed
eight-rotation proof is plausible when the Boolean control depends only on
unchanged predecessor chunks, but its full fixed-tape timing and error repair
have not been verified here. The current negatives make that implementation
unnecessary for promoting this family.

## Reproduction and next direction

```sh
python3 -B research/integer-mult-breakthrough/code/complex/test_nonlinear_blocks.py
python3 -B research/integer-mult-breakthrough/code/complex/nonuniform_convex_certificate.py \
  --family toffoli0 --output /tmp/fresh-toffoli-convex.json
```

Only Python's standard library is required. Tests reconstruct all four families,
check the literal variable-block example and reject a corrupted phase gauge.
This is bounded finite verification, not formalization. Independent review of
the new convex and tensor-limit argument is requested separately.

The next distinct hypothesis is a sparse center/null source basis, with fully
paid external basis adapters and dirty chronology. The nonlinear screen does
not constrain that mechanism.

## Independent coordinator review of the limit

The coordinator independently replayed all four bounded family checks and
reviewed the fixed-pair comparison. For iid ranks in [0,3], variance of their
mean is at most 9/(4f). For 0<tau<=1 the power map satisfies
abs(x^tau-y^tau)<=abs(x-y)^tau on nonnegative arguments. The second-moment
bound therefore gives an explicit difference from the limiting moment of at
most (3/(2 sqrt(f)))^tau. This justifies the limit without ordering finite-f
moments. Jensen applies to the fixed Clifford pair after this limit; it cannot
be applied directly to order arbitrary finite nonuniform block distributions.
The review accepts this conditional local asymptotic conclusion, with complete
volume-preserving grouping still a premise. It supplies no native router or
whole-network exponent.

Complete row certificates can be recovered from [Toffoli0](../../evidence/20261008T234042Z-checkpoint-five-20261008T231408Z-complex-nonuniform-convex/results/toffoli0.json.gz),
[Toffoli1](../../evidence/20261008T234042Z-checkpoint-five-20261008T231408Z-complex-nonuniform-convex/results/toffoli1.json.gz) and
[Toffoli2](../../evidence/20261008T234042Z-checkpoint-five-20261008T231408Z-complex-nonuniform-convex/results/toffoli2.json.gz).
Their original local files remain unchanged and ignored.
