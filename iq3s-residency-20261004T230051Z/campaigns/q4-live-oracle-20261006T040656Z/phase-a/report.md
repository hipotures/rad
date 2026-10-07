# Phase A — faithful full-runtime logical replay

The final common runtime is oracle-v3, source117bc89b3bacbf263379c336557e6c8aa07aff5e, binary30a31432b5aff51bcd4340900c13cad0c8487a832bfdb22d05f9157b88d5bdb3, frozen Strata0.1.39 ancestry6f32ec070f23ced9f50e704d854d775da52591ab. Original production binary remains unchanged. See schema-v2.md and initial-state-v3-contract.md.

Logical clock: request2 after fixedwarmup request1, verifier window, role(main/MTP catchup/draft), absolute position/speculative lane, main routedlayer eventwindow*48+layer. Each T-by10 complete batch retains natural dependency/concurrency. Causal masks follow position/lane; dense/attention/KV/PLE/GDN/router/expert/shared/head/main/MTP/rejected-branch computation still runs. Override only after actual computation of discrete router/head/QSA decisions. Token chain, probabilities governing draft stopping, acceptance/commit/rollback and all12QSA selection lists are frozen. No hidden activations are substituted.

All48main routedlayers and3expert classes are covered. Full MTP routedsteps are recorded; MTP uses its existing all-resident512expert cache and deterministic sliding attention, with unchanged residency. Physical local/CPU/mapped grouping may differ because this is the treatment. Logical T, token-to-expert assignments, coefficients and attention selection/masks remain fixed. Work hashes exclude service and timestamps; initial numerical/service state has a separate strict identity.

| Profile | Actual input | Visible output | Windows | Main routed invocations | MTP full steps | Main entries | Tape MB | Work SHA256 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
|32k|28378|4096|1289|61872|3563|2200320|528.120|237ee8e7d981129238afaa1a754453d3ecee8087af0c9c1a3f2fc950f9b36fd9|
|128k|126715|4096|1533|73584|4039|2413440|628.424|ba5432b95f973e50ad5cdb644e9667303231e3b46c551572face35b6c788fe7f|
|256k|257781|4096|1628|78144|4199|2491200|667.848|4046f4345f2cf4344bc6c6d2fc066c8cb646e55821de72607161c1cacab666ab|

Prefill runs naturally from the exact saved IDs with reuse0. At decode boundary, native pending admissions are joined, then initial expert slots/heat/adaptation phase and meaningful GDN/PLE/KV/MTP state must match the recorded sidecar. Oracle withdrawal/copies begin only after timed decode starts. Initial-state attestation is setup, measured separately and included in request wall; it is not hidden in PP/TG. Streamed GPU KV payload is redundant with checked canonical host prefix and exact mappings, with native mover tests. Unwritten host tail/unused old MTP ring prefix are excluded as unread.

Output normalization is the actual4096visible emitted/accepted output IDs. Internal KV commit position advances can exceed4096 and include the last prompt input plus end-budget excess; every computed lane is charged and retained, never counted as additional user-visible generated text.

All recordings pass structural/checksum/native-counter/branch/weight/shape/finite-activation conservation. First replay-current guards at32/128/256K match initial state bitwise and show zero natural router/coefficient/QSA/head disagreements. Final oracle arms enforce the identical tape, but natural arithmetic diverges after residency changes. Forced equality is not a math/quality success claim. Existing actual-Q4 CPU/GPU parity passes all3classes at layers0/2/4/24/30 against dequant reference; CPU Q8_K versus GPU Q8_1 activation quantization gives expected small numerical differences.

Earlier v1 pilots did not freeze QSA selections. v2 additionally froze QSA and native adaptation phase, but did not attest numerical KV/GDN state. They remain immutable scoped evidence and are excluded from final v3 headline data. Relative tape path, malformed validator indexing, compile includes and stale-symlink build attempt failures were preserved and repaired in the ledger.

Final same-binary ordinary/replay overhead confirmation was completed after the main matrix, as transparently recorded in the protocol-order limitation below. Recording overhead is diagnostic and never a natural speed arm. Earlier v1 provisional overhead remains separate.

## Final v3 overhead guard

Three paired fresh short-development runs have identical output IDs and MTP trajectories. Median replay/natural decode-time ratio: 1.0243857209086695; request-wall ratio: 1.0963873981514238. Replay-current overhead is small in decode but initial-state checking adds meaningful setup to this short request. Original frozen-binary output matches every experimental natural run: True. See overhead-v3-summary.json.

## MTP catchup structure

Source audit confirms that each actual MTP round first computes KV-only catchup for all T main-window cells, including rejected lanes, then a full one-row MTP routed layer for accepted row a, followed by recorded one-row draft steps. The KV-only prefix has no router or expert kernel. Its call count and T-row shape derive from recorded T and draft_count; all full MTP router/coefficient batches are explicitly recorded. These catchup kernels are computed in both replay arms, not skipped. Prompt MTP prefill remains natural and untaped before the strictly checked initial state.
