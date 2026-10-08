# First SMT XOR model: all four attempts timed out

Four independent single-thread Z3 5.1.0 jobs searched the five-vertex
pair-exclusion map. The unrestricted, no-outside-cone and cancellation-free
19-gate tasks, and an unrestricted 20-gate control, all returned UNKNOWN
with timeout after 90 seconds. No negative optimality certificate, finite
improvement or exponent conclusion follows. The 20-gate map has a known
explicit word, so its timeout identifies an inefficient search encoding.

The authored [model](../../code/synthesis/xor_smt_probe.py) and complete result
receipts preserve selectors, constraints, seeds, solver version, source hash,
SMT2 input hashes and solver statistics. SMT2 files remain in the ignored
execution root and are deterministically regenerable from source/config.
The follow-up QF_BV model uses bit-vector parent selectors, useful-cone
strengthening and a pinned exact control. Its attempt receives a separate
run ID, source and outputs.
