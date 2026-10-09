# Actual Gaussian wrapper plans and endpoint controls

Status: **EXACT FINITE OPERATOR CONTROLS** and an explicit **CONDITIONAL NATIVE
WRAPPER PLAN**. The plan retains paid payload routing, fourth-root phases and
one Gaussian child. It does not supply that child's recursive implementation,
a whole scalar chronology, auxiliary stock, or a multiplication exponent.

The [routing contract](native-gl-routing-contract.md) supplies the native cost
for one repeated-column binary transvection under the pinned original complete
stream assumptions. This work binds that contract to the actual compact
normal-form fields. It avoids treating a polynomial descriptor compiler as
payload execution, and avoids treating an audited global phase as a second
physical phase gate.

## Literal temporal plan

For a normal form of ambient dimension h, selected rank r, and f columns, the
plan executes the following stages in order:

1. Implement the inverse input GL matrix by its actual transvection word.
2. Apply the input quadratic fourth-root chirp, including its constant in
   every column.
3. Invoke one C child on the first r slots and f columns, when r is nonzero.
4. Apply the output quadratic fourth-root chirp.
5. Implement the output GL matrix by its actual transvection word.
6. Apply the output affine XOR in every column by paid translations.

The unit metadata `global_unit_exponent` is already the sum of the two
quadratic constants modulo four. The temporal word applies those constants;
the metadata is checked against them and adds no separate phase. In an
f-column tensor, their aggregate is multiplied by f. Adding that metadata as
another gate would double the actual phase and is rejected.

The inverse plan reverses all stages and each self-inverse transvection word,
negates the actual chirps, and uses the inverse C target. An affine offset on
the input of an inverse is retained in its actual stage order. A reflected
right-to-canonical interface has two monomial normal-form stages. The plan
concatenates both complete words and pays for all their GL routes, chirps and
translations. It does not erase an intermediate gauge because its selected
Gaussian rank is zero.

The [plan source](../../code/complex/native_frame_wrapper_plan.py) imports only
the frozen paid-route verifier. It reads the pinned
[canonical interface fixture](../../fixtures/complex/scalable-subspace-normal-forms.json)
and [reflected fixture](../../fixtures/complex/right-reflected-frame-interfaces.json)
as immutable data. It does not import the producers, their path-sum eliminator,
or their frame compiler. Its finite operator reference independently evaluates
the stated compact coefficients, while its temporal reference executes
elementary dyadic C factors and the complete wrapper stages.

## Conditional payload bill

Let g count the plan's actual transvections and s its nonzero affine slots.
With `L=fK`, `V=MR`, `A=ceil(log2(2V))`, and
`delta=min(1,80(f-1)2^-K)`, its complete wrapper cost is bounded by

```text
O((g+s) [V((fK)^tau+1) + M A^3 + delta M A(R+A)]
  + V + M poly(A)).
```

The last terms include all fourth-root phase scans and descriptor setup.
Their polynomial degree is fixed for a fixed local interface. For a single
normal form `g<=2[h(h-1)+3(h-1)]` and `s<=h`; a retained two-stage monomial
interface carries the sum of its actual stage counts. Each GL transvection
temporarily uses an existing third complete address slot in the same role
stream and restores it. No extra scalar payload bank is introduced.

For fixed h>=3, the original long-record and large-guard family reduces this
to `O_h(V((eK)^tau+1))` with `e=hf`. Growing h retains the growing number of
full payload passes. Incomplete slots, an unproved companion range, short
records, small guards and exceptional sorting retain their separate costs
as stated in the routing report. This is a conditional application of the
original routing lemma, not a measured Python time bound.

The child has profile rank r and actual selected-axis count rf. It is one
bulk recursive call, rather than rf separately charged recursive calls. The
finite reference happens to expand it into elementary factors to test the
operator. At r=h it is a same-width child and still needs a decreasing row
budget or another paid termination argument. The plan records this boundary
explicitly; it does not infer contraction from the route.

Unit phases and completed address permutations have no grid or magnitude
charge. Every coefficient field must still have the actual signed encoding
reserve; child excursions, scalar prefixes, buffers and whole dirty-source
endpoints remain in the separate precision proof. A route or a tensor
operator identity cannot provide those missing bounds.

## Complete finite evidence

The [full wrapper run](../../runs/20261009T031039Z-complex-native-wrapper-full/)
uses one and two columns for all 17 immutable fixture cases. Four workers
completed 34 cases in 0.363 seconds. The small n3/n4 cases compare every
complete four-field payload against the tensor normal form, totaling 10,368
forward reference field values and 10,368 inverse field values. Both retained
reverse monomial stages are tested as their whole composite operator. The
n16 cases check every input/output GL basis image, actual stage counts,
profile rank, selected-axis count and tensor constants; they allocate no
complete address arrays and do not independently reconstruct a large
Clifford operator.

The first [bounded run](../../runs/20261009T031018Z-complex-native-wrapper-bounded/)
checks a two-column n3 interface, all 256 forward and 256 inverse field values,
in 0.008 seconds. Corrupt global metadata and a second application of the
aggregate audit phase reject. Source, imported route source and both fixtures
are checked before and after every run.

Separate [endpoint controls](../../code/complex/native_wrapper_endpoints.py)
construct zero-width identity, full-width C, and full-width inverse C plans.
They compare them to a direct tensor kernel depending only on the Hamming
distance of whole addresses. This reference does not obtain its coefficients
from the quadratic normal form. In particular, the inverse endpoint's
per-column constant `-h mod4` is tested against the direct conjugate kernel.

The [endpoint run](../../runs/20261009T031235Z-complex-native-wrapper-endpoints/)
checks 12 controls at h3/h4, one/two columns, and all 4,128 field values in
0.081 seconds with four workers. Every same-width call is flagged, and every
zero-width plan has zero Gaussian children. Inverse execution restores the
original numerators with exactly the trailing zeros required by the full
fixed grid. No numerical truncation, hidden precision reset, or free format
change is used. These controls verify target endpoints; they do not test a
same-width recursive implementation.

```sh
python3 -B research/integer-mult-breakthrough/code/complex/native_frame_wrapper_plan.py \
  --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/complex/native_wrapper_endpoints.py \
  --workers 1 --bounded
```

The wrapper check's closure is its source, `native_gl_routes.py`, and the two
immutable JSON fixtures. The endpoint check additionally imports the wrapper
source but needs no fixture read during execution. Both checks use only the
Python standard library, have no fixed output path, and save optional retained
certificates using exclusive `--output <fresh-path>` creation. Full protocols
pin all source/config/input hashes, Python version, actual launch times and
closure checks. Original execution evidence remains unchanged in task-owned
ignored work with hashes and complete recovery instructions.

The compact frame algebra and independent fixture reviews remain the source
of those actual normal forms. This work supplies their paid wrapper plan and
finite complete-field binding. An independently accepted routing component
would remove a real implementation obligation, while whole network stock,
source/sink chronology and asymptotic transfer still decide whether it yields
a larger kappa. Developed with OpenAI Codex; no formal verification or external
novelty claim is made.
