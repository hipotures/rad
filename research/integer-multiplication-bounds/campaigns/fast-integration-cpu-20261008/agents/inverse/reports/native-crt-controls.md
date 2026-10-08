# Independent native controls of the complete guarded CRT

These controls reimplement the finite Python address/payload compiler in
C++17. They evaluate every ordinary rotation and temporary-field swap inside
the raw masked F_u, extract actual bad records, compute their keys using the
literal reverse program, and run stable binary radix passes. Inner repairs
finish before conditional reflections consume their restored fields. Outer
repairs finish before joint occupied-slot scans consume zero padding.

This is an independent finite implementation, not an implementation or timing
measurement of the all-size fixed-tape integer multiplier. Named-bit gathers
are evaluated as conjugated address functions. Their all-size tape charge is
supplied by the separately reviewed routing contract. Reported times compare
validation implementations only and support no multiplication exponent.

The authored source is [compiled_crt_native.cpp](../code/compiled_crt_native.cpp).
Source snapshots, g++ identity, exact flags and compact certificates are
retained in each fresh run. All binary executables and full progress logs
remain under ignored work/inverse/. Every native job uses one CPU and one
native thread. The queue replaces one assigned Python slot while it runs;
it automatically resumes that owned Python job at completion.

## Complete positive cases

Every case starts with scalar provenance k+1 for 0<=k<S and explicit zero
padding at all other addresses. It checks the complete triangular-CRT oracle
leaf_i=P_i^-1*k mod s_i, with P_i the product of preceding primes. It then
executes the entire reverse event program and recovers every scalar tag and
padding zero. All scratch bits come from existing inactive node coordinates.
No address bit or clean bank is appended.

| Run suffix | T / S | Changed mechanism | Completed evidence |
|---|---|---|---|
| `1526Z-native-reference` four |4096 /1155 | Independent implementation of the Python four-prime tree |113 events; complete forward/inverse PASS;0.16s |
| `1526Z-native-reference` bank leaf |131072 /19635 | Actual two-node batch with original17 bank |198 events;14,608 wrong outer records repaired; complete forward/inverse PASS;10.59s |
| `1530Z-native-inner2-three` |16384 /3855 | TWO-bit inner dirty digits, including nonzero good digits, on(3,5,257) |52 events;18 actual F_u calls/180 rotations; PASS;0.28s |
| `1530Z-native-inner2-two-nodes` |1048576 /151305 | Two-bit INNER F_u digits inside the full simultaneous-node program |198 events;84 F_u/840 rotations;118,322 wrong outer records repaired; PASS;72.83s |
| `1530Z-native-outer2-two-nodes` |1048576 /151305 | Two-bit OUTER predicate/guard digits and all-ones carry boundaries |198 events;84 F_u/840 rotations;104,216 wrong outer records repaired; PASS;73.82s |
| `1530Z-native-six-balanced` |2097152 /255255 | Full balanced six-prime tree with real two-node late batch |307 events;132 F_u/1320 rotations;270 forward/inverse radix repairs;187,967 wrong outer records repaired; PASS;265.23s |
| `1540Z-native-inner2outer2-two-nodes` |4194304 /601755 | Two-bit INNER and OUTER digits together, with ten original bank bits |198 events;317,908 wrong outer records repaired; full forward/inverse PASS;265.76s |

All complete run IDs have the prefix 20261008T. The reference bank-leaf case
exactly matches the independent Python result's 198 events and 14,608 wrong
pre-repair records. The same case additionally counts 3,992 NONZERO payloads
at invalid addresses immediately before outer repair. These return to valid
addresses when the full repair finishes.

The larger inner-G2, outer-G2 and six-prime cases count respectively 32,338,
42,632 and 57,005 nonzero invalid intermediate records. These counts concern
the actual tagged input and its zeros; they are not uniform guard-failure
probabilities or asymptotic sparse-volume estimates. They give direct
counterexamples to premature padding deletion.
The combined inner-G2/outer-G2 case similarly restores 69,460 such records.

## Mandatory-repair negatives

The source has two explicit omission controls. Both use the complete
(3,5,7,11,17) physical cube with T=131072 and S=19635.

- `20261008T1530Z-native-missing-inner-repair` omits the actual inner F_u
  bad-hole repair. The later outer inverse-key repair escapes its marked bad
  set at physical address 20488. This falsifies using the outer repair as a
  substitute for completed inner exact shears. The first failure is retained
  in its certificate; execution stopped at that assertion after 0.74 s.
- `20261008T1530Z-native-missing-outer-repair` keeps the exact inner shears,
  but omits the final three-reflection outer repair. The completed node
  fails its modular-rotation oracle after 2.86 s. Padding must not be consumed
  at that boundary.

Both are recorded as EXPECTED_NEGATIVE rather than positive verification.
Their event/call counters are zero because the complete run function returns
those counters ONLY after full forward/inverse success. Those zero fields
must not be read as claims that no partial program executed. Their actual
allocated shapes, first failure, run flags and raw progress logs are retained.

## Reproduction

Use the exact run's source snapshot for byte-level reproduction. From the
repository root, choose a fresh ignored output directory and run:

```sh
mkdir -p research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/work/inverse/reproduce-native-inner2
g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic \
  research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/inverse/runs/20261008T1530Z-native-inner2-two-nodes/code/compiled_crt_native.cpp \
  -o research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/work/inverse/reproduce-native-inner2/control
research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/work/inverse/reproduce-native-inner2/control \
  --family guard2-bank --outer-guard 1 --inner-guard 2 \
  --output research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/work/inverse/reproduce-native-inner2/certificate.json
```

Replace the family/guard flags with the corresponding retained protocol to reproduce
the other cases. Add --omit-inner-repair or --omit-outer-repair for the two
negative cases, which must report EXPECTED_NEGATIVE.

The fresh wider source
[compiled_crt_native_wide.cpp](../code/compiled_crt_native_wide.cpp) adds a
combined inner-G2/outer-G2 bank and an outer-G3 bank. The combined case passes
as retained above. The full outer-G3 cube has an explicit running protocol
under 20261008T1540Z-native-outer3-two-nodes and is not yet completed evidence
in this report.
