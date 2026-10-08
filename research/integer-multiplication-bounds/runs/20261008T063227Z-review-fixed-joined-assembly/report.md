# Preserved reviewer schema failure

The complete independent joined primitive and numerical assembly checks
passed until the native-interface annotation attempted to read
`side_roles` from the derived arithmetic count dictionary. That dictionary
exposes the independently recomputed arithmetic counts; the role count
belongs to the raw primitive identity. This is a reviewer schema error,
not a failed characteristic or a promoted result.

The exact executed source `code/review_joined_assembly.py`, inputs,
protocol and failure log remain unchanged. A fresh
`code/review_joined_assembly_repair.py` reads the already checked primitive
role identity. A new run is required; this attempt has no certificate.
