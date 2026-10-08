# Rectangular simultaneous auxiliary flag construction

This is a proposed all-size algebraic component. It generalizes the support idea in Swapnil Jain's `notes/flag-basis.tex` at public commit `c2c2f279d936` (full identity retained by the scout). It does not yet prove the data-corner transfer or a stronger multiplication bound.

Let `2 <= a <= b`, `delta=b-a`, and identify the ambient space with matrices of size `a by b`. Prescribe the first `b` row functionals of an ambient basis by matrices `U R_i V^T`, and the last `b` inverse columns by matrices `U^{-T} C_j V^{-1}`, where `U,V` are invertible. Use supports

`R_i[r,c]=0` unless `r<=min(i,a-1)` and `c<=i`,

`C_j[r,c]=0` unless `r>=max(0,j-delta)` and `c>=j`.

Require `R_(b-1)[a-1,b-1]=0` and otherwise choose generic supported entries. For each `j<b-1`, solve `trace(R_i^T C_j)=0` in increasing `i=j,...,b-1` through the entry `C_j[max(0,j-delta),i]`. Its coefficient `R_i[max(0,j-delta),i]` is generically nonzero. Earlier trace constraints are unchanged because `R_k` has zero column `i` for `k<i`. For `j=b-1` the trace vanishes by the required final zero. For `i<j`, disjoint column supports make the trace zero without equations.

The first `b` rows and last `b` columns for a projector `P_a tensor I_b` have zero entry at `(i,j)` for `i<j`, by disjoint column support. For `I_a tensor P_b`, the first `a` rows pair with the last `a` columns, namely `C_delta,...,C_(b-1)`; the entry at `(i,j)` is zero for `i<j`, by disjoint row support of `R_i` and `C_(delta+j)`.

The latter diagonal is a product of two nonzero linear forms, because both matrices meet in row `i`, with independently nonzero supported row vectors. The former diagonal is similarly a product using column `i`. Even at the final index the imposed zero leaves nonzero early rows in `R_(b-1)` and a nonzero final-row entry in `C_(b-1)`. The diagonal conditions can therefore be nonzero simultaneously for a finite collection of rank-one line projectors, by the irreducible parameter and finite-product argument, provided the prescribed row and column families have full rank.

With full row and column ranks and all pairings zero, complete the basis by choosing a right inverse `Z` of the row family and a complement `W` of the column family in its kernel. The ambient inverse basis is `[Z | W | mu]`. This is a fixed address-basis construction; it is not a runtime stream adapter.

Unresolved requirements: a separate full-rank argument for the prescribed families; generic local rank profiles and the actual data entrance corner in this restricted family; all physical maps, rank-one copied endpoint corrections, and complete recurrence/precision composition. The small modular script checks the rank and pairing assumptions for explicit points but does not discharge these general obligations.
