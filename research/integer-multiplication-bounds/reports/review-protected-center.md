# Independent construction: protect the first bit gather center

Changing one central gather chart reduces the bit primitive's actual rank
loss. For the independently accepted h51 R485680 scalar graph, the resulting
explicit saving is

`a=143657287356815973/10^24`.

The previous generic native-basis saving was
`143492327855947419/10^24`. This is a changed central chronology and frame
construction, with the same scalar gather map, auxiliary roles and wire
count. It is not a final multiplication kappa. Its complete parameter
assembly must use the new counts and this explicit saving.

The [rational/count checker](../code/review_protected_center.py) has SHA256
`e49ed88a4e8f54c55f9dacf91d0ab9c5774f20797e683bd6e5dbde1c07c56ac6`.
The [native address checker](../code/review_protected_center_native.py) has
SHA256 `dbf631e119094838c6661c58edb3cf68c2413e121c0eee8e0923b16621200ddf`.
Both sources and their distinct attempt/repair records are retained.

## Positive rational star frame

Let `F=Q^h`, `H=I-J/9`, and fix one point i, independently of the
invocation. Assume h>=4 and h!=9. Define

`E_i={x : sum_j x_j=3x_i}`.

Every triple indicator t containing i belongs to E_i. These indicators
span it: take all triples `{i,a,j}` for one fixed other point a and each
remaining point j, and one additional triple `{i,b,c}` with distinct
other points b,c. This gives h-1 independent vectors. Equivalently, the
leaf pair vectors e_a+e_b span the h-1 leaf coordinates over Q, since
`2e_a=(e_a+e_b)+(e_a+e_c)-(e_b+e_c)`.

For x in E_i,

`x^T H x=sum_(j!=i) x_j^2`.

The restriction is positive definite. If all leaf coordinates vanish,
the defining equality also forces x_i=0. Thus E_i has dimension h-1
and is nondegenerate, including when the ambient metric is indefinite.

Set `n=1-3e_i`, viewed as a covector, and

`z=H^-1 n=6/(9-h) 1-3e_i`.

The normal line N_i=span(z) has norm `36/(9-h)`, which is nonzero.
Hence `F=E_i perpendicular N_i`. For any relevant triple t containing i,
`N_i subset t^perp`. The additional orthogonal splitting inside E_i is
`E_i=span(t) perpendicular (E_i intersect t^perp)`; its second summand
has dimension h-2 and remains positive/nondegenerate because t has norm2.
These formulas also give exact rational projectors.

## Actual forward central chronology

Use the accepted invocation notation `D0=B tensor F`,
`D1=A tensor F=D0 perpendicular (P tensor F)`, and tensor every label
by the unchanged future line Q. The side circuit, source copies and
scalar scatter are retained. Split the first gather G+ into two gates:

1. Add `sum_(T containing i) X_T` to the protected center C_i.
   Touch only these X_T and C_i. Assign common frame
   `D0 perpendicular (P tensor E_i)`.
2. Gather all other center coordinates together. Assign the old D1
   frame. Every triple contains at least one unprotected point, so this
   gate touches every X_T.

The two gates commute as scalar maps and their composition is exactly
the original gather. The original late undo gather retains the full
D1 frame on every center and every X_T. In particular, the protected
star frame is used only for the first gather, not for both gathers.

After source copying, an affected X_T has frame
`D0 perpendicular (P tensor span(t_T))`. It grows through the protected
frame and then to D1. Unaffected X_T grows directly to D1. Every path
is nested and every nonzero residual is nondegenerate. The common B
summand and the nondegenerate lines P,Q do not change these facts.

The protected center's relevant P-factor dimensions are

`0 -> 0 -> h-1 -> 0 -> h -> h`.

Its only decrease loses h-1 dimensions. Each other center has the old
path `0 -> 0 -> h -> 0 -> h -> h`, losing h dimensions. The protected
center's total absolute rank is 3h-2 rather than3h. The changed X paths
split an existing positive increase; their absolute rank sum is
unchanged. All late center and data frames remain exactly the original
ones. No data wire acquires an additional decrease.

## Reversed stage uses the complementary normal line

