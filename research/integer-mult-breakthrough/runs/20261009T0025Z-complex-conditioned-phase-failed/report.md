# Failed Gaussian-unit phase convention

The initial bounded control rejected its own literal inverse `(1+i)^(-1)=(1-i)/2`. The exponent at `1+i` was correct, but the fourth-root exponent had the wrong sign when dividing by a power of two. A singleton screen also stopped immediately on its exact reconstruction assertion. No numerical discovery was accepted.

The repair uses `2^(-d)=i^d(1+i)^(-2d)`. Original source and complete failure log are unchanged in the ignored execution directory. The tracked zero-context recovery patch converts the corrected source back to the exact failed hash; apply it only to an isolated copy. The repaired complete screen has its own run ID.
