# Actual gauges for right-background frame reuse

The [new interface source](../../code/complex/right_reflected_frame_gauges.py)
retains the exact monomial relation between a canonical `F_E` and the
right-background frame `F_(Eperp)*F`, where `F=C_h`. This supplies consistent
phase representatives for possible cross-body helper reuse. It does not
prove that a whole signed-swap word has a favorable stock or recursive
moment.

The right/left distinction matters. A common right background cancels from
every relative operator:
`(F_G*F)*(F_E*F)^-1=F_G*F_E^-1`. A common left background conjugates the
relative instead. The earlier
[orientation controls](common-background-swap-boundary.md) distinguish
these statements; the left-background counterexamples do not reject the
right-background word.

## Reflection of the diagonal label subspace

Conjugating Pauli labels by `F^-1` maps `(z,x)` to `(z,x+z)` over GF2.
Applying this to

```text
L_E = {(a+b,b) : a in Eperp, b in E}
```

gives `{(a+b,a)}`, which is exactly `L_(Eperp)`. Therefore
`F_E*F` has inverse-Z Lagrangian `L_(Eperp)`, including degenerate E.
No complement disjoint from E or nondegenerate chart is required.

Consequently

```text
G_E = (F_(Eperp)*F)*F_E^-1
```

has mixing rank zero. It is an actual affine binary route with a Z4
quadratic coefficient, not an identity that may be discarded. The source
compiles G using exact Pauli images and the same exact dyadic path-sum
normalization as the independently reviewed scalable compiler. All constants,
affine offsets and routing columns remain in its result.

The pinned endpoints simplify exactly:

```text
G_zero = X_allones,
G_full = I,
G_line(T) = X_(allones XOR T),       for odd T,
G_(Tperp) = X_T,                   for odd T.
```

These use `F^2=X_allones`, `C_T^2=X_T`, and commutation of the endpoint
convolutions. A generic F_E need not be a convolution. For example, for
`n=4, E=span(1,7)`, whose radical contains6,

```text
G_E |y> = i^(1+2y_0+3y_1+2y_3) |8 XOR P*y>,
P columns = [1,6,4,8].
```

That nontrivial route and phase cannot be replaced by a free reflection.

## APIs for adjacent body interfaces

`reflection_gauge(E,n)` returns the exact rank-zero G_E. Its monomial
execution still requires complete payload routing and address-controlled
fourth-root arithmetic, even though it needs no recursive C child.

`compile_canonical_to_right(E,F,n)` returns
`(F_F*F)*F_E^-1`. It first compiles the canonical transition
`E -> Fperp`, then fuses G_(Fperp) into its output route and quadratic.
There is exactly one child, at Grassmann distance `d(E,Fperp)`.

In particular an odd-label RIGHT birth obeys

```text
C_T*F = X_T * (F*C_T^-1) = X_T*F_(Tperp).
```

If a donor subspace satisfies `E subset Tperp`, this interface therefore
pays rank `n-1-dim(E)`. A canonical transition followed by final XOR T
implements it exactly. The simplification holds even if E is degenerate.

`compile_right_to_canonical(E,F,n)` returns a retained rank-zero reflected
gauge inverse followed by the canonical transition `Eperp -> F`. Its
one child pays `d(Eperp,F)`. The two monomial stages are not erased or
assumed to have free input offsets. Both stages' stream executions remain
paid. Complete Pauli-generator equality and a separately evaluated global
coefficient bind the composition to the actual original word.

The APIs describe exact address operators on arbitrary dirty fields.
For f columns, each global fourth-root constant occurs once per column.
The selected child width is the per-column rank; the literal number of
two-by-two tensor factors is rank times f. Wrappers preserve the grid and
component magnitude but still need a native complete-stream implementation.

## Finite evidence and open native obligations

The first one-worker control checks every reflected gauge for all16
dimension-3 subspaces and all20 odd-label nested donor births, totaling
2,304 exact matrix entries. It rejects a corrupted affine gauge. Its
unchanged run is retained separately from the larger controls.

The first full attempt failed in the reverse reference word. The inverse
of `F_E*F` must execute `F_E^-1` followed by `F^-1`; the failed expected
word used the opposite temporal order. Its [run](../../runs/20261009T023551Z-complex-right-gauge-full/report.md)
retains the exact original source hash, traceback and protocol. The
corrected source swaps only those two inverse words. The
[recovery patch](../../fixtures/complex/right-reflected-inverse-order-recovery.patch)
restores the original source byte-for-byte from the corrected source;
isolated `git apply` and both hashes are recorded in the
[recovery receipt](../../configs/complex/right-reflected-recovery.json).
The first bounded attempt exercised reflection and forward births only;
it did not establish reverse interfaces.

The corrected [full attempt](../../runs/20261009T024028Z-complex-right-gauge-repaired/report.md)
adds all67 dimension-4 subspaces, every odd nested birth in that dimension,
and selected dimension16,32,64 gauges and forward/reverse interfaces. All83
reflected gauges and148 forward births pass52,224 small coefficients.
The larger controls pass all1,792 Pauli generator images and their exact
global coefficients. The four-worker run completed in158.658 seconds.
It never promotes sampled origins to a complete convolution test:
generic F_E is not a convolution.

An additional [complete reverse-matrix attempt](../../runs/20261009T024150Z-complex-right-gauge-reverse-matrices/report.md)
checks every20/128 odd nested reverse birth in dimensions3/4, including
34,048 full coefficients of the explicitly multiplied physical operator
`C_T*C_full^-1*F_E^-1`. Two workers completed in1.196 seconds. Its
negative control independently detects the incorrectly reordered
inverse word. The [bounded check](../../runs/20261009T024537Z-complex-right-gauge-ci/report.md)
combines all dimension-3 reflected/forward and reverse interfaces in
0.132 seconds with one worker.

The [eight-case literal fixture](../../fixtures/complex/right-reflected-frame-interfaces.json)
contains arbitrary degenerate reflection, forward and reverse mixed-frame
births and dimension16 cases. It retains all actual words and monomial
stages for independent review. The fixture's source closure is explicit;
[its generator](../../code/complex/make_right_gauge_fixture.py) does not
depend on an external native implementation.

This algebra permits a body-one helper in E to reach a body-two odd RIGHT
birth geodesically when E is contained in the required perpendicular.
It does not guarantee that the donor's old virtual value can be discarded,
that all birth-cut response coefficients are accounted for, or that the
next target clock is causally compatible with that reuse. Those are the
remaining substantive word/stock obligations. Three separately restored
bodies still pay three helper paths against one actual stock; their negative
capacity result is unchanged.

Native routing must retain every affine flip, binary route, quadratic
phase, complete dirty field and guard buffer. Classical compilation of
these wrappers is polynomial metadata work; it does not make their
fixed-tape execution free. No canonical native primitive, conditional
multiplier exponent or larger kappa is certified by this interface alone.

Reproduce bounded exact controls with standard Python:

```sh
python3 -B research/integer-mult-breakthrough/code/complex/verify_right_reflected_interfaces.py --workers 1 --bounded
```

The effective bounded closure includes this verifier, the reflected source,
the pinned scalable interface compiler and its pinned canonical
representative library. Larger discovery uses the reflected source with
four workers without bounded mode and optional fresh output.
This is AI-assisted internal mathematical and finite exact research;
independent literal review is required before promoting any resulting
whole-word capacity claim.
