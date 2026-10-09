# A full Walsh block is not one cyclic convolution with free diagonal gauges

Status: **SCOPED ANALYTICAL OBSTRUCTION**, supported by **EXACT FINITE
AUTOMORPHISM AND OPERATOR CONTROLS**. This is not a lower bound on arbitrary
convolution algorithms, multiplication, native routing or bilinear encodings.

## Mechanism and leverage

A possible changed supplier would replace a complete line transform on
2^f orbit coordinates by one ordinary cyclic convolution, using only address
permutations and nonzero coordinate factors at its boundaries. Packed integer
products can implement cyclic convolution without recursively calling that
same complex transform. If each packet were strictly smaller than the parent,
this could change the coupling between binary and complex recurrences. Packet
size, full-record layout, coefficient width, fixed-kernel construction and
inverse recovery would still require a new ledger before any exponent claim.

The algebraic first discriminator fails for f>=3, even if all those boundary
permutations and nonzero scalings are granted for free. A single complete
cyclic or negacyclic convolution of length 2^f cannot be monomially equivalent
to the Sylvester Walsh matrix H_f, or to its Gaussian C_f representative.
No parameter sweep of that precise representation is warranted.

This does not refute the existing [nonzero field-core construction](../synthesis/finite-field-cyclic-core.md).
That construction uses length 2^f-1 together with a separately treated zero
coordinate and invertible border operations. It changes the interface covered
here and retains its open native field-order routing and recursive-size bills.
Multiple convolutions, Toeplitz restrictions, larger extensions, sums or
products of structured maps, and nonmonomial input algebras are also outside.

## Elementary cross-ratio argument

Let H_f[x,y]=(-1)^(x dot y), with indices in GF(2)^f. Suppose arbitrary
permutations pi and sigma and nonzero complex factors r_x,c_y give

    r_x c_y H_f[pi(x),sigma(y)] = H_f[x,y].

Divide the equation at (x,y) by its equations at (x,0) and (0,y), and multiply
by its equation at (0,0). All nonzero factors cancel. The remaining identity is

    (pi(x)+pi(0)) dot (sigma(y)+sigma(0)) = x dot y  over GF(2).

Both centered maps are bijections. The right side is additive in x. Subtract
its instances at x, z and x+z; the resulting vector is orthogonal to every
centered sigma(y), hence is zero. Therefore pi(x)+pi(0) is additive and pi is
affine. The same reasoning makes sigma affine, with inverse-transpose linear
parts. The proof allows arbitrary nonzero complex amplitudes, not just signs
or unit phases.

A cyclic convolution matrix commutes with the full coordinate shift S.
Conjugating this simultaneous row/column symmetry through any proposed
monomial equivalence gives a monomial automorphism of H_f whose row permutation
is a single cycle of length 2^f. A negacyclic convolution commutes with the
signed shift; its underlying permutation is the same full cycle. Nonzero
weights on a cyclic shift do not remove this necessary permutation condition.

Such an affine full cycle is impossible for f>=3. Embed an affine map as an
invertible (f+1)-dimensional homogeneous binary matrix B. A cycle of length
2^f makes B have order 2^f. In characteristic two,

    (B-I)^(2^f) = B^(2^f)-I = 0.

Thus B-I is nilpotent and its nilpotence index is at most f+1. Consequently

    B^(2^ceil(log2(f+1))) = I.

For f>=3 this upper bound is strictly smaller than 2^f, a contradiction.
This is an all-size argument; the finite enumeration below is a control of
the generator, conventions and small exceptions, not its proof by sampling.

The actual Gaussian block has entries

    C_f[x,y] = alpha^f (-i)^weight(x xor y)
             = alpha^f D[x] H_f[x,y] D[y],
    alpha=(1+i)/2,  D[x]=(-i)^weight(x).

These nonzero diagonal factors transfer exactly the same obstruction to C_f.
The result concerns one complete block, not a sparse input subspace or an
unpaid change of desired outputs.

## Primary attribution and independent derivation

Egan and Flannery's *Automorphisms of generalized Sylvester Hadamard matrices*
describes affine actions of the full monomial automorphism group. The author
manuscript is dated September 14, 2016; the published article is *Discrete
Mathematics* 340(3), 2017, pp.516-523, DOI10.1016/j.disc.2016.09.014.
[Original author manuscript](https://doras.dcu.ie/31216/1/Automorphisms%20of%20generalized%20Sylvester%20Hadamard%20matrices%20V2.pdf).
The immutable downloaded PDF has SHA-256
`d0eaf7fa44f46c4fb969db357db54f8b61e3c200c4df2a3aaa130ab0aad539c4`.
The campaign's elementary derivation above extends the necessary permutation
argument directly to arbitrary nonzero complex diagonal factors. It does not
claim novelty for the underlying affine automorphism fact.

## Exact controls and recovery

The [standalone source](../../code/obstructions/walsh_cyclic_embedding.py)
exhaustively enumerates all invertible binary matrices and all translations
for f=1,2,3,4. Counts are respectively 2,24,1344,322560 affine maps. Full-cycle
counts are 1,6,0,0; largest power-of-two orders are 2,4,4,8. The expected GL
counts are independently checked by the product of (2^f-2^j).

Complete signed matrix identities are checked for a deterministic sample of
linear maps, including every linear map in the two smallest cases. Binary
increment is affine only in those two cases. An exact signed/permuted Walsh
matrix of order four equals the circulant with first row (1,1,1,-1), preserving
the genuine small positive exception rather than extrapolating the negative.

The [four-worker run](../../runs/20261009T043158Z-walsh-cyclic-embedding/report.md)
retains original protocol and compact complete results. No randomized or
floating-point computation is used. From the repository root:

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/walsh_cyclic_embedding.py --workers 4
python3 -B research/integer-mult-breakthrough/code/obstructions/walsh_cyclic_embedding.py --workers 1 --bounded
```

Use a fresh optional `--output` to retain a new execution. The downloadable
primary input and the exact exhaustive generator are distinct provenance
items. This deduction is subject to internal mathematical review and is not
formal verification or an independently established multiplication exponent.
