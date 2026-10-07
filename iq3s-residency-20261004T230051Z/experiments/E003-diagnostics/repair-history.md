# Diagnostic repairs

- v1 / diagnostic-v1: patch guard found four identical residency assignment anchors. No binary produced, no inference run. Partial source and command log retained.
- v2 / diagnostic-v2: narrowed anchor still occurred in both serve and standalone generation. No binary produced, no inference run. Partial source retained.
- v3 / diagnostic-v3: promotion anchor likewise occurred in both serve and standalone generation. No binary produced, no inference run. Partial source and patch-script snapshot retained.
- v4 / diagnostic-v4: patch applied and was committed locally. Build rejected a trace helper taking int64 token IDs while the actual verify window is int32. No binary produced, no inference run. Source commit, templates and full build error retained.
- v5 planned repair: use the actual int32 token-ID type, keeping all runtime behavior unchanged. Build in a new checkout/directory. Repeated anchors are now explicitly counted; inactive hooks on the standalone path do not enable tracing there.

These are instrumentation implementation failures, not inference/model failures or completed negative policy experiments. None are advertised as runnable variants. Their diagnosis does not consume measured repetitions of an unchanged speed point.
