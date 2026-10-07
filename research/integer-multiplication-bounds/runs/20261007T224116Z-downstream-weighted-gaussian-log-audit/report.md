# Independent logarithm audit

The checker reran all 1,099,640 rational transition checks and both strict
conditional assembly witnesses. It additionally encloses log(125000) with
an exact atanh series, verifies log(125000)<11737/1000 independently,
and confirms the retained complex spare-coordinate and stopping-guard counts.

See [certificate](results/certificate.json), [protocol](protocol.json),
and [mathematical proof](../../reports/downstream-weighted-gaussian.md).

The source checkout remained unchanged; the checker uses only the Python
standard library and is deterministic. This is arithmetic and written-proof
verification under retained upstream interfaces, not a full multiplication
algorithm implementation or formal proof.
