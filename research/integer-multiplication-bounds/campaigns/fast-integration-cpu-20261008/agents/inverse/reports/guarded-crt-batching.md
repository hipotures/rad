# Guarded batching of independent CRT rotations

This is a new conditional fixed-tape movement lemma developed after the
13:47 UTC discovery that the packed Gaussian composition still retained
`d` full-payload triangular CRT rotations. It does not follow from an
arbitrary binary coordinate permutation. The changed mechanism implements
many controlled interval rotations together, using actual existing dirty
address bits, ordinary prefix-controlled cyclic rotations, and an explicit
extension of the inherited masked BIT shear to repeated source bits.

The independently implemented finite address checker is
[crt_guard_controls.py](../code/crt_guard_controls.py). Its controls are
discriminators for the identities and sparse repair, not formal verification
of the inherited tape primitives. Full multiplier assembly remains with the
campaign coordinator.

## 1. Guarded binary additions are two ordinary rotations

Suppose independent active operations have binary target words `Y_i` of
width `L_i`, offsets `0<=f_i<2^L_i`, and endpoint/offset controls fixed
outside every active target. Borrow `G` dirty guard bits `T_i` per target
from an inactive address bank. Let `B=2^G` and initially `T_i<B-1`.

Route coordinates so all controls precede the one target field made by
concatenating the blocks `Y_i+2^L_i T_i`. Add the packed integer

`sum_i f_i * 2^(sum_{j<i}(L_j+G))`

by ONE ordinary prefix-controlled rotation of this complete binary field.
This is ordinary integer addition, not digit-wise arithmetic. The dirty
high guards stop every carry before the next block on the good set. Each
completed low word is `Y'_i=(Y_i+f_i) mod 2^L_i`, and its guard is
`T'_i=T_i+c_i`, where `c_i=1[Y'_i<f_i]`.

Route all completed `Y'_i` before the packed `G`-bit guard field. Its controls
now compute every `c_i` from earlier coordinates. Subtract
`sum_i c_i B^i` by ONE ordinary prefix-controlled rotation of that field.
Since `T'_i>=c_i`, no borrow reaches a neighboring digit, and every original
dirty guard is restored. Restore the requested field layout. This uses a
constant number of known coordinate routers and two full-volume rotations.

Both ordinary rotations are bijections on ALL addresses, including the bad
ones. Their explicit inverse adds the same carry function to the completed
guard field, undoes the layout, and subtracts the original packed offset.
No precomputed inverse table is needed.

## 2. The inherited BIT shear permits repeated source bits

The completed historical RaD report
`compact-arbitrary-source-routing.md`, at commit
`6b32837aee0561af85e4efaca21af07b9f2749d2`, writes distinct sources in its
masked simultaneous XOR identity. Distinctness is stronger than its proof
uses. If the target positions are `j_i` and the source positions are `s_i`,
the loaded word is `A(y)=sum_i y[s_i] B^i`. The two four-update `F_u`
identities only change ACTIVE target positions and fix every other middle
bit on good addresses. Therefore they preserve `A(y)` whenever all `s_i`
are outside the simultaneous ACTIVE target set, even when some source
positions repeat. The two parity toggles still give
`y[j_i] <- y[j_i] XOR y[s_i]`, and all temporary digits restore.

The ideal repeated-source shear is an involution because it fixes its
source bits. It also preserves the same good predicate: only selected
parities change, while guards and temporary digits remain fixed. The
original bijective bad-address repair consequently applies unchanged.
The descriptor now contains a polynomial-size source list with repetitions;
it is not advice. Splitting the targets into `K=256G_router=O(log b)`
residue classes, with actual enlarged spectator records, retains
`O(V b^tau polylog b)` cost. The final `K` positions have the original
bounded elementary fallback. This is a newly stated extension of the
written contract and is credited to its inherited identity.

In particular, one BIT `parity(U_i)` may fan out to every bit of its target
word `Y_i`, with all `U_i` bits outside every active `Y_i`. This implements
the conditional bitwise complement of all active target words. It does NOT
assume that a nonlinear interval predicate is a BIT-router source.

## 3. Dirty predicate loads implement partial reflections

