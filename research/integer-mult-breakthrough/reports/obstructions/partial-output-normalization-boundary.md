# Partial outputs do not rescue the retained joint core's uniform moment

The joint mutable-source core has rank 22 against a nominal six-full-bank
capacity of 24. Its canonical repair costs two additional line children.
A possible alternative is to retain its two partially transformed outputs
as a different supplier. For this particular core, the correct partial/full
target rank is already 22. Its children split that target exactly, and its
uniform power moment cannot contract for any positive saving.

This is a conditional normalization obstruction for the retained core and
its proposed extension. It does not exclude other partial primitives,
stage fusion, or a genuinely different coupled recurrence.

## Physical output and correct target

After the paid constant-bank decoding of the
[joint core](../synthesis/joint-mutable-birth-algebraic-cleanup.md), its original
source banks have operators `F_h A_U^-1`, with `A_U=C_line(U)`. The other two
data banks and two arbitrary dirty carriers have `F_h`. Each odd-line partial
operator has selected mixing rank `h-1`; it is the actual odd-kernel frame,
with its phases and translations retained. Applying `A_U` returns full `F_h`.

The six target widths are therefore

```text
[h-1, h-1, h, h, h, h],
total target rank = 2(h-1)+4h = 6h-2.
```

The finite word is constructed at h=4. To assess its proposed dimension-two
common-frame extension, retain two source entrances of width 1, four other
entrances of width 2, and six final moves of width `h-2`. These are
hypothetical all-h child counts until a complete family is constructed.
Their total rank is also `6h-2`. At h=4 they give the actual histogram
`{1:2,2:10}`. Treating all six targets as full transforms falsely counts two
unprovided directions as completed work.

## Exact all-saving inequality

For a common time ansatz proportional to `width^p`, with `0<p<1`, the child
numerator and the actual target denominator are

```text
A_p = 2*1^p + 4*2^p + 6*(h-2)^p,
D_p = 2*(h-1)^p + 4*h^p.
```

Each partial target splits into `1+(h-2)`, and each full target splits into
`2+(h-2)`. All parts are positive for h>=3. Strict subadditivity
`a^p+b^p>(a+b)^p` gives

```text
A_p > D_p,            0<p<1, h>=3,
A_1 = D_1 = 6h-2.
```

Thus the correctly normalized mixed-output moment `A_p/D_p` is strictly
above one at every positive saving `b=1-p`. A shared positive core is useful
physical progress, but renaming these two incomplete outputs does not
produce a contracting uniform supplier.

This comparison assumes the same uniform exponent and unit leading weights
for these actual transform widths. It is not an exclusion of unrelated
operator types, different weights justified by a complete new assembly,
restricted inputs, or fusion with later arithmetic. Those alternatives need
their own workload, complete physical stock and transfer proof.

## Exact finite discriminator

The [independent checker](../../code/obstructions/partial_output_budget.py)
imports previously published literal Gaussian arithmetic, not the joint
producer. Four workers test h=3,4,16,64 at the reference saving
`20/189981` and at `1/1000`. Exact outward logarithm/exponential intervals
confirm both the false contraction under six-full-bank normalization and
the failed contraction under the mixed target.

Separate h=3/4, f=1/2 literal tests check all 688 partial-operator columns,
139,904 exact coefficients, their rank support and the missing line repair.
They do not independently replay the complete joint helper word; its
[separate review](../transfers/joint-mutable-birth-independent-review.md)
has that purpose. The all-h inequality is elementary mathematical evidence;
the larger-dimensional profile is conditional and no new native family is
claimed.

The [run receipt](../../runs/20261009T030904Z-partial-output-budget/report.md)
retains unchanged full intervals and effective source hashes. Reproduce
one complete width-four endpoint and its exact mixed budget with standard
Python:

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/partial_output_budget.py --workers 1 --bounded
```

Omit `--bounded` and use four workers for all discovery cases. An optional
output must be fresh. The source SHA-256 is
`9665d3fdb9fb4eaacb9f546f78312d407e8b9b481dcd3ff757ed8c605424fd15`.
Source hashes are rechecked after execution. This is an exact finite
certificate and a scoped conditional inequality, not formal verification or
a multiplication exponent.
