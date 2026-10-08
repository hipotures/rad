# Source criticism of deferred reserved-axis transforms

## Question and conclusion

The layout agent proposes completing the active axes A first while B supplies row and compact-control fields, then routing B into an active block and using already transformed A as external dirty row and scratch fields. The full B transforms are deferred, instead of applying one reserved-axis kernel in every shared round.

The exact algebraic reordering is supported by the pinned public contracts. I found no requirement that the reserved selected kernels have already been applied. This review supports an algebraic lemma; it does not independently prove the new physical schedule or its complete analytic composition.

## Pinned evidence

In PR 36 at `11817ccacb564bb7f98789c20dc11d3fece207e3`, `notes/compact-control-layout.tex` lines 56–62 states that each completed invocation acts as the desired active-axis tensor and as identity on reserved and spectator coordinates. Its earlier individually applied kernels are then justified by commutation. The text explicitly allows arbitrary temporary contents and intermediate scratch payloads, and restores each original row separately. Processing the reserved kernels earlier is therefore not a precondition on field contents.

The pinned upstream `build/sections/06-transforms.tex` lines 132–156 defines the multidimensional transform as a tensor product. A twiddle for axis i depends only on axis i's address bits and commutes with every other axis's butterfly. Consequently complete exact axis transforms can be grouped and reordered, provided within-axis round order is preserved.

The native row proof separates the row index from compact-field bits and gives each role the complete same within-row address set. Transformed A payloads remain arbitrary disk-array inputs on that same complete address cube. Their frequency interpretation changes no completeness or dirty-scratch condition. A router must preserve and later restore the coordinate descriptor accurately.

## Conditions still requiring a new written proof

- Row regions and complete compact fields must be carved from external A with the same row-stock divisibility, aligned gate domains, field placement and paid padding as the original proof. This is an adaptation of the contract, not merely renaming an internal reserved set.
- The bank exchange and its reverse must be actual paid fixed-tape permutations with a fixed number of tapes. Logical tensor commutation does not charge routing.
- The two input operands must undergo the same forward permutations. The inverse must consume the resulting frequency coordinates and execute the inverse grouping and routing in the proper reverse order.
- Computed truncations need not commute with other axis transforms. Use contractions to bound accumulated error of the new order, rather than asserting that rounded intermediate operators commute. Two groups of at most ell rounds each give a constant multiple of the original ell truncation bound. The coefficient and semantic guard charges must still include every group.
- If B is small relative to the chosen leaf threshold, its individually executed fallback must fit the complete cost bound. An external-bank call must not quietly reserve some of B again and create an endless deferral.
- Retain the polynomial suffix throughout. Its width and scalar arithmetic charges are separate from the axis reservation argument.

## Equal-axis shape clarification

The layout agent's actual proposal uses an address budget `N=D*ell+h` with `0<=h<ell`, `D-1` main axes of width ell and one polynomial suffix of width `ell+h`. Thus the suffix has fewer than `2*ell` bits. Its pointwise ring multiplication retains the old `log(rp)=Theta(ell+log p)` order. A hypothetical suffix of width d would create a new cost row, but that is not this proposed shape and is not an outstanding objection to it.

The underlying tensor commutation and dirty-field contracts are attributed prior interfaces, not newly invented facts. The proposed avoidance of repeated reserved-axis processing is the campaign's application and remains subject to the listed full-machine checks. This is independent agent criticism, not external peer review.