For endpoints `0<=a_i<=b_i<=2^L_i`, set

`J_i(y)=a_i+b_i-1-y mod 2^L_i`,
`c_i(y)=1[a_i<=y<b_i]`.

`J_i` is an involution. It maps `[a_i,b_i)` onto itself, and maps its
complement onto itself. Thus it preserves `c_i` exactly, including empty
and full intervals. The required partial reflection acts as `J_i` on the
interval and fixes its complement.

Borrow another dirty `G`-bit digit `U_i` per target, initially `U_i<B-1`.
Conditional `J_i^parity(U_i)` is: first conditionally complement every
target bit using the repeated-source BIT shear, then perform the guarded
binary addition with offset
`parity(U_i)*(a_i+b_i mod 2^L_i)`. Every `T_i` restores.

Execute the following four operations on all independent targets:

1. Apply `J_i^parity(U_i)` to every `Y_i`.
2. Route all completed `Y_i` and fixed endpoint controls before packed `U`.
   ONE ordinary prefix-controlled rotation adds `sum_i c_i(Y_i)B^i`.
3. Apply `J_i^parity(U_i)` with the newly loaded dirty controls.
4. Route completed `Y_i` before `U` again and subtract the same computed
   predicate sum in ONE ordinary prefix-controlled rotation.

There is no carry between `U` digits on the good set. Loading toggles each
parity by `c_i`; the two conditional involutions give exactly `J_i^c_i`.
The predicates are preserved throughout each completed `J_i`, so unloading
restores every original dirty `U_i`. This remains true for arbitrary initial
parities. All endpoints' controls must stay fixed and outside ALL active
targets. This is why the old triangular per-axis schedule cannot simply be
declared parallel.

Every primitive in this program is globally bijective. Reversing the four
operations and reversing the actual guarded additions gives a polynomial
address inverse even on bad addresses. Merely assuming that the implemented
conditional reflection is an involution on bad addresses would be wrong;
the checker explicitly uses the reversed primitive program.

## 4. Arbitrary valid-interval rotations require three reflections

For `0<=f<s<=2^L`, right rotation by `f` on `[0,s)`, fixing `[s,2^L)`, is:
reflect `[0,s)`, then reflect `[0,f)`, then reflect `[f,s)`.
If `y<s-f`, the result is `y+f`; otherwise it is `y+f-s`.
Padded target addresses remain fixed. All three reflections can be batched
as above when each pair's offset and modulus controls are outside all active
target words. Each completed good-address call restores `U,T`.

For `m` active targets, the common outer bad set is
`some U_i=B-1 or T_i=B-1`. Its density in the complete binary address box is
at most `2m/B`. Choose `G=6 ceil(log2(b+2))+6`, so the density is `O(b^-5)`
for `m<=b`. The ideal interval rotations fix `U,T`, hence preserve this good
set. Because the actual completed program is a bijection and agrees with
the ideal map on every good address, it maps the bad set onto itself too.

Extract current bad records, compute key `ideal(actual_inverse(address))`,
ordinary stable-radix-sort these keys, and reinsert into marked holes. All
copies, keys, and passes are paid. With complete coefficient width `Q>=b`,
key width `O(b)`, and stored bit volume `V`, extraction/reinsertion costs
`O(V)` and bad sorting costs `O((2m/B)*V*b)=O(V)`. The inner repeated-source
shear has its own original exact repair; its calls are separately paid.

## 5. Divide-and-conquer CRT and simultaneous monotone splitting

Let a node contain an ordered list of pairwise coprime odd leaf moduli.
Write their products `S_L,S_R` and binary capacities `T_L,T_R`, where
capacities are the products of the original power-of-two leaf capacities.
For scalar node index `k=A+S_L B`, perform

`(A,B) -> (A, B+S_L^-1*A mod S_R)`.

Then recurse independently in the left and right groups. The right group's
input is `S_L^-1*k mod S_R`; induction therefore gives leaf coordinate
`P_i^-1*k mod s_i`, exactly the original triangular CRT map. The left
group's input is `k mod S_L`. Node endpoints/control words are disjoint
across nodes at the same tree level.

