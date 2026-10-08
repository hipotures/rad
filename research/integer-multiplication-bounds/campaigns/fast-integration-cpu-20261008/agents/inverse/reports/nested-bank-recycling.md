# Recycling dormant outer-register bits inside completed exact shears

Status: written composition principle, one completed positive native control,
and a preserved unexpectedly successful missing-repair control. Further
distinct cases are queued. No new multiplication exponent is asserted here.
The current full composition already has enough disjoint inactive-bank space;
this refinement tests a smaller finite bank and states its restoration premise.

## Exact completion makes dormant bits available

Let an inner exact shear F toggle target bits Y from source bits S and fix
every other bit. Its implementation may temporarily alter a dirty bank R
outside Y and S. Assume its actual bad-address repair has COMPLETED, so the
implemented map equals F on every address, including initially bad ones.
For any next outer operation A on the full address state, A composed with
that completed implementation equals A composed with F pointwise. A may
read R: its original contents have returned before A starts. The reverse
program likewise uses the completed implementation's literal inverse.

This permits borrowing an outer register inside the inner call whenever its
contents are dormant during that call and all LIVE source bits avoid the
borrowed bank. It does not permit passing a partially repaired state to A.
The previous native missing-inner-repair counterexample already demonstrates
that the outer repair is not a substitute for this exact completion.

In the conditional reflection, inner BIT fanout reads only parity(U_i),
meaning its integer low bit U_i mod2, not population parity of all its bits.
The high bits of outer U_i and every outer T_i bit are dormant until the
fanout finishes. They may therefore be inner scratch, provided those parity
sources stay outside it and all inner repairs finish before the outer guarded
addition or predicate load. Endpoint controls remain outside all outer U/T;
the independent fixed-control collision is not bypassed.

The modified inner layout passes ONLY the m live parity-source bits to F_u.
It removes borrowed high U bits from the middle field. Passing the old full
U list while also borrowing high U as scratch would duplicate an address bit
between fields and is invalid. The existing field-partition assertion checks
that every physical bit occurs exactly once.

## Finite bank counts and planned controls

For m targets, outer digit width G_o and one inner call needing three H-bit
fields, the recycled donor bank needs

```
D >= max(2*m*G_o, m+3H, full-top-guard requirement).
```

The first term stores the original outer U/T fields. The second leaves three
H-bit scratch fields after excluding the m live parity sources. The top guard
also has to fit the actual middle field; it is separately charged, not assumed
from scratch capacity alone. Real all-size routing retains its named reservoir
and suffix contracts. The finite formula is not substituted for those charges.

The authored sources are
[compiled_reflection_four_recycle.cpp](../code/compiled_reflection_four_recycle.cpp)
and [compiled_crt_native_recycle.cpp](../code/compiled_crt_native_recycle.cpp),
forked from the retained four-target and native implementations. They still
execute every raw F_u rotation, actual inverse-key radix repair, independent
modular-rotation oracle and complete reverse payload program. The tagged input
includes all original bank patterns and explicit invalid-target zeros.

The queued run prefix is 20261008T1650Z-reflection-recycle. Cases are:

- Two targets(2,3), G_o=2 and G_inner=3: an entire 19-bit cube, with fifteen
  original bank bits and both high outer U bits actually selected as scratch.
- The same fixture with inner exact repair deliberately omitted, testing the
  completed-map premise rather than just an ideal fanout oracle.
- The same fixture with its fixed endpoint source deliberately borrowed as
  U[0], extending the nonbijectivity discriminator to two-bit outer guards.
- Four targets(2,3,4,5), G_o=2 and G_inner=3: an entire 25-bit cube with sixteen
  original bank bits, borrowing four high outer U bits plus outer T bits.

The last case's old disjoint-U assignment would require seventeen donor bits
and a 26-bit cube. This is a finite factor-two volume difference, not an
asymptotic saving. Inner spacing K=8 keeps the three-bit guard interval
[16,112) nonempty; using the earlier tiny-case K=6 would make it empty.
The native certificate reports the actual high-U and outer-T scratch counts.

## Completed evidence and an informative anomaly

[20261008T1650Z-reflection-recycle-two-target-smoke](../runs/20261008T1650Z-reflection-recycle-two-target-smoke/protocol.json)
passes its independent modular-rotation oracle and complete reverse program
on every one of 524,288 physical records, including 393,216 valid tags and
all original dirty-bank patterns. It executes 49 events, 18 actual F_u calls,
180 raw rotations and 38 forward/inverse radix repairs. The repairs process
8,753,152 summed records and restore 79,872 wrong outer records and 20,480
nonzero invalid intermediate records. Two high outer-U bits and four outer-T
bits are actually selected as inner scratch. It takes 9.05 seconds on one
thread; the entire 19-bit address cube was supplied at the start.

[20261008T1650Z-reflection-recycle-two-target-missing-inner](../runs/20261008T1650Z-reflection-recycle-two-target-missing-inner/protocol.json)
deliberately omits every inner exact repair. Contrary to its predeclared
negative outcome, this particular fixture returns through both complete
oracle checks. Its raw status is UNEXPECTED_NEGATIVE_PASS, with error
`invalid contract unexpectedly passed`; it is preserved unchanged. The
certificate's two oracle booleans are status-derived and therefore false,
even though returning the successful measurement object means both actual
assertions passed. It executes 18 F_u calls and 180 rotations, but only two
outer forward/inverse radix repairs over 716,800 summed records. Those
outer repairs restore 129,536 wrong records and 30,720 nonzero invalid
intermediates. Runtime is 7.33 seconds.

