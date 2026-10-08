# Cancellation-free complex side circuit with binary frames

Campaign `20261007T222521Z`; start `2026-10-07T22:25:21Z`, deadline
`2026-10-08T08:25:21Z`. This clock is unchanged. The immutable reference is
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2` of
`https://github.com/CrocSwap/integer-mult-bounds` as identified by the
campaign input manifest. The local reference remains unmodified.

## Status and scope

The h=50 finite side circuit is verified by exact formal supports,
1,180,834 directed frame-edge checks with explicit norm-one witnesses,
and three signed dirty-scratch probes. It has 590,417 active additions and
39,200 designated partial outputs, hence 629,617 physical auxiliary roles
under the baseline reversible compiler. The old complex side construction
uses 320,577,600 roles. At h=8, all 963 local source/scratch/center basis
vectors and three signed dirty probes pass. The complete finite,
phase/rank/guard and decaying-recurrence transfer, as well as all three
strict arithmetic rows, now pass [independent review](review-complex-transfer.md).
The strongest conditional witness in this checkpoint is
`kappa=96380770761102682050463/10^40`.

The full-bank stage sharing and terminal checks are separate fresh exact
evidence, so the original executed prototype and its hashes remain intact.
The fresh h=8 forward/inverse/forward test checks all 175,616 coordinates
in each data bank and restores all 5,688,704 dirty auxiliary coordinates
across 9,408 invocations. The h=50 shared rank arithmetic passes.
The complex scalar field is the Gaussian dyadic field, while its label
field is F2, as in upstream section 3. This is the existing binary phase
interface; no inference of rational frames from a modular computation is
being made. The separate bit primitive retains its rational frame proof.

Novelty is unclaimed. The changed finite circuit and frame assignment are
substantive constructions; they are not a re-rounding of an old exponent.
The complete integer multiplication claim remains conditional on the
unmodified upstream fixed one-dimensional tape interfaces and assembly.

## Exact side map

Let h be even and at least 8, and index input coordinates by all triples
T in [h]. Write v=binom(h,3), m=h^3, N=v^3. For a target triple S define

```
D_S = sum(x_T : T intersection S is empty),
E_S = sum(x_T : |T intersection S|=2).
```

The original complex correction is `(D_S-E_S)/2`: its coefficient is
`-(|T intersection S|-1)/2` when T differs from S. The central gather/scatter
has coefficient `(|T intersection S|-1)/2`, including coefficient 1 when
T=S. Their sum is exactly the identity, with all zeros included.

E is computed using one leave-one-out prefix/suffix circuit for each pair
P: its outputs sum all x_(P union {j}) except one chosen third vertex.
The three pair outputs for S are disjoint formal sums, and their sum is E_S.

D uses the following weighted deletion recursion. Its inputs are disjoint
formal sums associated with hyperedges of size at most k, including a
possible empty-edge constant, and it returns sums avoiding every omission
set of size at most k. Here k starts at 3.

1. Pair consecutive vertices into blocks and sum weights with the same set
   of touched blocks. Recursively compute deletion answers on the contracted
   set of blocks.
2. For every nonempty set X containing at most one vertex in each block,
   collect weights whose edge contains X and no other vertex in those
   blocks. Contract the remaining vertices into the other blocks and
   recursively compute deletion answers of order k-|X|.
3. For an omission S let B be its touched blocks. Each block in B has at
   most one remaining vertex; call their union R. Add the contracted answer
   avoiding B to the component answer for every nonempty X subset of R,
   excluding all touched blocks in B outside those containing X.

A surviving original edge occurs in exactly one part: X is its intersection
with R. Edges meeting S occur in none. This proves correctness and disjoint
support at every output combination. Contracted weights also partition
their original supports. The recursion decreases the number of vertices;
order 1 uses prefix/suffix leave-one-out sums, order 0 takes a balanced
total, and at most four vertices are handled directly. The executable
checker verifies disjoint operands at every retained addition and compares
every D/E output to an independent exact stripe-mask formula.

