# Final independent review

COMPLETE_REVIEWED_WITH_NEGATIVE_EXPERIMENTAL_OUTCOMES

- Q4 fast build rejected by upstream numerical correctness gate; speed A/B deliberately absent and no patch
- Controlled runtime PP improvement small0.36–2.68% at32–256K; larger tuned PP+60–74% is NOT_CONTROLLED_A_B
- Final selection K24/prefill16384/workers12/pcie.28/spec3/minp.3/K8V4 follows actual confirmed screens, not best single-run cherry picking
- Agent128 full lifecycle has4 negative minimum-output outcomes103/171/97/13; no EOS suppression or claim of full requested length success
- Long8K6324 initial EOS retained; one full8192 retry separately labelled; INT8 negative6777/235 not promoted
- PP evidence GPU timeline GEMM+dequant dominant with both GPUs mostly busy; TG mixed CPU fallback/verify/synchronization; no proof PCIe saturation
- Logical expert file fetch0 differs from physical host SSD traffic hidden by virtiofs; PLE timer not disk-only nor additive wall
- Quality24 literal responses/hashes/diffs plus3 archived IQ3 answers; no automated quality ranking or claim higher bitrate is better
- Needle9 mechanically found at literal actual contexts, not proof general reasoning quality
- IQ3 only64K/256K runtime controls n3; autoK25 both, CLI/model/profile unchanged, no paired prompt identity
- All21 plots actually inspected; split warmup/smoke removed and MTP confirmations separately labelled; agent wall-time drops disclosed as short outputs
- No new production server launched; commands are concrete reproducible configs with tested model flags; quality and general agent reliability remain unproven

All latest user sections0–26 reviewed; machine-readable requirement evidence: final-manual-review.json. Negative/unsupported results are retained experiment outcomes, not passed tests.
