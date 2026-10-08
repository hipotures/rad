# Actual network exponent in the stopped guard

The coarse premise `s<m^5` in the accepted compact guard can be replaced
by any fixed rational `s<m^nu`, nu>=1, for the supplied complex network.
With the same E, B, C0 and stopped-depth parameter beta, the layer exponent
becomes

```
C1 = 1 + (nu-1)(1-beta) + zeta.
```

This is a sharper dependency-depth estimate. It does not change the graph,
recurrence cost, record movement or any completed finite witness. For the
accepted h28 shared complex network, the exact integer test
`s^500 < m^1921` certifies nu=1921/500=3.842. Even the simpler integer
nu=4 is valid. The refinement lowers the full-guard cutoff but is inactive
for the current exponent bottleneck; no new kappa is claimed.

## All-size coefficient-depth proof

Retain the accepted recurrence
`A(e)<=s A(e/m)+E`, with `A(e)<=8e` below `d^beta`, and s>=2.
A root e<=d has at most `(1-beta)log_m(d)+1` internal levels j.
Thus `s^j<=s d^(nu(1-beta))`. The stopped leaf has size below d^beta,
and the sum of fixed node charges is at most E s^j/(s-1). Therefore

```
A(e) <= s(8+E) d^(beta+nu(1-beta))
     <= 9B^2 d^(1+(nu-1)(1-beta)),  B=s+E.
```

An already-leaf root obeys the same bound because nu>=1. The number of
base-m pieces is at most `m(1+1/zeta)d^zeta`, exactly as in the accepted
proof. Individually processed axes and outer phases contribute at most
18d. Since the new C1 is at least one, the same fixed C0 majorizes

```
9mB^2(1+1/zeta)d^C1 + 18d.
```

The current conservative `C0=32mB^2(1+1/zeta)` passes the unchanged
integer constant inequalities. Denominator depth, coefficient magnitude,
O(p) encoding widths and rational integer-power stopping tests transfer
unchanged when `epsilon*C1<1`. The additive E has not been multiplied by
the number of address records or by a descriptor charge; new address
operations introduce no scalar coefficient arithmetic.

## Exact independent evidence

[review_sharp_guard.py](../code/review_sharp_guard.py) imports only
independent reviewer logarithm/cutoff routines. It encloses log_m(s)
with 64-term exact rational logarithms, rounds that upper bound to a
strict rational nu, and checks `s^denominator<m^numerator` using integers.
It also runs 1120 actual stopped coefficient-depth recurrences across
integer m/s choices and nu=1,3/2,2,5/2. Direct bottom-up recurrences
must equal an independent tree sum and fit the sharper one-piece bound,
including roots below the stopping threshold.

[Run 20261008T021825Z](../runs/20261008T021825Z-review-sharp-guard/)
passes the conservative and tight accepted R473026+h28 generic and
balanced rows. The complex network is the same in every row.

| Family / mode | Old guard cutoff | Integer nu=4 | Rational nu=1921/500 |
|---|---:|---:|---:|
| Generic conservative | 931 | 826 | 812 |
| Generic tight | 1033 | 917 | 901 |
| Balanced conservative | 937 | 832 | 817 |
| Balanced tight | 1033 | 917 | 901 |

These are full-guard log2(b_input) cutoffs only. The generic common
numeric cutoff can consequently fall to 901 in the tight row. The
balanced common cutoff remains dominated by its separate geometry
condition, `3*2^64`. Other eventual prime, logarithmic-absorption and
record-setup thresholds are unchanged. The measured run used
Python 3.14.4, one process, 0.06 seconds and 22,708 KiB peak RSS.

## Where the refinement could matter

For a decaying compact branch, let a and b be the bit/complex savings,
and q the strict layer saving. The leaf inequality requires
`1-beta>q/b`. With the new guard, any limiting family satisfies
`epsilon[1+(nu-1)q/b]<=1`. For the balanced family the CRT constraint
still supplies `G<=a(1-epsilon)`, while `G<=epsilon*q` and q<=a.
The candidate a/2 limit has guard headroom when `b>(nu-1)a`, improving
the previous sufficient condition b>4a. It can admit a weaker complex
primitive in an alternative family.

For the earlier unbalanced compact layout, the corresponding scoped
upper envelopes become

```
min { a/(2+a), ab/[b+(nu-1)a], b/nu }.
```

They follow by eliminating epsilon from the prefix/movement, guard/leaf
and primitive constraints. For the accepted h28 primitive, b>4a, so both
old and sharpened guards already have strict headroom at the optimal
prefix or balanced limit. Hence this refinement cannot increase the
current limiting kappa. It is useful for a smaller numeric guard cutoff
or for later alternatives whose complex saving is closer to a. It is
not a bound for every network or an unrestricted optimality result.
