# Dirty restoration and address-component scope

The literal joint-word verifier checks an invertible binary payload network on
2v endpoint roles and R auxiliary roles. Its `complete_basis_vectors=2v+R`
is the number of independent payload-role basis vectors. It must not be
described as an explicit enumeration of every rational address component.
Rational frame containment, projector identities and transition ranks have
separate exact receipts.

There is a dimension-free restoration identity. Let X, Y and Q be vector spaces
over a field of characteristic two. Let U be any invertible linear map on Q,
A:X→Q the source injection, and B:Q→Y the output scatter. A section executes
U, scatters by B, executes U inverse, and injects by A. On an arbitrary dirty
auxiliary state q, it sends

    (x,y,q) → (x, y+B U q, q+A x).

Executing the same section twice sends

    (x,y,q) → (x, y+B U A x, q).

Thus arbitrary dirty data is restored independently of the dimension of Q,
the number of newly admitted components, and the individual linear operations
used to realize U. The argument needs the actual inverse chronology and
requires source and destination endpoints to remain disjoint from Q. The
transposed complete operator gives the reversed endpoint orientation and the
same absence of auxiliary-state dependence. Both finite orientations are
independently replayed in the word checker.

For an address-aware implementation, Q can be the direct sum of all physical
auxiliary component spaces. Every implemented middle gate must be linear, its
reverse must be its actual inverse, and injection/scatter must be the specified
linear endpoint maps. The identity then applies to every component. This is
an algebraic statement about the implemented binary operators; it does not
reduce rational projector coefficients modulo two.

The restoration identity does not prove that B U A equals the desired source
map. That obligation needs the scalar support reconstruction, actual frame
containment, source and sink compatibility, copied-center identities and the
selected fixed-basis DATA geometry. Nor does the identity establish an all-size
recursive implementation or its cost. Those remain part of the explicitly
inherited conditional transfer, routing, precision, resampling and fixed-tape
assumptions, with all finite rank and moment charges separately certified.

The interval construction is credited to Avi Eisenberg (PR62), invertible joint
synthesis and paid reclamation to eumemic (PR57), and parameter refinement to
Alejandro Zarzuelo Urdiales (PR61). Signed positive-frame and rational-basis
extensions here preserve those contributions. This note was prepared with
Codex assistance.
