# Independent balanced operator control

PASS: 38 shapes, 454 input basis columns and 114,180 exact forward polynomial
matrix entries agree with an independently computed tensor Fourier formula.
The normalized opposite composition equals input/M exactly. All tiny basis
columns are checked; larger unequal-width cases use five selected boundary
columns per shape. This executes actual butterflies and negacyclic monomial
multiplications, not just label reordering. There is no producer import.

Python 3.14.4, one process, 1.71 seconds measured by time -v, peak RSS 22,772 KiB.
The dedicated reservation was released on completion. Exact commands, hashes,
start/end times and external evidence paths are in protocol.json. The all-size
layout, precision and fixed-tape cost transfer remains a separate written proof.
