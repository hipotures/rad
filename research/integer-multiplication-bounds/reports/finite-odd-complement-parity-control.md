# Small discriminator for the odd-ground complement lead

The parity shortcut proposed in the frozen
[complement-frame note](finite-odd-complement-parity-lead.md) is false:
not every core-two union has even size. A 0.165-second bounded original-DAG
constructor/count test found 72 odd unions of size five at h7, 400 of size
nine at h11, and 720 of size eleven at h13. All used base2 and positions0.
Their logical DAG hashes and exact size histograms are recorded in the
[small control protocol](../runs/20261008T094500Z-finite-odd-complement-parity/protocol.json).

This does **not** disprove the larger complement family. In these three
examples, every odd core-two union has size h-2, hence outside size two.
That special target span has nonsingular Gram matrix I+J. No node with
outside size eight was found, so the stored radical-check branch was not
exercised and no degenerate frame was observed.

The useful next algebraic question is narrower: whether top-level pair
strips give even unions until their last single cross-edge correction,
which yields outside size two. If that structural statement holds for the
whole odd paired DAG, it could exclude the size-eight degeneracy despite
the failed even-union shortcut. It has not been proved or checked on the
final h53 actual clone frames. There is no new role, transfer or exponent
claim from this control. The independently accepted final finite witness
and source-frame result remain unchanged.
