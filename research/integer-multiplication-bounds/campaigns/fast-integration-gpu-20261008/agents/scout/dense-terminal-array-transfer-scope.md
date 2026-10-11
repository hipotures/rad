# Arbitrary source arrays obstruct a signal-only terminal transfer

The proposed transfer from a full common-point frame \(\Gamma_c\) to the
terminal kernel \(K_T\) needs an additional hypothesis about the source
arrays. That hypothesis is absent from the inherited compiler interface.
This rejects that particular justification for omitting a transition; it
does not reject every dense circuit or a different paid scatter schedule.

The source baseline is PR #62 at
`ad0f25ff7b23cff7f08ad237c2254e6ecf74257e`. Its inherited
`upstream/build/sections/03-motifs.tex:147–185` treats each wire as an array
in \(R^\Omega\), applies the scalar circuit pointwise, and conjugates it by
the chosen address frames. The physical input is arbitrary. Interpreting
it through an invertible source frame preserves that freedom. Lines
475–486 give the rational address-shear instance of the same interface.
`notes/copied-centers-lemma.tex:30–38` requires a copy to contain the
complete original role stream, including its control and spectator ranges.
`notes/endpoint-gauge-construction.tex:162–168` retains the prescribed data
terminal gauges.

For triples \(U,T\) meeting only at \(c\), primitive address coordinates
satisfy \(d_U^t w_T=0\). Also,
\[
 P_{\Gamma_c}-P_{K_T}=P_T,
 \qquad D_{P_{\Gamma_c}}=D_{P_{K_T}}D_{P_T}.
\]
Thus a ridge function depending only on \(d_U^t x\) is invariant under the
terminal-source reflection. An arbitrary array associated with the source
role \(U\) need not be such a function. A source's address label is not a
restriction on the values of its array.

The independent check chooses \(U=\{0,1,2\}\),
\(T=\{0,3,4\}\), and an array supported at one address. All other source
arrays vanish, so this is a legal single contribution to the proposed
side sum. Exact rational Gram projectors establish the displayed
projector identity at the actual selected bases \(1/15\) for dimension 23
and \(7/207\) for dimension 25. Reduction modulo 101 gives an explicit
address moved by \(D_{P_T}\). Consequently the delta array is not fixed,
and its images under the two terminal gauges differ. The same test passes
when the delta is replaced by a function of the primitive ridge address.

Old-value cancellation does not remove this difference. Scattering the
old dirty value and then the dirty value plus the signal through the same
\(\Gamma_c\) frame cancels the arbitrary dirty component exactly. The
remaining signal still has the \(\Gamma_c\) gauge, whereas the required
\(K_T\) signal has a different value at the tested output address. The
receipt includes this control and a rational-shear counterexample.

Run the check with the immutable public source snapshot:

```bash
python3 agents/scout/code/check_dense_terminal_array_transfer.py \
  --snapshot "$PINNED_PR62_SNAPSHOT" \
  --output "$FRESH_OUTPUT_JSON"
```

The retained evidence is
[dense-terminal-array-transfer-adversarial-20261008T2150.json](gpu-parameter-results/dense-terminal-array-transfer-adversarial-20261008T2150.json).
The script hashes the inherited contract files, reconstructs the rational
projectors independently, and records both addresses and signal values.
It does not claim to verify another network or its exponent.

A new proposal must either supply a lossless source representation that
really enforces the required restriction and pay its complete volume and
restoration costs, or implement the correct scatter and endpoint operators
on arbitrary arrays. Cancellation across a larger address-aware word is
also a separate question; the single-signal invariance argument does not
establish it.

The underlying array compiler comes from the OpenAI preprint. Avi
Eisenberg contributed the interval-strip construction in PR #62, eumemic
the joint compiler in PR #57, and Alejandro Zarzuelo Urdiales the parameter
refinement in PR #61. Earlier frame and copied-center interfaces retain
their original attribution, including Rohan Arun and Paureel. This scoped
audit was developed with Codex assistance; its conclusions are supported
by the supplied exact controls.
