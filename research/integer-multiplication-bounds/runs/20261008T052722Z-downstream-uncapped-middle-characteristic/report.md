# Preserved interface failure

The first exact uncapped-characteristic invocation failed while reading
the newly accepted clone review's count schema: it requested `h` inside
`full.exact_counts`, while that review stores h and roles at the full
object level. No scientific certificate was written. The prior capped
certificates and accepted finite review were unchanged; the owned worker
reservation was released.

The executed source is preserved as
[downstream_uncapped_middle_characteristic_v1.py](../../code/downstream_uncapped_middle_characteristic_v1.py).
Its hash matches the original protocol. The repair compares the actual
v/m/N/W/L/D/s count fields, validates h/roles separately, and checks the
saved physical, rational-frame, matching, controller and dirty-invocation
controls without assuming the older histogram-schema booleans. A retry
uses a fresh run ID and result path.
