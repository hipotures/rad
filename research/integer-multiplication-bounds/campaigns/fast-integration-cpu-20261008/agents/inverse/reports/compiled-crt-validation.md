# Actual masked BIT gadgets inside the guarded CRT pipeline

The indefinitely extended campaign validates a changed interface that the
earlier separate controls did not exercise: actual masked `F_u` source fanout
and its computed-inverse-key repairs are executed INSIDE the conditional
reflections and full padded CRT tree. The inherited BIT fanout is not replaced
by an ideal complement during payload execution.

The finite compiler is
[compiled_crt_pipeline.py](../code/compiled_crt_pipeline.py).
It is an address/payload model, not an implementation or timing measurement
of the all-size fixed-tape integer multiplier. Its Python lists are finite
verification storage. The written tape transfer remains in
[guarded-crt-batching.md](guarded-crt-batching.md).

## What the compiler executes

Each selected target residue class routes actual existing named bits to
the three temporary fields and middle source/target field. It computes the
ten ordinary rotations and twelve temporary-field swaps in the inherited
masked `F_u` program. Repeated sources are actual dirty outer-U parity bits,
not copied clean bits. The inner fields are selected from the current tree's
inactive node coordinates. All remaining physical bits occur exactly once
in the middle field. No address bit is appended.

After the raw program, the compiler extracts its ACTUAL bad addresses and
computes key `ideal_BIT_shear(raw_F_u_inverse(current_address))`. It performs
stable least-significant-bit radix passes and reinserts into the marked
holes. The raw inverse is obtained by reversing the actual rotations and
swaps with recomputed controls. There is no inverse-address table.

The conditional global reflection then performs the actual guarded packed
binary addition; computed interval predicates are loaded/unloaded by packed
ordinary rotations. Three partial reflections complete each odd-modulus
rotation. Its outer repair uses the composed reverse program, including
every previously completed inner repair. For an inner repair's inverse,
the computed bad-hole key is `raw_F_u(ideal_BIT_shear_inverse(address))`.
Thus the full reverse pipeline also executes actual radix-sorted inverse
repairs; it does not restore a saved initial payload array.

Every source record has provenance `k+1` for `0<=k<S`; the other addresses
are explicit zero padding. Joint splitting scans delete only completed old
zero padding and insert new zeros. Node-validity masks are checked after
every completed depth. The final leaf array is compared with an independent
prefix-product CRT oracle:

`leaf_i(k)=P_i^-1*k mod s_i`, `P_i=product_{j<i}s_j`.

This is the original upstream triangular normalization, NOT the conventional
idempotent coefficient `(S/s_i)^-1`. Reversing every event, including joint
occupied-slot scans, must recover all original records and all padding.

## Completed evidence

| Run | Physical box | Actual compiled mechanism | Result |
|---|---|---|---|
| `20261008T1440Z-compiled-crt-four` | T=4096, S=1155 | 42 inner `F_u` calls / 420 rotations inside two CRT node batches; 113 map/repair/split events | Complete leaf oracle and reverse payload pipeline PASS; 10.83 s, one CPU |
| `20261008T1440Z-compiled-crt-five` | T=65536, S=15015 | Same two compiled node types plus three joint CRT depths; 115 events | Complete leaf oracle and reverse pipeline PASS; 174.01 s, one CPU |
| `20261008T1448Z-compiled-crt-bankleaf-five-bank` | T=131072, S=19635 | Two simultaneous nodes, target widths(3,4), with five existing donor bits; 14,608 wrong outer records repaired; 198 events | Complete leaf oracle and reverse pipeline PASS; 710.43 s, one CPU |

The first two versions use one active node per finite bank class. Consequently
outer packed digits cannot carry into another active word, and the measured
number of wrong pre-outer-repair records is zero. This is a useful scope
qualification: these runs exercise nontrivial INNER gadget repair and whole
CRT integration, but do not independently discriminate multi-target outer
overflow. The earlier complete multi-target guard controls do discriminate it.

All executed source and dependency hashes, exact reproduction commands and
compact certificates are retained in each run's `code/`, `protocol.json`,
and `results/`. They use Python 3 standard library and one CPU/native thread.

## Running stronger variants