Equal non-input sums are interned separately within D and E. These two
families may need different frames; equality of scalar sums alone does not
authorize their physical identification. Only the input nodes are shared
between families.

## Binary frames for the complete finite DAG

Work in F=F2^h with its ordinary dot product. Triple indicators t_T have
norm 1. Frames are assigned to retained nodes as follows.

* An input node has its triple line `<t_T>`.
* A D node has the coordinate span on the union V of its contributing
  triples if |V|<=h-4. If |V|=h-3, use `t_(V complement)^perp` immediately.
* An E helper for the pair P and the set J of third vertices has frame
  `span(t_P+e_j : j in J)`. This basis has Gram matrix I because |P|=2.
* Both additions combining the three E helpers for target S have frame
  `t_S^perp`. Every designated D or E output has exactly this frame.

Every retained D node is an ancestor of a D_S output and the DAG has no
cancellation. Its contributors avoid S; consequently |V|<=h-3. A used
node with |V|=h-3 determines S uniquely. Thus the enlarged kernel frame is
consistent with every downstream use. A retained E helper has |J|<=h-3:
it is an ancestor of a leave-one-out sum over h-2 possible third vertices.

Each frame is nondegenerate. Triple lines and their complements split F
orthogonally. Coordinate frames have a coordinate basis; pair helpers have
the displayed orthonormal basis. Every forward edge joins nested frames.
Inclusions into a target kernel use either disjointness from S or even
intersection with S. Nonzero orthogonal residuals have explicit norm-one
witnesses:

* Coordinate into coordinate: an unused coordinate unit. A triple line
  entering a larger coordinate frame also leaves such a unit.
* A proper coordinate frame entering a target kernel: a coordinate outside
  S union V. The borderline |V|=h-3 node was already enlarged to that
  exact kernel, so it gives a zero residual instead.
* Pair helper into a larger helper: the unused vector t_P+e_j.
* Triple line into a target kernel: a coordinate outside T union S, which
  exists for h>=8.
* Pair helper into t_S^perp: a coordinate outside S union J, if one exists.
  Otherwise J=S^c, and for P={a,b}, S={a,b,c}, use
  `e_a+e_c+sum(e_j:j outside S)`. It is orthogonal to the helper and t_S,
  and its weight is h-1, which is odd because h is even.

The source checker also checks the last witness against every helper basis
vector. Nested nondegenerate frames split orthogonally, so each residual is
nondegenerate. Over F2 a nondegenerate symmetric residual containing a
norm-one vector is nonalternating and has an orthonormal basis, by the
elementary splitting argument in upstream section 3.

For the reversed middle circuit use the complementary node frames in F.
If U is contained in V, the reversed residual between V^perp and U^perp is
the same space V intersection U^perp. Its witnesses and dimension are
unchanged. Original outputs begin at the physical X triple line and
original inputs end at their exact physical Y triple complement.

Terminal residuals also have norm-one vectors: a coordinate complement
uses a coordinate outside V; a pair-helper complement uses a coordinate
outside P union J; a triple-line complement uses a coordinate outside T;
and a target-kernel complement is the norm-one line t_S. These checks are
included explicitly in the fresh certificate rather than inferred from
the earlier source's summary string.

The h=6 direct disjoint-leaf-to-target-kernel transition has an alternating
four-dimensional residual. This theorem excludes h=6; its tests start at
h=8. This is a real boundary of this particular binary-frame proof.

## Reversible physical circuit and arbitrary dirty values

For c retained additions and q=2v designated outputs the standard compiler
uses R=c+q roles. At an addition, add the second incoming value into the
first, retain that first role as one outgoing pivot, and copy it into fresh
roles for other uses. The second input retires. At an input, retain a
source pivot and copy to the other uses. The executable proves the role
formula and checks that simultaneously occupied slots never collide.
Its inverse uses subtractions in reverse order, not binary XOR.

Let L be this invertible mixer, V the source copy, J the signed half-
injection selecting D/E outputs, G the central gather, and R0 the scatter.
The chronological schedule is

