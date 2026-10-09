# Publication readiness after checkpoint fourteen

Assessment date: 2026-10-09 UTC. The user asked whether the campaign has
results worth publishing. The current evidence supports a reproducible
technical report and research artifact release. It does not yet support
a new integer-multiplication exponent theorem or a claim that the campaign
has crossed kappa=1e-4.

The public checkpoint is
[`c21fb0c4dfe0e90cbefceeee390e6dd2182e3732`](https://github.com/hipotures/rad/commit/c21fb0c4dfe0e90cbefceeee390e6dd2182e3732).
All 148 local registered checks passed. Its
[GitHub Actions run](https://github.com/hipotures/rad/actions/runs/37898127797)
also passed all ten jobs, including the three groups on Python3.11,3.13
and3.14. These checks verify their declared finite components and scope
controls, not unimplemented native algorithms or formal mathematics.

## Claims suitable for a technical report

| Component | Supported statement | Remaining publication boundary |
| --- | --- | --- |
| Complete Gaussian product recovery | Explicit normalization and full-array error bounds imply exact coefficient recovery; all retained finite cases pass and an independent analytical review accepts the argument. | Exact products, native transform costs and the final integer assembly must still be supplied. Literature novelty of the general stability argument is unestablished. |
| Weighted-union basis | The campaign's exact basis conversion and direct incidence comparisons are verified, with full polynomial records and temporary grids retained. | The underlying covering product is classical. A faster paid conversion or a new assembly is absent. |
| Recursive fixed-grid arithmetic | A complete-state numerical lemma handles unitary or uniformly bounded child endpoints, scalar error injection and charged projection. | The theorem is conditional on the literal state and norm contracts. Its application-specific value and novelty need further review. |
| Circuit and layout limitations | Exact counterexamples and model-specific bounds reject several proposed shortcuts, including inferring computational ancestry from endpoint zeros. | Each limitation applies to its explicit model. It is not a general multiplication or circuit lower bound. |

## Classical algebra that must receive attribution

Bjorklund, Husfeldt, Kaski and Koivisto, *Fourier meets Mobius: fast subset
convolution*, [arXiv:cs/0611101v1](https://arxiv.org/pdf/cs/0611101v1),
Section2.5, equations(15),(17), define the covering product and evaluate
it through the subset transform, pointwise multiplication and inversion.
The campaign's weighted-union product is a diagonal conjugate of that
classical product. With `c=-2i` and `S_c[f](A)=c^|A| f(A)`,

```text
m_y(f,g) = S_c^-1 ((S_c f) *_cover (S_c g)).
```

Indeed, on `A union B=S`, the diagonal factor is
`c^(|A|+|B|-|S|)=c^|A intersection B|`. This deduction explains the
relationship without treating a known transform identity as a new
discovery. The narrower candidate contribution is its fully charged
connection to the campaign's canonical product and implementation model.

## What would justify a stronger paper

A stronger result needs an actual circuit or product architecture with a
strict complete cost improvement, a lawful native implementation, a
well-founded recurrence with every error and movement charge, and an
independently reviewed transfer to integer multiplication. Its specific
claims must then be compared with primary literature. The public PR127
result remains attributed external work; reproducing it does not make its
claimed exponent a new campaign theorem.

The fresh activity and geometric-precision work is still being integrated.
In particular, the [activity moment discriminator](obstructions/activity-gate-moment-boundary.md)
shows that ordinary gate counts cannot gain merely from successful packing
in that model. A hypothetical shorter circuit is a research target.

Suggested report scope: exact certificates and integration barriers for
structural integer-multiplication mechanisms. Preserve positive components,
counterexamples, unresolved searches and explicit claim levels together.
This work and its internal reviews were produced by Codex research agents;
external sources retain their authorship, and internal model-assisted
review is not external human peer review.
