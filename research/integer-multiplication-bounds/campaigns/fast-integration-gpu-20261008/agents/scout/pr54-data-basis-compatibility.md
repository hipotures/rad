# Pinned PR54 data geometry and conjugate common bases

The user's explicit authorization released the implementation hold for PR54,
PR53 and PR51. The coordinator acquired immutable public snapshots and verified
PR54 head84eb0b067741dc2690da837743fda06d133da865 against the current remote.
This review consumes that exact implementation only, with Chafik Boukhalfa's
PR54, Avi Eisenberg's PR53, Rohan Arun and retained predecessor credits.
Other mutable campaign-source exclusions remain active.

The [compatibility receipt](gpu-parameter-results/pr54-IJ-conjugate-data-compatibility-20261008T1714.json)
proves that four common basis choices have entrywise identical normalized DATA
matrices: beta23 in{-1,5/108}, beta25 in{-1,5/117}. All four therefore reuse
the retained complete I+J data proof at the same physical order. This is a
universal coordinate identity, not an inference from a few sampled matrices.

For a triple T, original primal1_T and dual(1_T-1/3)/2 have norm one in
H0=I-J/9. Conjugation by L(beta)=I-beta J gives

```
p_T=1_T-3beta*1,
xi_T=(1_T+gamma*1)^T/2,
gamma=(9beta-1)/(3(1-hbeta)).
```

At beta=-1 this is exactly the pinned implementation's primal coordinates
4 inside T and3 outside; dual coordinates1/2-5/[3(h+1)] inside and
-5/[3(h+1)] outside. Their inverse products are

```
x_inside=3(h+1)/[2(3(h+1)-10)],
x_outside=-(h+1)/5.
```

These are the exact coefficients in `copied-fixed/data_corners.cpp` and
`data_recovery.py`. The controlled physical permutation has first47 left
coordinates0,...,22,22,0,...,22 and last47 left coordinates0,...,22,0,0,...,22.
The other factor's row coordinates are i modulo25 and its column coordinates
(528+j) modulo25. The audit compares these actual coordinates directly to
the inherited geometry. No additional gather or arbitrary coordinate order
is introduced.

For conjugate beta-star=(1-9beta)/[9(1-hbeta)], gamma-star=-3beta.
Thus p-star=2xi and xi-star=p/2 for every source. All coordinate products
remain identical and nonzero. Normalizing a tensor null corner by invertible
source-coordinate row/column diagonal scalings yields

```
M[(r,b),(c,d)]=delta(r,c)/z23[r]+delta(b,d)/z25[b]-1.
```

The four complete families consequently agree for every choice of triples.
Copied-center norm and nonzero coordinates were also checked exactly in both
dimensions and both bases. With k=(h-9)/4, a center has p_i=e_i+c1 and
xi_i=v1-k e_i; conjugation gives p-star=-xi/k, xi-star=-k p.

The bounded check executes pinned `geometry()`, including exact rank-cut
controls, the schema and lexical coverage of the retained primary prime
sweep, and all ten primary-prime failures with rational ordered elimination.
The primary sweep covers4,073,290 pairs; all ten exact recovered pairs have
the same ordered profile. Every one of the4,073,300 sources therefore has
nine width-one calls, width21, width17 and middle width481 per data front.
The upstream sweep is retained attributed evidence, not a new scout replay.
No large binary pivot tables or million-pair baseline computation were repeated.

Local profiles still require separate validation. The exact identity
L(beta-star)L(beta)=H0 implies L-star=L^{-T}H0. For every original
H0-orthogonal projector P0, H0P0=P0^T H0, giving

```
L-star P0 (L-star)^(-1) = (L P0 L^(-1))^T.
```

This applies to each unchanged original or signed-frame subspace and to
source/center projectors. Its restricted nondegeneracy is the same original
condition. Transposition preserves rank, but changes the ordered NE profile;
the new actual PR54 DAG must be profiled separately in each basis. This
review certifies data compatibility, not the scalar graph, complete dirty
compiler word, bridge costs, address-prime restrictions or final saving.
