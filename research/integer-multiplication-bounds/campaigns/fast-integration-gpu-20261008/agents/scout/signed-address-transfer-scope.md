# Address transfer scope of the signed joint words

The finite signed-word receipts prove a complete F2 **role** matrix identity on `2v+R` basis vectors in each orientation. This dimension counts input, target and auxiliary payload roles. It does not enumerate the physical address domain or prove an implementation on every address. The actual signed frame dimensions and complete rational transition profiles are separately checked. Neither a terminal rank identity nor the source/copied-center endpoint decomposition alone proves dirty address restoration.

The relevant inherited written contract is in Avi Eisenberg's pinned PR #62 source, `ad0f25ff7b23cff7f08ad237c2254e6ecf74257e`:

- `notes/endpoint-gauge-construction.tex`, “Exact lower-triangular conjugation”: nested projector differences, partial-swap identities and commutation of a scalar gate with a common address permutation.
- The same file, “Complementary auxiliary gauges”: a framed scalar word telescopes to `D_out S D_in^{-1}`; on an auxiliary role individually restored by `S`, its residual address action is the corresponding endpoint gauge product for every initial array.
- `notes/structured-bulk-bit.tex`, “Retained scalar and partial-swap contract”: arbitrary dirty scalar cancellation, retained inverse-copy scheduling, complementary auxiliary endpoint gauges and the remaining residual compiler contract.
- `research/pair-assembly/PROOF.md`, “Stacking with PR #57's frame compiler”: the stacked witness retains eumemic's compiler argument and its review status. PR #57's tested construction is `cd350f76c9bc01489ec83568bded532cb69be938`.

The pointwise lift is an exact algebraic implication. For a finite address domain \(\mathcal A\), let \(V=\mathbb F_2^{\mathcal A}\) be the vector space of all payload arrays. A scalar word whose role matrix is \(S\) induces \(S\otimes I_V\) when its XOR operations use corresponding addresses. Therefore a role restored by \(S\) is restored at every address, for arbitrary initial arrays. One does not need to enumerate \(|\mathcal A|\) separate basis vectors to establish this implication.

For actual rational frame \(A\), the nondegenerate projector \(P_A\) defines the involution

\[
D_{P_A}=\begin{pmatrix}I-P_A&P_A\\P_A&I-P_A\end{pmatrix}.
\]

At an eligible address prime this induces an invertible address relabeling. A common relabeling \(G\) commutes with a same-frame XOR because \(G(f+g)=Gf+Gg\) on arrays. If \(G_t\) is the full rolewise relabeling at a compiler step, the framed elementary operation is

\[
G_{t+1}(S_t\otimes I_V)G_t^{-1}.
\]

The complete product telescopes to

\[
G_{\mathrm{out}}(S\otimes I_V)G_{\mathrm{in}}^{-1}.
\]

For nested nondegenerate spaces \(A\subseteq B\), the identities
\(P_BP_A=P_AP_B=P_A\) and
\(D_{P_B}D_{P_A}=D_{P_B-P_A}\) supply the prescribed rank-difference transition. The actual word audit checks containment and a common frame at each executed XOR; exact CRT profiling checks its rational matrix and ordered recursive widths. These facts support the gauge algebra. They do not themselves produce a complete finite physical address-layout replay of the all-size residual compiler.

The required conditional premise is that the inherited residual compiler realizes this complete gauge-conjugated word, with the declared source and sink gauges, in the finite-alphabet fixed-tape model, charging every transition, endpoint correction, inverse copy, cleanup, routing pass and temporary stock. The endpoint action on each restored auxiliary role must match its declared physical output layout. Equal gauges give identity; complementary gauges have product \(D_I\), the prescribed complete interchange, which must be handled under the inherited layout convention. The reverse-complement orientation has the corresponding exchanged gauge obligation. A saved frame table or a correct payload matrix does not authorize silently skipping either obligation.

The signed enlarged frames introduce no new scalar payload identity assumption: the literal F2 word, source labels and copy/scatter instructions are independently replayed. Their nondegenerate positive spaces and actual transitions are also exact finite data. Their address realization nevertheless remains **conditional on the explicit general gauge/residual-compiler transfer contract above**, together with the inherited analytic, routing, precision, resampling, prime-setup and fixed-tape interfaces. This note does not promote that contract to a separately implemented or exhaustively verified address machine.

Credit remains with Avi Eisenberg for the interval/core-aware scalar construction, eumemic for joint synthesis and paid reclamation, Alejandro Zarzuelo Urdiales for PR #61's parameter refinement, and the directly inherited partial-swap, endpoint-gauge, semantic and tape contributors identified in the pinned source notices. The campaign's signed positive-frame and conjugate rational-basis refinements are additions to those constructions. OpenAI Codex assistance is retained.