```
L, -J, L^-1, -R0, V, G, R0, L, J, L^-1, -G, -V.
```

For arbitrary initial scratch z and central scratch c, the two side
injections total `-JLz+JL(z+Vx)=JLVx`. The two central scatters total
`-R0c+R0(c+Gx)=R0Gx`. All scratch is restored. Since JLV+R0G=I, the map is
`(x,y,z,c) -> (x,y+x,z,c)`. This algebra is exact over Gaussian dyadics.
The finite probes use integer coordinates divisible by 2 solely to avoid
a floating-point representation of halves; exact linearity certifies the
unscaled Gaussian-dyadic identity. The full basis test covers source,
side-scratch and central-scratch coordinates; Y is unchanged except for
the additive shear by inspection.

At stage j retain the upstream tensor decomposition A=B perpendicular P
and future line Q. Suppressing Q, set D0=B tensor F, D1=A tensor F and
DU=D0 perpendicular (P tensor U). The initial L/-J/L^-1 and initial scatter
use D0. Source copy uses its physical X line. Central gather/scatter have
the original D1/D0 assignment. Middle L uses the common DU frame of each
logical node, including every incoming and fresh outgoing role. Retired
roles subsequently grow to D1. Output injection uses the physical target
Y kernel. Late L^-1 and cleanup use D1. New roles enter from D0.
Thus every non-central path increases. Stage 2 reverses and inverts the
schedule with logical banks exchanged, using the complementary middle
frames just proved. Forward, inverse, forward invocations yield (-Y,X)
and restore every auxiliary role; the unchanged sign correction restores
the requested exchange.

Tensoring nonzero residuals by P and Q preserves a norm-one witness.
The remaining data, B/F and terminal tensor residuals have the coordinate
witnesses in upstream section 3: earlier/future tensor triple supports
have sizes 3^k<h^k. The only decreasing edges are the h+1 central returns
per invocation, each of dimension h. Over all 3v^2 invocations,
`L_complex=3v^2(h+1)h`.

## Sharing the complete first and third auxiliary banks

Pair consecutive ground points and let pi flip every point to its partner.
On triples this is an involution. A triple either contains a full pair,
so |T intersection pi(T)|=2, or contains three different pairs, so that
intersection is empty. Thus `t_T dot t_pi(T)=0`. Match the full stage-1
auxiliary bank at fixed triples (A,B) with the stage-3 bank at (B,pi(A)),
matching every local role index, including centers. Stage 2 keeps its own
bank. Restoration for arbitrary inputs makes the scalar reuse legitimate.

The two joined labels are

```
E = F tensor <t_A> tensor <t_B>,
H = <t_B tensor t_pi(A)>^perp tensor F.
```

They are nondegenerate and E is contained in H by binary orthogonality.
Their dimensions are h and m-h. Choose a middle coordinate outside
A union pi(A), which exists for h>=8. A tensor coordinate unit using it
lies in H intersection E^perp and has norm 1. Consequently the join has
an orthonormal residual basis of length m-2h. Separate terminals had total
length 2(m-h); each joined role removes exactly m of phase rank and one
role, with no new decrease.

This gives the proposed complete counts

```
W_complex = 2N + 2v^2(R+h+1),
s_complex = W_complex*m - 2N + 2L_complex,
D_complex = W_complex*m-s_complex = 2N-2L_complex.
```

Without sharing replace the coefficient 2 in W by 3. At h=50, R=629617,
the unshared values verified by the original prototype are
`W=740738848640000`, `L=2938824000000`,
`s=92592346898576000000`, and `D=9181424000000`.
The shared arithmetic and bijection are checked by the fresh certificate:
`W=498845589760000`, `s=62355689538576000000`,
`eta=239/1623170000`. The deficit and decreasing dimension are unchanged.

## Phase, precision, fixed-tape and recurrence transfer

