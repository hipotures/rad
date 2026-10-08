# Preserved failed first negative control

The complete exact reflection, metric and all-triple coefficient checks
finished, but an incorrectly written h6 negative-profile assertion then
failed. At h6 the reflected triple has first source coordinate zero, so
the first row of its complement is the ordinary diagonal pivot (0,0).
The intended negative was that this pivot differs from the claimed
generic (0,5), not that its row index differs from zero.

The executed source bytes are retained in
[review_reflected_basis_v1.py](../../code/review_reflected_basis_v1.py).
The initial protocol/log is unchanged. The repair changes that negative
comparison and runs under a fresh identity. There is no accepted saving
from this first attempt.
