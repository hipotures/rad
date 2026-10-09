# Independent analytical review of the weighted-scan channel classification

Status: **INDEPENDENT SOURCE AND MATHEMATICAL REVIEW**. The coordinator
accepts the stated all-size classification within the additive scan class.
This is not a duplicate physical replay, a formal proof or a general native
streaming lower bound.

The [producer report](../synthesis/weighted-scan-intertwiner-structure.md)
asks for X and C_f X in the same explicitly additive weighted-scan space.
It permits arbitrary complex coefficients and cancellation, but excludes
arbitrary scan products and changed coordinate orders. Its two standalone
sources have SHA-256 values:

| Source | SHA-256 |
| --- | --- |
| `code/synthesis/weighted_scan_intertwiners.py` | `0e6e1e3af2da37a0ada5eb599ec568f7125479dd88717148335a7c484f4e12ac` |
| `code/synthesis/weighted_scan_structure.py` | `d5257962c4812e7a8310c70a61098350b5974a355bd2ced54b3601b824ceafa0` |

The reviewed report hash is
`c9d293c270420d293dc45788e99862a363de2e4bfcb75d772b439063b3ccbda8`.
The following checks concern its actual argument rather than an extrapolation
from the exact finite solver.

Adjacent mixed differences of an additive strict triangle vanish outside
the tridiagonal. Conversely the zero mixed differences reconstruct row and
column contributions on each triangle, with arbitrary diagonal retained.
Thus A=Delta X Delta^T is tridiagonal exactly for the stated space. Kernel
terms are u 1^T+1 v^T, and the cumulative-sum right inverse gives its explicit
reconstruction without treating division as a native operation.

Since C_f fixes the constant vector, its invertible quotient is
H=Delta C_f P and Delta C_f=H Delta. In the highest-bit split the side blocks
are alpha H0 and beta H0, while the middle column is i e_(m-1). This follows
directly from C_f s=beta 1+i s for the half indicator s. Both side quotient
blocks are invertible.

A tridiagonal column away from the midpoint cannot keep its image supported
in its original local window: its opposite-half component is an invertible
nonzero multiple of H0. The adjacent midpoint columns can retain only their
central coordinate. For the central column, the coordinator independently
checked the crucial interior entries, with n=f-1:

    H0[2,0] = G[2,0]-G[3,0] = i alpha^(n-2) beta,
    H0[2,m-2] = G[3,m-1]-G[2,m-1] = i alpha beta^(n-2).

Both are nonzero. The two side equations have determinant proportional to
alpha^2-beta^2=i, so both endpoint components vanish. Row two is interior
when m>=8, explaining the f>=4 threshold rather than concealing the retained
small exceptions.

Only three entries of the midpoint row of A remain. Reconstruction yields
X=u 1^T+1 v^T+s w^T, with the same three nonconstant midpoint functionals
available to every bank. Each scalar block therefore has rank at most three.
A vertical stack of W blocks depends on one shared constant functional,
W arbitrary v functionals and those three shared midpoint functionals,
giving rank at most W+4. For W=6 and f>=4 this is strictly below 2^f. A full
inverse-source column cannot be assembled from those channels.

The restriction applies to the actual inverse-input blocks and actual
output blocks in this class. Cheap forward inputs alone do not certify that
their inverses belong to it. Nonlinear orderings, reversals, products of
scans, extended payload algebras and different coupled interfaces remain
outside. The separately derived [cut-rank bound](../transfers/coupled-cut-rank-transfer-boundary.md)
uses weaker assumptions and has a correspondingly weaker threshold; the two
arguments should not be conflated.