Every scalar gate has a common binary frame on all its incidences, and
every edge has comparable nondegenerate labels and an orthonormal residual
basis. Therefore the unchanged common-frame telescoping and binary phase
factorization from upstream section 3 apply. Source/sink weights remain
27, all endpoints are unchanged, and all auxiliary scalar values are
restored. Each residual vector costs one forward or inverse child in the
unchanged finite phase network. The exact child count is s_complex.

The motif is fixed finite data. No growing number of tape heads, arbitrary
transpose or numerical primitive is introduced. Coefficients are additions,
subtractions, halves and fourth-root signs; all are evaluated exactly
until completion of one normalized layer. Precomputed bases and physical
role lists are also fixed finite data.

A new gate-count proof retains the old guard constant without relying on
the old statement that each physical wire touches at most twelve gates.
The mixer has c+v grouped node gates, while R=c+2v. Four mixer passes,
two source-copy groups and two D/E target-injection groups, and four
central gates give `4(c+v)+4v+4=4R+4` grouped scalar gates per invocation.
Across 3v^2 invocations there are fewer than 6W such gates even after bank
sharing, since `W>=2v^2(R+h+1)`. Each output is a sum of at most W terms
with coefficients 0, +/-1 or +/-1/2. Evaluating all outputs from saved
inputs at 2W^2 elementary operations per gate therefore gives at most
`12W^3+4s+4W+4` including inverse-child and endpoint corrections. Retain

```
E_guard = 64(W+m+1)^3,
B_guard = s+E_guard.
```

This strictly dominates that charge and is a fixed finite constant. With
`2<=s<m^5`, the stopped guard recurrence remains
`A(e)<=s*A(e/m)+E_guard`, with leaf `A(e)<=8e`.
For stop d^beta the unchanged proof gives one-piece depth
`9B_guard^2*d^(5-4beta)`. Partitioning into at most
`m(1+1/zeta)d^zeta` pieces and including preprocessing is covered by
`C0=32mB_guard^2(1+1/zeta)`, `C1=5-4beta+zeta`.
The changed finite constants affect eventual cutoffs, not the dimension
exponent. A composed certificate must recompute those cutoffs.

The strongest h=50 complex saving is already larger than the bit saving.
Write a=1-tau for the bit saving and b=1-sigma for the complex saving.
Here b>a, so sigma<tau. The growing-geometric recurrence in
[the packed-unrolling report](downstream-packed-unrolling.md) explicitly
assumes a>b and must not be reused. For this new order the exact internal
sum has a decaying geometric ratio m^(sigma-tau): at depth J,
`sum_(j<J) m^(j*(sigma-tau)) < 1/(1-m^(sigma-tau))`.
This is a fixed finite constant, possibly large. Keeping K^tau outside
gives total internal overhead `O(K^tau*e^tau)`, hence exponent
`tau*(1+c)`, while the leaf exponent remains `sigma+beta*(1-sigma)`.
If x=1-beta, the constraints on the saving q are

```
q < a*c,
q < a-tau*c,
q < b*x.
```

Their movement/internal balance is at c=a (since a+tau=1), with q=a^2.
The precise composed optimizer must use all three displayed constraints.
Their scoped guard supremum is `a^2*b/(b+4a^2)` as zeta tends to zero.
The full seven-margin assembly also retains the prefix cost
`1-epsilon*(1+c)`. For q saving, its balancing epsilon is at most
`1/(1+c+q)`; nonadjacent movement imposes the weaker
`1/(1+q/a)` because q<=ac. The best c and x for a fixed q approach
q/a and q/b, respectively. Thus this decaying branch's full scoped
supremum is
`a^2 / (1+max(4a^2/b, a+a^2))`.
This includes a prefix constraint which becomes relevant when b is
approximately 4a or larger. A certificate must check all seven margins.
Improving b mainly reduces the necessary
x and its guard penalty. It does not turn this movement algorithm into
an a*b-saving algorithm.

