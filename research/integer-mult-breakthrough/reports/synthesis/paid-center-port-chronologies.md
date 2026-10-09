# Paid center-basis port chronologies

## Baseline obstruction and test

The new dyadic center/null basis acts reversibly on existing banks with no
zero-initialized temporary. Applying the same basis B to source and sink,
copying coordinate j to coordinate j, and inverting B is nevertheless a
geometric obstruction, independent of scalar cancellations.

Let the physical source for odd label T start at `L_line(T)` and end at full
`D`; let the matched sink start at zero and end at `L_Tperp`. If any scalar
gate joins that source and that sink at frame F, crossed endpoint triangles
bound their total path charge below by

`d(L_line(T),F)+d(F,L_Tperp)+d(zero,F)+d(F,D) >= h+h`.

The first anchor distance is h because odd T is outside `Tperp`; the second
is h by zero/full transversality. Other intermediate gates can only add path
length. Summing one such matched incidence for every original label forces
rank mass at least `W*h`, `W=2v`. Renaming coordinates does not remove this
literal-port premise. This argument holds for the full Lagrangian metric,
not merely graph or nondegenerate projector frames.

The [new complete word](../../code/synthesis/center_basis_port_search.py)
lifts that particular restriction through a **paid** permutation P of the
sink's transformed coordinates. Every middle copy is from source label T to
an orthogonal original sink label S. The scalar chronology is

`B on x and y; P on y; y[P(j)]+=x[j]; P^-1 on y; B^-1 on y and x`.

This exactly gives `y+=x` and restores x for arbitrary initial x and y.
Each basis swap and permutation swap is expanded into three signed shears
and one sign scale. Inverses reverse and invert every actual operation.
Unary scalar scales commute with address frames; their paid gate counts are
retained separately from phase transitions. There are no extra clean banks.

## Discovery evidence

Four workers independently tested h7/h8, batched/interleaved source/sink basis
gates, two strict/plateau alpha sweeps and 128 eligible `L_E` frames per case.
The domain includes full physical anchors, selected pair/source spans and
general possibly degenerate subspaces. Many-label optimization is heuristic;
every binary expansion is solved exactly by min-cut and checked against
independent bounded enumeration controls.

| h | Layout | Middle role swaps | Scalar shear incidences | Best rank mass | W*h |
| ---: | --- | ---: | ---: | ---: | ---: |
| 7 | batched | 18 | 1,333 | 294 | 294 |
| 7 | interleaved | 20 | 1,345 | 294 | 294 |
| 8 | batched | 52 | 3,112 | 896 | 896 |
| 8 | interleaved | 51 | 3,106 | 896 | 896 |

Every complete source/sink scalar column and wrong-middle-copy-sign control
passes its expected result. Independent chronological rank replay counts
every source/sink anchor, incidence, frame transition and final return. It
matches the graph energy. No rank deficit was found. This is a retained
negative discovery, **not** an exhaustive exclusion of other frame assignments,
port matchings, source bases or circuit topologies.

The illustrative homogeneous width moment
`sum_r n_r*r*2^(kappa*(h-r))/(W*h)` is greater than one at `kappa=1e-4` for
each discovered word. This is an optimistic screen only: it omits phase lift
adapters, native routing, scalar precision and full outer assembly. Since rank
mass already equals capacity, those candidate words cannot justify a positive
root in that model. No kappa is asserted.

## Persistence and reproduction

The [completed run](../../runs/20261008T235630Z-synthesis-center-ports/report.md)
contains the exact protocol and compact measurements. The original complete
2,043,085-byte certificate, with all scalar operations and selected frames,
remains unchanged under ignored
`work/synthesis/20261008T235500Z-center-ports/results/certificate.json`, SHA256
`9684fc7054a401c6bb80d75351c95524e85fcdf68c992bceef74597f15d79e80`.
The compact export omits those word/frame rows and identifies their recovery
path. Complete text evidence should follow the repository gzip publication
contract before checkpoint publication; the compact JSON alone is not the
full word certificate.

```bash
python3 -B research/integer-mult-breakthrough/code/synthesis/center_basis_port_search.py --workers 4 --rounds 2 --frames 128 --output research/integer-mult-breakthrough/work/synthesis/<fresh-center-ports>/results
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_center_ports.py --output research/integer-mult-breakthrough/work/synthesis/<fresh-center-check>/check.json
```

The bounded standard-library entrypoint replays both h7 scalar words and
corruptions, checks the orthogonal port matching and paired anchor obstruction,
then independently replays the exact complete zero/full binary cut optimum.
The linked center source and its exact dependency closure are pinned. This
does not rerun the 128-label heuristic discovery or verify literal Gaussian
frame operators.

Its [completed receipt](../../runs/20261009T000914Z-synthesis-center-ci/results/check.json)
pins the exact nine-file standard-library dependency closure, two full words,
84 independent scalar initial columns and all negative controls.

## Next structural direction

Adding more operations to the same complete chronology cannot itself lower
its exact metric optimum. A useful change must replace the topology or fitting
completion. At h7, coloring the complementary pair graph by four stars and
one triangle gives five mutually orthogonal color classes and an integral
rank-five fitting center. Sparse sum/side bases then replace the dense pair
basis. Noncoordinate parity hyperplanes can release many odd source labels
through one lost direction; they can be degenerate and are explicitly eligible
in the next separate experiment. This is a hypothesis about a new complete
word, not a consequence of the current negative.

The complete unchanged word/frame certificate is now published as [gzip evidence](../../evidence/20261009T001615Z-checkpoint-six-34/certificate.json.gz). Decompress it to recover every omitted scalar operation and selected frame.
