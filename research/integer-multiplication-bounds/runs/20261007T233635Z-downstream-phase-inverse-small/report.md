# Initial phase-cell prototype failure

The first s=15,t=16,u=4 case reached boundary preparation, then failed its overly strict n>2*bandwidth condition. The first and last boundary groups are disjoint at equality, which is the two-cell finite case. This is an implementation domain restriction, not evidence against the Schur hypothesis. The repaired attempt uses fresh paths and records the mathematical reason for n>=2*bandwidth. The original one-neighbour tail choice also needs a wider truncation to meet the deliberately coarse rigorous tail threshold.
