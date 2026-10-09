# Sparse color centers and complete release topologies

## A rank-five integral completion

For h=7, five-subset labels are complements of pairs. Distinct complement
pairs intersect exactly when the original labels have even intersection.
Color pairs by their smaller endpoint if it is 0,1,2,3, and put the remaining
triangle on 4,5,6 in the fifth class. The class sizes are 6,5,4,3,3. Distinct
labels within a class are binary orthogonal, and each label has odd norm.

Let G be the five-row class-incidence matrix and `K=G^T G`, so K is a block
of ones on each class. Its diagonal is one and every required distinct
odd-intersection entry is zero. A principal one-per-class minor is identity;
therefore its characteristic-zero and dyadic rank is exactly five. This is
a fitting completion for this finite family, not the polynomial pair center
of rank 21 and not a claimed minrank optimum.

For a class with pivot 0 and m members, B replaces the pivot by
`S=sum x_i` and retains the other inputs. It needs m-1 additions and is
unimodular. D also replaces each nonpivot by `z_i=x_i-S`. Its inverse is

`x_i=z_i+S` for i>0, `x_0=(2-m)S-sum_(i>0) z_i`.

Thus sum and side coordinates are available without zero-initialized banks
or an inverse of `I-K`. In fact I-K is full rank here; its class eigenvalues
include odd factors -5 and -3, so a Gaussian-dyadic inverse of I-K itself
would be unjustified. The sparse B/D words do not make that assumption.

The complex agent independently accepted the coloring, rank completion and
unimodular formulas. It also confirmed the triangle geometry: its three
original labels sum to the all-ones vector u. Every vector in its orthogonal
complement has zero norm because `w dot w=u dot w=0`. That complement is
alternating; there is no free norm-one singleton normal. General `L_E`
frames, including radicals, must be paid according to their exact interface.

## Complete sparse basis-port words

The [color compiler](../../code/synthesis/color_center_release_search.py)
uses the entire source/sink word with paid within-class middle permutations
and all inverses, not merely a quotient map. Its sum basis needs 16 scalar
additions; the side basis needs 32. Each middle permutation uses 16 real
bank swaps, each expanded into three signed shears and a sign correction.
All complete arbitrary source/sink columns and corruption controls pass.

Four worker cases compare sum/side and batched/interleaved placement. Their
192 eligible frame domain explicitly includes noncoordinate class parity
hyperplanes, their perpendiculars, coordinate subspaces and possibly
degenerate `L_E` frames. Dropping a parity hyperplane can remove many original
odd labels through one lost dimension; excluding it a priori would miss the
shared-release hypothesis. Each word has 42 actual banks and capacity 294.
The bounded many-label heuristics found no deficit. This is **not** an
exhaustive finite optimization or a universal limitation.

The completed
[sparse color run](../../runs/20261009T000748Z-synthesis-color-centers/report.md)
retains both B/D topologies separately from the earlier dense-pair-basis
negative. Its compact export locates the full unchanged word/frame receipt.

## A distinct arbitrary-dirty center echo

To change the topology, consider m mutually orthogonal source labels and one
independent arbitrary-dirty helper r. A center echo performs

`y_i-=r; r+=sum x_j; y_i+=r; r-=sum x_j`.

It adds the class sum Jx to every sink and restores r exactly. Adding
`y_i-=x_j` for every i!=j supplies `(I-J)x`, so the complete scalar map is
`y+=x`, x and r restored. There is no literal matched source/sink copy.
Every initial source, sink and helper value is independent. The physical
helper still has its paid zero-to-full endpoint, so stock is `W=2m+1`.

Three placements of the side network are tested: before the center echo,
after it, and between its gather and positive scatter. Both an arithmetic
array lookup encoding and a complete Boolean finite-distance encoding of the
SMT model timed out. **Every such result is UNKNOWN**, including the tiny
16-frame case. Their source hashes, seeds, limits and solver statistics are
retained; these are not negative finite certificates.

## Exact finite min-sum results

The [deterministic runner](../../code/synthesis/dirty_color_echo_dp.py) uses
Python to construct all anchors, distances and actual incidence graph. A
[retained C++ kernel](../../code/synthesis/frame_variable_elimination.cpp)
then exactly minimizes finite nonnegative factors by variable elimination:
collect factors incident to one gate, minimize over its complete frame label,
and retain the minimizing label for every neighboring assignment. Reverse
backtracking yields a complete word. Independent Python path replay agrees
with its exact cost. Sixteen small random factor graphs agree with independent
complete enumeration of all 64 assignments each.

| Bits | Data roles | Frame domain | Side placement | Exact minimum | W*bits |
| ---: | ---: | --- | --- | ---: | ---: |
| 2 | 2 | all 15 Lagrangians | after echo | 10 | 10 |
| 3 | 3 | all 16 L_E frames | after echo | 21 | 21 |
| 3 | 3 | all 16 L_E frames | before echo | 21 | 21 |
| 3 | 3 | all 16 L_E frames | inside echo | 21 | 21 |
| 3 | 3 | all 135 Lagrangians | inside echo | 21 | 21 |

