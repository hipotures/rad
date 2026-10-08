# Bit-vector XOR model: explicit control passes, searches time out

The pinned 20-gate cancellation-free circuit satisfies the unrestricted
QF_BV model and independently replays every input/target column in 0.06 s.
The 19-gate unrestricted, no-outside-cone and cancellation-free searches
return UNKNOWN after 180 s each. Those statuses do not supply optimum or
negative certificates. The elementary restricted-family lower bound below
is mathematical reasoning rather than an interpretation of timeout.

Every target is the sum of the three edges of a K5 triangle. Any two distinct
target triangles share at most one source edge. Under a no-outside-cone
restriction, every shared signal's entire source ancestry must belong to the
intersection of all target supports using it. Therefore every signal shared
by two targets is either zero or a single input. Each three-input target needs
at least two binary XOR gates. Nontrivial gates cannot be shared, so at least
20 gates are necessary. A 20-gate cancellation-free word attains the bound.
Cancellation-free circuits obey the same ancestry restriction, so their
optimum is also 20. Unrestricted cancellation circuits remain outside this
proof and unresolved by these solver attempts.

Source [xor_smt_probe_v2.py](../../code/synthesis/xor_smt_probe_v2.py) imports
[xor_smt_probe.py](../../code/synthesis/xor_smt_probe.py); both hashes and all
solver parameters are retained in [protocol](results/protocol.json). Literal
control gates, exact source/target replay, solver statistics and SMT2 input
hashes are in the result receipts. This is an auxiliary straight-line circuit
result; dirty reversible implementations, physical frames and transfer are
not inferred from it.

Reproduce in a fresh ignored environment with
`configs/synthesis/solver-requirements.txt`, then run the v2 source with
`--workers 4 --output <fresh ignored directory>`. The optional Z3 wheel's
SHA-256 and download provenance are in
`configs/synthesis/solver-provenance.json`. No solver binary is committed.
