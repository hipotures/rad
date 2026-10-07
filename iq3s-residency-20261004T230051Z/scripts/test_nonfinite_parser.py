"""Regression checks for preserved debug-log formats, including zero-count reports."""
from diagnostic_logs import has_nonfinite_failure as failed
assert not failed('last residual row 0 non-finite (max |x| 0.467); PLE history 0 non-finite; GDN state 0 0 non-finite')
assert failed('last residual row 4 non-finite (max |x| 0.467)')
assert failed('row 3: 7 of 100 logits non-finite (token out 8)')
assert failed('non-finite GU 0 H -1 Dm 2 bo 0 of T 4')
assert not failed('non-finite GU 0 H -1 Dm 0 bo 0 of T 4')
assert failed('last residual row 0 non-finite (max |x| inf)')
print('PASS: zero-count and positive-count formats distinguished')
