# Wrapper failure before child launch

This attempt launched no mathematical child. The inline admission
wrapper mistyped `fcntl.LOCK_UN` as `fcntl.fLOCK_UN` immediately after
incrementing its own one-worker reservation. It failed before admission.
The file context released its lock; a separate locked operation released
only this attempt's increment and recorded the exception in the protocol.

The mathematical source and both immutable input certificates remain
unchanged. A fresh attempt uses the corrected unlock call and the same
science command. This failure asserts nothing about the proposed bound.
