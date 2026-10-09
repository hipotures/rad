# Independent source review of the zeta ancestry discriminator

Status: **ANALYTICAL SOURCE REVIEW**. This review did not rerun the
producer's finite search, inspect the external paper proof, or establish
a new zeta gate minimum or native supplier.

Inspected on 2026-10-09 UTC:

- `code/obstructions/zeta_dependency_ancestry.py`, SHA256
  `5946771baf8a52a129cec2ec5599ea96f1cf004765255b8f161630513b126f2e`.
- `reports/obstructions/zeta-dependency-ancestry-scope.md`, SHA256
  `cf1ba9330c15a609166eb831a16b41f06c9b5ea381a430d0aa90530a66b8d51d`.

The row-ancestry update correctly unions both versioned parents even
when their numerical coefficients later cancel. The signed excursion
`x0 += x_(n/2); x0 -= x_(n/2)` has identity endpoint and leaves an
actual right-input path in the ancestry of x0. Appending the ordinary
Yates word therefore keeps the exact triangular zeta matrix while
violating the no-right-to-left ancestry predicate. This is an all-size
two-extra-gate counterexample to inferring ancestry from the final zero
block. It does not save a gate, and the report states that scope.

The XOR search retains each new nonzero signal in an immutable available
set. Thus its breadth-first depth counts newly computed values, with
free fanout and retained intermediates. The disjoint-support branch
is a restriction of that clean DAG model. It is not a reversible
four-register resource ledger. State-set deduplication is sound for
this existence/minimum question because the available values fully
determine all future gates, and each transition adds one new value.

The separately retained Gaussian word correctly implements the four
requested sums in output order b,c,d,a: after b+=a, c+=b, d+=c, the
update `a=-a; a+=d` produces b_original+c_original+d_original.
Its four additions, unit sign and output permutation are all explicit.
Reversing the additions and retaining the inverse sign/permutation
restores the original arbitrary input matrix. The unsigned XOR lift
would have coefficient two on a in the final fourth register, so the
sign is necessary in characteristic zero. The declared negative
controls address that distinction.

I accept the code/report's model separation. The finite DAG minima and
full operator execution remain producer evidence; this source review
checks why their scopes and algebra are consistent. In particular,
neither a triangular endpoint nor the clean DAG's four-gate example
justifies a lower bound or a free dirty/helper chronology for the
Gaussian-dyadic zeta search.
