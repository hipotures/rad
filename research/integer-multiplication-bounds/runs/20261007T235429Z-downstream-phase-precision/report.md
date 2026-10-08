# Invalid initial symbolic-precision checker

The generated PASS is not accepted. Two allowance comparisons substituted p^k<=2^(kp) with negative k, which reverses the bound. The corrected argument instead uses p^3<=p^20 and p^7<=p^20 directly. Boundary error terms are separately constrained below1/2. All matrix proofs and kappa arithmetic are unaffected; this checker is auxiliary evidence.

The original certificate, source hash and exact repair are retained in [protocol](protocol.json). A fresh corrected run will hold accepted evidence.
