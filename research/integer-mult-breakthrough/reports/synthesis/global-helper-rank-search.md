# Complete small global helper searches and Gaussian-residue exclusions

**Status: EXACT FINITE EXCLUSIONS IN THE DECLARED RANK MODEL. No general circuit lower bound or multiplication bound is claimed.**

The full-Lagrangian four-port improvement is a valid local component. These experiments ask whether it already produces a total rank deficit when arbitrary reversible gates and dirty helpers are synthesized globally. The small models do not admit such a deficit. The search includes arbitrary circuit length and all common frames, and its final extension includes every constant-coefficient invertible scalar gate over the Gaussian residue field F9.

## State, operations, and complete budget

The state contains each physical wire's Lagrangian frame and the entire current invertible scalar matrix. A scalar row is the linear combination of all independent initial data and dirty-helper columns in that wire. Scalar restoration is checked against the complete target matrix, including every helper column.

A gate chooses two physical wires and one common frame B. It pays

```text
d(L_source,B) + d(L_destination,B),
d(L,K) = n - dim(L intersect K).
```

Both wires then have frame B and an elementary scalar row addition is applied. Other wires keep their frames. Final completion charges every wire's distance to its prescribed endpoint. The full capacity is Wn, with W the complete number of physical payload wires. Full-width calls are admitted. The search tests whether any total rank charge is strictly below Wn, without imposing the historical strict-width rule.

Any single-wire moves before/between gates can be absorbed into the next chosen common frame, or final completion, without increasing cost by the triangle inequality. Thus arbitrary solo frame changes do not add missing cheaper words. Similarly, any invertible two-wire scalar gate over a finite field decomposes into row additions and nonzero row scalings while its endpoints stay at the same common frame. Their additional scalar costs are optimistically free in this rank model. Gate counts, coefficient precision, and physical movement can only add obligations to a positive discovery.

The start/end frame geometry for one data pair and one dirty helper is

```text
starts: (G_P, G_0, G_0),
ends:   (G_I, G_(I+P), G_I),
scalar target: SWAP on the data pair, identity on the dirty helper.
```

P is an idempotent coordinate projector. The n=2 cases use rank(P)=1; the broader n=3 cases use rank(P)=2. A separate four-wire case uses n=2, two orthogonal rank-one projectors, two data pairs, and scalar target diag(SWAP,SWAP), with no helper omitted from capacity. The finite frame domains are all symmetric graph frames or all Lagrangians: respectively 8/15 frames at n=2 and64/135 at n=3.

Every search prunes a state only when its accumulated charge plus the sum of distances to its physical endpoints exceeds the strict budget Wn-1. Any remaining word must pay at least those per-wire endpoint distances, so this pruning is admissible independently of its scalar program. Nonnegative rank weights and the complete finite scalar/frame state make Dijkstra or bucket enumeration exhaustive below budget. No circuit-length cutoff is used. Time/state limits are reported separately and never interpreted as exclusions.

## Binary global results

All eight GF2 models completed without a resource limit:

| Geometry | Graph states | Full-Lagrangian states | Capacity |
|---|---:|---:|---:|
| n=2, rank-one P, one dirty helper | 120 | 120 | 6 |
| n=3, rank-one P, one dirty helper | 348 | 462 | 9 |
| n=3, rank-two P, one dirty helper | 1,074 | 2,178 | 9 |
| n=2, two orthogonal data pairs | 90,036 | 100,452 | 8 |

None admits a word strictly below capacity. A matching upper bound exists: move each source to G_0, perform the three-shear data swap at that common frame, and complete every wire to its required endpoint. For one pair/helper, its rank is `rank(P)+n+(n-rank(P))+n=3n`. For the two data pairs it is 8. Thus the optimum equals capacity in these finite models.

The GF2 statement is an abstract binary scalar/rank result. Binary cancellation does not prove the corresponding claim for characteristic-zero complex circuits. The next experiment explicitly changes that scalar domain.

## Odd-field and Gaussian-dyadic residue extension

The signed scalar search includes every nonzero-coefficient elementary addition and every nonzero single-wire scalar multiplication. Over F3, the n=3 rank-two one-helper model completely excludes rank below 9, with 33,312 graph states and67,680 full-Lagrangian states.

The first F9 implementation reached its 500,000-state cap at n=2 in both domains. Those attempts are retained as **UNKNOWN**, not negative evidence. The explosion largely came from repeated free independent row scalings.

The revised engine quotients these free units exactly. Normalize every nonzero scalar row by making its first nonzero entry one. If the normalized rows are R_d and R_s, all nonzero relative coefficients in `R_d+cR_s` remain enumerated, followed by a free normalization. Different choices of current row units merely change c through another nonzero field element. Consequently this projective quotient preserves rank minima and complete reachability up to final free row scalings; the target SWAP/identity matrix can be normalized in the same way.

An independent F3 comparison verifies that the earlier 33,312 and67,680 states correspond exactly to 4,164 and8,460 projective states times `(3-1)^3=8`. The Gaussian F9 searches then complete without limits:

| Geometry over F9 | Graph projective states | Full-Lagrangian projective states | Capacity |
|---|---:|---:|---:|
| n=2, rank-one P, one dirty helper | 24,480 | 24,480 | 6 |
| n=3, rank-two P, one dirty helper | 227,790 | 463,590 | 9 |

