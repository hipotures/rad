# Unequal tensor factors with shared physical scratch

The reviewed composition with outer ground size `p=52` and middle ground
size `q=48` supports the strict conditional exponent

```text
kappa = 6412736146231 / 10^30 > 3.696690703179 * 2^-59.
```

This combines independently checked positive support envelopes, their
controller compiler, the reusable circular-banded Gaussian inverse, and
the unequal bit motif below. The complex motif remains the pinned `h=50`
construction. This is conditional on the retained upstream multiplication
theorem and fixed-tape interfaces. It has an enormous eventual input cutoff
and establishes no practical multiplication speedup or global optimality.

## Construction and exact counts

Let `v_p=C(p,3)`, `v_q=C(q,3)`, `m=p^2 q`, and `N=v_p^2 v_q`.
Use the same verified circuit on the first and third axes, with `R_p`
physical side roles, and the `q` circuit on the middle axis, with `R_q`.
The three scalar shears implement a bank exchange in characteristic two.
All local invocations restore arbitrary dirty scratch.

The first and third stages share the complete auxiliary invocation bank,
including the central roles. The exact counts are

```text
W = 2N + v_p v_q (R_p+p) + v_p^2 (R_q+q),
L = 2 v_p v_q p^2 + v_p^2 q^2,
D = N-2L,
s = Wm-D,
eta = D/(Wm).
```

At `p=q` these reduce identically to the previously reviewed uniform
counts. All eleven uniform rows were independently checked.

The sharing map uses the **middle** ground's matching. For every `q`
triple `A`, choose a bijection `pi_q` with
`|A intersect pi_q(A)|=1`. Pair the stage-one bank `(A,B)` with
the stage-three bank `(B,pi_q(A))`, where `B` is a `p` triple.
For every physical role in this bank, the retained endpoint frames are

```text
E = F_p tensor t_A tensor t_B,                 dimension p,
H = (t_B tensor t_pi_q(A))^perp tensor F_p,     dimension m-p.
```

In coordinate order `(p,q,p)`, the pairing vanishes because the middle
triple lines are orthogonal. Thus `E` is contained in `H`. The ambient
forms and these frames are nondegenerate: `I-J/9` is nondegenerate when
the ground size differs from nine, and every triple indicator has squared
norm two. Two former transitions of rank `m-p` are replaced by one of
rank `m-2p`, saving exactly `m` per shared physical role. The old data
endpoint correction and central decreasing ranks are retained. The full
argument is independently checked in
[the asymmetric review](review-asymmetric-motifs.md).

| Quantity | Selected value |
|---|---:|
| Outer physical side roles `R_p` | 549,120 |
| Middle physical side roles `R_q` | 426,624 |
| `v_p`, `v_q` | 22,100; 17,296 |
| `m`, `N` | 129,792; 8,447,539,360,000 |
| `W` | 435,202,334,195,200 |
| `L` | 3,192,459,212,800 |
| `D` | 2,062,620,934,400 |
| `s` | 56,485,779,297,242,464,000 |
| `eta` | 8,629 / 236,308,959,744 |
| Joined physical auxiliary roles | 209,916,383,955,200 |

The last count includes all roles in `v_p v_q` joined invocation banks;
these banks are not themselves individual physical roles. Version two
renames that distinction in the certificate metadata. Version one's
source/output remains retained, and its main `W,L,D,s` counts are unchanged.

## Evidence and parameter transfer

The full individual circuits at ground sizes 40, 42, 44, 46, 48, 52, 54,
56, 58 and 60 passed exact logical coefficient maps, physical forward and
reverse frame checks, and all designated target pairings. Eight separate
single-thread workers completed the ten cases in 23 to 115 seconds per
case. The already reviewed `h=50` envelope circuit supplies `R=486200`.
The exact graph results are retained in the ground-scan run.

At `(p,q)=(6,8)` and `(8,6)`, full three-stage scalar executions with
two independent dirty payload seeds, 1 and 109, exchange the data banks
and restore both physical scratch banks. The full local identity shears
also expand all input/output, side scratch and central dirty registers
at ground sizes six and eight: 196 and 816 basis vectors, in both
directions. These finite tests calibrate the general written identity;
they do not simulate the enormous selected whole tensor network.

All 121 ordered ground pairs were scored with exact primitive logarithm
enclosures. The selected pair is uniquely best within this measured
grid, not an optimum over all finite circuits or ground sizes. An
independent checker used longer logarithm bounds and verified the
selected root signs, thirty strict assembly constraints, absorption
margin and all ordered primitive comparisons.

The analytic transfer uses the independently reviewed
[reusable banded inverse](downstream-reusable-banded-inverse.md),
`epsilon=2/3-2^-20`, squared-width power `r=1/3`,
`delta=2^-22`, and guard exponent `C1=3/2`. The explicit Gaussian
cutoff is `b>=2^7340032`; Baker-Harman-Pintz's eventual prime threshold
and other retained cutoffs also apply. `b` is the logarithm of the input
bit length, not the input length itself. The complete set of exact
parameters/slacks is in the certificate, avoiding rounded values in
the proof.

For comparison, the uniform envelope/LU composition supports
`6404050041509/10^30 > 3.691683504717 * 2^-59`.
The unequal factors provide a small further finite improvement after
the substantive Gaussian and frame changes.

## Recovery and limitations

Sources: [asymmetric_motif.py](../code/asymmetric_motif.py),
[ground orchestrator](../code/asymmetric_ground_scan.py), and the
independent checker linked above. Commands and hashes are in the
individual protocols and [reproduce.md](../reproduce.md). Completed raw
logs, original metadata versions and compact certificates have gzip
recovery copies. No dependency source was modified.

The ground orchestrator's first version had an unexercised timeout
defect: killing `/usr/bin/time` alone could leave its child running.
Every ground case finished normally. The current source creates and
terminates its own process group, including descendants which ignore
SIGTERM; bounded controls checked actual terminal states. The original
source is retained so its recorded run hash is recoverable.

The next construction question is whether a different scalar graph or
nondegenerate indefinite frame family permits more controller links.
The analytic branch separately investigates reuse of phase-cell Toeplitz
inverses; it is outside this accepted milestone until reviewed.
