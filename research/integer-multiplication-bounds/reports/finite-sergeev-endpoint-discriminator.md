# Exact Sergeev 2012 endpoint-packing discriminator

The faithful p=q=2 endpoint-packing circuit from Igor S. Sergeev's
*On additive complexity of a sequence of matrices*, arXiv:1209.1645v1,
7 September 2012, passes complete formal support and physical/frame checks.
Its actual physical role count is worse than the accepted paired base2
family on every screened small ground. This is a scoped negative for this
2012 implementation and two global point orders. The stronger 2014 IPL
construction was not acquired or implemented, and is not excluded.

The primary source is https://arxiv.org/abs/1209.1645, section2, pages2–3.
The acquired full PDF hash is retained in the run certificate. For p=q=2,
pack the endpoint n into endpoint1: replace x_1a by x_1a+x_na for a other
than2, and x_12 by x_12+x_1n+x_2n. Recurse on n-1. Repair queries containing2
by adding x_1n; queries with exactly one endpoint add the appropriate
leave-one row sum; query {1,n} adds the row2 sum to the old {1,2} query.
The n=4 base is a permutation of the input edges.

Every sum combines disjoint formal supports. The implementation interns equal
sums, computes the exact global common-point graph, uses the accepted positive
envelopes and unchanged retained-controller optimizer/compiler/checker, and
checks every designated physical target. Local CSE reduces n49 from the
paper's recurrence upper bound 11,790 additions to 11,023, still above the
paired comparator's 9,813 additions. Actual roles are screened directly:

| Ground | Paired base2 roles | Endpoint natural roles | Endpoint paired roles |
|---:|---:|---:|---:|
| 8 | 665 | 750 | 761 |
| 12 | 3,804 | 4,144 | 4,317 |
| 20 | 23,839 | 26,074 | 27,552 |

At h20 the natural endpoint circuit has 25,516 additions, 2,024 globally
merged sums and 2,862 retained links; the paired comparator has 22,599
additions and 2,180 links. Additional retention does not offset the addition
increase. These exact small results do not justify a large endpoint sweep.

[finite_sergeev_endpoint.py](../code/finite_sergeev_endpoint.py) is the complete
authored reconstruction. The terminal evidence is
[runs/20261008T051300Z-finite-sergeev-endpoint-small](../runs/20261008T051300Z-finite-sergeev-endpoint-small/).
The run takes 4.580 seconds and uses one owned dynamic reservation, then
releases it. Local n4,5,6,7,10,20,49 maps and global h8,12,20 maps were checked.
No independent final multiplication transfer or dirty stage is claimed for
this uncompetitive comparator.

Reproduce under the campaign math environment with the immutable original
reference and a fresh output path:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python -B code/finite_sergeev_endpoint.py --reference "$REFERENCE" \
  --h 8 12 20 --primary-pdf "$SERGEEV_PDF" --output "$FRESH_OUTPUT"
```

The remaining potentially useful literature direction is a faithful stronger
2014 construction or a distinct decomposition of its endpoint corrections,
with exact global sharing and actual role counts. A failure of the earlier
2012 Kaski tree comparator is separate evidence and is not conflated here.
