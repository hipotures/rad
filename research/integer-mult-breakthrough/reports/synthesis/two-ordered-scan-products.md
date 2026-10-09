# Two ordered one-bank scans cannot supply subset-zeta

**REFUTED WITHIN STATED SCOPE.** An invertible one-bank product of two complete prefix or difference scans, with invertible diagonal gauges between and outside them, cannot equal Boolean subset-zeta on two or more axes. The two-axis finite result fixes the original labeled inputs and outputs. The all-size result for at least three axes also allows arbitrary outside row and column permutations. Neither result excludes borrowed dirty banks, projections, three or more scans, segmented scans or nonlinear changes to the endpoint map.

This family changes the earlier additive-scan ansatz: products can have large cross-cut rank and therefore are not excluded merely by the earlier additive rank controls. A constant number of genuinely fast native scans would have substantial potential leverage. The present obstruction concerns the exact complete operator before assigning native costs.

## Complete operator model

Write \(L_\pi\) for a prefix scan in a total order \(\pi\) on all \(N=2^f\) addresses. Its inverse \(D_\pi=L_\pi^{-1}\) is the ordered difference: diagonal one and minus one at the previous address. The tested model is

\[
Z_f=\operatorname{diag}(a)\,S_\pi\,\operatorname{diag}(b)\,T_\sigma\,\operatorname{diag}(c),
\qquad S,T\in\{L,D\},
\]

where every entry of \(a,b,c\) is nonzero and \((Z_f)_{ij}=1[j\subseteq i]\). Scalars can be arbitrary characteristic-zero complex numbers; the proof does not require bounded coefficients, positivity or absence of cancellation. No uncharged native address permutation is inferred from granting arbitrary scan orders in this algebraic model.

## At least three axes: support alone is decisive

Two differences and diagonal or monomial wrappers have at most four entries in each row. The final row of \(Z_f\) has \(2^f\) nonzeros, so two differences fail for \(f\ge3\). For two prefixes, invert the complete product. Its inverse has two differences, while the Möbius inverse \((Z_f^{-1})_{ij}=(-1)^{|i\setminus j|}1[j\subseteq i]\) again has a full row. The same support bound applies. These two arguments were independently proposed and reviewed by the coordinator; they are distinct from the additive cut-rank model.

For a mixed product \(L_\pi\operatorname{diag}(b)D_\sigma\), each column is the weighted sum of at most two nested suffix indicators in order \(\pi\). If the tail coefficients cancel, the nonzero support is one interval between the two starting points. If they do not cancel, it is the suffix beginning at the earlier point. A single-column difference endpoint is itself a suffix. Thus every column support is one interval. Nonzero external scalar gauges preserve these supports.

The \(f\) columns of \(Z_f\) indexed by singleton labels are the coordinate-filter sets. The vector of membership in these sets distinguishes all \(2^f\) rows. In any row order there must therefore be at least \(2^f-1\) adjacent membership changes. If all \(f\) sets were intervals, they would create at most \(2f\) endpoint changes. The inequality \(2^f-1>2f\) for \(f\ge3\) is a contradiction. Arbitrary outside row and column permutations preserve this distinction argument.

For the other mixed orientation \(D_\pi\operatorname{diag}(b)L_\sigma\), use rows and the \(f\) target rows whose labels omit exactly one coordinate. Their supports distinguish every column, and the same interval argument applies.

These arguments are mathematical proofs in the specified model, not proof-assistant formalization. They do not impose a time lower bound on a richer native circuit.

## Two axes: exact complete-order elimination

The first four-worker attempt, `20261009T093521Z-ordered-scan-products`, checked all \(24^2\times2=1152\) mixed order/orientation cases. For each case the required zeros of \(Z_2\) are exact homogeneous rational linear equations in the four middle-diagonal entries. Their nullspace determines whether an invertible diagonal or a required nonzero target entry is forced to vanish.

All 1152 cases fail this necessary test: 1104 force a zero middle-diagonal entry and 48 force a required target entry to zero. Exact rational kernel identities also hold over \(\mathbb Q(i)\) and \(\mathbb C\); no modular rank inference is used.

The separate four-worker attempt `20261009T093730Z-ordered-scan-same-type` checks the 1152 same-type cases. All 576 difference/difference cases fail the zero-pattern test. Of 576 prefix/prefix cases, 574 fail. The two remaining cases use the same topological order on both scans: `(0,1,2,3)` or its coordinate interchange `(0,2,1,3)`. The completed discovery attempt correctly retains these two as `UNRESOLVED GAUGE COMPATIBILITY`; its source and results remain unchanged.

The later bounded verifier resolves both survivors by an exact symbolic identity. In natural order the required zero gives \(b_2=-b_1\). If \(M=L\operatorname{diag}(b)L\), the all-one target rectangle on rows \(1,3\) and columns \(0,1\) must have zero determinant after invertible row/column scalar gauges. Its determinant is

\[
M_{10}M_{31}-M_{11}M_{30}
=b_0(b_3-b_1)=M_{00}M_{32}.
\]

Both factors on the right must be nonzero to match \(Z_2\), a contradiction. The second order is the coordinate interchange of the same identity. The verifier checks the polynomial identity on the complete rational nullspace, rather than relying on a selected numerical middle diagonal.

Across all four type pairs there are 2304 complete fixed-label cases: 2244 forced-zero middle diagonals, 58 forced-zero target entries and two symbolic gauge-minor contradictions. This two-axis finite census does not include arbitrary outside input/output permutations; that extension is not claimed. On one axis a valid invertible dyadic control is \(Z_1=\operatorname{diag}(1,1/2)L^2\operatorname{diag}(1,2)\), so the model is not intrinsically inconsistent.

## Reproduction and persistence

Sources are [ordered_scan_products.py](../../code/synthesis/ordered_scan_products.py), [ordered_scan_same_type_controls.py](../../code/synthesis/ordered_scan_same_type_controls.py) and [verify_ordered_scan_products.py](../../code/synthesis/verify_ordered_scan_products.py), with the frozen rational-elimination dependency [rational_frame_completion.py](../../code/synthesis/rational_frame_completion.py). No external solver or downloaded checkout is needed.

```bash
python3 -B research/integer-mult-breakthrough/code/synthesis/ordered_scan_products.py \
  --workers 4 --output <fresh-mixed-output-directory>
python3 -B research/integer-mult-breakthrough/code/synthesis/ordered_scan_same_type_controls.py \
  --workers 4 --output <fresh-same-type-output-directory>
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_ordered_scan_products.py \
  --output <fresh-receipt-file>
```

Expected bounded status: `PASS COMPLETE TWO-SCAN ALGEBRAIC CONTROLS`. It recomputes every exact fixed-label order case, both survivor identities, all 4608 signed/cancelling interval controls, complete Möbius inverses through seven axes and the one-axis positive control. Omitted difference signs, corrupt kernel directions, corrupt survivor identities and invalid scalar units are negative controls.

The complete original row-level certificates remain unchanged under ignored `work/synthesis/20261009T093521Z-ordered-scan-products/results/` and `work/synthesis/20261009T093730Z-ordered-scan-same-type/results/`. Readable summaries identify the original hashes and omissions. The source deterministically regenerates the full mathematical rows, though wall times and UTC fields change. Complete text archives are a coordinator publication obligation; do not describe ignored originals as already present in a Git clone.

The next substantive family must change at least one premise, for example a three-scan product, an actual shared-bank shear chronology, or a changed endpoint representation. A finite algebraic witness would still need arbitrary dirty restoration, native address-order costs, complete record buffers, precision and a noncircular asymptotic supplier ledger.
