# Local factors separated by unitary children

Status: **EXACT COUNTEREXAMPLE WITHIN THE STATED NORM CONTRACT**.
This independently explains the local-factor repair in the
[geometric precision contract](../transfers/geometric-nonunit-endpoint-guards.md).
It is not a circuit lower bound or a multiplication exponent claim.

For any integer e>=2, set D=diag(2^e,2^-e) and let S swap the two
coordinates. Execute, in chronological order,

```text
D, S, D^-1, D, S, D^-1.
```

Every child S is unitary and acts on one selected bit. Extend this word
by identical blocks over arbitrary spectator coordinates to obtain an
e-bit complete operator. Every complete endpoint is the identity. Each
child width is one and hence at most e/2. The arbitrary real and imaginary
coefficient components follow from the full linear operator identity.

After the first three gates the complete prefix is
`D^-1 S D=[[0,2^-2e],[2^2e,0]]`, whose Euclidean operator norm is 2^(2e).
All matrices are weighted permutations; their norms are exactly their
largest absolute nonzero entries. The complete word has no larger prefix.
If the two intervening children are omitted before multiplying the local
word, its maximum prefix norm is only 2^e. Its endpoint remains the
identity. Cancellation across the omitted children therefore hides an
exponentially larger actual prefix. In contrast, the product of the
individual local-factor norms is 2^(4e) and safely bounds the word.

The [standard-library checker](../../code/obstructions/interleaved_local_norms.py)
verifies both basis columns and every exact prefix with rational arithmetic.
The full four-worker run covers e=2,4,16,64. The independently launched
bounded invocation covers e=2,8. Removing the second child must change
the endpoint and is a retained negative control.

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/interleaved_local_norms.py --workers 1 --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/interleaved_local_norms.py --workers 4 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/interleaved-norms
```

The original run started at 2026-10-09T07:33:25.321797Z. Its local raw
directory uses the shorter label `20261009T0733Z-interleaved-local-norms`;
the retained protocol preserves the actual start rather than inferring it
from that label. See the
[durable run](../../runs/20261009T073325Z-interleaved-local-norms/report.md).
The complete original JSON evidence is preserved unchanged and published
through the checkpoint's gzip archives. No spectral sampling or machine
floating-point comparison establishes this result. This is AI-assisted
internal research, not external peer review or formal verification.

The conditional geometric precision proof must charge individual local
factors, their actual temporaries and completed child endpoints. Its
O(e) logarithmic bound remains useful when those charges themselves sum
geometrically. Endpoint cancellation alone cannot supply that hypothesis.
