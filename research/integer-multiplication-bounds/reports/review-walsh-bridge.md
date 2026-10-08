# Independent Walsh bridge and joint-basis recurrence review

The F9 Walsh bridge in
[downstream-f9-walsh-bridge.md](downstream-f9-walsh-bridge.md) is an exact
binary address permutation on arbitrary fixed-alphabet payloads. The
independent per-edge basis compiler described there loses its recursive
rank deficit. A valid common-Walsh telescope exists for the native
commuting address shears, but leaves two same-size complex calls. Neither
construction establishes an improved movement exponent. A different
joint physical basis schedule remains open.

This is a new interface review, dated 2026-10-08. Its finite count input
is the accepted h28 complex circuit with side roles R97586, as recorded
in the immutable R472885 semantic/bulk composition. No graph is rerun.
The newly proposed R92309 controller-reuse circuit is a separate
construction and has not been substituted into this negative witness.

## Exact field and bridge

Use F9=F3[i], i^2=-1. The polynomial is irreducible over F3, and both
two and the Gaussian units used below are invertible. The address fields
remain binary. Only payload symbols become a fixed nine-symbol alphabet,
which changes bit volume by a fixed factor. Arbitrary nonbinary
intermediates are permitted; a completed address permutation returns
the original payloads, including original zero/one symbols.

For the ordinary complex kernel
`C=((1+i)I+(1-i)X)/2` and `S(x)=i^wt(x)`, direct multiplication gives

```
W_f=(1-i)^f S C^tensor f S,
W_f^2=2^f I,
XOR_(x<-x+y)=2^-f W_x diag((-1)^(x dot y)) W_x.
```

W is unnormalized. Dropping its scale or either S wrapper changes the
operator. The formula is valid in F9 and for every control value y.
It calls C^tensor f twice on the unchanged f selected coordinates.
The finite-field factors have fixed symbol width; `(1-i)^f` depends on
f modulo eight and `2^-f` on its parity.

The bilinear sign can be scanned with the aligned, masked bank counters
in [the alternating phase review](review-alternating-quadratic-phase.md).
Toggling a selected target bit changes its dot product by the aligned
control bit, and conversely. This uses complete address enumeration,
not a separate dot-product computation per payload. For constant-width
F9 symbols, counter setup is charged to the retained complete native
address rectangle; ancestor chunk bits remain spectators rather than
being removed. An O(fK) setup is bounded by the complete within-row
traffic. Outer prefix counters are reused across consecutive rows.
The finite-field setting eliminates numerical precision concerns, but
does not eliminate the two recursive C calls.

## Independent adapters exhaust the rank saving

Let A be the number of independently compiled word-XOR adapters in a
phase-network invocation. Suppose each uses the bridge above, and every
call has its retained role-stream volume V/W and selected size f=e/m.
With C(e) denoting time divided by the current logical volume, its
literal uncancelled child count gives

```
C(e) <= ((s+2A)/W)*C(e/m)+O(1),
required for a sublinear power: s+2A<Wm.
```

The source-growth directions are tensor indicators of three triples,
with support 27. An ordinary coordinate child does not implement such
a direction without a nontrivial address adapter. The independent
per-edge row-addition compiler therefore has at least one word-XOR
on each of its 3N source-growth edges. This intentionally weak A>=3N
bound ignores inverse adapters, most required coordinate additions and
all other edges. It is a count for this compiler, not for every possible
representation of the operator.

The independently accepted h28 counts are

```
W=2165559937632, m=21952, s=47538353720841984,
N=35158608576, L=26143580736,
D=Wm-s=2N-2L=18030055680.
```

Thus already `2A>=210951651456=(117/10)D`. Its child count exceeds Wm
by 192921595776 and its normalized growth relative to m is
`79098865/79098544>1`. This is the wrong recurrence orientation for
a sublinear movement proof. Supplying the exact bridge rather than
assuming a linear-time whole-word XOR makes the failure concrete.

A proposed two-family recurrence also needs an explicit coupling test.
Write normalized coefficients a_C,a_B for its own-family children and
t_C,t_B for the cross-family children. For shrink factors m_C,m_B, a
power bound with exponent tau and positive constants u_C,u_B requires

```
u_C >= m_C^-tau*(a_C*u_C+t_C*u_B),
u_B >= m_B^-tau*(a_B*u_B+t_B*u_C).
```

Multiplication of these inequalities gives the necessary condition

```
t_C*t_B <= (m_C^tau-a_C)*(m_B^tau-a_B),
a_C<m_C^tau, a_B<m_B^tau.
```

