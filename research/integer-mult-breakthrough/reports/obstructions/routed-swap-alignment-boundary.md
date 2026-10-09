# Routed signed SWAP: alignment restores a full-rank interface

The question is whether coordinate routing can turn the previously proposed
framed signed SWAP into a canonical transform while retaining a smaller child
at the source-to-sink interface. It can correct the data end map, but this
particular routed interface has full support and loses the two-direction
saving. This is a limitation of a single-child implementation with monomial
and diagonal wrappers, not a lower bound for general circuits.

## Exact identities and scope

Write `F=C_h`, and let `A_U=C_line(U)` and `A_T=C_line(T)` be the actual
Gaussian line operators for odd labels. Let `P` permute address coordinates,
with `P U=T`. The line operators obey

```text
P A_U^-1 = A_T^-1 P,
A_T^2 = X_T,
F P = P F,
F A_T^-1 P A_U^-1 = F X_T P.
```

Here `X_T` is the address translation by `T`, applied independently to each
selected column. The last equality follows by substitution and
`A_T^-2=X_T`. It does not require an asymptotic assumption or a scalar
approximation. Coordinate permutations and translations are retained as
explicit operations; their native cost is not asserted to be zero.

For orthogonal odd labels `U,T`, the unrouted relative
`F A_T^-1 A_U^-1` has selected mixing rank `h-2`. Its binary mixing block is
`I+U U^t+T T^t`, with kernel exactly `span(U,T)`. On `f` independent selected
columns every matrix column has `2^((h-2) f)` nonzero entries. The routed
relative equals `F X_T P`; every column has `2^(h f)` nonzero entries because
all coefficients of the full tensor transform are nonzero. Thus the routed
relative has selected mixing rank `h`.

Invertible monomial or diagonal wrappers preserve the number of nonzero
entries in each matrix column. Therefore this routed relative cannot consist
of one `C_(h-2)` child acting on the same selected columns, with only such
wrappers and untouched spectators. This does not rule out multiple children,
shared paths, dirty-register birth reuse, nonunitary intermediates, different
stock accounting, or arbitrary circuits. Full support by itself is not an
asymptotic native time lower bound.

## Canonical data end map

Take initial data frames `diag(A_U,I)` and final frames
`diag(F,F A_T^-1)`. The routed virtual signed SWAP is

```text
S_P = [[0, P^-1], [-P, 0]].
```

Its physical data end map is

```text
F * [[0, P^-1], [-X_T P, 0]].
```

Postprocess its two outputs by `P` on the upper bank and `-P^-1 X_T` on the
lower bank, then exchange the raw bank labels. The result is `F` on both
original inputs. These explicit monomial corrections establish the two-bank
algebra only. No helper chronology or complete canonical native circuit is
supplied here.

The matching virtual router is essential. Omitting it from the lower block
while keeping the monomial corrections fails on actual physical input
columns. The result also avoids an invalid endpoint inference: obtaining the
right data end map does not certify a cheap decomposition of every internal
relative operator.

## Finite evidence and provenance

The [checker](../../code/obstructions/routed_swap_alignment.py) uses exact
Gaussian dyadic arithmetic and previously published literal line/full
operators. Four workers checked four complete cases:

| Selected width | Source/sink labels | Selected columns | Full pair columns |
| --- | --- | --- | --- |
| 3 | 1 / 4 | 1 | 16 |
| 3 | 1 / 4 | 2 | 128 |
| 4 | 1 / 8 | 1 | 32 |
| 4 | 7 / 14 | 1 | 32 |

All 208 complete pair columns passed, together with every routed and
unrouted interface coefficient, exact support counts, commutation with the
full transform and the unmatched-router failure control. The two-column case
tests translations on both columns rather than treating one scalar phase or
one address translation as the entire tensor operator.

Source SHA-256 is
`215a9d1b84df93c01ac1cd2b09c4475d3b2f388616fa9bfd0f85cbeab3285af5`.
The [run receipt](../../runs/20261009T023046Z-routed-swap-alignment/report.md)
records all five effective source hashes. The ignored raw directory was
allocated with label `20261009T023103Z`; the actual protocol start was
`2026-10-09T02:30:46.327263+00:00`. The durable run uses the actual start and
records the raw label as an allocation alias. Original logs and JSON bytes
remain unchanged.

Reproduce one complete width-four case using Python's standard library:

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/routed_swap_alignment.py --workers 1 --bounded
```

Omit `--bounded` for the four discovery cases. Optional `--output` must name
a fresh directory. Source hashes are checked again after execution. The
result is an exact finite certificate plus an elementary operator identity;
it is not a formal verification package, a complete multiplier construction,
or evidence of a larger campaign kappa.

The next useful direction is joint helper lifecycles across the three bodies
of a signed SWAP. Such a word must bind actual frames, chronological
birth-response subtraction, dirty restoration and the whole native stock.
