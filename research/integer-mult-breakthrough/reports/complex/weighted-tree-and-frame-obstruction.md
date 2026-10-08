# Joint weighted side sums and their nested-frame obstruction

## Literature-led scalar discriminator

Primary source: Petteri Kaski, Mikko Koivisto, Janne H. Korhonen,
[Fast Monotone Summation over Disjoint Sets](https://arxiv.org/abs/1208.0554v1),
arXiv:1208.0554v1, 2 August 2012, Sections 2.2-2.3. Their generalized
intersection summation allows an input g(I,X) depending on the individualized
intersection I. Projection onto levels of a binary point tree partitions
the source sets; the active target may be restricted to the leaves below
the current source projection. Memoizing those restricted states shares
subcomputations across targets. Our original implementation applies this
recurrence to exact five-subset side coefficients and globally interns
equal weighted supports. No implementation text was copied.

For input five-subset X, choose g(I,X)=-3x_X for |I|=0,4, +x_X for |I|=2,
and zero for odd |I|. The output for S is exactly eight times the desired
even-intersection side correction. Every addition joins disjoint source
supports; source coefficients require two weighted kinds, -3 and +1.
The final target coefficient is uniformly 1/8. This is a scalar DAG,
not a common-frame phase network.

Four independent size cases ran concurrently, with a 10 GiB per-process
virtual-memory cap and exact weighted output checks:

| h | v | Active additions | Unmatched side roles/v | Seconds |
| --- | ---: | ---: | ---: | ---: |
| 10 | 252 | 9279 | 37.821 | 0.033 |
| 12 | 792 | 40043 | 51.559 | 0.211 |
| 16 | 4368 | 350384 | 81.216 | 3.294 |
| 20 | 15504 | 1586466 | 103.326 | 31.475 |

The h20 role ratio exceeds three times the optimistically necessary
mixed-pair envelope at that axis. The method improves the separate-side
scalar screen at small h but is not the immediate target route. Centers,
carrier matching and physical feasibility were not included in those counts.

## Exact obstruction to assigning monotone nondegenerate frames

For a retained scalar node n, let U_n be the F2 span of all source labels
contributing with a nonzero coefficient. Let M_n be the span of all target
labels reachable from that node. Disjoint supports ensure that a source
contribution survives along every retained path; there are no hidden
cancellations. Each target requires its side output to lie in its binary
kernel. Therefore a nested frame assignment would require

    U_n <= F_n <= H_n=M_n^perp.

The radical of H_n is exactly `M_n intersect M_n^perp=rad(M_n)`.
If a nonzero w belongs to both U_n and rad(H_n), then w belongs to F_n
and is orthogonal to every vector of F_n, because F_n is contained in H_n.
Thus F_n is degenerate. No nondegenerate frame can meet both containments.
This is a necessary local obstruction for this DAG and chronology; it is
not a lower bound for an architecture with paid decreases, cancellation,
different scalar sharing, or a changed target schedule.

Exact binary elimination found:

| DAG | Active nodes | Degenerate common kernels | Obstructed nodes |
| --- | ---: | ---: | ---: |
| h8, balanced joins | 1022 | 34 | 18 |
| h8, serial joins | 1247 | 21 | 16 |
| h10, balanced joins | 9783 | 1493 | 685 |
| h12, balanced joins | 41627 | 9975 | 4221 |

The retained certificates contain explicit source-span bases, downstream
target-span bases, radical bases and nonzero forbidden vectors. One
independent toy boundary uses two weight-five source labels 31 and 103
in F2^8. They intersect in three positions, and their sum 120 is the
radical vector of their span. If the downstream kernels intersect in
that span, the necessary frame is degenerate. Labels 31 and 55 instead
intersect in four positions and form a nondegenerate orthogonal span;
this is a targeted negative control.

Independent track C reconstructed every h8 weighted output entry without
importing this producer and accepted node 28 with witness 204 in both U and M,
orthogonal to M. See its [scoped component review](../transfers/five-subset-component-review.md).
Internal agent review is distinct from formal proof.

## Reproduction

```sh
python3 -B research/integer-mult-breakthrough/code/complex/tree_intersection.py \
  --h 12 --output /tmp/fresh-tree-intersection.json
python3 -B research/integer-mult-breakthrough/code/complex/frame_feasibility.py \
  --h 12 --output /tmp/fresh-tree-frame-obstruction.json
python3 -B research/integer-mult-breakthrough/code/complex/test_complex.py
```

Outputs must be new. The tests independently partition all input indices
by their exact target-intersection count, reject a corrupted weighted
output, and distinguish the radical-intersection toy from its orthogonal
control. Scalar correctness and failure of a frame assignment are separate
outcomes. No full characteristic or exponent is asserted.
