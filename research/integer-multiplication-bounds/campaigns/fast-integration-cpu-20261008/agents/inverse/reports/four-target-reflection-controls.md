# Four simultaneous reflection controls and a necessary bank exclusion

These controls extend the completed native CRT checks from two simultaneous
nodes to four independent target words. They use actual raw F_u rotations,
temporary field swaps, completed inner repairs and outer inverse-key radix
repairs. They share one fixed left source BIT across every offset. The target
moduli need not be coprime: this isolates the reflection lemma from CRT prime
supply. It is a finite full-payload validation, not a fixed-tape timing or
integer-multiplication exponent measurement.

The authored source is
[compiled_reflection_four.cpp](../code/compiled_reflection_four.cpp), including
the retained native implementation. Every run snapshots both C++ files,
the controller, hashes, compiler identity, flags and input generator. A
positive case tags each valid physical address a with a+1 and puts explicit
zero at all invalid target addresses; its original bank ranges over every
bit pattern. No address bit is appended. The independent oracle uses the
shared source BIT c: c=1 decrements each valid target digit, with zero wrapping
to modulus-1; c=0 fixes targets. Invalid digits are fixed in either case.
The full reverse event program must recover every tag and padding zero.

## Completed positive case

[20261008T1620Z-reflection-four-mixed-G1](../runs/20261008T1620Z-reflection-four-mixed-G1/protocol.json)
uses target moduli (2,3,4,5), one-bit inner/outer guards and eight original bank
bits. Its complete T=131072 cube contains 61,440 valid tagged records. It
passes the independent decrement oracle and the complete reverse program:

- 109 events; 48 actual F_u calls and 480 ordinary rotations;
- 98 actual forward/inverse radix repairs over 11,271,168 summed records;
- 51,594 wrong outer records restored;
- 12,920 nonzero payloads at invalid addresses before outer repair restored;
- 6.89 seconds in this finite native validator, using one CPU/thread.

The counts and runtime concern this finite program and its tagged input.
They are not asymptotic guard probabilities, sparse-volume proofs or evidence
for a multiplication exponent.

## Deliberate fixed-control bank violation

[20261008T1620Z-reflection-four-source-bank-negative](../runs/20261008T1620Z-reflection-four-source-bank-negative/protocol.json)
replaces the first legal bank bit by the fixed source BIT c. Thus c becomes
U[0] while still controlling every reflection endpoint. The raw program fails
with `nonbijective native map at 1` after 0.91 seconds.

This has an exact two-state explanation. In the phase interval [0,f_i), take
all target digits zero, f_i=(s_i-1)c and U=(c,0,0,0). Every modulus exceeds 1,
so the four interval predicates equal c. With one-bit digits, the packed U
load is

```
c=0:  U'=0+0 =0 mod16,
c=1:  U'=1+15=0 mod16.
```

The preceding conditional reflection also fixes these current addresses:
only U[0] can be nonzero and the first interval is [0,1), whose zero is fixed.
All other targets and physical bits agree. The two physical addresses 0 and 1
therefore collide. This is a counterexample to borrowing an endpoint control
as its own predicate register, not a failure of the legal bank construction.
The all-size CRT lemma selects banks from inactive node groups, excluding
all active left endpoint controls, and satisfies that necessary condition.

The original certificate is retained unchanged with status FAIL. The run was
predeclared as a negative, but the native exception classifier only recognized
repair/oracle errors and did not classify a nonbijective ordinary map as
EXPECTED_NEGATIVE. Its expected_matched=false and queue halt are preserved.
The mathematical negative interpretation is stated here rather than rewriting
that raw result. Zero event/call counters in the failed certificate mean that
the complete success-return object was never produced; they do not mean no
partial program ran.

## Remaining distinct cases and recovery

The original queue restored its positively identified owned Python worker
when the classification mismatch stopped it. A fresh retained continuation
controller skips both completed results without rerunning them and executes
only the previously queued legal cases: mixed targets with inner-G2, unequal
odd targets (3,5,7,11), and mixed targets with inner/outer-G2 together. These
are running/queued until their own certificates are completed. The controller
uses one replacement compute slot and resumes the paused worker in finally.

To reproduce a complete case, use its frozen code directory. Compile
compiled_reflection_four.cpp with both retained C++ files in that directory:

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic <run>/code/compiled_reflection_four.cpp -o <ignored-work>/control
<ignored-work>/control --family mixed-small --outer-guard 1 --inner-guard 1 --output <fresh-ignored-work>/certificate.json
```

Add --borrow-left-control to reproduce the source-bank counterexample;
the original implementation must retain FAIL and its nonbijectivity error.
Use the exact other protocol's flags for its guard or modulus family. Source
hashes, raw paths, actual child PIDs and completion times are in the protocols;
PIDs are provenance, never authority to control a later live process.