On padded controls `A>=S_L`, set the offset to zero. The repaired valid-
interval rotation fixes every target `B>=S_R` and is the identity when its
left control is invalid. Its inactive banks restore. Thus each completed
node-batch boundary preserves the current product of valid node intervals
and keeps every invalid payload zero. Temporary dirty-bank layouts and
primitive additions may change intermediate validity masks; no padding
deletion or numerical operator consumes those intermediate layouts.
The next joint splitting scan deletes only the known zero records at
invalid OLD node addresses, and emits zeros at invalid NEW addresses.

Splitting each contiguous valid node interval `[0,S_L*S_R)` into fields
`[0,S_R) x [0,S_L)` is not a free binary reinterpretation. The injection

`k=A+S_L B -> B*T_L+A`

is strictly increasing. Jointly splitting all independent nodes preserves
the original Cartesian lexicographic source order. Thus ONE scan of the
complete new binary box reads the next valid original payload record at
each new occupied address and writes zero at unoccupied ones. Invalid
source slots are deleted in the same sequential source traversal. The
binary capacity remains exactly `T`, with no extra address axes or volume.
Counter and validity work is `O(b^2)` per record and is absorbed
by the campaign's `Q=Theta(d^18)` record width. For `epsilon>1/2`, the
conservative `O(b^2)` metadata work is `o(Q)`.

Each level then routes the left group words to fixed control fields and
right group words to target fields, batches the independent valid-interval
rotations, and restores the layout required for the next splitting scan.
The first bounded number of levels has only a bounded number of nodes and
may use the original ordinary rotations. At later levels split nodes into
two classes by greedily balancing their TOTAL binary word widths, not their
counts. The inactive class and all already unsplit singleton leaves provide
actual dirty coordinate banks for the active class. In the campaign every
leaf has width ell except one suffix leaf of width below `2ell`; after a
bounded number of balanced levels the largest remaining node has at most
`N/4` bits. Greedy balancing puts at most `(N_split+N/4)/2<=5N/8` bits in
either active class, where `N_split<=N` is the total split-node width. Hence
the complement contains at least `3N/8` existing inactive bits, more than
the conservative `N/8` bank used below. Highly unequal arbitrary leaf
widths need a separate width-balanced tree argument. There are
`O(log d)` levels for the campaign's specified leaf widths.

Write `N=log2(T)=Theta(b)`. For fixed `epsilon<1`,
`2mG=O(d log b)=o(N)`. Use the conservative inactive
bank lower bound `N/8` beyond a common finite threshold. Choose spacing
`K_router=256G_router` and `H=ceil(N/K_router)*G_router`. Even reserving
NINE disjoint `H` pieces costs at most `9N/256+O(log b)<N/16` eventually.
Only one fixed three-piece reservoir is needed for the repeated-source
fanout, because all its active target and source bits already avoid the
inactive donor bank; the matching-specific three-reservoir partition is
not invoked. Reserving nine pieces is a conservative allowance for field
placement. Reserve `U,T` in at most `N/64` additional bits and one untouched
suffix of width `ell=Theta(b/d)` in at most `N/64` bits, beyond another
common threshold. These disjoint requirements total less than `3N/32<N/8`.
That suffix gives genuinely enlarged
records of size `Q*2^Omega(b/d)`, dominating every fixed polynomial in `b`.
All field placements use the accepted original swaps or already reviewed
coordinate routers, and all borrowed bits restore before another class.
No added address bit or clean ancilla is assumed.

Every ordinary prefix rotation has its controlling coordinates earlier
than its entire target field. With schoolbook arithmetic, `m<=b` modular
offset products and concatenations take at most `O(b^4)` work per prefix.
All moduli, prefix products and inverses are precomputed with at most
`O(b^5)` scalar setup. The complete address inverse and repair-key function
take `O(b^4 polylog b)` work, including the `O(log d)` known layouts and
constant reflection stages. These are explicit loose bounds. An untouched
superpolynomial spectator suffix absorbs prefix work within actual
enlarged records. For the campaign's `Q=Theta(d^18)`, `epsilon>1/2` also
gives `b^4 polylog b=o(Q)`, so base-record inverse/key work is absorbed
even without this enlargement. No arbitrary unspecified polynomial is
silently charged to a `Q`-bit base record. Together with the repeated-source
shear and known routers, the candidate CRT movement bound is

