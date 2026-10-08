# Independent literal review of the four-incidence common frame

Status: **EXACT FINITE COMPONENT REVIEW**. The Gaussian-dyadic operator and
the five-versus-six rank comparison pass. A complete native motif, physical
all-size guard, and improved exponent remain open.

The complex track supplied a shear with incoming graph frame codes 3 and 23,
outgoing graph frame codes 35 and 56, and common Lagrangian basis
`[32,19,10]`. This review reads only the serialized candidate adapters. It
imports none of the producer's source and reconstructs the endpoint matrices,
common operator, geometry and literal complete-payload program independently.

## Geometry and actual phases

An independent enumeration of all isotropic three-dimensional subspaces of
F2^6 gives 135 Lagrangians. The 64 symmetric graph candidates have minimum
total four-incidence rank six. The unique full-space minimum is the supplied
common subspace, with ranks `[1,1,1,2]` totaling five.

The literal common operator is
`F=K_3*Htilde_2`, where `Htilde=(1+i)/2*[[1,1],[1,-1]]` acts on bit two.
The reviewer computes its exact Pauli images `F^-1 Z_j F`. Using the convention
`i^phase * Z^z * X^x`, the labels and phase exponents are
`[(25,3),(10,0),(32,0)]`. Their span is exactly the claimed common Lagrangian.
The phase three on the first image is retained; a symplectic label check
alone would not retain that information.

Each of the four candidate normal forms is reconstructed by a literal
forward C tensor child, full affine input/output record adapters, and
fourth-root pointwise phases. All 64 entries of each eight-by-eight edge
matrix agree exactly with the independently computed physical transition.
The full two-role operator also passes all sixteen physical basis inputs.
Linearity extends those exact fixed-matrix identities to arbitrary Gaussian
dyadic values. Column tensoring extends the operator identity while retaining
every spectator bit and payload field.

No separately normalized irrational Hadamard is executed. The common
Htilde is itself `S*C*S`; the apparent eighth-root normalization is paid by
the C child rather than by a free scalar gate. Every outer phase in the
compiled edge is a fourth-root unit. The nonzero affine offset on the fourth
edge is indispensable. Bulk constants must be summed once per column: its
input constant three contributes `3f mod4`, rather than three once for an
entire f-column call. Both omissions are rejected by the independent controls.

## Full payload, reverse operation and endpoint bounds

The literal adapter moves complete four-field records. After alignment, the
first r slots supply one contiguous selected interval of rf axes. The child
acts on those selected bits; all unselected bits, other slots and full fields
remain present. The four paid child widths are `[f,f,f,2f]`.

The two aligned roles use the identical common frame, so the scalar shear
is a coefficientwise addition at matching complete addresses. The retained
x role and updated y role are both returned through their explicit outgoing
transitions. The independent reverse uses the literal opposite routes,
opposite unit phases, inverse shear, and forward C children wrapped by
`(C^-1)^tensor(t)=(-i)^t Z^tensor(t) C^tensor(t) Z^tensor(t)`.
Every original dirty physical value is restored.

For the elementary finite C implementation, each selected axis adds at most
one denominator and one component-magnitude bit. Unit wrappers and complete
address movement add none; a scalar shear adds at most one magnitude bit.
The x output path has rank mass 2f. The two y dependency paths have rank
mass 3f. Thus an input common grid `2^-p` is sufficient for output grid
`2^-(p+3f)`, and component magnitude increases by at most `3f+1` bits.
These endpoint bounds are checked on the finite payloads. They do not bound
the internal excursion of an eventual fast recursive child.

## Paid routing and scope

The finite array adapters are exact affine permutations. The existing
packed binary linear router and the [paid constant-translation extension](paid-packed-translations.md)
are a conditional implementation path when their complete rectangle,
companion-chunk, record-size, K and descriptor hypotheses hold. The test
layouts with K one or two check semantics; they are not instances of the
`K>=6` packed-router cost theorem. No array timing is promoted to a fixed-tape
implementation or benchmark.

All four local continuation incidences are charged, but their chosen incoming
and outgoing frames are conditions for a surrounding architecture. Costs to
establish or dispose of those conditions have not disappeared. In particular,
the local rank deficit cannot be inserted into a native recurrence before
the full motif, endpoints, row division, helpers, copies, restoration and
child distribution are supplied. This review confirms a real component in
the wider frame family; it does not claim a larger kappa.

## Evidence and reproduction

The four-worker run checked 38,464 forward physical values over complete
four-field arrays, with exact reference comparison and dirty reverse. It
includes f one, two and three, K one and two, both selected positions, and
the f-two/K-two shape beyond the producer's first replay. Runtime was
4.219 seconds. Separate spectator-fiber controls pass. Omitted affine offset,
per-column constant and full payload fields are rejected.

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/lagrangian_component_review.py \
  --workers 1 --small
```

The bounded CI closure is only the [review source](../../code/transfers/lagrangian_component_review.py)
and [serialized candidate fixture](../../fixtures/transfers/four-incidence-gate-witness.json).
It checks four finite shapes, the entire fixed operator, geometry and negative
controls. The [run protocol](../../runs/20261008T222244Z-transfer-lagrangian-component-review/protocol.json)
pins both hashes, the producer result identity, seeds, base revision, exact
command and UTC interval. All compact outcomes are in its results directory.
There are no external execution dependencies.

The proposed component is attributed to the complex track's
[producer report](../complex/noncommuting-lagrangian-component.md). Candidate
data are pinned to its result bytes and source hash in the fixture. This
independent implementation, elementary endpoint bounds and review were
authored with OpenAI Codex. No formal verification, external review or
novelty claim is made.
