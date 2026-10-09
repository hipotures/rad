# Paid moment and deficit loss for noncontained birth reuse

Allowing a general Grassmann frame move does not automatically make a
noncontained dirty-role reuse useful. In the proposed two-axis birth ledger
below, every such merge loses endpoint deficit. At the reference saving
`b=20/189981`, a uniform analytical bound excludes a threshold improvement
for every `2<=h<=2048`. At h=4096 the bound is no longer an obstruction and
the extremal paid ledger has a saved moment above one. That arithmetic does
not supply a legal birth/sink chronology, complete master circuit or new
exponent.

This is a new conditional cost hypothesis, not a transplant of the frozen
campaign controller or an alteration of PR127. The independent
[actual-frame review](scalable-frame-independent-review.md) establishes the
selected-width algebra needed to ask this question. Native realization,
copied-stream background, existing dirty offsets and the literal birth
response must still be bound to a complete word.

## Proposed paid ledger

Let the ambient master width be `m=h^2`, donor end-frame dimension e,
recipient birth-frame dimension s, and intersection dimension d. Assume a
complete legal word removes the donor's final width `h-e`, removes the
recipient's initial width `m-h+s`, replaces them by the actual Grassmann
move `r=e+s-2d`, and removes one physical stock unit. All scalar readout,
source/sink, native route and inverse costs must remain paid elsewhere.
Here `1<=e<h`, `0<=s<h` and
`max(0,e+s-h)<=d<=min(e-1,s)` specify a noncontained pair.

The weighted rank removed is

```text
(h-e)+(m-h+s)-(e+s-2d) = m-2(e-d).
```

Because capacity also falls by m, the endpoint deficit falls by `2(e-d)`.
For a contained merge, d=e and that loss is zero; the strict majorization
lemma applies without losing deficit. A general frame move has a different
ledger even when it is an exact one-child operator.

For `p=1-b`, define the normalized saved numerator

```text
mu = [(h-e)^p + (m-h+s)^p - (e+s-2d)^p] / m^p.
```

If the old complete stock is W and its moment is Phi, a single replicated
merge removing a paid stock units gives
`Phi_new=(W*Phi-a*mu)/(W-a)`. Starting from `Phi>=1`, threshold contraction
requires

```text
a*(mu-1) > W*(Phi-1).
```

Thus `mu<=1` cannot repair a failed target moment. A positive `mu-1` is only
an opportunity: the actual number of legal pairs and the old failed margin
must satisfy the displayed inequality. Positive endpoint deficit also
requires that the total `2a*(e-d)` loss stay below the old deficit. Physical
stock and child multiplicities must use the same paid replication units.

## Exact universal extremum

For fixed e,s, mu increases when d increases, because its subtracted width
r decreases. The largest admissible intersection is `d=min(e-1,s)`.
Put `A=h-e` and `C=s-e`.

When `C>=-1`, this gives `r=C+2` and the unnormalized numerator is
`A^p+(m-A+C)^p-(C+2)^p`. Its derivative with respect to C is negative:
`m-A+C>C+2`, and `x^(p-1)` decreases. Therefore C=-1 maximizes this class.
At C=-1, the numerator `A^p+(m-A-1)^p-1` increases in A throughout
`1<=A<=h-1`, because its second positive argument is larger than A.
Its maximum is A=h-1, or `e=1,s=0,d=0`.

When `C<-1`, write c=-C. The largest intersection is d=s, so the numerator
is `A^p+(m-A-c)^p-c^p`. It decreases with c and then is bounded by the same
c=1 class. These comparisons hold for `m=h^2`, h>=2. Hence every feasible
noncontained proper-frame pair satisfies the sharp dimensional bound

```text
mu <= mu_max(h)
   = [(h-1)^p+(h^2-h)^p-1] / (h^2)^p.
```

