# Whole-cylinder activity does not create a gate saving

Status: **EXACT VOLUME IDENTITY AND CONDITIONAL MOMENT DISCRIMINATOR**.
The prospective scalar word, native routing bill, stopping supplier and
integer assembly remain separate obligations. No larger kappa is claimed.

Consider a width-h scalar row gate acting on two letters of an alphabet
of size D=2^h. Tensor it across f columns, with selected width e=hf.
Each letter carries its complete K-bit chunks, including all spectators.
Assume the prefix codec partitions the entire physical address space into
disjoint cylinders with w active chunks free, and that the child acts on
all fields of each complete cylinder. The remaining prefix determines its
unchanged inactive letters and controls.

There are `A=2^((h-1)(K-1))` active prefix choices per column, each with a
free K-bit tail, and `I=(D-2)*2^(h(K-1))` inactive prefix choices. Therefore
the fraction of full physical volume at width w is exactly

```text
binom(f,w) A^w I^(f-w) 2^(wK) / 2^(hfK)
  = binom(f,w) (2/D)^w (1-2/D)^(f-w).
```

Thus W has the binomial law Bin(f,2/D), independent of K. This identity
counts complete records of the same width. Extra helper streams, copied
records, padding or an enlarged child format must change the volume
weights or receive separate charges. A correct address permutation alone
does not establish a cheap implementation of that permutation.

Suppose a full proposed primitive uses g such scalar gates and its assumed
normalized recurrence has power moment

```text
Phi_f(p) = g E[(W/(hf))^p],       0<p<=1.
```

Its first moment is exactly `2g/(hD)`. Since every nonzero child ratio is
at most 1/h<1 and positive width has positive probability, for every p<1
we have `Phi_f(p)>Phi_f(1)`. The ordinary Yates gate count g=hD/2 therefore
fails every sublinear power moment in this ledger. Neither successful
activity compaction nor a precision bound changes that conclusion.

Conversely, concavity gives the sufficient bound

```text
Phi_f(p) <= g (2/(hD))^p.
```

For the HYPOTHETICAL width-three eleven-gate word, p=97/100 gives a strict
bound, certified without floating point by `11^100 < 12^97`. The actual
twelve-gate word fails the same comparison. This is a useful sensitivity
test because it distinguishes a potentially substantial primitive gain
from a mere layout improvement. It is not a certificate of an eleven-gate
word; the search for that word remains unresolved.

A stopped recurrence also requires an actual local overhead exponent
tau compatible with p, such as tau<=p in the previously reviewed contract.
An inherited supplier with tau near one does not automatically support
p=.97. Complete body, cleanup, routing, metadata, rounding, scalar weights
and integer recovery must all enter a replacement ledger before any
end-to-end saving can be asserted.

The [independent exact source](../../code/obstructions/activity_gate_moment.py)
retains every activity class, verifies mass, mean and variance over the
rationals, checks integral full-cylinder volumes, and encloses half-power
moments with integer square roots. It rejects deleting the rare all-active
class. The [four-worker run](../../runs/20261009T072520Z-activity-gate-moment/report.md)
passes eight cases through f=256 and K=3. The general conclusions above
follow from the displayed identities and inequalities, not finite sampling.

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/activity_gate_moment.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/activity_gate_moment.py --workers 4
```

Optional `--output` must name a fresh directory. These controls require
only standard-library Python and have no imported producer implementation.
