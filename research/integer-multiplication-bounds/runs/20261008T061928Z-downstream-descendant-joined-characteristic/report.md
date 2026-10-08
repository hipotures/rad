# Histogram schema failure

The first thin descendant characteristic failed with `KeyError: 'v'`
before it wrote a result certificate. The producer's complete histogram
stores the number of triples as `local_program.physical_sources`; both
independent compact audits expose v directly in their count objects.
The first adapter incorrectly expected v at the producer histogram root.

The exact executed source is preserved as
[downstream_descendant_joined_characteristic_v1.py](../../code/downstream_descendant_joined_characteristic_v1.py),
with the source hash recorded by the unchanged [protocol](protocol.json).
The fresh repair compares the physical-source count with both independent
v values and also checks the physical partial-output count 3v. It retains
all frame, target, rank, histogram and literal-guard assertions.

This is an interface failure, not a failed mathematical saving. The own
worker reservation was released. The accepted R500703 and full promoted
R485680 artifacts remain unchanged.
