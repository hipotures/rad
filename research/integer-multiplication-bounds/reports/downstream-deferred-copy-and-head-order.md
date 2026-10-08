# Deferred copy and head-pivot order discriminators

These are two distinct bounded controls. The first validates deferred
scalar cleanup but rejects retaining the old cleanup frames without a
new chart. The second shows that full complementary flags alone do not
give a free increasing batch of head pivots. Neither is a universal
obstruction to different restoration contracts or stronger basis choices.

## Deferred first source copy

Omit the first invocation's final input-copy undo. Its helper bank retains
`z+V A_old`. Later dirty-scratch invocations remain scalar-correct on this
arbitrary baseline. The three XOR shears exchange A and B; afterwards
`B_final=A_old`. Subtracting `V B_final` restores the leaked first helper.
The first and third invocations may share the same helper bank: the third
restores the arbitrary dirty baseline it received.

The [source](../code/downstream_deferred_copy_discriminator.py), SHA256
`58ed8ce07c0bd19e36792de5f87b70313c12c65d09fefb9596a458dd0edfe0c9`,
executes this exact scalar program with an invertible four-role mixer,
three data coordinates and two arbitrary dirty four-role helper banks.
It verifies the complete14-coordinate bit basis and128 arbitrary word
probes. Both helper banks are restored. Cleaning from A_final instead
of B_final fails every one of the129 packed probes.

The scalar identity does not remove the native cleanup boundary. If the
first helper retains its old full frame I while the final data wire has
its prescribed rank-(m-1) frame K, a common cleanup frame M incurs

`2 rank(I-M)+2 rank(K-M) >= 2 rank(I-K)=2`.

This is the matrix rank triangle inequality, independently of whether M
is a projector. Thus N such original copy pairs add at least2N ranks,
already larger than the old deficit `D=N-6v^2h^2`. Small exact rational
rank controls and positive excess budgets at h49,51,53,56 are retained.
The conclusion is scoped to the old late full helper chart and original
final data kernel. Source-specific late cleanup frames and changed
restoration contracts need a new proof and are not excluded.

The [completed protocol](../runs/20261008T084723Z-downstream-deferred-copy/protocol.json)
and [certificate](../runs/20261008T084723Z-downstream-deferred-copy/results/certificate.json)
retain the exact command and current queue admission. Certificate SHA256
is `3a8766926192a8c09f33039838ec0903a40433156738857e82bd288c73b13eb2`.

## Full flags and reversed head order

The [head-order source](../code/downstream_head_pivot_order.py), SHA256
`8e62e7b5704d9d0765e1f18bb5767ad682384df96f83f6f034656394e22ca0f3`,
constructs a six-dimensional rational projector P=UV with VU=I_2. Both
the front two-by-two U flag and last two-by-two V flag are invertible.
It constructs an exact positive rational metric making P self-adjoint
by combining bases of image(P) and kernel(P).

For A=I-P, actual lower/lower rightmost elimination gives pivots

`(row0,col5), (row1,col4), (row2,col2), (row3,col3)`.

The middle identity run has the expected length m-2d. The two head
pivots instead require source order5,4 into target order0,1. One free
increasing contiguous whole-bit interchange takes order4,5 and produces
a different labelled result. The example satisfies all full-flag and
nondegeneracy hypotheses; those hypotheses alone therefore do not
justify grouping the head pivots as one increasing child.

A reversal or arbitrary block gather must be paid through the actual
native address contract. Constant finite dimension is not, by itself,
an O(V) tape algorithm for fields whose widths grow recursively.
Additional simultaneous-basis constraints or an actual physically
telescoped routing schedule remain distinct possibilities.

The [protocol](../runs/20261008T084723Z-downstream-head-pivot-order/protocol.json)
and [certificate](../runs/20261008T084723Z-downstream-head-pivot-order/results/certificate.json)
retain the exact matrices and pivot pattern. Certificate SHA256 is
`2145230629a860cd7666b4dd735d996509ebbbbdae86584a1adafc1bcc83d94a`.

Both children ran sequentially under one owned worker reservation, using
the actual084300 queue chunk marker. Each took0.065 seconds and21416 KiB
peak RSS. Reproduce each protocol's source command with a fresh output;
there are no downloaded or unrecorded inputs and no accepted baseline
graph is replayed.
