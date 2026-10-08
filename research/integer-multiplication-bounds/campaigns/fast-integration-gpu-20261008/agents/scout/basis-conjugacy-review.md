# Conjugate bases and source-weight classes

The coordinator supplied the quadratic closure on 2026-10-08 at 15:44 UTC.
This independent algebra review confirms the universal identities below;
it does not certify a new local profile or multiplication bound.

For `L_h = I - beta J`, `h > 9`, put

```
gamma = (9 beta - 1)/[3(1 - h beta)],
z_out = -beta(9 beta - 1)/[2(1 - h beta)],
beta* = -gamma/3 = (1 - 9 beta)/[9(1 - h beta)].
```

The two roots of `9 beta^2 - (1 + 2 h z_out) beta + 2 z_out = 0`
have the same `z_out`. Direct substitution gives `gamma(beta*) = -3 beta`
and `(beta*)* = beta`. The inside source coordinate product is
`[1 - (h - 3) z_out]/3`; therefore the complete source weight vector is
identical for the two roots, with each actual triple kept fixed. All data
matrices depending only on these weights are identical over Q, and over
any field where the same rational weights exist. Searching both roots on
the same source fixture and permutation duplicates the data experiment.

For a signed frame, use the already reviewed formula

```
P_beta = D + [s u z^T + s w u^T + V w z^T - (f - 1) u u^T]/d,
w = 1_F - 3 beta 1,  z = 1_F + gamma 1.
```

The matrices `D`, `u u^T` and the coefficients are symmetric and independent
of beta. Conjugacy exchanges `w` and `z`, so `P_beta* = P_beta^T` for every
actual frame, including source lines. Every difference of these projectors
also transposes. Its northeast corner rank table generally changes; it must
be rebuilt, or transferred through an explicitly proved flag/reversal map.
Identical source weights alone do not permit reusing local null-corner runs.

Copied centers admit the same exact transfer. Write

```
k = (h - 9)/4,
c = [2 - 3 beta(h - 3)]/(h - 9),
v = (h - 9)(1 - 3 beta)/[12(1 - h beta)],
p_i = e_i + c 1,  xi_i = v 1 - k e_i.
```

Substitution gives `c* = -v/k`, `v* = -k c`. Hence
`p_i* = -xi_i/k` and `xi_i* = -k p_i` for every center index. Every primal
and dual coordinate is exchanged up to a nonzero scalar; all coordinate
products are preserved. The copied-center nonzero requirement therefore
transfers without an index exception. The excluded finite values pair as
`0 <-> 1/9`, `1/3 <-> 2/[3(h - 3)]`, and
`(h - 7)/[3(h - 3)] <-> 2/[3(h - 1)]`; the singular value `1/h` is excluded.

Three useful pairs are

| Basis parameter | Conjugate parameter |
| --- | --- |
| `4/[3(h + 3)]` | `-1/3` |
| `-1` | `10/[9(h + 1)]` |
| `1/[3(h - 6)]` | `1/6` |

The last pair has `gamma = -1/2` at its first root, with positive source
products `(h - 7)/[4(h - 6)]` inside the triple and `1/[4(h - 6)]` outside.
Its copied-center primal is `e_i + 1/(h - 6) 1`; the dual is
`(h - 7)/8 1 - (h - 9)/4 e_i`. These are all nonzero at h = 23 and 25.

The exact rational pair `(z_out23, z_out25)` is a complete source-weight
class key for GPU discovery. Either root may represent each factor; the
other root remains a useful separate local-frame experiment, rather than
a new data-family experiment. Existing finite-field sample improvements
remain sample evidence. Full source-family, local-frame, bridge and physical
cost validation is still required before any assembled claim.
