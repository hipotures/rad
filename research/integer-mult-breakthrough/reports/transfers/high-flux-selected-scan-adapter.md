# A paid alternating high-flux selected-order scan adapter

Status: **EXACT FINITE OPERATOR EVIDENCE AND CONDITIONAL NATIVE ADAPTER**.
One existing selected guard bit, two fixed bit swaps, and one complete
packed-mask word implement the alternating complement-shear permutation.
Conjugating the new natural selected-fiber scan by that permutation gives
the intended high-flux prefix/difference endpoint. The mask router keeps
its full paid ordinary exchange exponent. No faster zeta or integer
multiplier is supplied by this component.

## The order and its exact endpoint

For f selected action bits and D=2^f, use the involution

    P(a) = a XOR [(a AND 1)(D-2)].

For f=3 its order is [0,7,2,5,4,3,6,1]. It alternates even labels in
ascending order with odd labels in descending order. The grouped order
[0,2,4,6,7,5,3,1] is different. Keeping a temporarily relocated pivot
as the most significant selected scan bit would produce that grouped
order. It is retained as an explicit negative here. The actual adapter
restores the low pivot and original selected mask before every scan.

Let L be the natural selected-fiber prefix operator, with every original
spectator value and old row fixed. The complete operator is

    P^-1 L P = P L P.

Its true inverse is P L^-1 P with the actual difference scan. All four
Gaussian fields and their complete record positions are transported.
Control chunks, original guard values and every K-1 plane are retained.

The high-flux order was independently developed by the synthesis track;
its source is [the nonlex flux probe](../../code/synthesis/nonlex_scan_flux_probe.py).
That track's three-factor algebraic tests remain separate. This adapter
does not adopt an unfound matrix factorization or its exponent.

## Existing complete guard geometry

Take three existing address bands, each with f+4 complete K-bit chunks:
there are exactly 3f+12 chunks and no added address volume. Positions are
counted from the least significant end, and every selected bit has the
common offset rho, 0<=rho<K. The low band is the action band. Its pivot
is bit rho in chunk zero. The target range begins at chunk one and contains
f complete chunks: f-1 active action chunks and one existing complete
terminal guard chunk. Its width is L=fK.

The equal-width routing companion is the first f complete chunks in the
middle band. The borrowed bit is at offset rho in the last complete guard
chunk of the highest band. It is above and disjoint from both mutable
ranges. It is an existing address bit, with arbitrary original value;
it is not a new Gaussian helper bank, zero ancilla or extra independent
volume. All unused portions of all three bands remain spectators.

The complete temporal permutation is:

1. Swap the original low action pivot with that highest guard bit.
2. Execute one generalized mask word on the target, using the distinct
   equal-width companion. Its mask complements each of the f-1 active
   selected target positions exactly when the relocated pivot equals one.
3. Swap those two bits back.

The original guard value temporarily sits in the old pivot position,
which is outside the target and companion ranges. It is not read by
the mask. The relocated action pivot is immutable throughout the packed
word. Thus the final target update depends on the original action pivot,
while the original pivot and borrowed guard values are restored exactly.
The resulting permutation on original action coordinates is P, independent
of every original guard/control value.

If the terminal selected guard was processed by an earlier scalar kernel,
the completed adapter still preserves that coordinate and is independent
of its value. Consequently its completed operator commutes with that
separate guard kernel. This endpoint statement does not permit omitting
the earlier guard processing, reprocessing it, or assuming an incomplete
row allocation already has this physical complete guard shape. Native
rehydration and a network's actual complete row stock remain caller
obligations. Extra residual chunks may be spectators of this standalone
adapter; their separate target kernels in a supplier are still charged.

## Literal mask word, complete repairs and inverse

Let G be the sparse target mask with all f-1 active positions set if the
relocated pivot is one, and zero otherwise. G reads only that immutable
control bit. It never reads a target or companion bit to decide which
selected action positions are meant to flip. The original eight-addition
rotation word reads current target/companion bits only to construct its
reciprocal rotation offsets. Every offset is applied modulo the complete
range 2^L. All wraps, current addresses and guard values are kept.

The code replays every one of the eight actual rotations as a finite
complete-record permutation. Their order and signs come from the immutable
[independent native GL control](../../code/transfers/native_gl_review.py),
SHA256 1ae606d030f1f71ebe2d2497399601f1cdc6e59aa4e3209527533ecf57432d19.
The generalized immutable-mask proof is credited to the coordinator's
[earlier complete control word](../../code/obstructions/general_control_bit_reversal.py)
and the pinned original `05-layers.tex`.

Let S be the eight-rotation permutation and T the intended active-bit
XOR. On the invariant exceptional set B, the repair is T*S^-1; elsewhere
it is identity. The actual repair inverse is S*T on B. The literal
inverse route therefore swaps the two bits, applies that inverse current-
address repair, undoes the eight rotations in reverse order, then swaps
back. It is not an assumed inverse oracle or a forward repair inserted
at the wrong time. The terminal selected guard position is excluded from
G, so no additional top-bit NOT is silently required or waived.

After the first complete adapter, the original low pivot and all guard
values are back in their original physical positions. The natural scan
therefore consumes its original selected mask. The second adapter uses
the literal inverse route. In total, one complete high-flux scan pays
four fixed bit swaps, sixteen literal rotations, two complete current-
address repairs, the actual natural scan, mask preparation and cleanup.

## Conditional native bill

