# Failed final display after completed arithmetic

Both strict rows and the certificate were computed and written, but the
final CLI display looked for bit count key R, which the inherited bit count
schema does not contain. It exited with KeyError before reporting success.
This attempt is retained as failed; its certificate is partial evidence,
not a terminal accepted run. A fresh source and run repair the display using
the independently promoted finite-audit role field.

Executed source is preserved at
../20261008T015011Z-downstream-balanced-assembly484264/initial-v1/source.py.
Protocol and the external execution log retain the original failure.
