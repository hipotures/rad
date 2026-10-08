# Independent critique of the endpoint-aware precision guard

Status: **CONDITIONAL ANALYTICAL REVIEW**. The transfer track's proposed
[endpoint-aware guard](../transfers/endpoint-aware-guards.md) is sound under
its explicit complete-endpoint and literal-buffer hypotheses. This review
does not validate a native motif, supply time contraction or prove an exponent.

The central distinction is mathematical: after a child has COMPLETED, its
operator is exactly `C^tensor t` on every permitted input field. Its Gaussian
coefficients have denominator dividing `2^t`, and a conservative component
infinity row bound is `2^t`. Hence its output charge is at most t denominator
bits and t magnitude bits, independently of its internal recursive path.
This holds on arbitrary current dirty arrays. A common fourth-root unit and
a complete address permutation add neither charge.

Before the next sibling starts, completed widths and actual scalar prefixes
therefore bound its current input. At most one depth-first child is active;
its internal excursion is added to that current input bound. An induction
on the decreasing budget L proves endpoint correctness and active precision
together. With the actual local sum of child widths at most `q*e+q0`, this
gives `G(e,L) <= q*e+q0+S + max G(ej,L-1)`. Thus same-width siblings require
`O(eL)` precision guard under the specified local program. Their time and
row stock remain fully charged; this argument does not change the volume
moment or make same-width recursion self-justifying.

I separately checked the literal stress word's arithmetic. The forward C
numerators for Gaussian inputs a+ib,c+id are
`a-b+c+d`, `a+b+d-c`, `a+b+c-d`, and `b-a+c+d`, followed by division by two.
Every partial numerator has component magnitude at most four times the
incoming maximum. An e-direction elementary leaf therefore needs e extra
grid bits and at most e+1 magnitude bits, including its temporary registers.
The scalar `(3+i)/4` has numerators `3a-b` and `a+3b`; its largest temporary
is at most four times the incoming maximum. Two such shears conservatively
charge four grid and four internal magnitude bits. These are the literal
register charges, rather than the smaller endpoint-only scalar bound.

The proof depends on several substantive interface conditions:

- Exact child normalization and all-field output semantics are necessary.
  A projectively equal Clifford frame could carry an arbitrarily large
  dyadic scale and would not satisfy the endpoint charge.
- The starting bound must cover all live streams and ancestor scratch,
  including arbitrary dirty values and complete retained copies. Copying
  preserves a numeric bound but does not remove its storage/time charge.
- Fixed global grid buffers must be selected before arithmetic. Exact zero
  trailing grid bits at a returned endpoint are an algebraic fact; they do
  not authorize truncating an overflowing intermediate or uncharged format
  changes.
- Every scalar multiplication/addition temporary, wrapper, inverse word and
  precision conversion must appear in the local prefix budget. An abstract
  unitary endpoint alone supplies no literal register bound.
- The leaf, semantic induction, row allocation and stopped recursion budget
  must refer to the same actual program. The finite stress word has no time
  contraction and cannot stand in for that missing integration.

These requirements are already explicit in the proposed report. I found no
circular appeal to a same-width oracle: child correctness is established at
the strictly smaller budget, not assumed at unchanged `(e,L)`. The review
supports the conditional lemma and its next native-integration test. It does
not promote the existing finite random payload controls to all-size proof,
formal verification, or a kappa improvement.

The two implementation sources reviewed read-only are
`code/transfers/endpoint_guard.py` and `endpoint_guard_literal.py`; their
pinned hashes and complete finite evidence are in the transfer run protocols.
This critique is an independent derivation by the complex-primitives track,
assisted by OpenAI Codex; it imports neither producer and changes neither.