Strict inequality supplies the usual margin for absorbing overhead.
Equality can sometimes permit an exact boundary power when the overhead
has smaller degree, so it is not excluded just by these inequalities.
For any tau<1 the right side is strictly smaller than the product of
the linear-size rank gaps. Thus a sublinear power still necessarily
requires `t_C*t_B<(m_C-a_C)*(m_B-a_B)`.
In the same-shrink symmetric case the spectral
radius is `a+sqrt(t_C*t_B)`. This is a discriminator for a supplied
physical compiler. It is not an assertion that every unconstructed
coupled scheme has the same coefficients. In particular, the bridge
`B(e)<=2C(e)+O(1)` alone gives no recursion reducing e; the C program
and its adapter calls must still be supplied.

## What actually telescopes

Two consecutive XOR shears with the same target x and unchanged control
words y,z do share their two Walsh transforms:

```
XOR_(x<-x+y) XOR_(x<-x+z)
=2^-f W_x diag((-1)^(x dot (y+z))) W_x.
```

This is a real grouping opportunity. Counting two bridge calls for
every matrix nonzero without grouping a target row would overestimate
that compiler. The conservative source-edge bound above counts only
one nontrivial adapter per edge, so this grouping does not remove its
obstruction.

For all native address frames Phi_M(H,D)=(H+MD,D), a *common full* Walsh
transform of the H coordinates simultaneously conjugates them into
sign diagonals. The odd-payload scalar gates are constant linear maps
on aligned records, so applying the same Walsh transform to every
operand and output commutes with those gates. All internal native
frame edges can therefore telescope in this representation.

The two physical boundaries remain: transform every input role with
W_H and every output role with `2^-e W_H`, where e=mf. The resulting
operator is the desired XOR, but costs two C^tensor e calls per role.
Decomposing those transforms into ordinary f-axis children costs 2m
such calls per role, already twice the rank budget m before any other
children. Omitting the boundaries executes a sign diagonal rather than
moving an input payload. Implicit logical interpretation cannot turn
that diagonal into a physical address permutation on arbitrary input.

Transforms on different role bases cannot simply be canceled across an
unchanged scalar gate. If `u<-u+v` is conjugated by A_u,A_v on its two
roles, the needed cross term is `A_u^-1*A_v*v`. It remains the original
pointwise addition only when those bases agree, up to any explicitly
paid fixed scalar correction. With u zero, v the impulse `(1,0)`, and
only u in one-bit Walsh coordinates, a literal addition followed by
inverse Walsh returns `(2,2)` over F3, whereas the correct result is
the original impulse. Restoring v's basis is an operator call, not a
free cancellation.

Generic lower-triangular adapters also do not all have one common
diagonalizing basis. On three address bits the elementary maps
`x1<-x1+x0` and `x2<-x2+x1` are both lower triangular but do not commute:
address one becomes seven in one order and three in the other. Common
conjugation into diagonals would make them commute. This refutes a
universal static-diagonal shortcut; it does not exclude a carefully
ordered basis schedule, merged gates or another scalar construction.

## Independent evidence

[review_walsh_bridge.py](../code/review_walsh_bridge.py) imports no
producer. It computes F9 operators through ordinary C butterflies and
compares Walsh coefficients with a separate direct character sum.
Controlled XOR is compared with a literal complete address permutation
in both physical directions. Complete small input bases and arbitrary
F9 symbol streams exercise all-input behavior.

The [fresh run](../runs/20261008T035308Z-review-walsh-bridge/) passed
3,272 controlled-XOR output checks over f=1..5, three grouped
same-target schedules and two full two-role common-basis frame
schedules. The latter include arbitrary payloads on both roles and
restore their original routing. It preserves the failed mixed-basis
addition, noncommuting triangular updates and the missing-scale/phase
controls. These are actual finite operator comparisons, not floating
fit failures or a full large-network replay.

Seed 613, Python 3.14.4, one worker, 0.27 seconds elapsed, 22,328 KiB
peak RSS. Reviewer source SHA256:
`51e0ef1564a1c3c89b49594035fd7027576b31401ecd92d6ebe3c6e7e70c4a28`.
Certificate SHA256:
`bc2bb38c2737a69a6beaa379709848c1010151ec929f3ffb0d28c14912495cf8`.
The exact executed inputs, source/producer hashes, actual 03:55:34 UTC
start, original campaign clock and authorized 10:00 UTC deadline are
in the protocol. The descriptive run name is not a claimed start time.
The owned reservation was released in finally, preserving the other
agent's reservation.

An improved native binary movement claim still needs a complete physical
schedule whose actual smaller-call volumes satisfy the coupled criterion.
The exact identity and finite payload are available tools; their current
uncancelled compiler is a useful negative result. No universal movement
lower bound or novelty claim follows.