The maximum is attained by a donor line descending to a zero-dimensional
recipient frame. This identifies a cost extremum, not an available recipient
in a real graph. A descending cut cannot be used if its target sinks have
already advanced to incompatible actual frames unless their additional
transitions and payloads are paid.

There is a uniform small-h exclusion without any wide parameter sweep.
Concavity gives
`h^p-(h-1)^p>=p*h^-b` and
`m^p-(m-h)^p>=p*h*m^-b`. Therefore

```text
h^b * m^p * (mu_max-1)
  <= h*[1-(1-b)*h^-b] - (1-b) - h^b
  <= b*h*(log(h)+1) - (2-b).
```

The right side is increasing with h. Also
`exp(7/10)>482921/240000>2`, by its positive degree-four Taylor partial sum,
so `log(2)<7/10`. At h=2048,

```text
(2-b) - b*2048*(1+11*(7/10)) = 23590/189981 > 0.
```

This proves `mu_max<1` for every `2<=h<=2048` at the reference b. The exact
finite controls below corroborate the bound and exhibit the larger-h
opportunity; they are not the proof of the uniform statement.

## Exact interval discriminator

[noncontained_birth_budget.py](../../code/transfers/noncontained_birth_budget.py)
uses independent rational logarithm/exponential intervals and four workers.
It tests four dimensions only, with no graph generation or exhaustive large
parameter search. The
[actual-time attempt](../../runs/20261009T023924Z-transfer-noncontained-birth-budget/report.md)
passes in 0.2163 seconds.

| h | Universal mu maximum, approximately | Strict status |
|---:|---:|---|
| 24 | 0.996544450021213 | below one |
| 128 | 0.999882653327309 | below one |
| 2048 | 0.999999966090970 | below one |
| 4096 | 1.000000120212130 | above one |

At h=4096 a transverse line pair `e=s=1,d=0` also has
`mu>1`, approximately `1.000000120110094`. Its removed widths are 4095
and 16773121; its paid replacement width is two. Both this pair and the
descending extremum lose two units of endpoint deficit per physical merge.
All 287 other feasible dimensional triples at h=2 through 8 are checked by
exact outward intervals to lie strictly below the analytical maximum.

The negative control deletes the transverse pair's rank-two frame move.
The two removed widths then sum to m, so strict concavity falsely presents
an improving paid merge at every tested h, including h=24. The retained
actual replacement child eliminates that false improvement at small h.
This control is an explicit unpaid-cost counterexample, not a circuit.

The result field `threshold_crossing_possible_from_one_legal_merge` means
only that the tested saved numerator exceeds one and can satisfy the
displayed threshold inequality for a sufficiently close old moment. It
does not certify a legal merge, a complete stock reserve, a usable supplier
or an exponent. All such fields are accompanied by false circuit/native
and exponent flags.

## Research implication and reproduction

Contained reuse and exact common-frame reuse remain the useful immediate
directions for the current small-dimensional circuits. The
[degenerate finite component](degenerate-birth-independent-review.md)
demonstrates that such reuse can keep nonzero radicals and source-dependent
offsets without losing deficit. General noncontained moves should not be
added to a target search merely because an exact compiler now exists.

The large-h positive ledger is parked as a separate hypothesis. Before any
large experiment it would need a complete circuit family with available
low-frame recipients, compatible sink chronology, sufficient original
deficit and a baseline moment close enough to the target. Its ambient width
is 16,777,216 and no corresponding graph or tape program is generated here.

Reproduce from the new worktree:

```sh
python3 research/integer-mult-breakthrough/code/transfers/noncontained_birth_budget.py --workers 4
```

Bounded CI uses the same four compact tasks with `--workers 1`. The closure
is this source, its config and independent `encoding_slack.py` with its
`conditioned_frame_review.py` arithmetic import. Their exact hashes are pinned
in the config and protocol. No producer source, downloaded input, seed or
third-party package is used. Protocol and compact results are retained
unchanged; all results are deterministically regenerable.