The original `02-streams.tex` fixed-two-digit operation implements each
bit swap in O(V), including collapsed shape preparation, counters,
complete record transport and cleanup. This fixed radix-two operation
does not become a free full variable-width field permutation.

The mask primitive is the supplied original packed selected-bit rotation
and exceptional sorting/repair interface. Its reciprocal target/companion
updates retain the full arbitrary-width exchange bill. With complete
payload V=M R, actual header length A and inherited exponent tau, the
conditional bound for the two wrappers plus scan is

    O(V[(fK)^tau+1]
      + M[A^3+C_G(A)]
      + delta M A(R+A)),
    delta <= min(1,80(f-1)2^-K).

The fixed wrapper count is absorbed into the constant. G is only a
broadcast of one immutable pivot bit, but its actual sparse mask/descriptor
preparation is still charged by C_G(A). The original polynomial-long
record regime permits that address work to be o(V). The finite Python
array permutations do not measure this native routing time. The complete
exceptional records, including all fields, must still be sorted, moved
and restored by the original interface. At the small K controls the bad
set can be the whole domain; those are semantic tests rather than an
asymptotic cheap-repair measurement.

The natural scan contributes O(V) under its full p+f+O(1) signed-width
contract, proved in [the separate scan report](natural-selected-fiber-scan-tapes.md).
It amplifies arbitrary bounded coefficients by at most 2^f. The two
wrappers are exact address permutations and add no coefficient magnitude
or grid growth. Under the pinned w=Theta(p), f<=p^epsilon, epsilon<1,
the added magnitude reserve leaves R=Theta(rp). If coefficients instead
use only K numeric bits, the real 1+f/K payload overhead is retained.
Neither a floating exponent nor modular wrap supplies the missing exact
signed-grid contract. Whole recursive prefix/tail norms and outer integer
recovery remain separate from this standalone component.

## Finite evidence, failure and recovery

The [fresh source](../../code/transfers/high_flux_selected_scan_adapter.py)
imports only the frozen native GL and literal natural polynomial scan
implementations. The four-worker accepted attempt is
`20261009T111953Z-transfer-high-flux-adapter-repair`, actual start
2026-10-09T11:19:53.059577+00:00; elapsed 0.634159497 seconds.

Three complete relevant-coordinate cubes f/K/rho=2/1/0,3/1/0,2/2/1
pass 1,344 full records and 10,752 signed Gaussian component values.
Each forward route uses every actual rotation and repair. The complete
route-scan-inverse-route pipeline and true inverse retain all fields and
spectator coordinates. The full physical arrays at all 3f+12 chunks
are not materialized in those tests. Only the complete read/write set is
materialized; every omitted address plane is an exact identity factor.
The read/write-set proof and the general all-size natural scan, rather
than sampled zero guards, justify that extension.

A separate seeded full-address case tests 4,096 complete 144-bit addresses
at f=4,K=6,rho=1. It contains both carry-free and exceptional guards,
preserves every control, companion and unselected plane, and verifies the
literal chronological inverse. The omitted-repair and omitted-final-swap
controls give actual corrupted endpoints. The grouped order gives a
different complete scalar matrix and is rejected.

The first attempt `20261009T111817Z-transfer-high-flux-adapter-first`,
actual start 11:18:17.366437 UTC, failed an overly strong negative-control
requirement. In the complete one-active-bit small cubes, S=T already:
omitting repair changes zero addresses at f2/K1 and f2/K2/rho1.
At f3/K1 it changes 128 of 256 complete relevant addresses. The endpoint
and inverse assertions preceding that negative passed. The repaired source
requires the final-swap negative in every small cube and the actual repair
negative over the complete aggregate, including the wider K6 guard case.
It does not change the routing/scalar program.

Rejected source SHA256 is
5f9de7a4497587cc7b61748850db5925075bb00932a4314397aad68c3eb3d8e4.
Current SHA256 is
fd636fbb77ef31d20e5a4c7fb75fef0f62854b1e95c3f548a44c07f308e97dc1.
The exact [recovery patch](../../fixtures/transfers/high-flux-negative-recovery.patch)
has SHA256 7d3997ab8bd0e0148354e975b917299d09f10ae8be37ac72efabbc2b0e8cbfee.
Applying it to the current source in an isolated tree reproduces the
rejected hash. The `111952Z-transfer-high-flux-negative-recovery` receipt
retains that actual check, original failure and exact small-cube counts.
Original source/config/protocol/evidence bytes for each attempt are
preserved. Reference serialization assigns implicit current physical
addresses before the literal scan; these are test framing labels, not
unpaid replacements of arbitrary payload fields in the native procedure.
The original native layout uses implicit addresses and can consume the
separate headerless scan contract.

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/high_flux_selected_scan_adapter.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/transfers/high_flux_selected_scan_adapter.py --workers 4
```

The exact adapter and its paid bound were developed with AI assistance.
The main leverage is to replace an unpriced high-flux layout obligation
with a stated complete-payload conditional interface. Its tau is still
the supplied ordinary routing exponent. A matrix factorization, completed
fast supplier and exponent require additional evidence; none is asserted.

The synthesis track's [independent source review](../synthesis/high-flux-adapter-source-independent-review.md)
accepts the chronological route, disjoint control geometry and invariant
repair scope without executing this producer or claiming new measurements.
The separate [format and parameter clarification](natural-scan-address-width-clarification.md)
records the original restrictions needed for A=O(p) and the paid component
bit-order conversion outside the measured seven-tape scan core.
