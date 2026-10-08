# Complete actual fixed geometry for new reversed dimensions

The eligible pinned PR40 already contains James Chang's parameterized reversed `(h,h+2)` permutations and universal incidence cuts. The original fixed-basis specialization proves actual nonvanishing only at `(23,25)`. This campaign extends that finite actual I+J pair check to new dimensions while preserving the inherited geometric proof obligations. It does not infer a physical controller from the rank-mass identity.

[fixed_geometry_family.py](code/fixed_geometry_family.py) is the complete serial reproduction wrapper. It pins the eligible source inputs in [the protocol](fixed-geometry-protocol.json), retains their author attribution and Apache-2.0 provenance, and records generated source, compiler command, executable identity and real UTC times for each distinct dimension. Generated source and native executables remain ignored.

The completed controls are:

| Dimensions | Actual triple pairs | Nonzero prefixes | Data profile |
|---|---:|---:|---|
| `(8,10)` | 6,720 | 114,240 | nine singletons; `6,2,46` |
| `(10,12)` | 26,400 | 554,400 | nine singletons; `8,4,78` |
| `(24,26)` | 5,262,400 | 257,857,600 | nine singletons; `22,18,526` |
| `(26,28)` | 8,517,600 | 451,432,800 | nine singletons; `24,20,622` |

The `(24,26)` run retained 18 primary-prime zero events and `(26,28)` retained44; each affected pair was completely replayed at another admissible prime. All pairs obtained a full nonzero prescribed-pivot sequence; no unresolved pair was omitted. Both full new-dimension runs are complete.

## Fixed basis and exact corner matrix

Let `a=h`, `b=h+2`, `m=ab`, `d=a+b−1`. The common basis is the inherited controlled permutation applied to `(I_a+J_a) tensor (I_b+J_b)`. A source triple indicator `t` gives the conjugated rank-one projector `v nu`, where

`v=t+3*1`, `nu=(t−10/[3(h+1)]*1)^T/2`.

The products of matching primal/dual coordinates are `(6h−14)/(3(h+1))` inside the triple and `−5/(h+1)` outside it. They are nonzero and sum to one over the coordinates. Thus every actual source line has nonzero entries, without a generic-factor assumption.

The first-d row labels are `[0,...,h−1,h−1,0,...,h−1]`; last-d inverse-column labels are `[0,...,h−1,0,0,...,h−1]`. Their residue shift is three modulo `b`. The inherited completion gives one actual permutation in each residue field and two boundary trees. For actual triple lines `P=p xi`, `Q=v nu`, nonzero diagonal scaling turns the null corner into

`M_ij = [R_i=C_j]/(p_Ri xi_Ri) + [beta_i=gamma_j]/(v_betai nu_betai) −1`.

The data projector `(I−P) tensor (I−Q)` has the negative of this off-diagonal corner. The sign preserves ordered pivots and run widths.

## Universal zero proof and complete nonzero proof

The source integer incidence cuts are checked at each new dimension. Writing the corner as `F diag(weights) G^T`, a prescribed partition bounds the rank of every relevant northeast submatrix by the number of already selected right-hand pivots. Consequently every unselected column to the right of the next prescribed pivot is zero after elimination. These are algebraic identities for arbitrary weights; modular regression checks do not substitute for that proof.

Nonvanishing is a separate complete finite certificate. The native verifier enumerates the Cartesian product of EVERY left and right source triple. At a prime admissible for every displayed rational factor, it initializes the actual matrix and executes the entire prescribed-pivot elimination. If a pivot vanishes modulo the primary prime, it discards that elimination and reinitializes the complete matrix at an alternate prime. A successful complete replay proves the corresponding rational prefix minors nonzero. A primary zero alone is not a rational-zero certificate. Every unresolved pair fails the run.

The three primes are `1000003`, `2147483647`, `1000000007`, with explicit trial-division primality checks. Dimension-dependent numerator/denominator factors replace the old23/25 list. Initialization and field products use signed64-bit intermediates, including the alternate31-bit prime. This proof uses the one-sided implication from a nonzero field residue to a nonzero rational minor, so it needs no CRT determinant magnitude bound. Incidence cuts continue to establish all rational zeros independently.

[geometry_rational_controls.py](code/geometry_rational_controls.py) independently replays ALL62 preserved unlucky-prime pairs over exact rational arithmetic. [Its completed receipt](fixed-geometry-rational-controls.json) confirms every prescribed rightmost pivot is nonzero, the reported first primary-zero pivot is an exact nonzero fraction whose numerator vanishes modulo1000003 with admissible denominator, and every pivot in its complete alternate-prime replay remains admissible and nonzero. These are distinct exact controls; the complete Cartesian nonvanishing proof is still supplied by the all-pair native certificates.

The corner's increasing pivot runs are nine singletons plus `h−2` and `h−6`. The remaining middle is an exact identity block of width `m−2d`. Indeed, if the null projector is `U V^T`, the invertible first-d/last-d corner makes `U_first` and `V_last` invertible. Eliminating that corner in `I−U V^T` cancels the null term on the middle coordinates and leaves their identity. The projection rank `m−d` exhausts the remaining pivots. This proves the full data profile, not only its mass.

## Local, auxiliary, copied and growth interfaces

Actual completed-permutation indices are checked exhaustively. The first-a/last-a transfer has diagonal source scales at second-factor indices `i` and `j+2`. The first-b/last-b transfer uses first-factor lists `[0,...,a−1,a−1,0]` and `[a−1,0,0,...,a−1]`. These entry identities hold for arbitrary local matrices; the nonzero source scales preserve every separately certified fixed internal profile. Identity local matrices give the unchanged invertible auxiliary fronts. Their complement projectors similarly give exterior widths `h` and `m−2h`.

For EVERY copied center at both dimensions, the wrapper checks exact primal/dual formulas, unit pairing, all nonzero coordinates and the retained-total orthogonality relation. A corank-one growth matrix `I−v nu` has nonzero first extreme pivot `−v_0 nu_last`; its central Schur block is identity, and its last residue is zero by `nu v=1`. Thus each growth front has profile `[1,h−2]`. The copied read itself has rank one. These are checked exact interfaces, distinct from the internal full five-prime producer profiles.

## Recovery and scope

From the campaign directory, obtain the eligible dependency at `43f59ff533598762cbc43a5e14af2bbbc76fabbd` using the acquisition commands in [the weighted recovery](weighted-matching.md), then run:

```bash
python3 -B agents/scout/code/fixed_geometry_family.py \
  --source-root work/<fresh-pinned-source> \
  --dimensions 8 10 24 26 --output work/<fresh-geometry-run>
```

The compact completed certificates are [8/10](fixed-geometry-h8-h10.json), [10/12](fixed-geometry-h10-h12.json), [24/26](fixed-geometry-h24-h26.json), and [26/28](fixed-geometry-h26-h28.json). These finite exact geometric statements do not certify a new complete multiplier exponent. Changed producer/output families, original matching uses, full fixed matrix moments, native wire/halving/row parameters and the all-size compiler/assembly remain separate requirements. In particular `(24,26)` has `m=624`, largest inherited exterior child576 and halving degree9; `(26,28)` has `m=728`, exterior child676 and degree10. Its degree9 is insufficient.
