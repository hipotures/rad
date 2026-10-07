# Q4 live oracle residency

Fixed logical main/MTP work, identical routing IDs/coefficients/shapes/commit schedule, real same-device RAM-to-VRAM transfers, frozen Q4 capacity/settings. No predictor training. Natural serving baseline stays unchanged.

Start 2026-10-06T04:06:56+00:00; cutoff 2026-10-06T11:21:56+00:00; deadline 2026-10-06T12:06:56+00:00.

## Frozen contract and limits

Only Qwen3.8-Flash-Next UD-Q4_K_XL revision38bb39ee97821de2c9009abb7e93950eec396e66. Original serving Strata0.1.39 source6f32ec070f23ced9f50e704d854d775da52591ab and binaryeca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d remain unchanged. Both4090s, K24, PCIe.28,100usspin,15workers,spec4/.5,INT8,KVresident32768where applicable,prefillauto,lookup/reuseOFF,greedy,serial.

Three total limits32768/131072/262144, exact preserved28378/126715/257781 input IDs,4096 visible output tokens, fixed4096input/64outputwarmup. Main causal matrix REPLAY_CURRENT vs REPLAY_ORACLE_FULL through one common final experimental binary,3fresh paired attempts/context maximum. No favorable retries. One repeated tape/context measures timing repeatability only; substantive independent task separately. Natural/replay overhead guards and one boundedH64live case are separate declared evidence.

All48main layers and3byte classes, real immutable full-RAM source and asynchronous same-device staging/H2D/publication. Five existing physicalspares withdrawn inside timed decode, no extra expert VRAM. Complete main/MTP/QSA logical schedule frozen; real math still computed. Native adaptation unmodified in current arm; oracle sole admission authority inside scope. Full future is privileged knowledge, not a learned predictor or deployable model configuration. Mandatory drain/restoration counted in request wall.

No push/PR,model-weight changes,new model download,sudo,drivers/VM/global/clocks/power changes,paid/external compute,helper/K/pool/MTP tuning or mutation of prior research. Every owned process finite and cleaned up. All new artifacts English. Harddeadline includes reporting/cleanup and is never reset.
