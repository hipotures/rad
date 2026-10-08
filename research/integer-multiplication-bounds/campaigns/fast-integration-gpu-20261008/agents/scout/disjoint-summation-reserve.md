# Reserved producer source

Kaski, Koivisto and Korhonen, [Fast Monotone Summation over Disjoint Sets](https://arxiv.org/abs/1208.0554v1),
2012-08-02, arXiv1208.0554v1. The immutable external PDF and hash are in
[input-manifest.json](input-manifest.json).

Their constructive circuit sums p-subsets disjoint from each queried
q-subset using `O((n^p+n^q)log n)` monotone gates. Section2 groups inputs by
binary-tree projection; distinct child projection classes are disjoint.

Campaign fit, inferred here: after fixing center c, source triples become
pairs on h-1 other points, and paired excluded points are queries. This is
the p=q=2 problem. A finite implementation could pad the tree to32 leaves,
prune dummy inputs, and emit explicit disjoint-support labels. Existing
Paureel exclusion trees may already overlap this construction. Before
adoption, count actual paid gates, compatible links and matrix profiles.
The asymptotic theorem supplies no finite23/25 improvement. Keep this reserve
inactive while current-family compute remains productive.
