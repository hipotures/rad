# Static global center frames require full target dimension

**Status: CONDITIONAL RESULT / EXACT AUXILIARY CERTIFICATE. This theorem concerns a rational matrix intertwiner ansatz, not a general physical circuit or multiplication lower bound.**

The global incidence circuit offers very few scalar center channels, but a
physical implementation must reconcile their shared values with distinct
source or target projectors. A proposed extension of the old per-role frame
model permits a single off-diagonal operator acting jointly on all center
channels tensor the address space. The following test rejects a stationary
compressed frame in that ansatz. Dynamic frames and altered boundary geometry
remain open directions.

## Model and statement

Targets T are triples on an h-point set. Retain the source-line projector
P_T=w_T z_T^T/(6(h+1)), with w_T=3*1+1_T and
z_T=3(h+1)1_T-10*1. Let B be an arbitrary rational v-by-r center-channel
scatter matrix, v=binomial(h,3); its target row is b_T. Require every target
row nonzero. A stationary joint address operator P on r channels tensor h
address coordinates must satisfy

    (b_T^T tensor I_h) P = P_T (b_T^T tensor I_h)

for every T. No diagonal, selfadjoint, projector or positivity constraint is
imposed on P. Even this relaxed intertwiner has no solution unless B has
rank v. The same conclusion holds after replacing P_T by I-P_T.

## Proof

Write C for the column space of B in Q^v. From the (i,j) address block of the
intertwiner equation, for every center column b the vector with target entry
B_(T,b)*(P_T)_(i,j) lies in C. Therefore C is invariant under coordinatewise
multiplication by each projector-entry vector.

The diagonal entries are particularly simple:

    (P_T)_(i,i) = alpha + beta*1_(i in T),
    alpha = -5/(h+1),
    beta = (6h+1)/(3(h+1)) != 0.

Since C is a linear space, it is invariant under multiplication by every
point-membership indicator. Fix a target T={a,b,c}. Because B's row T is
nonzero, choose a channel vector f in C with f(T)!=0. Multiplying it
successively by the three membership indicators a,b,c leaves exactly
f(T)*e_T: every indexed set is a triple, so containing all three points
means being T. Thus e_T lies in C for every target, and C=Q^v. Hence
rank(B)=v. For I-P_T, the diagonal affine increment is -beta, still nonzero.

The full-dimensional requirement is sharp in this auxiliary model: choose
B=I_v and P=diag(P_T). That construction has v separate channels and is not
claimed to be a new low-cost implementation.

## Small explicit inconsistency

For point-incidence channels, take five distinct points d,i,j,k,l and targets
T1={d,i,j}, T2={d,k,l}, T3={d,i,k}, T4={d,j,l}. Their signed membership relation
b_T1+b_T2-b_T3-b_T4 is zero. Apply the putative intertwiner to center column d
and address matrix entry (i,j). Its right side is

    (P_T1)_(i,j)+(P_T2)_(i,j)-(P_T3)_(i,j)-(P_T4)_(i,j)=1/2.

Its left side is zero by the membership relation. This supplies a fixed
four-target counterexample independent of h>=5. It rejects any stationary
point-channel operator before solving a large joint matrix system.

The exact program checks these values, the diagonal affine identity and
three-membership target isolation at h=5,6,7,8,23,25. At small dimensions it
also independently performs rational rank elimination on the generated
point- and pair-channel closures. Point channels close through pair and
triple indicators to full dimension; pair channels likewise need triple
coordinates, except where they already have full dimension. Native target
isolation is tested for every triple, without asserting rational ranks from
binary rank computations. The complete four-worker run took about 0.3 s.

## Implication and limits

This changes the research question from 'can a fixed coupled carrier frame
hide the port mismatches?' to 'can a dynamic sequence of joint frames or a
different boundary representation charge those mismatches in aggregate?'
The invariant-space proof blocks the former compressed ansatz even with
arbitrary off-diagonal operators. It does not bound the cost of a dynamic
sequence, authorize an off-diagonal projector in the original native tape
model, or transfer rational scalar remixes to binary payload semantics.

The common-frame native model acts on address permutations of payload banks;
a coupled role-tensor-address matrix is an auxiliary proposal until its
physical semantics are supplied. Therefore this report does not treat the
matrix obstruction as a general lower bound for existing framed networks.
The historical [closed central projection-path bound](../../../integer-multiplication-bounds/reports/downstream-pair-star-central-negative.md)
is a separate constraint with different assumptions.

## Reproduction and provenance

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/static_joint_frame.py \
  --workers 4 --output research/integer-mult-breakthrough/work/synthesis/NEW-RUN/results
```

- [Authored source](../../code/synthesis/static_joint_frame.py), importing the exact rational projector/rank implementation in [global_incidence.py](../../code/synthesis/global_incidence.py).
- [Run and source-hash-bound certificate](../../runs/20261008T213521Z-synthesis-static-joint-frame/results/).
- Target projectors come from the pinned PR58/PR48 fixed-I+J chain described in the [initial incidence report](global-incidence-first-discriminators.md). The intertwiner ansatz, invariant-space proof and four-target witness were developed with OpenAI Codex. No external novelty claim or formal verification is made.

The program is deterministic and requires only standard-library Python.
