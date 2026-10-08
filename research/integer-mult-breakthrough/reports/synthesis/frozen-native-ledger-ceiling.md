# A favorable native ledger still cannot reach kappa = 1e-3

**Status: CONDITIONAL RESULT / EXACT RATIONAL CERTIFICATE. This is a necessary bound for the frozen 23-by-25 child ledger, not a general multiplication lower bound.**

Reducing scalar banks has enough hypothetical leverage for the first 1e-4 checkpoint. It does not offer an unlimited path to larger exponents while the old data, endpoint, growth and exterior distributions are retained. A favorable relaxation gives a rigorous ceiling even if every bank role is removed.

## Retained assumptions

Let h range over 23 and 25, m=575, N=binomial(23,3)*binomial(25,3), and let c_h=N/binomial(h,3) be the number of copied axis controllers. Let R_h be an arbitrary nonnegative bank-role count. The frozen capacity is

    W = 2N + c_23 R_23 + c_25 R_25.

Retain the historical data/endpoint children of ranks 1,21,17,481 with multiplicities 19N,2N,2N,2N respectively. Retain each axis's growth children of ranks 1 and h-2, with 2N copies each. Retain each axis's exterior children of ranks h and m-2h with c_h R_h copies each. Finally assume the internal axis profile has rank mass hR_h+h(h-1), and all its children have rank at most h. These are the only ledger facts used.

For saving a>0, every internal child of rank t<=h obeys

    t*(m/t)^a >= t*(m/h)^a.

Therefore replace the entire internal profile by R_h+h-1 children of rank h. This lowers or preserves the native moment. It is more favorable than the first sensitivity experiment's loss singletons and does not claim an implemented physical histogram.

## Role-independent exclusion

Write C(a) for the relaxed unnormalized rank moment with R_23=R_25=0, and let

    D_h(a) = 2h*(m/h)^a + (m-2h)*(m/(m-2h))^a.

The relaxed moment for arbitrary role counts is

    [C(a)+c_23 R_23 D_23(a)+c_25 R_25 D_25(a)]
    / [m*(2N+c_23 R_23+c_25 R_25)].

For every a>0, D_h(a)>m. Hence whenever C(a)>2Nm, every nonnegative choice of roles also has moment greater than one. No circuit improvement within the retained ledger can repair that failure.

The exact zero-role characteristic root lies strictly between

    0.000523483548 and 0.000523483549.

The upper endpoint has a rational lower moment strictly above one; the lower endpoint has a rational upper moment strictly below one. Each logarithm uses an atanh-series interval and each exponential a proved positive-tail enclosure. The certificate stores the full rational endpoint bounds.

Consequently every contracting native network satisfying the retained assumptions has

    a < 523483549/10^12.

If it also retains kappa<a/(1+a), it necessarily has

    kappa < 523483549/1000523483549,

approximately 5.23210e-4. The exact a=1/999 required by kappa>=1e-3 is excluded even after deleting every bank role. Other assembly inequalities can impose stricter limits; this is a favorable ceiling, not an achievable exponent. A path to 1e-3 must change at least one retained data/boundary/exterior/growth or transfer assumption, with a new derived cost ledger.

## Complete scalar center-output check

The follow-up auxiliary word includes all h center-total sinks omitted by the first ordinary-side discriminator. The full separate-side source/sink map uses

    slots = 4*binomial(h,3)+2h+binomial(h,2),
    paid CNOTs = 33*binomial(h,3)+2h.

The summed-side map with h center outputs uses 2*binomial(h,3)+2h slots and 13*binomial(h,3)+2h CNOTs. It changes the ordinary side-port boundary semantics. Both exact words preserve every source and arbitrarily dirty scratch column and update independent arbitrary output columns. Removing a center echo is rejected. Full map replay was exercised at h=6,7,23,25.

These are complete auxiliary scalar statements. The smaller slot counts cannot be substituted for physical bank counts before frames, paid transitions, causal payload access and boundary decoding are implemented. The hyperplane obstruction in the [first report](global-incidence-first-discriminators.md) still applies to the naive same-carrier port replacement.

## Reproduction and scope

From the repository root:

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/frozen_ledger_bound.py \
  --output research/integer-mult-breakthrough/work/synthesis/NEW-RUN/results
```

Source: [frozen_ledger_bound.py](../../code/synthesis/frozen_ledger_bound.py); it imports the first discriminator's exact scalar and logarithm routines. [Results and source hashes](../../runs/20261008T211335Z-synthesis-frozen-ledger-center-map/results/) bind every dependency. The tested single-process deterministic run completed in approximately six seconds and needs only standard-library Python.

Ledger provenance: the read-only PR58/PR48 controller reconstructed in RaD checkpoint def95e9c12f62a41fc7a50af13d5dcc87ce13d79 at joint-frame/agents/scout/code/check_joint_moment.py. The strict zero-role relaxation, analytic role-independent bound and complete-center auxiliary replay were authored with OpenAI Codex. This is mathematical reasoning with exact finite interval checks, not formal verification or external peer review.
