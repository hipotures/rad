# F9 payload Walsh bridge and an uncancelled recurrence negative

The exact word-XOR identity holds over the fixed payload field
F9 = F3[i], i^2 = -1, with binary addresses throughout. It does not by
itself give a faster movement recurrence. This report separates the
operator identity from a specific recursive compiler that fails its
child budget.

Let C = ((1+i)I + (1-i)X)/2 and let S(x) = i^wt(x) on an f-bit address
bank. The unnormalized Walsh operator is exactly

```
W_f = (1-i)^f S C^tensor(f) S,
W_f^2 = 2^f I.
```

Since two is nonzero in F3, all scales have inverses in F9. For a control
bank x and target bank y,

```
XOR_target = 2^-f W_target diag((-1)^(x dot y)) W_target.
```

This is the complete permutation `(x,y) -> (x,y+x)` over F2, on arbitrary
F9 payload values. It needs two C^tensor(f) calls, four S diagonals, one
bilinear sign diagonal, and fixed scalar factors. The bilinear diagonal
has the same aligned-counter form as the parent's reviewed quadratic
phase scan. That scan's paid-volume hypotheses still apply. Host vector
loops in this checker are reference operators and are not a tape
implementation.

The nine payload symbols have constant width. No address field is changed
to F9, no 9^e address bank is introduced, and no square-root extension is
needed. Intermediate payload entries can be nonbinary; the complete
operator returns the exact original payload entries at their permuted
binary addresses.

Consider the independent per-edge coordinate-basis compiler used in the
original phase construction. Each source-growth residual is the tensor
indicator of three triples, hence has coordinate weight 27. A coordinate
child alone does not give that direction. In this compiler, at least one
binary row addition is required on each of the 3N source-growth edges.
This deliberately weak count ignores inverse basis additions and all
other residual bases. If A is that row-add count, substituting the Walsh
bridge gives

```
C(e) <= ((s + 2A) / W) C(e/m) + linear phases,
A >= 3N.
```

For the independently accepted h=28 complex circuit,

```
W = 2165559937632, m = 21952,
s = 47538353720841984,
N = 35158608576, L = 26143580736,
D = W*m - s = 2N - 2L = 18030055680.
```

The additional children are already at least 210951651456, exactly
117/10 times D. The resulting count exceeds Wm by 192921595776. Its
rank-only normalized cost grows by 79098865/79098544 at each depth,
rather than contracting. Thus this uncancelled compiler does not prove
a sublinear movement exponent. The alternate complete identity
`B_word(e) <= 2 C(e) + linear phases` contains a same-size coefficient
two and is also not an inductive contraction.

These are scoped negatives. They do not rule out cancellation of adjacent
physical adapters, a common basis reused across gates, another scalar
construction, or a different coupled recurrence. Any such schedule must
preserve scalar gate chronology, arbitrary scratch, and actual child
volumes. No cancellation is assumed in the count above.

The fresh exact run passed 73 Walsh input probes with 1,103 output entries
and 116 complete controlled word-XOR probes with 7,088 output entries.
The latter include all basis vectors through f=3 and signed, nonbinary
F9 payloads. Two applications restore every tested payload. Omitting the
Walsh scalar or the S wrappers each failed on 66 discriminating probes.
The field control checked all 729 distributivity triples and all eight
nonzero reciprocals. Six exact stopped count controls confirm the
declared recurrence's growing orientation. This is separate from the
earlier F3 payload/Bruhat algebra controls.

Source: [downstream_f9_walsh_bridge.py](../code/downstream_f9_walsh_bridge.py).
Run: [20261008T034900Z-downstream-f9-walsh-bridge](../runs/20261008T034900Z-downstream-f9-walsh-bridge/).
Input: the immutable accepted R472879+h28 generic composition, whose hash
is retained in the result. No finite graph is replayed. Parent phase scan:
[quadratic_phase_counter.py](../code/quadratic_phase_counter.py).
The campaign retains start 2026-10-07T22:25:21Z, historical deadline
2026-10-08T08:25:21Z and the authorized extension to 10:00:00Z. No new
kappa, universal obstruction, or novelty claim is made.