At stage2, reverse the scalar chronology with logical banks exchanged.
The high physical-X scatter is followed by the inverse other-center
gather on physical Y at D0, then by the protected inverse gather.
The latter has common frame

`D0 perpendicular (P tensor N_i)`.

The affected physical-Y triples contain i, so `N_i subset t_Y^perp`.
Their paths grow from D0 through this normal line into the unchanged
target-side frame `D0 perpendicular (P tensor t_Y^perp)`. All other
physical-Y paths retain their old frames. The protected center's
dimensions are

`0 -> 0 -> h -> 1 -> h -> h`.

The high-to-normal return loses h-1. Other centers still lose h.
The final physical-X scatter returns every center to the original D1
frame. Thus the full interstage/terminal interfaces remain unchanged.
Using E_i itself in this reversed low slot would be invalid: the
relevant t_Y belongs to E_i and has nonzero norm, so E_i is not contained
in its target kernel. The normal-line qualification is essential.

## Scalar restoration and native address implementation

The central part alone sends `Y -> Y+Inc Inc^T X` over F2, leaves X
unchanged and restores arbitrary initial center values. Splitting G+
does not change this map. Its transpose-incidence coefficient is
`|S intersect T| mod2`. Adding the unchanged side map, whose coefficient
is one exactly at intersection1, gives the original identity shear.
The already accepted dirty side implementation is therefore inherited;
it is not replayed or re-described as a new central basis check.

At a common frame, every scalar gate acts pointwise on equally framed
arrays. The retained manuscript's common-frame invariant gives
`D_out S D_in^-1` on arbitrary dirty roles. Replacing the old central
segment by the split segment keeps S and its boundary frames identical.
The native address program therefore has exactly the same segment
operator for every address and every admissible fixed odd prime.

The actual new gates are fixed linear maps: one protected gather and
one remaining-center gather, followed by the original scatter/cleanup.
Each uses one common nondegenerate frame on every touched role. Untouched
roles retain their values. The rational projectors compile into edge
shears using the same lower/lower interface as the old primitive; there
is no runtime conversion between a star frame and the global native
basis. This changes the complete fixed rational factor table. A fixed
odd prime must avoid the finite additional denominators, determinant
and triangular-factor obstructions. These are computable finite setup
and separate eventual constants, not an instantiated giant table.

## Shared banks, selected boundaries and exact rank budget

No auxiliary wire is added. The old stage1/stage3 shared-bank matching
remains valid because each auxiliary and central role has the same
last/first boundary frame as before. There is one additional grouped
bit gate per invocation, hence 3v^2 additional fixed grouped gates.
The separate complex scalar graph and numerical guard are unchanged.
The bit program's fixed setup/work constant may increase.

For `v=C(h,3)`, `m=h^3`, `N=v^3`, and accepted side roles R, the actual
shared wire count is

`W=2N+2v^2(R+h)`.

All 3v^2 invocations now lose `h(h-1)+(h-1)=h^2-1` dimensions on
central returns. Thus

`L_new=3v^2(h^2-1)` and `D_new=N-2L_new=D_old+6v^2`.

Source/sink dimensions remain N and Wm-N. Signed incidence changes
still telescope at every gate. Replacing the central signed decreases
by absolute changes gives `Wm-2N+2L_new`. The rational negative-source
interface still adds exactly N source ranks, yielding

`s_new=Wm-D_new=s_old-6v^2`.

The three credited generic-basis families are disjoint actual edges
and keep both endpoint frames and frequencies:

| Family | Copies | Kernel dimension | Grouped diagonal run |
| --- | --- | --- | --- |
| Middle auxiliary/center final boundary | `(R+h)v^2` | h^2 | m-2h^2 |
| Shared auxiliary/center join | `(R+h)v^2` | 2h | m-4h |
| Two stage3 data first-edge families | 2N | h^2+h-1 | m-2(h^2+h-1) |

The first two depend on the unchanged final full frames, including the
protected center's late cleanup. The data edges are X incoming to
source-copy time2 and Y initial-side time0 to early-scatter time1;
both precede the modified first gather. The changed X time2-to-gather
pieces, reversed Y later-gather pieces and central high/low intervals
belong to none of those credited families. All new uncredited edge
pivots remain singleton children.

