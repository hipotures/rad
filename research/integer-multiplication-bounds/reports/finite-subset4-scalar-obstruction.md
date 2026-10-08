# Four-subset labels fail the unchanged binary scalar motif

Four-subset rational labels under H=I-J/16 are orthogonal at intersection
one. The scalar side circuit and point-incidence centers impose a separate
identity. For triple indicators, over F2, B_intersection1+I=A1*A1^T. For
four-subsets the exact parity identity is instead
B_intersection1=A1*A1^T+A3*A3^T. Consequently the proposed unchanged side
and point-center commutator yields A3*A3^T, whose diagonal is zero, and does
not yield the required identity shear.

The [exact discriminator](../runs/20261008T040000Z-finite-subset4-scalar/results/certificate.json)
checks every scalar entry at h6 through h10, with the original triple
identity as a positive control. The missing correction has rank at least
v-h-C(h,3). At h26 this lower bound is 12324, versus only 26 proposed
point-center channels. At h8 and h10 the correction is independently found
to have full ranks 70 and 210 respectively. This is an obstruction to the
unchanged scalar motif; it does not exclude other four-subset identities,
label forms or central factorizations.

A fresh scalar-only disjoint-three-subset recursion also verifies every
formal D-map and supplies unshared role upper counts: h17 143548, h20
313940, h22 491810, h26 1064414 and h28 1492456. Its subclass permits
odd scalar local size without importing the old binary phase frames. Those
counts do not include a valid corrected global scalar motif and imply no
multiplication saving. No large four-subset sweep was launched.

The authored source finite_subset4_scalar_discriminator.py, run protocol,
complete exact certificate and command are retained. Runtime was 0.65
seconds. Reproduction is the protocol's pinned-reference CLI, and the
explicit parity formula is independent of rational frame nondegeneracy.