These are exact scoped optima for the specified finite frame domains and
literal scalar chronologies. They do not exclude another word, more roles,
per-address scalar gauges or larger embedded geometry. The 16-frame results
and the later 135-frame result are separate exact experiments. The complete
[small-domain run](../../runs/20261009T002443Z-synthesis-echo-exact-small/report.md)
preserves the word, domain, ordering and independent replay.

## Completed full-domain discriminator and storage

A separate targeted side-inside experiment tests every one of the 135
three-bit Lagrangians. The same serial kernel plus a retained OpenMP patch
reconstructs its parallel source. It preflights each factor scope and retained
argmin vector, enforces an eight-GiB budget with a one-GiB reserve, and uses
four native workers. Its exact minimum is 21, equal to capacity; it took
136.223 seconds. The predicted and completed factor/decision payload agrees
at 5,353,959,600 bytes, about 4.99 GiB. The exact evaluation count is
271,374,460,110 and the maximum induced width is four. The recorded order is
`0,17,5,12,16,14,1,3,2,7,8,4,6,9,10,11,13,15`. Reverse argmin reconstruction
returns frame label zero on each of the 18 gates. Independent full path
replay has histogram `{1:3, 2:3, 3:4}`, hence charge 21.

The [full-domain run](../../runs/20261009T002747Z-synthesis-echo-exact-full/report.md)
pins the base source, OpenMP patch, generated source SHA, compiler/flags and
complete graph input SHA. The coordinator independently reviewed factor
indexing, complete label minimization, constant accumulation and reverse
reconstruction. This is computational finite evidence with source review,
not formal verification. Literal Gaussian frame operators and a native tape
word are not claimed by this metric calculation.

The retained engine parser narrows supplied integer distance/unary values to
uint16 without checking every malformed input. The successful input is
independently regenerated and validated: all costs are nonnegative integers,
the complete original-factor maximum sum is 129, and every accumulated factor
is bounded by that same sum. Its SHA matches the completed input. The new
[factor guards](../../code/synthesis/frame_factor_guards.py) reject malformed
values and a complete charge bound of 65,535 or more before invoking the
engine. They protect future reuse while preserving the exact successful
source rather than silently substituting a new binary for old evidence.

The [bounded verifier](../../code/synthesis/verify_echo_elimination.py)
compiles both retained serial and reconstructed parallel kernels, compares
each against 16 complete 64-assignment factor controls, checks two exact
small-domain words, and rejects truncation, duplicate order variables and
storage-limit violations. It also exercises negative/oversized charges and
total overflow guards, validates all 135 frames, reconstructs the full input
hash and replays its recorded witness. It does **not** repeat the large
width-four optimization.

All binaries, factor tables, graph inputs and generated parallel source live
in ignored work. They are deterministically regenerable from the retained
authored sources and patch. No compiled binary is research source. Completed
JSON evidence follows the gzip contract where row-level words are archived;
compact exports explicitly state omissions and full original identities.

## Reproduction

Use fresh ignored paths from the repository root. The two SMT runs require
the existing pinned z3-solver environment; the exact DP needs a C++17 compiler
and the Python standard library.

```bash
python3 -B research/integer-mult-breakthrough/code/synthesis/color_center_release_search.py --workers 4 --rounds 4 --frames 192 --output research/integer-mult-breakthrough/work/synthesis/<fresh-color>/results
research/integer-mult-breakthrough/work/synthesis/<pinned-solver>/bin/python -B research/integer-mult-breakthrough/code/synthesis/dirty_color_echo_smt.py --workers 4 --timeout 60 --output research/integer-mult-breakthrough/work/synthesis/<fresh-array>/results
research/integer-mult-breakthrough/work/synthesis/<pinned-solver>/bin/python -B research/integer-mult-breakthrough/code/synthesis/dirty_color_echo_bool_smt.py --workers 4 --timeout 60 --output research/integer-mult-breakthrough/work/synthesis/<fresh-boolean>/results
python3 -B research/integer-mult-breakthrough/code/synthesis/dirty_color_echo_dp.py --workers 4 --output research/integer-mult-breakthrough/work/synthesis/<fresh-exact>/results
python3 -B research/integer-mult-breakthrough/code/synthesis/dirty_color_echo_full_dp.py --threads 4 --memory-budget-GiB 8 --output research/integer-mult-breakthrough/work/synthesis/<fresh-full>/results
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_echo_elimination.py
```

The mathematical value is the distinction between a cheap rank-five scalar
completion, no deficit in several complete supplied words, and the still
separate native circuit obligation. No kappa is asserted.