`O(V*b^tau*polylog b)`.

The stated campaign transfer therefore uses both `epsilon>1/2` and
`Q=Theta(d^18)`, or any explicitly comparable coefficient width. A general
shorter-record extension would need its own metadata amortization proof.

This replaces a sum of `d` full-payload rotations only if all bank,
descriptor, inverse, splitting, and repair interfaces in this report are
accepted. It is not obtained by applying a coordinate permutation to CRT
output keys. An independent bank-layout and machine-interface review is
required before promotion.

## Finite evidence and reproduction

The first extended run checks eight complete partial-reflection address
spaces, including unequal target widths, nonzero interval lower endpoints,
full intervals, arbitrary dirty parities, and dirty guard overflow. It checks
global bijectivity on both good and bad addresses, exact good-state
identities, and composed odd rotations. The CRT tree is independently
compared with `P_i^-1*k mod s_i` for every input through five small primes.

The second run checks complete THREE-reflection rotation programs, explicit
primitive inverses on every address, and actual stable binary-radix repair
of every bad record. It retains the number of wrong records before repair.
Neither run silently ignores the dirty-guard all-ones boundary.

Additional completed controls:

| Run | Changed interface | Evidence |
|---|---|---|
| `20261008T1400Z-crt-guards-extended` | Guarded partial reflection | 1,634,304 complete states; bijections and exact good-state maps |
| `20261008T1404Z-crt-guards-complete-repair` | Full odd rotation and inverse | 1,077,248 complete states; 564,400 wrong pre-repair records repaired |
| `20261008T1408Z-crt-four-target-repair` | Four unequal target words | 2,097,152 complete states; 1,892,810 wrong pre-repair records repaired |
| `20261008T1412Z-masked-bit-fanout` | Actual inherited ten-rotation program with repeated BIT sources | 327,680 complete states and 400,000 adversarial states, including 200,117 good cases |
| `20261008T1416Z-crt-joint-splits` | Full payload monotone splitting and recursive leaf map | Six-prime T=2,097,152 box; 255,255 valid records and every padded zero verified |
| `20261008T1419Z-masked-fanout-inactive-sources` | ACTIVE masks and repeated inactive-position BIT source | 200,000 adversarial states; 100,000 good; 95,705 wrong unrepaired negatives |
| `20261008T1423Z-crt-existing-bank` | Actual borrowed coordinate bits and invalid zeros | All 65,536 padded addresses, zero added bits; 3,466 nonzero invalid intermediate records restored by completed repair |

The last control is a particularly useful negative interface: deleting padded
addresses BEFORE the outer repair would discard real nonzero payloads.
All four borrowed bits are part of the existing inactive fifth coordinate.
The completed repaired map restores that coordinate and the entire validity
mask. Source hashes and exact reproduction commands are retained with each
run under `../runs/`.

The first fanout run's active-source rejection check redundantly caught its
own failure assertion; its positive fanout and inverse checks were unaffected.
The final masked-source run repairs that check and confirms actual rejection.
Both executed source versions remain available. This correction does not
replace or overwrite the first run.

Local independent review by the scout and layout agent accepted the repeated
source identity, independent-node endpoint controls, monotone splitting,
inactive bank allocation and padding-boundary qualifications. The durable
layout review is `../../layout/crt-reflection-layout-review.md`. These are
internal mathematical reviews, not external peer review or formal proof.

From the repository root, reproduce using Python 3 standard library:

```bash
python3 research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/inverse/code/crt_guard_controls.py --extended --output research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/work/inverse/reproduce-crt-extended/certificate.json
python3 research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/inverse/code/crt_guard_controls.py --complete-repair --output research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/work/inverse/reproduce-crt-repair/certificate.json
```

Both runs use one CPU process, one native thread, no dependency environment,
and distinct execution directories. The first source revision is preserved
with its run because explicit inverse/repair support was subsequently added.
