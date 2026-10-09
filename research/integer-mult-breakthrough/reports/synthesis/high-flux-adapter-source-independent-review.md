# Independent source review of the alternating high-flux adapter

Status: **ACCEPTED ANALYTICAL SOURCE REVIEW OF A CONDITIONAL COMPONENT**.
No producer was imported or executed for this review, and no new numerical
measurement is reported. This review concerns the immutable adapter source
`fd636fbb77ef31d20e5a4c7fb75fef0f62854b1e95c3f548a44c07f308e97dc1`
and its declared natural scan and packed-mask premises.

For D=2^f, the requested selected-address permutation is
P(a)=a XOR [(a AND 1)(D-2)]. It is an involution. With the original low
pivot restored before the scan, the complete conjugation is P L P, where
L is the natural inclusive prefix on the selected fiber. For f=3 the
order is 0,7,2,5,4,3,6,1. Leaving that pivot in the highest position at
scan time would produce the different grouped order; the accepted source
explicitly swaps back and retains this negative control.

The physical geometry uses exactly three bands of f+4 complete K-bit
chunks. The target consists of action chunks 1 through f-1 plus an
existing terminal guard, of total width fK. The equally long companion
occupies the first f chunks of the middle band. The borrowed control is
a bit in the last guard chunk of the highest band. These ranges and the
original pivot are disjoint. Temporarily swapping pivot and control
puts the original arbitrary guard value at the low pivot, outside both
mutable ranges. The wanted mask reads only the relocated action pivot.
The final swap restores both pivot and guard. Thus the completed address
map is independent of every original guard value and fixes the complete
companion and all unselected planes. It can commute with a separately
completed guard kernel; transient borrowing does not permit dropping that
kernel or assuming the caller already has a complete rectangular row.

The eight rotation offsets may read reciprocal mutable bits, as required
by the supplied packed word. Those bits are not used to determine the
wanted mask. The last selected guard is excluded from that mask. No
unpaid highest-bit toggle is hidden in the adapter.

Let S denote the packed rotation permutation and T the wanted sparse XOR.
The admitted carry-free contract gives S=T on the safe region, and T
preserves it. Since S is a permutation, this also makes its complement B
invariant. Repair T S^-1 on B, and identity elsewhere, therefore completes
T exactly. Its inverse is S T because T is an involution. The accepted
source places that inverse repair before the reversed rotations; a second
forward repair would have the wrong chronology. Control and range values
remain available at their actual current addresses throughout.

The finite arrays replay every rotation, current-address repair and bit
swap, then invoke the literal seven-tape natural polynomial scan. The
materialized quotient includes the complete read/write set, including
all bits of the target and companion ranges. Omitted physical address
planes are an identity factor because the address word never reads or
writes them. The reference implicit-address headers frame the test; they
do not authorize changing arbitrary payload fields during a native route.
The separate headerless scan contract is the relevant native interface.
The repaired negative-control requirement correctly permits a one-active-
bit tiny cube to have S=T already, while demanding a repair counterexample
in the complete aggregate. This does not change the address program.

The report retains its conditional bill
O(V[(fK)^tau+1]+M[A^3+C_G(A)]+delta M A(R+A)),
with delta<=min(1,80(f-1)2^-K). Fixed-two-digit stream moves, complete
packed rotations, exceptional full-record sorting/repair, metadata and
shape preparation remain admitted native components. This source review
does not turn the finite array permutation into a tape-time measurement.
It does not independently prove those earlier native lemmas. All fields,
current row stock, complete guard allocation and residual target kernels
remain paid. The natural prefix needs f extra magnitude bits; permutation
wrappers add no grid or magnitude growth. Under w=Theta(p) and f<=p^epsilon
with epsilon<1, its stated record-width contract is compatible with this
standalone bill. A complete recursive precision argument, fast zeta
factorization and integer-multiplication exponent remain unproved here.

The source and report were read without mutation. This is an independent
scope/chronology check, developed with AI assistance. The producer's own
finite counts and timings remain its separately archived evidence.
