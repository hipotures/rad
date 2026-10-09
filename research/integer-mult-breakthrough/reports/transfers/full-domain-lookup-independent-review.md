# Independent scope review of full-domain lookup regrouping

The setup-count deduction in the
[full-domain lookup report](../obstructions/full-domain-lookup-boundary.md) is
sound for a uniform algorithm that materializes a separate record for every
possible block input. The measured sequential scan is correctly scoped as an
access baseline. It supplies no lower bound for all fixed-tape lookup methods.

For a block of `K=2^t` symbols with alphabet size `q>=2`, there are exactly
`q^K` inputs. If materializing these distinct records costs at least one stored
bit per record and setup is at most `C N^delta (log N)^c`, with fixed constants
`C,c,delta>0` uniform in the parameters, then

```text
K log2 q <= delta log2 N + c log2 log2 N + O(1),
t <= log2 log2 N - log2 log2 q + O(1).
```

The latter is `O(log log N)`. It counts grouped binary address dimensions, not
the number `K` of grouped records, which is `O(log N/log q)`. A precomputed
uncharged advice table is a different interface and does not satisfy this
materialization proof. For zero polynomial exponent the bound can be made
stronger; that case is not needed for the report's `delta=1/2` controls.

To infer a limitation on the integer-multiplication logarithmic exponent, also
bind the transform width to its input length: `log N=O(log n)` suffices. The
global row-stock or time ledger may imply this relationship. Under that
relationship, a gain of only `O(log log N)` cannot supply a factor
`(log n)^kappa` for fixed positive `kappa`. A changed transfer using the table
as only one component is not excluded.

I verified the exact pinned primary paper's model. Alman's Section 1.1 defines
the bit complexity of a RAM algorithm, and its tree-based lookup interface
costs `O(b)` bit operations for `b`-bit keys and values. Theorem 3.2 uses the
complete-domain table to group transform layers. This supplies neither a
fixed-tape lookup implementation nor a Gaussian-dyadic lift.
[Alman, arXiv 2211.04643v1](https://arxiv.org/pdf/2211.04643v1).

Source inspection of `full_domain_lookup_boundary.py` confirms that its scan
charges every table read and move, key read and rewind, and output write and
move. The comparison continues reading the complete query at every record.
It retains both tapes and writes a fresh result. Its last-key access visits
the complete table, so this particular routine costs
`Theta(q^K K log q)`. That trajectory cannot be identified with the paper's
faster RAM lookup. Initialization, encoding and controller compilation are
separate interfaces, as already acknowledged by the producer.

The bounded producer replay passes. I separately check the exact integer
inequalities for all three retained setup controls: the selected power-of-two
block fits and its double fails. This is a producer replay and analytic/source
review, not an independently implemented scan or a formal machine proof.
The [immutable review run](../../runs/20261009T005456Z-transfer-lookup-scope-review/protocol.json)
pins the effective producer source and command.

Compressed or partial-domain tables, constrained signals, batched paid
sort/merge access, and direct arithmetic remain possible alternatives. They
must pay actual keys, return addresses, all payload fields and table setup.
No RAM access, free relabeling, entropy restriction on arbitrary dirty fields
or general tape lower bound follows from this receipt.
