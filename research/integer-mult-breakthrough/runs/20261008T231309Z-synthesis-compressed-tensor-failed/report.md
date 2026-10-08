# Rejected inverse-scale ordering

The first compressed tensor attempt fails exact complete-column replay with `ValueError: Full in-place address/dirty operator replay failed`. The low and high dyadic inverse-scale entries were exchanged. No accepted certificate was produced. All original protocol bytes are unchanged.

The [failure record](results/failure.json) names the observed exception, original effective hash, raw path and recovery limitation. Applying [the reconstruction patch](../../fixtures/synthesis/compressed-inverse-order-failure.patch) to an isolated copy of the corrected source recreates the failed source with SHA256 `825f43e27f5a68c17806aab61610d89dbde0ae545a733c3693182df6605a3dcc`, matching [protocol](results/protocol.json).

The [fresh corrected run](../20261008T231328Z-synthesis-compressed-tensor/) passes, and the bounded verifier now deliberately reproduces this regression and requires rejection. See [full analysis](../../reports/synthesis/residual-gauge-tensor-costs.md).
