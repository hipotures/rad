# Preserved serialization failure

The exact source-frame and unchanged-complex characteristic calculations completed, then JSON serialization failed because rational logarithm endpoints were stored in tuples. No certificate was written and no candidate was promoted. The source snapshot is `code/downstream_source_frame_characteristic_v1.py`, SHA-256 `a3dfc1d381e92775d880e9d48afd24d8f31f462f6dc126475f020a61b00f2a46`; the full error remains in the external log recorded by the protocol. The child used 0.116 seconds and 24,116 KiB peak RSS; its reservation was released.

The fresh 093546 repair uses lists for those endpoints, preserving the mathematics and this failed attempt. [The cross-run report](../../reports/downstream-source-frame-characteristic.md) records both.
