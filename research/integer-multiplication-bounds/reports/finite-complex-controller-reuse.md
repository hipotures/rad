# Nonalternating binary controller reuse for the complex D/E circuit

The existing even-ground D/E circuit admits retained nonpivot controllers
under exact binary frame containment. The new admissibility test also checks
that every nonzero residual is nonalternating, as required by the established
phase implementation. This changes the physical compilation without changing
the logical disjoint-sum graph, its Gaussian coefficients or its source and
output frames. A separate independent generic-Gram review now passes the
full h28 witness and all bounded dirty-scratch and sharing controls. Final
integer-multiplication composition remains a separate arithmetic interface.

## Exact admissibility

Use the standard dot product on F2^h. For a nondegenerate subspace U, write
P_U for its orthogonal projector and chi(U)=P_U*1. For nondegenerate U subset V,
the residual E=V intersect U-perp is nondegenerate and P_E=P_V+P_U. The quadratic
norm x dot x equals x dot 1 over F2, so E is nonalternating exactly when
chi(V) differs from chi(U). A nonzero residual with equal characteristic is
rejected. Equal frames have zero residual and are allowed.

When the characteristics differ, choose an index i where their difference
has coordinate 1. The vector w=(P_V+P_U)e_i lies in E and has norm 1. Indeed,
idempotence and self-adjointness give w dot w=e_i dot P_E e_i=chi(E)_i.
This supplies an explicit norm-one witness for each admitted residual.
The reversed complementary inclusion V-perp subset U-perp has exactly the
same residual E, so the witness also certifies that transition.

All existing frames have exact projector formulas. A coordinate frame
projects by masking its support. A triple line projects x to (x dot t)t,
where t has odd weight 3. Its orthogonal complement projects x to
x+(x dot t)t. A pair-helper frame has the orthonormal basis
e_a+e_b+e_j for j in J. With c=x_a+x_b, its outside coordinates are
y_j=x_j+c; its two anchor coordinates both equal sum_j y_j.
These formulas certify nondegeneracy and source-copy compatibility.

Containment in a pair-helper frame is checked by support containment and
orthogonality to the two defining constraints e_a+e_b and e_a+sum_J e_j.
Containment in a triple complement is checked by P_U t=0. Coordinate
containment is exact support containment. Line containment is equality of
the one-dimensional support. Independent small binary elimination checks
the formulas and every original/selected inclusion, as well as seeded
unrelated frame pairs that include rejected alternating residuals.

## Physical and network transfer obligations

The root flow planner, retained-controller compiler and forward/reverse
checker are imported unchanged. A process-local binding substitutes only
the exact binary admissibility predicate. Every source starts on its original
triple line. Every gate has its original common frame; both scalar arguments
enter that frame, and retained nonpivot values keep their exact coefficients.
An independent physical replay accepts either original argument as the result
pivot and checks the exact ordered or swapped inputs, disjoint union, fresh
copies and all designated outputs.

The physical timeline checks an explicit norm-one witness for every positive
frame increase, every fresh-role entry and every terminal complement. The
original logical map, original binary residual checker, terminal checks and
full-bank matching still execute. The small complete Gaussian dirty-basis
test executes both the shear and inverse on all data, side and central
coordinates. The h8 full shared three-stage exchange executes arbitrary dirty
values under the actual reversed middle schedule.

The shared network count remains W=2v^3+2v^2(R+h+1), with m=h^3,
L=3v^2(h+1)h, D=2v^3-2L and s=Wm-D. This uses the same source, complementary
sink and full-bank joining proof as the existing even complex family. The
logical grouped-gate count does not fall when physical roles are retained:
G=3v^2(4R_baseline+4). The guard therefore checks the actual saved-input
operation bound 2G W^2+4s+4W+4 against E=64(W+m+1)^3. Substituting R into
the unchanged logical gate count would be incorrect and is not done here.

## Recorded controls and status

[Small controls](../runs/20261008T034400Z-finite-complex-reuse-small/results/certificate.json)
pass at h8, h10 and h12. Their physical roles change from 898 to 830,
2400 to 2175, and 4973 to 4555. The h8 complete dirty matrix has 951
coordinates and checks 7472 elementary operations in both directions.
All three grounds pass independent Gram, projector, containment and residual
checks; the seeded h10 comparison includes an alternating pair rejected by
the new predicate. The h8 shared three-stage control also passes.

The bounded even-ground grid at run034600 passes h14 through h40 but reaches
its 180-second limit during h50. Its source, stdout and timeout evidence are
preserved. Its main routine wrote complete result rows only at the end, so
the retained interim grid lines are count screens, not complete certificates.
A separate single-ground h28 run034800 persists the full witness for promotion.
The original grid and its source are not overwritten.

The [full h28 producer](../runs/20261008T034800Z-finite-complex-reuse28/results/certificate.json)
has R=92309, down from 97586, with 5277 retained-controller links. Its
compiled SHA256 is
`d9fae1f5a927a34822c569cf407efbfc2fabbc39717cef692101ce885d737ce3`.
The exact network has W=2052292552128, m=21952, D=18030055680,
s=45051908074258176 and eta=15/37480688. The strict simple complex saving
4003/100000000000 is supported by independently enclosed logarithms.
The actual G=12567850311744 fails G<6W, but the required enlarged guard
has positive exact operation-depth slack
447350725581767717519021519392417975612.

The [independent review](../runs/20261008T0415Z-review-complex-controller/results/certificate.json)
constructs projector columns from the binary Gram matrices instead of the
producer's closed formulas. It checks 63602 unique frames, 1780856 columns,
all 7780500 output coefficients and 548754 physical forward/reverse
transitions. It reproduces the identical compilation and 5277 links, and
passes the complete h8 Gaussian dirty basis and shared three-stage exchange.
The reviewer also independently recomputes matching, rank counts, the guard
and logarithm enclosure. Runtime was 25.76 seconds, with peak RSS
578416 KiB. Its own separate sources and protocol preserve the audit.

The result is a finite binary-frame/physical-program improvement. It does not
introduce the newer alternating-residual phase interface, change the scalar
field to F2 or assert a new integer-multiplication exponent without the
exact downstream parameter composition. The even binary-frame transfer,
norm-one residual witnesses and finite guard are independently reviewed.

Reproduce with the campaign math environment and one BLAS thread:

```bash
python -B code/finite_complex_controller_reuse.py --h 8 10 12 --exchange-h8 --output /tmp/complex-reuse-small.json
python -B code/finite_complex_controller_reuse.py --h 28 --output /tmp/complex-reuse28.json
```