The finite simultaneous-flag family in the accepted generic-isometry
theorem is consequently unchanged. The same isometry T is applied
to every new source/gate/sink frame as well; their nondegeneracy and
nesting are preserved. No extra generic flags are required for the
new singleton matrices. The largest grouped child, reflection bound,
depth651 and bit row degree66000 are retained. The complete compiled
table/prime is new, as explained above.

For the accepted h51 R485680 input:

| Count | Before | Protected first center |
| --- | ---: | ---: |
| W | 439367045355000 | 439367045355000 |
| L | 3384009916875 | 3382708875000 |
| D | 2263379181875 | 2265981265625 |
| s | 58282475670006923125 | 58282475667404839375 |

The exact rank gain is2602083750. The checker recomputes W from the
two-bank sharing formula, agrees with every immutable old input count,
and changes only L,D,s in the primitive rank budget.

Let M be the unchanged credited first moment. Safe independent
80-term rational logarithm intervals verify

`D_new-a(s_new ln(m)-M)-a^2 s_new ln(m)^2/[2(1-a ln(m))]>0`.

This implies the strict nonuniform characteristic at the explicit a
quoted above. The next 10^-24 gridpoint fails this sufficient Taylor
test. The old explicit a has strictly larger slack under the new
budget. The retained whole-complex phase saving1e-6 is still greater
than2a; it does not limit a beta-half assembly. Such an assembly
must nevertheless be checked on its complete new inputs.

## Executed evidence and limits

The [rational/count run](../runs/20261008T0808Z-review-protected-center-count-repair/protocol.json)
has [certificate](../runs/20261008T0808Z-review-protected-center-count-repair/results/certificate.json)
SHA256 `0a0874769b3ad35d8c92d35b644a9a2dd975b3aedee03510734fe6c6e2b8e8b8`.
It checks all triple containment/normal orthogonality identities at
h4,6,8,12,51,53 and72 stage/orientation/data-membership timelines.
The complete central invocation basis sizes are12,46,120,452,
total630 in each literal forward/reversed orientation. Every center
is included as an arbitrary dirty scalar. The unchanged side-plus-
central coefficient identity is independently checked, and omitting
cleanup fails. This is central-only basis evidence, not the complete
original side-invocation or full tensor exchange basis. Python3.14.7
used one worker,14.80s,23336KiB peak RSS and zero swaps.

The [native run](../runs/20261008T0809Z-review-protected-center-native-nonzero/protocol.json)
has [certificate](../runs/20261008T0809Z-review-protected-center-native-nonzero/results/certificate.json)
SHA256 `7bfb22658b276c3e86c978d5f317ffa1826b4916f50e73744cbe34099dc1c254`.
At h4/q7, each complete H fiber contains2401 addresses and12 data/center
roles. Two fixed D fibers, both orientations and both identity and
Householder metric charts give230496 complete scalar/address basis
probes. The literal old/new native central programs agree with an
independently computed boundary-gauge central RG map. Omitting the
protected center's frame-entry edge fails. Every dirty center basis
is represented. This is two selected D fibers, not exhaustive all-D
address evidence. The all-size identity follows from the common-frame
argument, not extrapolation from those fibers. The run used2.53s,
373144KiB peak RSS and zero swaps, and released its owned slot.

Failed attempts are preserved separately: the first count reader
used R instead of the input's side_roles; a second allocated three
auxiliary banks instead of the two-bank sharing formula; the first
native admission met a terminal summary schema; one native D fixture
gave a zero normal shift after reflection and was rejected as vacuous.
Executed sources, protocols and logs are retained, and each repair has
a fresh run ID. Protocol actual UTC timestamps identify execution
ordering; nominal run labels are not claims about their start times.
No failed characteristic or vacuous reflected fiber was promoted.

The conclusion is a complete conditional bit primitive construction,
with exact bounded changed-gate evidence and constructive finite
native setup. It inherits the previously accepted side circuit,
arbitrary-dirty sharing and upstream fixed-tape transfer assumptions.
It does not claim an independently instantiated giant new h51 table
or a complete new multiplication parameter assembly.
