# Joint mutable-source births and paid final-data cleanup

Two arbitrary dirty carrier banks can serve all three stages of a coupled
signed exchange, retaining source-dependent values between every life and
visiting full only once. Exact CUT responses convert to current-data
preimages, and a paid algebraic cleanup from final mutable data restores
their original dirty values. This removes the repeated helper traversals
of the [independent-body control](joint-signed-swap-independent-body-control.md).
The positive core has rank 22 against capacity 24. Its explicit raw-input
canonical boundary consumes the entire two-rank deficit.

There are four data banks `(x0,x1,y0,y1)` and two carrier banks `(r0,r1)`.
The ambient address dimension is 4. Initial x operators are `C_1,C_7`,
while y and r start at identity. All banks reach the chosen actual
`F_E`, where `E=span(1,7)` has a one-dimensional radical. The source
entrances cost rank 1 each and the other entrances rank 2 each.

For either retained unimodular matrix

```text
S = [[1,1],[2,3]]  or  [[1,2],[1,3]],
```

the clean three-stage program is

```text
y += S*x
x -= S^-1*y
y += S*x.
```

Each stage has two carrier births, retains the actual old g, compensates
the current target by `-sign*g`, adds the current source image into the
carrier, and reads it with the stage’s sign. Neither carriers nor source
data are restored between stages. The second and third births contain
old source contributions and earlier mutable-data values.

The backward derivative tracks all four mutable data outputs and cuts each
carrier at later births. If D is its old-value future response and G is
the current-data-to-final-data matrix, the actual compensation is
`-G^-1*D*g`. The producer independently derives these preimages by exact
elimination. In this word they reduce to the stated current-target
compensations. Using D directly as a final-output debit would be wrong
because the outputs become sources of later stages.

The middle actual common frame is RIGHT-composed `F_(Eperp)*C_full`.
It has the same Lagrangian as `F_E`, but its coefficient matrix differs.
The rank-zero adapter

```text
G_E = (F_(Eperp)*C_full)*F_E^-1
```

has address map `y -> 8 XOR P*y`, with route columns `[1,6,4,8]`, and
unit `i^(1+2*y0+3*y1+2*y3)`. It is applied literally to all six banks
before the middle stage and inverted before the third. Its full affine,
quadratic and global phase are paid and retained. A one-helper omitted
phase control corrupts the actual data/dirty map. Generic frames are not
assumed to commute with address XOR.

At the end, all six banks reach `C_full`; these moves each cost rank 2.
The final virtual data are

```text
x_f = -S^-1*y_0
y_f = S*x_0.
```

The accumulated carrier increment is

```text
(S+I)*x_0 + (S^-1-I)*y_0
  = (I+S^-1)*y_f + (S-I)*x_f.
```

Subtract the right-hand side from r at the **same actual full operator**
as both final data vectors. This explicitly reconstructs the required
source preimages from mutable final data; it does not group historical
source uninjects or assume they still have their old values. The actual
bill is seven scalar bank shears, with five nonunit integer coefficients;
fourteen unit shears suffice. Every coefficient has absolute value at
most 4. This gives dirty physical output `C_full` times each original
carrier value. The whole core pays 31 scalar bank gates. The compact
virtual scalar-prefix row L1 maxima are 18 and 16 for the two matrices;
these are scalar-only prefix bounds, not an all-size physical precision
theorem.

To close the raw canonical boundary, apply S to the final x vector and
negate it; apply `S^-1` to the final y vector. Both are literal in-place
integer unit-shear words at full and cost four further scalar shears plus
two constant signs. The y vector is now `C_full*C_U^-1` times each raw
original x bank. Each of the two source labels therefore needs one paid
`C_U` child of width 1, followed by two literal full-bank exchanges.
The final raw labeled data and dirty carriers are all exactly `C_full`
times their original values.

| Paid quantity | Positive core | Raw canonical word |
| --- | ---: | ---: |
| Payload stock W | 6 | 6 |
| Ambient dimension m | 4 | 4 |
| Width-1 child calls | 2 | 4 |
| Width-2 child calls | 10 | 10 |
| Recursive rank | 22 | 24 |
| Capacity Wm | 24 | 24 |
| Rank deficit | 2 | 0 |
| Scalar bank gates | 31 | 35 |
| Rank-zero reflection bank events | 12 | 12 |
| Final constant signs | 0 | 2 |
| Final full-bank exchanges | 0 | 2 |

All native and scalar events are literal operations in the finite replay.
Their fixed-tape cost and uniform guard remain additional obligations.
Carrier space is arbitrary dirty; no zero temporary payload bank is used.

The elementary all-b obstruction is exact. Whenever a paid profile has
`sum n_r*r=W*m`, its normalized moment is

```text
Phi(1-b) = sum_r [n_r*r/(W*m)] * (m/r)^b.
```

The first-moment shares sum to one. If some positive paid width is below
m and `b>0`, its multiplier is strictly above one, and none is below one.
Thus `Phi(1-b)>1`. In this actual canonical word every width is below 4;
explicitly its moment is `(1/6)*4^b+(5/6)*2^b>1`. No positive saving
contracts. This excludes the retained topology and boundary, not other
data interfaces or address-dependent intertwiners.

The [four-worker repaired run](../../runs/20261009T024741Z-synthesis-joint-mutable-birth-repair/report.md)
checks both S matrices. Each f1 case replays all 96 physical basis columns
for **both** core and canonical maps. Each f2 case checks all 6 bank origins
and three complete Gaussian dyadic fields for both maps. No origin-only
covariance promotion is made. Omitted later-birth compensation, incorrect
mutable-source cleanup, a helper phase omission and omitted raw source
repair corrupt complete actual operators.

Omitting the future CUT instead generates odd-denominator current-data
preimages, including thirds and elevenths. This is a forbidden-domain
rejection, not an executed Gaussian-dyadic corruption circuit. The initial
control dispatcher incorrectly let that expected rejection stop the run;
its unchanged protocol and reconstructible source patch are
[preserved](../../runs/20261009T024646Z-synthesis-joint-mutable-birth-attempt/report.md).
The repaired run changes only control handling. The source recovery path
was exercised and matches the failed producer hash exactly.

The [literal contract](../../fixtures/synthesis/joint-mutable-birth-contract.json)
retains the complete core and canonical event lists, all actual frame
words, every child normal form, reflected gauge, future/current birth
responses, paid final-data preimages and source boundary. Its
[exporter](../../code/synthesis/dump_joint_mutable_birth.py) regenerates
the compact fixture. The experiment pins a 21-file standard-library
source closure. Reproduce from the dedicated worktree root:

```bash
python3 research/integer-mult-breakthrough/code/synthesis/joint_mutable_birth_swap.py \
  --workers 4 --output research/integer-mult-breakthrough/work/synthesis/<fresh-actual-UTC>-joint-birth/results
python3 research/integer-mult-breakthrough/code/synthesis/dump_joint_mutable_birth.py \
  --output <fresh-contract.json>
```

The source is
[joint_mutable_birth_swap.py](../../code/synthesis/joint_mutable_birth_swap.py).
The positive core establishes that a genuinely joint lifecycle can avoid
three independent helper traversals. The complete canonical map identifies
the remaining paid source boundary. Neither result supplies a contracting
multiplier recurrence or a new kappa. The next discriminator is a different
data boundary or an actual address-dependent intertwiner that closes it
without the two extra source-line calls.