This control does not establish that an outer repair always replaces inner
completion. Existing full-CRT missing-inner controls fail. The new fixture's
successful composition was investigated with the full unique-tag control
below; it is not promoted to a general repair theorem. The controller
correctly halted on expected_matched=false
and restored its owned Python worker. A retained continuation skips these
two completed attempts unchanged and executes only the unstarted cases.

[20261008T1650Z-reflection-recycle-two-target-source-bank](../runs/20261008T1650Z-reflection-recycle-two-target-source-bank/protocol.json)
borrows the fixed endpoint source as outer U[0]. The same two-bit outer
guards and three-bit inner layout fail with the specific raw error
`nonbijective native map at 40`, after 1.30 seconds. Raw status FAIL and
the required error prefix match this predeclared negative. The retained
four-target one-bit control and its analytic larger-guard collision explain
why endpoint controls must avoid their own guard bank. This is a newly
executed finite negative, while the earlier every-G statement is analytic.
The failed certificate's zero counters are not an assertion that no partial
program ran; its successful return object was never produced.

[20261008T1650Z-reflection-recycle-four-target-inner-G3](../runs/20261008T1650Z-reflection-recycle-four-target-inner-G3/protocol.json)
now passes both complete oracles on all 33,554,432 physical records, with
15,728,640 valid unique tags and every original bank pattern. Four high-U
bits and five outer-T bits supply the actual inner scratch. Its 109 events
contain 48 F_u calls and 480 rotations. The 98 forward/inverse repairs
process 1,431,927,808 summed records, restoring 9,243,272 wrong outer
records and 1,743,512 nonzero invalid intermediates. Native runtime is
1,537 seconds. This completes the distinct three-bit-inner control and
restores the original owned Python worker; no address bits were added.

## Full unique tags resolve zero-padding ambiguity

The previous tagged input identifies every valid record uniquely but stores
the same zero in all invalid slots. A wrong permutation within those equal
zeros would be invisible. Three fresh diagnostics therefore assign payload
a+1 to EVERY physical address a, including every invalid slot, with the
same 19-bit original box, target periods (2,3), outer G=2 and inner G=3.
Their authored source is
[compiled_reflection_alltag_probe.cpp](../code/compiled_reflection_alltag_probe.cpp),
with the full retained raw implementation copied into each frozen run.

| Run | Actual forward program | Wrong valid / invalid destinations | Full literal reverse |
| --- | --- | ---: | --- |
| [completed](../runs/20261008T1720Z-alltag-completed/protocol.json) | 18 F_u, 180 rotations, 38 repairs | 0 / 0 | Recovers all 524,288 tags |
| [omit inner](../runs/20261008T1720Z-alltag-omit-inner/protocol.json) | 18 F_u, 180 rotations, 2 outer repairs | 0 / 0 | Recovers all 524,288 tags |
| [raw fanout only](../runs/20261008T1720Z-alltag-raw-fanout/protocol.json) | 3 F_u, 30 rotations, no repairs | 39,936 / 9,216 | Recovers all original tags |

The completed and omitted-inner programs take 9.14 and 7.15 seconds;
the isolated raw fanout takes 0.30 seconds. The latter differs from the
ideal repeated-source XOR at 49,152 physical destinations, first at 3600.
It remains bijective, so its own reversed raw event program recovers the
input even though its forward map is wrong.

Thus the small outer composition really absorbs raw-inner damage on ALL
addresses. Its success is not zero-padding blindness. This finite fact
coexists with the retained larger missing-inner CRT counterexamples and
does not justify dropping inner completion in the all-size argument.
The completed map remains the reusable sufficient interface. The probe
reports exploratory outcomes directly, without forcing a negative label.

Reproduce all three diagnostics by compiling the corresponding frozen
code/compiled_reflection_alltag_probe.cpp with its included native source,
using the same compiler flags above, then supplying --mode completed,
--mode omit-inner or --mode raw-fanout and a fresh --output path. The
source hashes, exact invocation, original inputs and completed result
hashes are in each protocol. The controller pauses only its positively
identified owned Python worker and restores it in finally; this is recorded
execution management, not a dependency of mathematical reproduction.

Protocols and both full source snapshots are written before execution. The
queue waits for the currently running owned native job to finish, then uses
that same assigned slot by pausing its identified Python worker. It resumes
the worker in finally. Further results will be added here only after their
own frozen certificates exist. A source-bank negative is predeclared with
raw status FAIL AND the specific nonbijectivity error prefix; unrelated
failures cannot satisfy that negative check.

Reproduce each case with its frozen sources and exact protocol flags:

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic <run>/code/compiled_reflection_four_recycle.cpp -o <ignored-work>/control
<ignored-work>/control --family two-small --outer-guard 2 --inner-guard 3 --output <fresh-ignored-work>/certificate.json
```

This is standard exact composition and register liveness applied to the
credited restored masked shear. It is not a worldwide priority claim.