All four exclude a strict rank deficit. The largest case finished in approximately 7.22 seconds. The explicit signed three-shear swap and free final scalar sign give the matching capacity upper bound over these fields too.

F9 is `F3[i]` with `i^2=-1`; the polynomial is irreducible because -1 is not a square in F3. Reduction modulo three maps the Gaussian-dyadic ring `Z[i,1/2]` into F9, because 2 is invertible. A scalar matrix with its inverse over that ring reduces to an invertible F9 matrix. Every local invertible two-wire residue matrix is generated by the elementary additions and units already included at its common frame.

Therefore a completed F9 exclusion also rules out constant-coefficient Gaussian-dyadic reversible scalar lifts **within the specified roles, endpoint geometry, finite frame domain, and rank model**. The forward and inverse scalar matrices must both be Gaussian-dyadic. The conclusion does not cover a coefficient ring with divisions by three, per-address scalar functions beyond the frame model, more wires/data labels, different endpoints, larger dimensions, different phase representations, nonlinear operations, or alternative recurrence normalization. No native tape or precision theorem follows from it.

That conditional lift statement also requires a coherent gauge in which the logical scalar state has constant coefficients. Residual monomial operators within one Lagrangian class must telescope into the chosen frame lifts; this certificate does not add independent same-Lagrangian per-address scalar actions to its finite constant-coefficient state. A broader residual-gauge program needs its own operator semantics and search model.

Any modular positive would require an exact characteristic-zero reconstruction; a matching modular final matrix would be insufficient. No such positive was found in these completed cases.

## Interpretation and next discriminator

Allowing nongraph common frames enlarges several explored state spaces, but the local four-port gain does not lower the complete stock-normalized cost for these small exchanges. Merely adding one dirty helper or the tested orthogonal second data pair does not integrate the gain.

The result redirects search toward genuinely different multi-role source-label geometry, a cancellation-allowing transform with many shared features, or a changed physical chronology. The coordinator's new trimmed-zeta odd-subset circuit is one such different scalar architecture. Its mathematical zero initialization, fan-out, dirty restoration and physical support/frame compiler must be charged explicitly; its cheaper scalar count is not excluded by these small exchange models.

The independent graph-completion lemma and exact local 5-versus6 witness remain valid. These finite exclusions supply a separate global test rather than retracting that component or proving a general complexity lower bound.

## Reproduction and retained provenance

All commands run from the repository root and write fresh ignored result directories:

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/dirty_helper_rank_search.py \
  --workers 4 --output research/integer-mult-breakthrough/work/synthesis/NEW-HELPER/results
python3 -B research/integer-mult-breakthrough/code/synthesis/multi_role_rank_search.py \
  --workers 4 --output research/integer-mult-breakthrough/work/synthesis/NEW-MULTI/results
python3 -B research/integer-mult-breakthrough/code/synthesis/scalar_field_rank_search.py \
  --workers 4 --max-states 500000 --output research/integer-mult-breakthrough/work/synthesis/NEW-FIELD/results
python3 -B research/integer-mult-breakthrough/code/synthesis/scalar_projective_rank_search.py \
  --workers 4 --max-states 500000 --output research/integer-mult-breakthrough/work/synthesis/NEW-PROJECTIVE/results
```

The ordinary unquotiented F9 state-limit receipts are intentionally reproduced by the third command. The fourth command establishes the completed Gaussian-residue exclusions. Reproduce the independent F3 quotient control by importing `search` from `scalar_projective_rank_search.py` and invoking `search(3,domain,3,300,500000)` for each domain; its exact projective state count must be 4,164 or8,460. All seeds are absent because these are exhaustive deterministic searches.

- [Initial helper source](../../code/synthesis/dirty_helper_rank_search.py) and [four-worker receipts](../../runs/20261008T221642Z-synthesis-dirty-helper/results/).
- [Broader multi-role source](../../code/synthesis/multi_role_rank_search.py) and [four-worker receipts](../../runs/20261008T221943Z-synthesis-multi-role/results/).
- [Odd-field source](../../code/synthesis/scalar_field_rank_search.py) and [complete F3/UNKNOWN F9 receipts](../../runs/20261008T222335Z-synthesis-scalar-field/results/).
- [Projective scalar source](../../code/synthesis/scalar_projective_rank_search.py) and [complete F9/F3-control receipts](../../runs/20261008T222534Z-synthesis-projective-field/results/).
- Independent frame linear algebra is in [lagrangian_graph_completion.py](../../code/synthesis/lagrangian_graph_completion.py). All effective source hashes and exact resource limits are recorded by the run protocols.

The original receipts remain unchanged in the corresponding timestamped ignored `work/synthesis/` directories. The separate F3 control is at `work/synthesis/20261008T222534Z-projective-F3-control/quotient-control.json`. No large explored-state dump is claimed as present; deterministic state hashes and complete counts are retained, and the full enumeration is regenerable from the sources. Only Python's standard library is needed.

The global scalar/frame synthesis, admissible pruning, modular extension, unit quotient and independent review were developed with OpenAI Codex. The abstract phase metric and endpoint question came from the complex/transfer/coordinator tracks. No external novelty, formal verification, or new kappa is claimed.
