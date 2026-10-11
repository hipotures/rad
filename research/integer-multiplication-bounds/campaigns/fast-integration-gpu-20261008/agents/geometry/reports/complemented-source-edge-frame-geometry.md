# Complemented source-edge frames

This is a geometric discovery. A complete scalar compiler, literal physical
word, independently reconstructed transitions and conditional recurrence are
separate acceptance requirements.

Fix a common coordinate c. Let T have columns e_c + 2e_i for i != c, and let
H0 = I - J/9. Direct multiplication gives T^T H0 T = 4I. The full positive
common frame Gamma_c is therefore isometric, up to this factor, to ordinary
Euclidean space on its h-1 outside coordinates.

A source triple {c,a,b} has vector (T/2)(e_a + e_b). For a set of actual source
triples, its smallest common address space is T times the column span of the
unsigned edge-incidence vectors e_a + e_b. This statement concerns source
address spaces. It imposes no restriction on the values of source arrays.

The orthogonal complement of that incidence span consists exactly of vectors
z satisfying z_a + z_b = 0 on every source edge. Each bipartite connected
component contributes one signed normal with entries +1 and -1; an isolated
vertex also contributes one normal. A component with an odd cycle contributes
none. These normals have disjoint supports. The address-space rank is

    h - 1 - number of bipartite components, including isolated vertices.

If A lists these normal rows, the exact projector is

    Pi_frame = Pi_Gamma - (T A^T)(4 A A^T)^(-1)(T A^T)^T H0.

For L_beta = I - beta J, its actual rational projector is
L_beta Pi_frame L_beta^(-1). The small normal Gram is diagonal, with entries
four times the component sizes. The representation must explicitly say that
its signed labels describe NORMALS. Reusing a positive-frame label format
without this distinction would give a different space and invalid profiles.

This representation expresses joins that positive signed partitions enlarge
unnecessarily. The spans of {e_a+e_b,e_c+e_d} and
{e_a+e_c,e_b+e_d} have a rank-three join on four coordinates, with normal
(1,-1,-1,1). A containing positive partition representation releases four
independent coordinate directions.

The independent verifier constructs every projector both from the literal
source-incidence basis and from the complemented normal formula. Its receipt
is `../results/complemented-source-edge-frame-controls-20261008T2229.json`:
all 64 graphs on four outside vertices, 32 additional h23/h25 basis cases,
all source-line inclusions and 24 exact nested transition checks passed.
The companion generic rational-constraint receipt is
`../results/rational-one-core-join-controls-20261008T2225.json`.

This does not authorize an uncharged frame shrink, a new dirty-state rule or
the substitution of source-ridge functions for arbitrary inherited inputs.
A new physical compiler must include every source frame and preserve every
literal containment, paid capacity, cleanup and output destination. Its
complete actual ordered child profiles must be recomputed before scoring.

The framework inherits Avi Eisenberg's interval-strip architecture (PR #62),
eumemic's paid joint-frame compiler (PR #57), and the prior source-partition,
whole-chain and rational positive-frame research documented in this campaign.
The present discovery concerns a different address-frame representation;
it does not claim authorship of those inherited scalar or physical networks.
