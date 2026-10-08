# Two disjoint protected centers

Two changed central gather rows can be protected without assigning two
incomparable low-dimensional frames to any data wire. The construction
uses the disjoint supports “triple contains point0” and “triple excludes
point0”. The scalar and complete native controls pass. A full independent
all-size transfer review is still required before using the new rank
budget in a multiplication composition.

This extends the independently reviewed [one-center construction](review-protected-center.md)
by changing the scalar central basis as well as the chronology. It does
not modify that construction's frozen sources, certificates or accepted
counts.

## Exact scalar basis and dirty restoration

Let Inc be the point/triple incidence matrix over F2, with h point rows.
Define T to have rows

`e0, sum_(j>=1) e_j, e2, ..., e_(h-1)`.

This is an invertible integer matrix of determinant1. Its inverse
reconstructs e1 by subtracting e2 through e_(h-1); after reduction to F2
the subtraction is XOR. Set

`G'=T Inc`, `R'=Inc^T T^-1`.

Thus `R'G'=Inc^T Inc` exactly. The two initial G' rows have disjoint
supports because a triple has odd cardinality: the first coefficient is
`[0 in T]`, and the second is `1+[0 in T]`. The remaining G' rows have
coefficient `[j in T]` for j>=2. Every triple contains such a point, so
the remaining gathers touch every data wire.

The scatter coefficient for triple S is

`[0 in S] C0 + [1 in S] C1 + sum_(j>=2)([j in S] XOR [1 in S]) Cj`.

Every center has a nonempty scatter support and every data wire receives
at least one center coefficient. All high/low scatters may therefore
retain the original grouped full-frame chronology. Their coefficients
are pointwise F2 additions, with no runtime coordinate-basis conversion.

For arbitrary dirty centers z, the four scalar gates

`scatter R'; gather G'; scatter R'; gather G'`

send `Y -> Y+R'G'X` and restore z exactly. The inverse physical
orientation reverses this chronology and exchanges the data banks. It
retains G' and R', rather than silently transposing either coefficient
matrix, and implements the same symmetric central shear. The unchanged
side coefficient correction still gives the identity shear because the
central coefficient is `|S intersection T| mod2`.

## The two rational frames

Use the same ambient metric `H=I-J/9`, with h>=4 and h!=9,10. The two
frames are

`E0={x: sum(x)=3x0}`, `E1={x:x0=0}`.

Each has dimension h-1 and contains its corresponding G' source lines.
The first restriction is positive definite: on E0 the metric norm is
`sum_(j!=0) x_j^2`. The second restriction has determinant `(10-h)/9`.
It may be indefinite, which is permitted for the rational bit-frame
compiler. It is nondegenerate at the intended h51/h53 grounds.

Their normal lines have exact representatives and norms

`z0=6/(9-h) 1-3e0`, `norm(z0)=36/(9-h)`,

`z1=e0+1/(9-h) 1`, `norm(z1)=(10-h)/(9-h)`.

The normal projectors are `z0(1-3e0)^T/norm(z0)` and
`z1 e0^T/norm(z1)`. Both are idempotent and H-self-adjoint. A relevant
triple t has norm2 and belongs to its E_i, so `E_i intersect t^perp`
and the corresponding complementary normal inside `t^perp` are
nondegenerate. No positivity assumption is made for E1.

## Actual forward and reversed paths

Write the original common labels as `D1=D0 perpendicular (P tensor F)`,
and tensor every displayed subspace by the unchanged future line Q.
Split the first high gather into three fixed gates:

1. Gather the first central row at `D0 perpendicular (P tensor E0)`.
2. Gather the second central row at `D0 perpendicular (P tensor E1)`.
3. Gather rows2 through h-1 at the original D1 frame.

The first two touch disjoint source sets. Each source line grows into
exactly one E_i before the last gate grows every source to F. No data
wire traverses E0 then E1. The old late undo gather uses the full D1
frame for all changed rows. The low scatter remains at D0. The scalar
product and every late/interstage/terminal boundary frame are unchanged.