The six-prime source box is T=2,097,152, S=255,255. A baseline compiler uses
disjoint inner scratch fields. A changed compiler,
[compiled_crt_pipeline_batched.py](../code/compiled_crt_pipeline_batched.py),
uses larger selected-bit spacing and permits the dormant outer-T digits to
be reused as inner `F_u` scratch. All outer-U BIT sources remain outside
that scratch. Each completed inner repair restores every temporary field
before any outer guarded addition reads T. This is a finite interface
variation; the general theorem can keep its simpler disjoint allocation.

The completed bank-leaf family uses the original last prime coordinate as an
inactive bank after ONE root split, then balances the remaining tree. Its
depth is `1+O(log d)`, not d. The source box is T=131072, S=19635 with
moduli(3,5,7,11,17). It permits a genuine TWO-node simultaneous batch using
the original inactive last coordinate, with no added address bits.

These variants have pinned running protocols. They are not yet promoted
by this report until their full certificates exist, except the bank-leaf
family whose forward AND inverse checks now pass. Partial depth/progress
messages must not be interpreted as completed inverse validation. Its
nonzero outer-repair count supplies the previously missing simultaneous
carry discriminator INSIDE the full actual-F_u CRT composition.

### Sequential reuse of dormant outer guards

The completed finite bank-leaf family reserves two U source bits and two
T guard bits within the five-bit inactive coordinate. Its inner F_u needs
three scratch bits. These three include the dormant outer T bits. This is
permitted only because the entire INNER shear and its exact inverse-key
repair finish before the outer addition reads T. The completed shear acts
as BIT-source XOR on the active target bits and fixes ALL other original
bits, including T. Outer U bits remain outside every inner scratch field
and every active target. During a raw inner call, original padding and T
may move; neither is inspected by a subsequent outer operator until repair
restores the full shear interface. The executed reverse program obeys the
same boundary rule. This finite reuse strengthens the composition control;
the written all-size tape theorem uses its simpler disjoint inactive-bank
allocation and does not need the reuse.

A new two-bit outer-guard family is running in
`20261008T1500Z-compiled-crt-guard2-bank131`. It changes both the available
good dirty digits and the all-ones carry boundary. Its box has T=1048576,
S=151305, moduli(3,5,7,11,131), with the original last coordinate supplying
the bank. It is not yet completed evidence.

## Distinct guard falsifications retained

While the compiler was authored, three new complete-state corner families
ran on the assigned three CPU slots. They changed zero offsets, full binary
moduli, and unequal target widths. The largest covered 8,388,608 addresses
with widths(3,4,4), two-bit dirty digits, moduli(7,9,15), offsets(0,8,14).
It repaired 4,427,864 wrong pre-repair records exactly, including all guard
boundaries, and used an explicit reverse program. Source snapshots and
protocols are retained under `runs/20261008T1435Z-*`.

The information contributed by the new compiler is interface composition,
not a new native network moment or a timing-based exponent claim. Conditional
full-multiplier assembly and the common eventual threshold remain the
coordinating agent's responsibilities.

## Coefficient-payload integration API

[compiled_crt_payload_api.py](../code/compiled_crt_payload_api.py) exposes
`transform_payload(primes, coefficients, reverse_check=True,
emit_stdout=False)`. It executes the SAME completed bank-leaf forward loop,
actual masked F_u and both levels of radix repair with caller-supplied
nonnegative integer coefficient values. Those values occupy scalar indices
`0<=k<S`; all remaining input addresses are numeric zero padding. Legitimate
coefficient zeros are allowed. The result's `output` is the full padded leaf
box of length T, axis zero in the least-significant binary field. An
independent triangular-CRT oracle uses the supplied value for each k, and
the optional reverse check must recover every initial coefficient and zero.

This API depends on the frozen `compiled_crt_pipeline_bankleaf.py` and
`crt_guard_controls.py` in the same directory. It does not support negative
sentinel values or arbitrary object payloads; ring residues should first be
represented by their nonnegative integer representatives. The API itself
has been syntax checked; a composed Gaussian/ring producer caller check
belongs to the layout branch and remains pending at this update.

The companion `inverse_payload(primes, leaf_coefficients,
emit_stdout=False)` accepts the entire padded binary leaf box. It separately
charges a forward compilation template with positive provenance labels,
then replaces only the coefficient payload and executes every actual reverse
event on the supplied recovered coefficients. The inverse oracle is used
only to check the result. It returns the full scalar padded box in `output`,
the first S recovered coefficients in `coefficients`, and a compact forward
template ledger. Nonzero leaf padding is rejected before compilation. No
saved initial coefficient stream or inverse address lookup supplies outputs.
