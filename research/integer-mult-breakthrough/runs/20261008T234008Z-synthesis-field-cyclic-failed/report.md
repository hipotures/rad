# Failed all-zero cyclic-word instrumentation

Initial source 3173c948 stopped with KeyError maximum_real_or_imaginary_component on an all-zero bank: no positive peak had initialized the record. No certificate was produced or accepted. The exact source can be reconstructed with fixtures/synthesis/field-zero-peak-failure.patch; a fresh reconstruction receipt below independently reproduces the error. The positive attempt is separate.

See [protocol](results/protocol.json), [source/commands and mathematical scope](../../reports/synthesis/finite-field-cyclic-core.md), and [persistence identities](results/persistence.json). Original completed files remain unchanged under ignored `research/integer-mult-breakthrough/work/synthesis/20261008T234142Z-field-cyclic/results`.
