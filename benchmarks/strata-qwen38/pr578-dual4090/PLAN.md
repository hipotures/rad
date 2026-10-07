# PR578 benchmark execution plan

1. Freeze GitHub main and PR snapshots; same-base clean merge, separate checkouts. COMPLETE.
2. Identical CUDA sm89 Release builds/tests. Model/profile/MTP reused, no downloads.
3. Untouched PR pilot auto capacity load plus warmup and single old32K request; preserve before local diagnostic build use.
4.10 identical greedy correctness prompts on original/optimized helper with same numeric initial slots; collect actual generated token IDs using correctness-only protocol tee, outputs and finish. No speed claim from correctness wrappers.
5. Primary32K sweep, suffixOFF: LS-A, LS-B pcie0.28, PR-LS (opt disabled), H-OLD, H-OPT, H-OPT-FIXED. Fresh start+old4096warmup+3literal old32Kpayloads perconfig. Initial slot count/set fairness mandatory for original/optimized helper.
6. Boundary instrumentation overhead A/B OFF/ON on optimized helper, same payloads and fresh-server warmup. If>1%, all final headline speeds instrumentationOFF; separate diagnostic runs retain overlap snapshots.
7. Secondary lookupON suite for principal layer split/original/optimized helper, otherwise frozen configs.
8. If top2 primary configs within5%,3 independent fresh-server replicates perconfig.
9. Steady decode bestLS/bestOPT (optionalOLD), shared deterministic prompt,1024output minimum/prefer2048, suffixOFF, warmup+3measured. Negative earlyEOS preserved; harness-only prompt adjustment ifneeded.
10. Final context matrix bestLS/bestOPT,3measured+warmup per31400/63400/127000/259500 using old raw requests ifavailable; exact token IDs acrossconfig,256output,reuse0. Atmost3finalists.
11. Report tables/raw audit/config fairness, historical comparisons labeled NOT_CONTROLLED_A_B, recommendation, safely stop all campaign processes.

Preserve all invalid/startup outcomes. No pushes/PRs/oldcheckout writes/model changes. Ramabort12GiB. No PSS1Hz, only outside request timers.

Update afterprimary32K: initialoptimizedwarmup naturalEOS <256 vsoriginal256. AddmatchedFAIR64confirmation (same4096input,64generatedwarmup),originalandoptimizedfixedinitialcapacities,3literaloldrequests each. Use64-outputwarmup forbothfinalists insteadofvariableEOS warmups; diagnosticsmatchFAIR64. Initial6-configsweep remainspreserved andwarmupcount differences flagged; noPRspeedattributionfromunmatchedwarmupwork.
