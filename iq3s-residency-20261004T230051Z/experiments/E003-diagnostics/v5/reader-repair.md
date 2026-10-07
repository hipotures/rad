# Reader repair

The first validation crashed with `IndexError: index 1241 is out of bounds ... size1241`.
Trace window numbers are runtime rounds, including prefill; this request starts at28,
not0. The reader now maps recorded numbers to array indices. No binary, trace or
request changed. The repaired reader reproduces every resident slot/path and the
final resident set, with zero discrepancies across2117280 routed entries.

v5 built successfully and passed the trace lifecycle test and real IQ3_S expert
parity on layers0,1,2,12. Native CTest has62pass/4environmental failures; two optional
fixture tests were not registered because this checkout has no separate venv.
This coverage gap remains explicit. No diagnostic result is a headline speed result.
