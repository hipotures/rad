# A conditional obstruction to closed materialized side outputs

## Model and conclusion

Let v source banks be transformed by a scalar central matrix K of rank at most
q. Suppose the center component, with every required endpoint, has rank charge
Wh-2v+2qh. A separate scalar side implements I-K through d materialized linear
channels. Each side channel is computed in the actual full frame, visits a
proper sink-compatible frame, and returns to full before cleanup. Other costs
are nonnegative. These are defining premises of this model.

W denotes the total paid physical stock of the combined architecture, with
the prescribed endpoints on every bank. Reusing center helpers does not create
an additional bank charge. If the side needs extra banks, their complete dirty
endpoints and corresponding h contribution must be included in both the real
charge and its baseline. Merely allocating banks to enlarge Wh is invalid.

Even optimal linear compression of the side cannot produce a rank deficit in
this model. The complete charge is at least

```text
Wh - 2v + 2qh + 2d
 >= Wh - 2v + 2qh + 2(v-q)
  = Wh + 2q(h-1).
```

For h>=2 and a nonzero center, this exceeds the baseline Wh. This is a
conditional obstruction to this particular separate-output architecture,
not a lower bound on general reversible circuits or integer multiplication.

## Proof and necessary premises

Factor the scalar side map through its d channel values. Its rank is at most
d, while identity=K+(I-K) implies

```text
v <= rank(K)+rank(I-K) <= q+d.
```

This rank statement holds over any field. The experiment checks rational
matrices directly; it does not reduce Gaussian-dyadic data modulo two.

For one closed helper excursion, the Lagrangian distance from full to any
proper frame is at least one. Its return costs at least one more by the same
metric. Thus d such materialized channels cost at least 2d. The conclusion
adds these fees to the stated center component's already complete endpoint
charge. It grants no free basis conversion, normalization or dirty cleanup.
All scalar factors must use the same actual address operators where required.

The bound uses the physical side channels of this architecture, rather than
adding an independent penalty for each output target. Allowing joint center
and side fields, side values on direct source-to-sink geodesics, open helper
endpoints, address-dependent mixtures or an entirely different central word
can invalidate its premises. Those are prospective escapes, not exclusions.
For multiple columns, the displayed per-column accounting requires the same
separable frame/child implementation; a general stronger tensor-copy bound
does not follow from this lemma.

## Exact controls and leverage

The [import-free checker](../../code/obstructions/materialized_side_release_bound.py)
forms complete rational odd-slice matrices for h9/k3 and h8/k5, computes both
ranks by exact elimination, and assesses their best compressed closed-output
charges. It also tests a center-profitable 64-bank rank-three projector at h7:
the center alone has deficit 86, but its 61-dimensional side needs at least 122
closed charge, leaving excess 36. This exact example makes the obstruction
relevant even when the center alone has substantial positive saving.

Twenty-four small projection cases attain the lower bound exactly, and a
nonprojector nilpotent example checks that equality is not assumed. Losing the
identity term is an explicit negative control. These finite tests support the
implementation and illustrate the analytical proof; they are not its all-size
formal verification. The experiment has no random seeds or solver dependency.

The immediate research consequence is to avoid a large sweep of separately
materialized side bases. A useful replacement must remove a named premise,
for example by intertwining side extraction with source/sink geodesics or by
finding a complete joint center/side chronology. A lower role count alone is
insufficient in this model.

## Reproduction

Python's standard library is sufficient. Use a fresh output directory:

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/materialized_side_release_bound.py --workers 4 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/materialized-side
python3 -B research/integer-mult-breakthrough/code/obstructions/materialized_side_release_bound.py --workers 1 --bounded
```

The source and this report were developed with OpenAI Codex assistance.
Independent analytical review and complete native alternatives remain separate.