The fresh [exact composition](../runs/20261008T003550Z-downstream-complex-assembly/)
uses the independently promoted singleton bit primitive R=485360. It
checks the separate exact logarithm intervals for both primitives and
certifies b>a at interval level. Set c=a, q=a^2(1-2^-64),
x=(q/b)(1+2^-64), beta=1-x, lambda_prime=1-q, and choose lambda
strictly between the actual top-dominated internal exponent and
lambda_prime. In the tight row use zeta=2^-64,
epsilon=(1-2^-64)/max(C1,1+c+q), r=(1-epsilon)/2 and delta=r/8.
All 23 recorded strict slacks and four cutoff calculations pass.

The tight shared arithmetic candidate is
`kappa=96380770761102682050463/10^40`, more than
`5.555973162052905` times the pinned advertised 2^-59 baseline.
Its declared all-size logarithmic-alpha cutoff is
`log2(b_input)>=6640328716877726785`; separate eventual BHP, recurrence
constant/logarithm and unchanged source-interface cutoffs are also required.
No practical-size runtime benefit follows from this asymptotic certificate.

The conservative row retains the old zeta=2^-30 and epsilon backoff
2^-20, isolating the new construction/decaying estimate from tighter
rounding of existing margin. It gives
`kappa=771045430068239396829/(8*10^37)`, baseline ratio greater than
`5.555967858465674`. The tight unshared row also passes and has the
smaller value `19276154124109255319919/(2*10^39)`.
The corrected recurrence deliberately rejects the growing-geometric
formula with an exact negative control: that formula underestimates the
true top-level overhead when sigma<tau. Independent review checks all
three rows with longer logarithm enclosures, 30 independent conditions per
row, all four parameter cutoffs and 680 complete stopped recurrences.
The tight row improves the accepted packed predecessor by more than
`47419193/12500000000000`, about 3.79 parts per million; this is distinct
from comparison to the older phase-only input carried by the producer.

## Evidence and reproduction

Producer: [downstream_complex_circuit.py](../code/downstream_complex_circuit.py),
SHA256 `5773617bf59ae7287080ae2b4d2c3ddf019670143197571507b7377c9c3f3bd3`.
Completed finite runs:

* [small h=8,10,12](../runs/20261008T001617Z-downstream-complex-small/)
* [h=8 complete local basis](../runs/20261008T001704Z-downstream-complex-basis/)
* [h=50 full construction](../runs/20261008T001704Z-downstream-complex50/)
* [terminal, sharing and full dirty exchange](../runs/20261008T003305Z-downstream-complex-sharing/)
* [decaying recurrence and exact phase assembly](../runs/20261008T003550Z-downstream-complex-assembly/)

The h=50 run took 12.13 seconds elapsed and 2,576,940 KiB maximum RSS,
with one CPU worker, a 14 GiB virtual-memory cap, and no swaps. External
complete timing logs live under the campaign's `logs/downstream/` directory
and are linked by each protocol. The compact certificates retain all
essential exact results; no large circuit payload is needed because the
generator deterministically regenerates the DAG.

```
python3 -B research/integer-multiplication-bounds/code/downstream_complex_circuit.py \
  --upstream "$REFERENCE" --h 8 --all-basis --output "$BASIS_RESULT"
python3 -B research/integer-multiplication-bounds/code/downstream_complex_circuit.py \
  --upstream "$REFERENCE" --h 50 --output "$FULL_RESULT"
python3 -B research/integer-multiplication-bounds/code/downstream_complex_certificate.py \
  --upstream "$REFERENCE" --h 8 50 --global-exchange-h8 --output "$SHARED_RESULT"
python3 -B research/integer-multiplication-bounds/code/downstream_complex_assembly.py \
  --upstream "$REFERENCE" --bit-certificate "$PROMOTED_BIT_RESULT" \
  --complex-certificate "$SHARED_RESULT" --output "$ASSEMBLY_RESULT"
```

REFERENCE is the immutable campaign reference described above; output
variables point to fresh paths. Only Python 3 standard-library dependencies
are needed. The imported authored logarithm/source-verification helpers are
preserved in the topic's code directory. The completed independent run is
[review-complex-transfer](../runs/20261008T004215Z-review-complex-transfer/).
No full multiplication-machine implementation or formal proof
assistant verification is claimed.