In the reversed stage, gather the remaining rows at D0 first, then use
the E1 normal line for the second row and the E0 normal line for the
first row. These complementary normal lines belong to their respective
target triple kernels. Their supports remain disjoint. The final high
scatter returns all centers to the original full frame. Using E_i
itself in a reversed low slot would be invalid; the normal is essential.

Both protected center paths lose h-1 dimensions at their central return,
instead of h. Every other center loses h. The data paths split monotone
increases and have the same total ranks. The repeated low scatter and
full late cleanup retain all previous auxiliary sharing boundaries.

## Full rank accounting and fixed setup

With `v=C(h,3)`, `m=h^3`, `N=v^3` and actual side roles R, wire count
remains `W=2N+2v^2(R+h)`. Each of the 3v^2 invocations now loses
`h^2-2` central dimensions. Hence

`L_two=3v^2(h^2-2)`,

`D_two=N-2L_two=D_old+12v^2`,

`s_two=Wm-D_two=s_old-12v^2`.

There are two additional fixed grouped bit gates per invocation. Their
fixed work constant increases; their scalar and address operations do
not add new recurring full-rank children outside the edge-rank count.
The complex graph, actual complex logical gate count G and numerical
E/C0 guard remain unchanged.

The three credited generic-bit boundary families retain both endpoint
frames and their exact multiplicities: final middle `(R+h)v^2`, shared
join `(R+h)v^2`, and the two stage3 data first-edge families `2N`.
Their kernel dimensions remain h^2,2h,h^2+h-1. All new central interval
matrices are individual-pivot children. The same constructively defined
generic ambient isometry can conjugate their nondegenerate frames;
the recurring three-family flag set and maximum grouped child are
unchanged. This requires a new fixed rational native table and a shared
admissible odd prime avoiding the new denominators and exceptional
factors. Neither the giant table nor its prime is instantiated here.

## Executed controls and first-attempt failure

The [executed source](../code/downstream_disjoint_centers.py) has SHA256
`947a84af79dbf2f7497bbb4fcb32c38e77545473329e748674975f1773557fa3`.
The [successful protocol](../runs/20261008T083232Z-downstream-disjoint-centers-repair/protocol.json)
and [certificate](../runs/20261008T083232Z-downstream-disjoint-centers-repair/results/certificate.json)
retain all settings and counts. Certificate SHA256 is
`95e97f9d7a57938dc5ccbea02ce105eb14ffac0f58b9a0e5d2be2f08c1ad77d1`.

Exact rational projector and full central scalar controls run at
h4,6,8,12. The native h4/q7 checker uses every one of the2401 H addresses,
all12 logical data/center roles, two nonzero D fibers, both physical
orientations and both ordinary/reflected ambient charts. It represents
the complete dirty linear operator using integer basis bitsets, covering
230496 basis probes. The old full-frame and new two-protected programs
agree with an independently computed boundary-gauge central RG map.
Omitting the second protected center's native frame transition produces
disagreeing output coordinates. Address alphabet stays fixed q=7 and
payload stays F2. No q-ary address inflation is introduced.

Execution used one worker, 1.871 seconds and364932 KiB peak RSS. Only the
changed central segments are tested; the accepted side graph and full
large-ground finite program are inherited rather than replayed.

The [first attempt](../runs/20261008T083116Z-downstream-disjoint-centers/protocol.json)
stopped when one chosen reflected D fiber made a normal shift zero,
before its native operator comparison. The exact failed source is
preserved as [v1](../code/downstream_disjoint_centers_v1.py). The repair
changes only that fixture to a nonzero normal-shift fiber. The first
protocol also records that the successor queue notification arrived
after the short child began; the repair uses the current083100 worker
chunk admission marker and releases only its own reservation.

Reproduce with a fresh output:

```bash
python3 code/downstream_disjoint_centers.py --output /tmp/fresh-two-centers.json
```

Independent all-size/native review and a separate complete parameter
composition are required before a final headline incorporates this
construction.
