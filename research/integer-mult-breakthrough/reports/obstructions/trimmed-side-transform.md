# A cancellation-allowing trimmed side circuit

Status: **EXACT SCALAR CIRCUIT AND FINITE COEFFICIENT CERTIFICATES**.
Arbitrary-dirty restoration, physical frame chronology and a new exponent
remain unproved. The measured role count below belongs to a mathematical
straight-line circuit, not the native recursive motif.

## Objective and established context

The five-subset candidate needs a much cheaper even-intersection side map
than the earlier weighted-tree circuit. At h=20 its optimistic necessary
envelope allows about 31.42 local physical roles per source, whereas the
published tree uses about 103.33 scalar roles per source. These are separate
models; this investigation first measures the scalar work before attempting
the physical compiler.

Bjorklund, Husfeldt, Kaski and Koivisto's
[fast intersection transform](https://arxiv.org/abs/0809.2489v1),
15 September 2008, uses dual trimmed zeta transforms on subset down-closures.
Their earlier [trimmed Moebius inversion](https://arxiv.org/abs/0802.2834v1),
20 February 2008, establishes the relevant trimmed Yates construction.
Those algorithms are established context. The weighted specialization,
literal gate counts and compiler assessment here are independently authored;
no novelty claim is made for zeta transforms.

## Scalar identity and circuit

Let the input and output vertices be all k-subsets of an h-element ground
set, with k odd. The central kernel is

```text
f_k(t) = product over odd r<k of (t-r)/(k-r).
e_k(t) = [t=k] - f_k(t).
```

Thus e vanishes at every odd intersection, including the self entry. For k=5
its values at t=0,...,5 are `(-3/8,0,1/8,0,-3/8,0)`. Its exact Newton
coefficients are `(-3/8,3/8,-1/4,0,0,1)`, giving

```text
F(J) = sum over T containing J of x_T,
side_S = sum over J contained in S of c_|J| F(J).
```

Indeed, each source T contributes
`sum_j c_j*C(|S intersect T|,j)=e_k(|S intersect T|)`.
In particular the degree-five term is the original x_S, not another
independent center. Removing it produces the incorrect self coefficient -1.
The scalar map is exactly `identity - central`; its cancellations are essential.

Keep slots for all subsets of size at most k. Initialize the k-layer by its
inputs and the other slots by mathematical zero. For each ground bit b,
perform `z[J] += z[J union {b}]` whenever b is absent and |J|<k. Each bit is
processed once, so the result is F(J). Multiply each slot by c_|J|. Then
process the bits once more with `z[J] += z[J minus {b}]` when b is present.
The final k-layer is the side map. During either pass an update's source
has the opposite current b-bit and is not modified during that bit's stage.
The usual induction therefore applies inside the truncated domain.

The [implementation](../../code/obstructions/trimmed_side_transform.py)
omits additions from literal zero and aliases an input when its destination
is literal zero. It assigns one authored SSA role to every remaining add or
nonunit scale, and counts all input roles. These simplifications allow fan-out
and require genuinely zero initial values. They are not free operations on
arbitrary dirty payloads. Nonunit dyadic factors are counted explicitly.
Each untrimmed pass has exactly `sum_(j=1..k) j*C(h,j)` potential edges.
The receipt accounts for every edge as an add, zero-source skip or zero-target
alias; the actual arithmetic savings do not erase physical storage obligations.

## Exact results

Four workers completed eight deterministic cases in 0.269 seconds. Complete
characteristic-zero matrices were checked at (h,k)=(8,5),(10,5),(10,3),(10,7),
covering 95,440 ordered source/target coefficients. Every odd-intersection
coefficient is zero. Larger cases below count the complete authored DAG;
their matrices were not exhaustively materialized.

| h | k | Sources v | Additions | Nonunit scales | SSA roles including inputs | Roles/v |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 8 | 5 | 56 | 973 | 37 | 1066 | 19.0357 |
| 10 | 5 | 252 | 3446 | 56 | 3754 | 14.8968 |
| 12 | 5 | 792 | 9508 | 79 | 10379 | 13.1048 |
| 16 | 5 | 4368 | 45807 | 137 | 50312 | 11.5183 |
| 20 | 5 | 15504 | 151822 | 211 | 167537 | 10.8061 |
| 24 | 5 | 42504 | 399457 | 301 | 442262 | 10.4052 |
| 10 | 3 | 120 | 687 | 11 | 818 | 6.8167 |
| 10 | 7 | 120 | 5500 | 176 | 5796 | 48.3000 |

The full receipts retain exact rational ratios. The bounded
[corruption tests](../../code/obstructions/test_trimmed_side_transform.py)
alter an actual total-feature scalar gate and remove an actual output's
identity contribution; both fail the independent coefficient comparison.
They also replay every (8,5) coefficient and all edge accounting. Four tests
pass. The larger run pins the source hash and records its protocol before
execution in [the run directory](../../runs/20261008T222526Z-trimmed-side-transform/).

The transfer track's [independent scalar oracle](../transfers/trimmed-side-independent-review.md)
imports none of this source and confirms all 95,440 coefficients using its
own two-pass implementation and Newton derivation. It separately rejects the
omitted self term and shows the limitations of scattering individual features
through the old nested-frame rule. It does not validate the producer's SSA
count or a physical dirty schedule.

## Interpretation and compiler obligations

This scalar arithmetic reduction has enough margin to justify a reversible
compiler experiment. It does not establish that physical R/v is 10.81,
that doubling the count is a valid dirty wrapper, or that the complete
characteristic contracts. A fourfold overhead would already exceed the
optimistic 31.42 envelope at h=20. Such factors are screening scenarios, not
measured compiler costs.

The synthesis track notes that four scalar compute/use/uncompute/use passes
can reuse the same physical SSA slots. Their rank-event cost can change
without quadrupling R. A complete ledger must count both stored roles and
every forward/reverse child invocation instead of conflating them.

The complex track independently identified a failure of the most direct
per-output chronology: subtracting a full-span central carrier from x_S,
then forcing the side carrier into its target-orthogonal frame, adds a local
loss for every output. The frozen two-axis deficit cannot absorb that loss.
This excludes that specified materialization schedule, not a jointly shared
cancellation frontier or all reversible implementations of this scalar map.
The precise frame argument is being developed separately; it is not inferred
from the arithmetic count.

The next discriminator must share the pair-center frontier and preserve the
complete dirty source/sink map. It must retain the +x_S term, every scalar
factor, all intermediate frame changes, tape movement, copies and reversals.
Top-degree source terms have odd self labels before cancellation; declaring
them independent norm-one centers would introduce v centers and destroy the
intended deficit. General Clifford support frames may handle degenerate
intermediate spans, but they do not make a canceled rank drop free.

For any same-width recursive children, the complete row profile and a
terminating depth budget must be supplied. Exact child endpoint semantics may
bound precision better than total elementary depth, but that changed guard
also needs an independent proof. No kappa >= 1e-4 follows from this report.

## Reproduction

From the repository root, using standard-library Python and fresh output:

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/test_trimmed_side_transform.py
python3 -B research/integer-mult-breakthrough/code/obstructions/trimmed_side_transform.py \
  --workers 4 --output research/integer-mult-breakthrough/work/obstructions/NEW-RUN/results.json
```

The original full JSON remains unchanged in the ignored run workspace.
Compact receipts and a complete gzip publication retain the scientific data;
timing and clock metadata vary on regeneration. No external executable,
downloaded source modifications or private configuration are required.
