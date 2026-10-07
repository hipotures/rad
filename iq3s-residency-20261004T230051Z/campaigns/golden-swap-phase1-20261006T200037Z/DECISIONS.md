# Decision and attempt ledger

- Start uses goal creation UTC, including initial reads. No deadline reset.

- 2026-10-06T20:05:42.070173+00:00: Candidate budget frozen: multi-horizon logistic C=1 and GBDT32 depth3; no MLP; uniform candidate decision weights; horizons1/4/16/64 windows. Scope all four families. Reserved results excluded from selection. {}

- 2026-10-06T20:07:30.438477+00:00: Integration substrate verified: bbfea295 decomposition-v2 differs from Phase0 capture117bc89 only in typed future views and opt-in unknown handling. Causal branch removes all victim future queries; incoming E64 and first-feasible order unchanged. Current-window safety remains privileged. Scoring cache valid at most one main window; prefix updates invalidate per-layer. Resident age/history omitted, so no stale native-policy placement feature is copied. {}

- 2026-10-06T20:10:33.795925+00:00: Counterbalanced main order and deadline fallback frozen before live timings {"requests": 36}

- 2026-10-06T20:21:22.425062+00:00: CPU stage START {"stage": "compile-offline", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/compile_offline.py"]}

- 2026-10-06T20:21:22.511136+00:00: Compile offline {"command": ["g++", "-O3", "-std=c++20", "-pthread", "-I/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/source/runtime/include", "-I/usr/local/cuda/include", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/offline.cpp", "-L/usr/local/cuda/lib64", "-Wl,-rpath,/usr/local/cuda/lib64", "-lcudart", "-o", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/offline"]}

- 2026-10-06T20:22:16.097525+00:00: CPU stage START {"stage": "compile-offline", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/compile_offline.py"]}

- 2026-10-06T20:22:16.146803+00:00: Compile offline {"command": ["g++", "-O3", "-std=c++20", "-pthread", "-I/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/source/runtime/include", "-I/usr/local/cuda/include", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/offline.cpp", "-L/usr/local/cuda/lib64", "-Wl,-rpath,/usr/local/cuda/lib64", "-lcudart", "-o", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/offline"]}

- 2026-10-06T20:22:18.216933+00:00: Compile scorer-fixture {"command": ["g++", "-O3", "-std=c++20", "-pthread", "-I/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/source/runtime/include", "-I/usr/local/cuda/include", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/tests/scorer_fixture.cpp", "-L/usr/local/cuda/lib64", "-Wl,-rpath,/usr/local/cuda/lib64", "-lcudart", "-o", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/scorer-fixture"]}

- 2026-10-06T20:22:18.933477+00:00: Compile history-fixture {"command": ["g++", "-O3", "-std=c++20", "-pthread", "-I/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/source/runtime/include", "-I/usr/local/cuda/include", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/tests/history_fixture.cpp", "-L/usr/local/cuda/lib64", "-Wl,-rpath,/usr/local/cuda/lib64", "-lcudart", "-o", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/history-fixture"]}

- 2026-10-06T20:22:19.649439+00:00: Compile policy-fixture {"command": ["g++", "-O3", "-std=c++20", "-pthread", "-I/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/source/runtime/include", "-I/usr/local/cuda/include", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/tests/policy_fixture.cpp", "-L/usr/local/cuda/lib64", "-Wl,-rpath,/usr/local/cuda/lib64", "-lcudart", "-o", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/policy-fixture"]}

- 2026-10-06T20:22:21.117144+00:00: Compile information-fixture {"command": ["g++", "-O3", "-std=c++20", "-pthread", "-I/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/source/runtime/include", "-I/usr/local/cuda/include", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/tests/information_fixture.cpp", "-L/usr/local/cuda/lib64", "-Wl,-rpath,/usr/local/cuda/lib64", "-lcudart", "-o", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/information-fixture"]}

- 2026-10-06T20:22:23.127988+00:00: CPU stage COMPLETE {"stage": "compile-offline"}

- 2026-10-06T20:22:23.135318+00:00: CPU stage START {"stage": "scorer-parity", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/test_scorer.py"]}

- 2026-10-06T20:22:24.302776+00:00: CPU stage COMPLETE {"stage": "scorer-parity"}

- 2026-10-06T20:22:24.309899+00:00: CPU stage START {"stage": "policy-fixture", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/policy-fixture"]}

- 2026-10-06T20:22:24.318410+00:00: CPU stage COMPLETE {"stage": "policy-fixture"}

- 2026-10-06T20:22:24.321038+00:00: CPU stage START {"stage": "full-reference-regression", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/information-fixture"]}

- 2026-10-06T20:22:25.087313+00:00: CPU stage COMPLETE {"stage": "full-reference-regression"}

- 2026-10-06T20:22:25.094564+00:00: CPU stage START {"stage": "learning-curves", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/diagnostics.py"]}

- 2026-10-06T20:22:26.261801+00:00: CPU stage COMPLETE {"stage": "learning-curves"}

- 2026-10-06T20:22:26.269321+00:00: CPU stage START {"stage": "offline-smoke", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/offline_campaign.py", "smoke"]}

- 2026-10-06T20:22:31.845753+00:00: CPU stage COMPLETE {"stage": "offline-smoke"}

- 2026-10-06T20:22:31.848295+00:00: CPU stage START {"stage": "offline-competition", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/offline_campaign.py", "competition"]}

- 2026-10-06T20:22:38.813667+00:00: First offline compile failed: vector heat passed to pointer API; corrected simulator adapter to heat.data(). Failure preserved in logs/compile-offline.log. No models, labels, threshold or policy change; no measurements existed. {}

- 2026-10-06T20:23:29.755089+00:00: Preserve initial smoke evaluator outputs under phase-tagged directories to avoid path collision in full competition. Smoke and competition evidence retained separately; deterministic repeats are not live timing attempts. {}

- 2026-10-06T20:24:00.866019+00:00: CPU stage START {"stage": "offline-competition", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/offline_campaign.py", "competition"]}

- 2026-10-06T20:24:01.007407+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-heg-full"}

- 2026-10-06T20:24:01.009575+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-heg-native-0.2"}

- 2026-10-06T20:24:01.014932+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-heg-native-0.5"}

- 2026-10-06T20:24:01.016976+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-heg-recency-0.2"}

- 2026-10-06T20:24:01.019362+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-heg-recency-0.5"}

- 2026-10-06T20:24:01.021864+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-heg-logistic-0.2"}

- 2026-10-06T20:24:01.024040+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-heg-logistic-0.5"}

- 2026-10-06T20:24:01.026317+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-heg-tree-0.2"}

- 2026-10-06T20:24:01.028630+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-heg-tree-0.5"}

- 2026-10-06T20:28:07.318141+00:00: Bounded pre-reserved repair justified: risk-only guard was effectively inactive; improved miss counts carried excessive churn/copy traffic. Add common amortization veto using already computed oracle incoming count, predicted victim risk and prefix rate. Native/recency receive matched veto. Incoming E64/order/first-feasible ranking and physical allocator unchanged. Cost proxy assumes40us net gain per demanded entry (not measured exclusive latency); staging25GB/s+H2D13.2GB/s copy cost. No new models or fit; no reserved result viewed. {"version": "cost-guard-v2", "evidence": "results/guard-diagnosis-v1.json"}

- 2026-10-06T20:28:37.623688+00:00: CPU stage START {"stage": "compile-offline", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/compile_offline.py"]}

- 2026-10-06T20:28:37.673806+00:00: Compile offline {"command": ["g++", "-O3", "-std=c++20", "-pthread", "-I/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/source/runtime/include", "-I/usr/local/cuda/include", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/offline.cpp", "-L/usr/local/cuda/lib64", "-Wl,-rpath,/usr/local/cuda/lib64", "-lcudart", "-o", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/offline"]}

- 2026-10-06T20:28:39.691889+00:00: Compile scorer-fixture {"command": ["g++", "-O3", "-std=c++20", "-pthread", "-I/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/source/runtime/include", "-I/usr/local/cuda/include", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/tests/scorer_fixture.cpp", "-L/usr/local/cuda/lib64", "-Wl,-rpath,/usr/local/cuda/lib64", "-lcudart", "-o", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/scorer-fixture"]}

- 2026-10-06T20:28:40.407687+00:00: Compile history-fixture {"command": ["g++", "-O3", "-std=c++20", "-pthread", "-I/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/source/runtime/include", "-I/usr/local/cuda/include", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/tests/history_fixture.cpp", "-L/usr/local/cuda/lib64", "-Wl,-rpath,/usr/local/cuda/lib64", "-lcudart", "-o", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/history-fixture"]}

- 2026-10-06T20:28:41.073503+00:00: Compile policy-fixture {"command": ["g++", "-O3", "-std=c++20", "-pthread", "-I/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/source/runtime/include", "-I/usr/local/cuda/include", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/tests/policy_fixture.cpp", "-L/usr/local/cuda/lib64", "-Wl,-rpath,/usr/local/cuda/lib64", "-lcudart", "-o", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/policy-fixture"]}

- 2026-10-06T20:28:42.440528+00:00: Compile information-fixture {"command": ["g++", "-O3", "-std=c++20", "-pthread", "-I/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/source/runtime/include", "-I/usr/local/cuda/include", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/tests/information_fixture.cpp", "-L/usr/local/cuda/lib64", "-Wl,-rpath,/usr/local/cuda/lib64", "-lcudart", "-o", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/information-fixture"]}

- 2026-10-06T20:28:44.353008+00:00: CPU stage COMPLETE {"stage": "compile-offline"}

- 2026-10-06T20:28:44.360254+00:00: CPU stage START {"stage": "scorer-parity", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/test_scorer.py"]}

- 2026-10-06T20:28:45.226651+00:00: CPU stage COMPLETE {"stage": "scorer-parity"}

- 2026-10-06T20:28:45.233910+00:00: CPU stage START {"stage": "policy-fixture", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/policy-fixture"]}

- 2026-10-06T20:28:45.242412+00:00: CPU stage COMPLETE {"stage": "policy-fixture"}

- 2026-10-06T20:28:45.244797+00:00: CPU stage START {"stage": "full-reference-regression", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/information-fixture"]}

- 2026-10-06T20:28:45.760338+00:00: CPU stage COMPLETE {"stage": "full-reference-regression"}

- 2026-10-06T20:28:45.767524+00:00: CPU stage START {"stage": "offline-smoke", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/offline_campaign.py", "smoke"]}

- 2026-10-06T20:29:39.180974+00:00: CPU stage COMPLETE {"stage": "offline-smoke"}

- 2026-10-06T20:29:39.184361+00:00: CPU stage START {"stage": "offline-competition", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/offline_campaign.py", "competition"]}

- 2026-10-06T20:32:32.667149+00:00: Final bounded pre-reserved development repair: v2 smoke recency/logistic have134315/135795 nonlocal vs94380 current, 11.2/11.9GB copies vs36.2GB; seven million rejects and24.5s selection. Lower proxy copy floor using160us assumed net entry benefit rather than40us (roughly2.2 rather than8.9 entries in smallest class). This is an assumed operating point, not measured exclusiveCPU cost. Cache same-layer eligible victim within the same logical event/ownership generation, and skip provably under-floor incoming candidates before victim scoring. Same guard/cache in both cheap controls and learned policies. No additional tuning after this version; all negative and interrupted results retained. {"version": "cost-guard-v3"}

- 2026-10-06T20:32:32.710666+00:00: CPU stage START {"stage": "compile-offline", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/compile_offline.py"]}

- 2026-10-06T20:32:32.760096+00:00: Compile offline {"command": ["g++", "-O3", "-std=c++20", "-pthread", "-I/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/source/runtime/include", "-I/usr/local/cuda/include", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/offline.cpp", "-L/usr/local/cuda/lib64", "-Wl,-rpath,/usr/local/cuda/lib64", "-lcudart", "-o", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/offline"]}

- 2026-10-06T20:32:34.779099+00:00: Compile scorer-fixture {"command": ["g++", "-O3", "-std=c++20", "-pthread", "-I/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/source/runtime/include", "-I/usr/local/cuda/include", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/tests/scorer_fixture.cpp", "-L/usr/local/cuda/lib64", "-Wl,-rpath,/usr/local/cuda/lib64", "-lcudart", "-o", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/scorer-fixture"]}

- 2026-10-06T20:32:35.495305+00:00: Compile history-fixture {"command": ["g++", "-O3", "-std=c++20", "-pthread", "-I/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/source/runtime/include", "-I/usr/local/cuda/include", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/tests/history_fixture.cpp", "-L/usr/local/cuda/lib64", "-Wl,-rpath,/usr/local/cuda/lib64", "-lcudart", "-o", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/history-fixture"]}

- 2026-10-06T20:32:36.161240+00:00: Compile policy-fixture {"command": ["g++", "-O3", "-std=c++20", "-pthread", "-I/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/source/runtime/include", "-I/usr/local/cuda/include", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/tests/policy_fixture.cpp", "-L/usr/local/cuda/lib64", "-Wl,-rpath,/usr/local/cuda/lib64", "-lcudart", "-o", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/policy-fixture"]}

- 2026-10-06T20:32:37.529045+00:00: Compile information-fixture {"command": ["g++", "-O3", "-std=c++20", "-pthread", "-I/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/source/runtime/include", "-I/usr/local/cuda/include", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/tests/information_fixture.cpp", "-L/usr/local/cuda/lib64", "-Wl,-rpath,/usr/local/cuda/lib64", "-lcudart", "-o", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/information-fixture"]}

- 2026-10-06T20:32:39.389595+00:00: CPU stage COMPLETE {"stage": "compile-offline"}

- 2026-10-06T20:32:39.396900+00:00: CPU stage START {"stage": "scorer-parity", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/test_scorer.py"]}

- 2026-10-06T20:32:40.278224+00:00: CPU stage COMPLETE {"stage": "scorer-parity"}

- 2026-10-06T20:32:40.285691+00:00: CPU stage START {"stage": "policy-fixture", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/policy-fixture"]}

- 2026-10-06T20:32:40.294297+00:00: CPU stage COMPLETE {"stage": "policy-fixture"}

- 2026-10-06T20:32:40.297294+00:00: CPU stage START {"stage": "full-reference-regression", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/information-fixture"]}

- 2026-10-06T20:32:40.812935+00:00: CPU stage COMPLETE {"stage": "full-reference-regression"}

- 2026-10-06T20:32:40.820200+00:00: CPU stage START {"stage": "offline-smoke", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/offline_campaign.py", "smoke"]}

- 2026-10-06T20:32:44.643305+00:00: CPU stage COMPLETE {"stage": "offline-smoke"}

- 2026-10-06T20:32:44.646118+00:00: CPU stage START {"stage": "offline-competition", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/offline_campaign.py", "competition"]}

- 2026-10-06T20:38:14.826164+00:00: Repair selection export circular reference by copying winning score record; no model, policy, evaluator, threshold or result changes {}

- 2026-10-06T20:38:14.848172+00:00: CPU stage START {"stage": "offline-competition", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/offline_campaign.py", "competition"]}

- 2026-10-06T20:38:14.971422+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-heg-full"}

- 2026-10-06T20:38:14.973903+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-heg-native-0.2"}

- 2026-10-06T20:38:14.979157+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-heg-native-0.5"}

- 2026-10-06T20:38:14.981277+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-heg-recency-0.2"}

- 2026-10-06T20:38:14.983367+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-heg-recency-0.5"}

- 2026-10-06T20:38:14.985577+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-heg-logistic-0.2"}

- 2026-10-06T20:38:14.987740+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-heg-logistic-0.5"}

- 2026-10-06T20:38:14.990251+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-heg-tree-0.2"}

- 2026-10-06T20:38:14.992720+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-heg-tree-0.5"}

- 2026-10-06T20:38:15.002991+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "math-rational-full"}

- 2026-10-06T20:38:15.005080+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "math-rational-native-0.2"}

- 2026-10-06T20:38:15.007200+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "math-rational-native-0.5"}

- 2026-10-06T20:38:15.009303+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "math-rational-recency-0.2"}

- 2026-10-06T20:38:15.011461+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "math-rational-recency-0.5"}

- 2026-10-06T20:38:15.013724+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "math-rational-logistic-0.2"}

- 2026-10-06T20:38:15.016026+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "math-rational-logistic-0.5"}

- 2026-10-06T20:38:15.018335+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "math-rational-tree-0.2"}

- 2026-10-06T20:38:15.020685+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "math-rational-tree-0.5"}

- 2026-10-06T20:38:15.048071+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "text-http-full"}

- 2026-10-06T20:38:15.050321+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "text-http-native-0.2"}

- 2026-10-06T20:38:15.052442+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "text-http-native-0.5"}

- 2026-10-06T20:38:15.054577+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "text-http-recency-0.2"}

- 2026-10-06T20:38:15.056727+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "text-http-recency-0.5"}

- 2026-10-06T20:38:15.059000+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "text-http-logistic-0.2"}

- 2026-10-06T20:38:15.061272+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "text-http-logistic-0.5"}

- 2026-10-06T20:38:15.063624+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "text-http-tree-0.2"}

- 2026-10-06T20:38:15.065962+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "text-http-tree-0.5"}

- 2026-10-06T20:38:15.074406+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "mixed-build-full"}

- 2026-10-06T20:38:15.076711+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "mixed-build-native-0.2"}

- 2026-10-06T20:38:15.078927+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "mixed-build-native-0.5"}

- 2026-10-06T20:38:15.081169+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "mixed-build-recency-0.2"}

- 2026-10-06T20:38:15.083714+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "mixed-build-recency-0.5"}

- 2026-10-06T20:38:15.086585+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "mixed-build-logistic-0.2"}

- 2026-10-06T20:38:15.089002+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "mixed-build-logistic-0.5"}

- 2026-10-06T20:38:15.091431+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "mixed-build-tree-0.2"}

- 2026-10-06T20:38:15.093789+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "mixed-build-tree-0.5"}

- 2026-10-06T20:38:15.104371+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-queue-full"}

- 2026-10-06T20:38:15.106688+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-queue-native-0.2"}

- 2026-10-06T20:38:15.108930+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-queue-native-0.5"}

- 2026-10-06T20:38:15.111435+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-queue-recency-0.2"}

- 2026-10-06T20:38:15.113763+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-queue-recency-0.5"}

- 2026-10-06T20:38:15.116248+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-queue-logistic-0.2"}

- 2026-10-06T20:38:15.118640+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-queue-logistic-0.5"}

- 2026-10-06T20:38:15.120922+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-queue-tree-0.2"}

- 2026-10-06T20:38:15.123450+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "code-queue-tree-0.5"}

- 2026-10-06T20:38:15.133078+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "math-sensor-full"}

- 2026-10-06T20:38:15.135388+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "math-sensor-native-0.2"}

- 2026-10-06T20:38:15.137599+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "math-sensor-native-0.5"}

- 2026-10-06T20:38:15.139957+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "math-sensor-recency-0.2"}

- 2026-10-06T20:38:15.142319+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "math-sensor-recency-0.5"}

- 2026-10-06T20:38:15.144597+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "math-sensor-logistic-0.2"}

- 2026-10-06T20:38:15.146857+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "math-sensor-logistic-0.5"}

- 2026-10-06T20:38:15.149174+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "math-sensor-tree-0.2"}

- 2026-10-06T20:38:15.151527+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "math-sensor-tree-0.5"}

- 2026-10-06T20:38:15.167078+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "text-tls-full"}

- 2026-10-06T20:38:15.169632+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "text-tls-native-0.2"}

- 2026-10-06T20:38:15.171826+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "text-tls-native-0.5"}

- 2026-10-06T20:38:15.174014+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "text-tls-recency-0.2"}

- 2026-10-06T20:38:15.176199+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "text-tls-recency-0.5"}

- 2026-10-06T20:38:15.178503+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "text-tls-logistic-0.2"}

- 2026-10-06T20:38:15.180820+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "text-tls-logistic-0.5"}

- 2026-10-06T20:38:15.183229+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "text-tls-tree-0.2"}

- 2026-10-06T20:38:15.185609+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "text-tls-tree-0.5"}

- 2026-10-06T20:38:15.195468+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "mixed-fields-full"}

- 2026-10-06T20:38:15.197811+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "mixed-fields-native-0.2"}

- 2026-10-06T20:38:15.200063+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "mixed-fields-native-0.5"}

- 2026-10-06T20:38:15.202332+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "mixed-fields-recency-0.2"}

- 2026-10-06T20:38:15.204664+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "mixed-fields-recency-0.5"}

- 2026-10-06T20:38:15.207175+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "mixed-fields-logistic-0.2"}

- 2026-10-06T20:38:15.210101+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "mixed-fields-logistic-0.5"}

- 2026-10-06T20:38:15.212771+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "mixed-fields-tree-0.2"}

- 2026-10-06T20:38:15.215362+00:00: Reuse completed identical deterministic offline point after artifact-path repair {"label": "mixed-fields-tree-0.5"}

- 2026-10-06T20:38:15.218136+00:00: Runtime finalist frozen before reserved evaluation {"policy": "logistic", "threshold": 0.5, "calibration_mean_proxy": 0.7675074278387561, "calibration_task_wins": 4, "selection_scope": "All four families, predeclared; development fit and calibration operating point only", "candidates": [{"policy": "native", "threshold": 0.2, "calibration_mean_proxy": 0.753096877581815, "calibration_task_wins": 4}, {"policy": "native", "threshold": 0.5, "calibration_mean_proxy": 0.753099370081815, "calibration_task_wins": 4}, {"policy": "recency", "threshold": 0.2, "calibration_mean_proxy": 0.7554621733766707, "calibration_task_wins": 4}, {"policy": "recency", "threshold": 0.5, "calibration_mean_proxy": 0.7554241608766706, "calibration_task_wins": 4}, {"policy": "logistic", "threshold": 0.2, "calibration_mean_proxy": 0.7675188028387561, "calibration_task_wins": 4}, {"policy": "logistic", "threshold": 0.5, "calibration_mean_proxy": 0.7675074278387561, "calibration_task_wins": 4}, {"policy": "tree", "threshold": 0.2, "calibration_mean_proxy": 0.7683209386175351, "calibration_task_wins": 4}, {"policy": "tree", "threshold": 0.5, "calibration_mean_proxy": 0.7683269886175351, "calibration_task_wins": 4}], "cheap_reference": {"policy": "native", "threshold": 0.2, "calibration_mean_proxy": 0.753096877581815, "calibration_task_wins": 4}, "promising": true, "version": "cost-guard-v3", "copy_cost_assumptions": {"staging_GB_s": 25, "H2D_GB_s": 13.2, "assumed_net_entry_gain_us": 160}, "checkpoint_sha256": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e", "ranking_weights": [1, 0.5, 0.25, 0.125], "fallback": "Invalid scores use same causal native-heat proxy; no victim-future fallback", "frozen_utc": "2026-10-06T20:38:15.217799+00:00"}

- 2026-10-06T20:38:15.263751+00:00: CPU stage COMPLETE {"stage": "offline-competition"}

- 2026-10-06T20:38:15.266599+00:00: CPU stage START {"stage": "offline-reserved", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/offline_campaign.py", "reserved"]}

- 2026-10-06T20:38:35.876786+00:00: CPU stage COMPLETE {"stage": "offline-reserved"}

- 2026-10-06T20:38:35.879407+00:00: CPU stage START {"stage": "prediction-reserved", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/train.py", "--evaluate-reserved"]}

- 2026-10-06T20:45:18.048306+00:00: CPU stage COMPLETE {"stage": "prediction-reserved"}

- 2026-10-06T20:46:08.137768+00:00: Repair summary reader for initial legacy progress record lacking message field; frozen evaluation unchanged {}

- 2026-10-06T20:46:08.235691+00:00: Integration stage START {"stage": "build-runtime", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/build_runtime.py"]}

- 2026-10-06T20:46:08.416376+00:00: Isolated runtime build step {"command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/cmake", "-S", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/source/runtime", "-B", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/runtime", "-G", "Ninja", "-DCMAKE_MAKE_PROGRAM=/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/ninja", "-DCMAKE_BUILD_TYPE=Release", "-DSTRATA_ENABLE_CUDA=ON", "-DCMAKE_CUDA_ARCHITECTURES=89", "-DSTRATA_GGML_DIR=/srv/ai/benchmarks/strata-qwen38/pr578-dual4090-refresh-20261004T124028Z/vendor/ggml-org-llama.cpp-3cf0325", "-DSTRATA_BUILD_TESTS=ON"]}

- 2026-10-06T20:46:13.348850+00:00: Isolated runtime build step {"command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/cmake", "--build", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/runtime", "-j", "8"]}

- 2026-10-06T20:47:15.690519+00:00: Integration stage COMPLETE {"stage": "build-runtime"}

- 2026-10-06T20:47:15.691055+00:00: Integration stage START {"stage": "safety", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/safety.py"]}

- 2026-10-06T20:47:15.742453+00:00: Safety fixture build {"command": ["g++", "-O2", "-std=c++20", "-pthread", "-I/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/source/runtime/include", "-I/usr/local/cuda/include", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/tests/cost_guard_fixture.cpp", "-L/usr/local/cuda/lib64", "-Wl,-rpath,/usr/local/cuda/lib64", "-lcudart", "-o", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/cost_guard-fixture"]}

- 2026-10-06T20:47:17.109906+00:00: Safety fixture build {"command": ["g++", "-O2", "-std=c++20", "-pthread", "-I/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/source/runtime/include", "-I/usr/local/cuda/include", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/tests/oracle_fixture.cpp", "-L/usr/local/cuda/lib64", "-Wl,-rpath,/usr/local/cuda/lib64", "-lcudart", "-o", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/oracle-fixture"]}

- 2026-10-06T20:49:02.705699+00:00: Real-copy learned fixture failure localized to mocked protection mutation at unchanged logical event. Fixed fixture to advance event when releasing protection, matching immutable replay contract; frozen runtime binary/source/model/guard unchanged; old failed log and fixture preserved {}

- 2026-10-06T20:49:02.759946+00:00: Safety fixture build {"command": ["g++", "-O2", "-std=c++20", "-pthread", "-I/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/source/runtime/include", "-I/usr/local/cuda/include", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/tests/cost_guard_fixture.cpp", "-L/usr/local/cuda/lib64", "-Wl,-rpath,/usr/local/cuda/lib64", "-lcudart", "-o", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/cost_guard-fixture"]}

- 2026-10-06T20:49:04.127469+00:00: Safety fixture build {"command": ["g++", "-O2", "-std=c++20", "-pthread", "-I/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/source/runtime/include", "-I/usr/local/cuda/include", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/tests/oracle_fixture.cpp", "-L/usr/local/cuda/lib64", "-Wl,-rpath,/usr/local/cuda/lib64", "-lcudart", "-o", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/builds/oracle-fixture"]}

- 2026-10-06T20:49:34.252160+00:00: Integration stage START {"stage": "live-identity-check", "command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/live.py", "check"]}

- 2026-10-06T20:49:34.570119+00:00: Integration stage COMPLETE {"stage": "live-identity-check"}

- 2026-10-06T20:49:34.570719+00:00: Development preflight command {"command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/live.py", "point", "--task", "math-rational", "--arm", "REPLAY_CURRENT", "--label", "preflight-math-rational-REPLAY_CURRENT"]}

- 2026-10-06T20:49:34.830076+00:00: Live attempt START {"task": "math-rational", "arm": "REPLAY_CURRENT", "label": "preflight-math-rational-REPLAY_CURRENT", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T20:52:06.472252+00:00: Live attempt END {"label": "preflight-math-rational-REPLAY_CURRENT", "valid": true, "operating_s": 151.58871116198134, "error": null}

- 2026-10-06T20:52:06.530638+00:00: Development preflight command {"command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/live.py", "point", "--task", "math-rational", "--arm", "ORACLE_FULL", "--label", "preflight-math-rational-ORACLE_FULL"]}

- 2026-10-06T20:52:07.034557+00:00: Live attempt START {"task": "math-rational", "arm": "ORACLE_FULL", "label": "preflight-math-rational-ORACLE_FULL", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T20:54:35.667358+00:00: Live attempt END {"label": "preflight-math-rational-ORACLE_FULL", "valid": true, "operating_s": 148.57236590603134, "error": null}

- 2026-10-06T20:54:35.735068+00:00: Development preflight command {"command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/live.py", "point", "--task", "math-rational", "--arm", "ORACLE_IN_LEARNED_VICTIM", "--label", "preflight-math-rational-ORACLE_IN_LEARNED_VICTIM"]}

- 2026-10-06T20:54:36.273279+00:00: Live attempt START {"task": "math-rational", "arm": "ORACLE_IN_LEARNED_VICTIM", "label": "preflight-math-rational-ORACLE_IN_LEARNED_VICTIM", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T20:56:50.864643+00:00: Live attempt END {"label": "preflight-math-rational-ORACLE_IN_LEARNED_VICTIM", "valid": true, "operating_s": 134.53328650002368, "error": null}

- 2026-10-06T20:56:50.925977+00:00: Development preflight command {"command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/live.py", "point", "--task", "math-sensor", "--arm", "REPLAY_CURRENT", "--label", "preflight-math-sensor-REPLAY_CURRENT"]}

- 2026-10-06T20:56:51.444244+00:00: Live attempt START {"task": "math-sensor", "arm": "REPLAY_CURRENT", "label": "preflight-math-sensor-REPLAY_CURRENT", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T20:58:51.983319+00:00: Live attempt END {"label": "preflight-math-sensor-REPLAY_CURRENT", "valid": true, "operating_s": 120.48856087302556, "error": null}

- 2026-10-06T21:00:04.866931+00:00: Live attempt START {"task": "code-archive", "arm": "REPLAY_CURRENT", "label": "code-archive-block1-REPLAY_CURRENT", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:01:58.316427+00:00: Live attempt END {"label": "code-archive-block1-REPLAY_CURRENT", "valid": true, "operating_s": 113.40139888605336, "error": null}

- 2026-10-06T21:01:58.561376+00:00: Live attempt START {"task": "code-archive", "arm": "ORACLE_FULL", "label": "code-archive-block1-ORACLE_FULL", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:03:51.776198+00:00: Live attempt END {"label": "code-archive-block1-ORACLE_FULL", "valid": true, "operating_s": 113.16711817897158, "error": null}

- 2026-10-06T21:03:52.013069+00:00: Live attempt START {"task": "code-archive", "arm": "ORACLE_IN_LEARNED_VICTIM", "label": "code-archive-block1-ORACLE_IN_LEARNED_VICTIM", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:05:47.476213+00:00: Live attempt END {"label": "code-archive-block1-ORACLE_IN_LEARNED_VICTIM", "valid": true, "operating_s": 115.4056346550351, "error": null}

- 2026-10-06T21:05:47.749830+00:00: Live attempt START {"task": "math-inventory", "arm": "ORACLE_FULL", "label": "math-inventory-block1-ORACLE_FULL", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:07:49.080237+00:00: Live attempt END {"label": "math-inventory-block1-ORACLE_FULL", "valid": true, "operating_s": 121.28078953799559, "error": null}

- 2026-10-06T21:07:49.333595+00:00: Live attempt START {"task": "math-inventory", "arm": "ORACLE_IN_LEARNED_VICTIM", "label": "math-inventory-block1-ORACLE_IN_LEARNED_VICTIM", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:09:44.730245+00:00: Live attempt END {"label": "math-inventory-block1-ORACLE_IN_LEARNED_VICTIM", "valid": true, "operating_s": 115.3436313039856, "error": null}

- 2026-10-06T21:09:44.996826+00:00: Live attempt START {"task": "math-inventory", "arm": "REPLAY_CURRENT", "label": "math-inventory-block1-REPLAY_CURRENT", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:11:30.212625+00:00: Live attempt END {"label": "math-inventory-block1-REPLAY_CURRENT", "valid": true, "operating_s": 105.18201963504544, "error": null}

- 2026-10-06T21:11:30.359640+00:00: Live attempt START {"task": "text-websocket", "arm": "ORACLE_IN_LEARNED_VICTIM", "label": "text-websocket-block1-ORACLE_IN_LEARNED_VICTIM", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:13:26.727921+00:00: Live attempt END {"label": "text-websocket-block1-ORACLE_IN_LEARNED_VICTIM", "valid": true, "operating_s": 116.3173446119763, "error": null}

- 2026-10-06T21:13:26.963928+00:00: Live attempt START {"task": "text-websocket", "arm": "REPLAY_CURRENT", "label": "text-websocket-block1-REPLAY_CURRENT", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:15:33.470653+00:00: Live attempt END {"label": "text-websocket-block1-REPLAY_CURRENT", "valid": true, "operating_s": 126.45803502603667, "error": null}

- 2026-10-06T21:15:33.713936+00:00: Live attempt START {"task": "text-websocket", "arm": "ORACLE_FULL", "label": "text-websocket-block1-ORACLE_FULL", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:17:38.075687+00:00: Live attempt END {"label": "text-websocket-block1-ORACLE_FULL", "valid": true, "operating_s": 124.30997693201061, "error": null}

- 2026-10-06T21:17:38.300950+00:00: Live attempt START {"task": "mixed-chinook", "arm": "REPLAY_CURRENT", "label": "mixed-chinook-block1-REPLAY_CURRENT", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:19:27.743652+00:00: Live attempt END {"label": "mixed-chinook-block1-REPLAY_CURRENT", "valid": true, "operating_s": 109.39422089001164, "error": null}

- 2026-10-06T21:19:27.977487+00:00: Live attempt START {"task": "mixed-chinook", "arm": "ORACLE_FULL", "label": "mixed-chinook-block1-ORACLE_FULL", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:21:19.252926+00:00: Live attempt END {"label": "mixed-chinook-block1-ORACLE_FULL", "valid": true, "operating_s": 111.22754448297201, "error": null}

- 2026-10-06T21:21:19.507072+00:00: Live attempt START {"task": "mixed-chinook", "arm": "ORACLE_IN_LEARNED_VICTIM", "label": "mixed-chinook-block1-ORACLE_IN_LEARNED_VICTIM", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:23:01.675414+00:00: Live attempt END {"label": "mixed-chinook-block1-ORACLE_IN_LEARNED_VICTIM", "valid": true, "operating_s": 102.1307239549933, "error": null}

- 2026-10-06T21:23:01.828484+00:00: Live attempt START {"task": "code-archive", "arm": "ORACLE_FULL", "label": "code-archive-block2-ORACLE_FULL", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:24:38.787385+00:00: Live attempt END {"label": "code-archive-block2-ORACLE_FULL", "valid": true, "operating_s": 96.92646395601332, "error": null}

- 2026-10-06T21:24:38.926182+00:00: Live attempt START {"task": "code-archive", "arm": "ORACLE_IN_LEARNED_VICTIM", "label": "code-archive-block2-ORACLE_IN_LEARNED_VICTIM", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:26:21.084379+00:00: Live attempt END {"label": "code-archive-block2-ORACLE_IN_LEARNED_VICTIM", "valid": true, "operating_s": 102.10219239600701, "error": null}

- 2026-10-06T21:26:21.335721+00:00: Live attempt START {"task": "code-archive", "arm": "REPLAY_CURRENT", "label": "code-archive-block2-REPLAY_CURRENT", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:28:19.794544+00:00: Live attempt END {"label": "code-archive-block2-REPLAY_CURRENT", "valid": true, "operating_s": 118.40956767403986, "error": null}

- 2026-10-06T21:28:20.038887+00:00: Live attempt START {"task": "math-inventory", "arm": "ORACLE_IN_LEARNED_VICTIM", "label": "math-inventory-block2-ORACLE_IN_LEARNED_VICTIM", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:30:15.406851+00:00: Live attempt END {"label": "math-inventory-block2-ORACLE_IN_LEARNED_VICTIM", "valid": true, "operating_s": 115.32010621100198, "error": null}

- 2026-10-06T21:30:15.647427+00:00: Live attempt START {"task": "math-inventory", "arm": "REPLAY_CURRENT", "label": "math-inventory-block2-REPLAY_CURRENT", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:32:14.058695+00:00: Live attempt END {"label": "math-inventory-block2-REPLAY_CURRENT", "valid": true, "operating_s": 118.3582625889685, "error": null}

- 2026-10-06T21:32:14.294873+00:00: Live attempt START {"task": "math-inventory", "arm": "ORACLE_FULL", "label": "math-inventory-block2-ORACLE_FULL", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:34:13.569471+00:00: Live attempt END {"label": "math-inventory-block2-ORACLE_FULL", "valid": true, "operating_s": 119.22569733002456, "error": null}

- 2026-10-06T21:34:13.823240+00:00: Live attempt START {"task": "text-websocket", "arm": "REPLAY_CURRENT", "label": "text-websocket-block2-REPLAY_CURRENT", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:36:14.120358+00:00: Live attempt END {"label": "text-websocket-block2-REPLAY_CURRENT", "valid": true, "operating_s": 120.26169395400211, "error": null}

- 2026-10-06T21:36:14.257752+00:00: Live attempt START {"task": "text-websocket", "arm": "ORACLE_FULL", "label": "text-websocket-block2-ORACLE_FULL", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:38:08.447352+00:00: Live attempt END {"label": "text-websocket-block2-ORACLE_FULL", "valid": true, "operating_s": 114.13976832403569, "error": null}

- 2026-10-06T21:38:08.709151+00:00: Live attempt START {"task": "text-websocket", "arm": "ORACLE_IN_LEARNED_VICTIM", "label": "text-websocket-block2-ORACLE_IN_LEARNED_VICTIM", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:40:23.269582+00:00: Live attempt END {"label": "text-websocket-block2-ORACLE_IN_LEARNED_VICTIM", "valid": true, "operating_s": 134.51203646394424, "error": null}

- 2026-10-06T21:40:23.495293+00:00: Live attempt START {"task": "mixed-chinook", "arm": "ORACLE_FULL", "label": "mixed-chinook-block2-ORACLE_FULL", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:42:13.836564+00:00: Live attempt END {"label": "mixed-chinook-block2-ORACLE_FULL", "valid": true, "operating_s": 110.28977736597881, "error": null}

- 2026-10-06T21:42:14.070717+00:00: Live attempt START {"task": "mixed-chinook", "arm": "ORACLE_IN_LEARNED_VICTIM", "label": "mixed-chinook-block2-ORACLE_IN_LEARNED_VICTIM", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:44:06.453884+00:00: Live attempt END {"label": "mixed-chinook-block2-ORACLE_IN_LEARNED_VICTIM", "valid": true, "operating_s": 112.33238178800093, "error": null}

- 2026-10-06T21:44:06.688928+00:00: Live attempt START {"task": "mixed-chinook", "arm": "REPLAY_CURRENT", "label": "mixed-chinook-block2-REPLAY_CURRENT", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:46:04.197621+00:00: Live attempt END {"label": "mixed-chinook-block2-REPLAY_CURRENT", "valid": true, "operating_s": 117.46238937898306, "error": null}

- 2026-10-06T21:46:04.438259+00:00: Live attempt START {"task": "code-archive", "arm": "ORACLE_IN_LEARNED_VICTIM", "label": "code-archive-block3-ORACLE_IN_LEARNED_VICTIM", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:48:02.758959+00:00: Live attempt END {"label": "code-archive-block3-ORACLE_IN_LEARNED_VICTIM", "valid": true, "operating_s": 118.28658308298327, "error": null}

- 2026-10-06T21:48:02.902219+00:00: Live attempt START {"task": "code-archive", "arm": "REPLAY_CURRENT", "label": "code-archive-block3-REPLAY_CURRENT", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:49:46.103896+00:00: Live attempt END {"label": "code-archive-block3-REPLAY_CURRENT", "valid": true, "operating_s": 103.15207198896678, "error": null}

- 2026-10-06T21:49:46.341296+00:00: Live attempt START {"task": "code-archive", "arm": "ORACLE_FULL", "label": "code-archive-block3-ORACLE_FULL", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:51:34.607840+00:00: Live attempt END {"label": "code-archive-block3-ORACLE_FULL", "valid": true, "operating_s": 108.22026100195944, "error": null}

- 2026-10-06T21:51:34.857106+00:00: Live attempt START {"task": "math-inventory", "arm": "REPLAY_CURRENT", "label": "math-inventory-block3-REPLAY_CURRENT", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:53:34.340061+00:00: Live attempt END {"label": "math-inventory-block3-REPLAY_CURRENT", "valid": true, "operating_s": 119.43387676001294, "error": null}

- 2026-10-06T21:53:34.583937+00:00: Live attempt START {"task": "math-inventory", "arm": "ORACLE_FULL", "label": "math-inventory-block3-ORACLE_FULL", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:55:33.883310+00:00: Live attempt END {"label": "math-inventory-block3-ORACLE_FULL", "valid": true, "operating_s": 119.2528166359989, "error": null}

- 2026-10-06T21:55:34.127071+00:00: Live attempt START {"task": "math-inventory", "arm": "ORACLE_IN_LEARNED_VICTIM", "label": "math-inventory-block3-ORACLE_IN_LEARNED_VICTIM", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:57:31.474438+00:00: Live attempt END {"label": "math-inventory-block3-ORACLE_IN_LEARNED_VICTIM", "valid": true, "operating_s": 117.2981803540024, "error": null}

- 2026-10-06T21:57:31.693435+00:00: Live attempt START {"task": "text-websocket", "arm": "ORACLE_FULL", "label": "text-websocket-block3-ORACLE_FULL", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T21:59:18.834877+00:00: Live attempt END {"label": "text-websocket-block3-ORACLE_FULL", "valid": true, "operating_s": 107.10549924301449, "error": null}

- 2026-10-06T21:59:18.971877+00:00: Live attempt START {"task": "text-websocket", "arm": "ORACLE_IN_LEARNED_VICTIM", "label": "text-websocket-block3-ORACLE_IN_LEARNED_VICTIM", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T22:01:10.193368+00:00: Live attempt END {"label": "text-websocket-block3-ORACLE_IN_LEARNED_VICTIM", "valid": true, "operating_s": 111.18435838498408, "error": null}

- 2026-10-06T22:01:10.327643+00:00: Live attempt START {"task": "text-websocket", "arm": "REPLAY_CURRENT", "label": "text-websocket-block3-REPLAY_CURRENT", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T22:03:05.682227+00:00: Live attempt END {"label": "text-websocket-block3-REPLAY_CURRENT", "valid": true, "operating_s": 115.30548632598948, "error": null}

- 2026-10-06T22:03:05.933412+00:00: Live attempt START {"task": "mixed-chinook", "arm": "ORACLE_IN_LEARNED_VICTIM", "label": "mixed-chinook-block3-ORACLE_IN_LEARNED_VICTIM", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T22:04:58.348500+00:00: Live attempt END {"label": "mixed-chinook-block3-ORACLE_IN_LEARNED_VICTIM", "valid": true, "operating_s": 112.36245194304502, "error": null}

- 2026-10-06T22:04:58.593309+00:00: Live attempt START {"task": "mixed-chinook", "arm": "REPLAY_CURRENT", "label": "mixed-chinook-block3-REPLAY_CURRENT", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T22:06:56.133220+00:00: Live attempt END {"label": "mixed-chinook-block3-REPLAY_CURRENT", "valid": true, "operating_s": 117.48947603697889, "error": null}

- 2026-10-06T22:06:56.382583+00:00: Live attempt START {"task": "mixed-chinook", "arm": "ORACLE_FULL", "label": "mixed-chinook-block3-ORACLE_FULL", "binary": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "checkpoint": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e"}

- 2026-10-06T22:08:51.686926+00:00: Live attempt END {"label": "mixed-chinook-block3-ORACLE_FULL", "valid": true, "operating_s": 115.25825312302914, "error": null}

- 2026-10-06T22:09:03.740327+00:00: Main matrix COMPLETE; all36 attempts valid; no fourth attempt, exclusions or policy retuning. Optional text-tls81.7K transfer check left unmeasured; complete bounded core study and handoff now. {}

- 2026-10-06T22:13:18.285868+00:00: Reproducer test START {"command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/reproduce.py", "--task", "math-rational", "--arm", "REPLAY_CURRENT"], "matching_prior_attempts": 1}

- 2026-10-06T22:15:30.566477+00:00: Reproducer test COMPLETE {"command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/reproduce.py", "--task", "math-rational", "--arm", "REPLAY_CURRENT"], "task": "math-rational", "arm": "REPLAY_CURRENT", "state": "PASS", "directory": "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-reproduction-20261006T221318.355672Z", "episode": "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-reproduction-20261006T221318.355672Z/raw/reproduction-math-rational-REPLAY_CURRENT/episode.json", "outer_wall_s": 132.27144673699513, "root_campaign_elapsed_s": 8093.557564564515, "checkpoint_sha256": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e", "binary_sha256": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "matching_point_attempts_in_this_study": 2, "classification": "Development reproduction check, not a headline reserved request; parent study clock remains unchanged."}

- 2026-10-06T22:15:30.592859+00:00: Reproducer test START {"command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/reproduce.py", "--task", "math-rational", "--arm", "ORACLE_FULL"], "matching_prior_attempts": 1}

- 2026-10-06T22:17:34.002208+00:00: Reproducer test COMPLETE {"command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/reproduce.py", "--task", "math-rational", "--arm", "ORACLE_FULL"], "task": "math-rational", "arm": "ORACLE_FULL", "state": "PASS", "directory": "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-reproduction-20261006T221530.708585Z", "episode": "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-reproduction-20261006T221530.708585Z/raw/reproduction-math-rational-ORACLE_FULL/episode.json", "outer_wall_s": 123.39992350398097, "root_campaign_elapsed_s": 8216.993292184488, "checkpoint_sha256": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e", "binary_sha256": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "matching_point_attempts_in_this_study": 2, "classification": "Development reproduction check, not a headline reserved request; parent study clock remains unchanged."}

- 2026-10-06T22:17:34.029239+00:00: Reproducer test START {"command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/reproduce.py", "--task", "math-rational", "--arm", "ORACLE_IN_LEARNED_VICTIM"], "matching_prior_attempts": 1}

- 2026-10-06T22:19:33.501934+00:00: Reproducer test COMPLETE {"command": ["/srv/ai/research/iq3s-residency-20261004T230051Z/src/control/.venv/bin/python", "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-20261006T200037Z/scripts/reproduce.py", "--task", "math-rational", "--arm", "ORACLE_IN_LEARNED_VICTIM"], "task": "math-rational", "arm": "ORACLE_IN_LEARNED_VICTIM", "state": "PASS", "directory": "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-reproduction-20261006T221734.141763Z", "episode": "/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase1-reproduction-20261006T221734.141763Z/raw/reproduction-math-rational-ORACLE_IN_LEARNED_VICTIM/episode.json", "outer_wall_s": 119.47021984000457, "root_campaign_elapsed_s": 8336.4998870095, "checkpoint_sha256": "065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e", "binary_sha256": "ccea78b7e67cd0d634880160f8d9d571ef65263d41622232ef149c6bb76038e3", "matching_point_attempts_in_this_study": 2, "classification": "Development reproduction check, not a headline reserved request; parent study clock remains unchanged."}

- 2026-10-06T22:23:12.041303+00:00: Final descriptive diagnostics regenerated after live measurements; no model or scheduler changes {"main_requests": 36, "reproduction_checks": "PASS", "threshold_accounting_equal": 32, "threshold_points": 32}

- 2026-10-06T22:27:01.025092+00:00: Entire feasible Phase1 study completed; all36 main requests valid; final artifact hash verification passed; normal serving preserved and no owned GPU work remains {"primary": "MECHANISM_IMPROVED_NO_CONFIRMED_LATENCY_GAIN", "artifact_hashes_verified": 3616, "elapsed_s": 8784.024824695487, "audit_state": "COMPLETE_WITH_DOCUMENTED_PROTOCOL_DEVIATION", "required_work_remaining": 0, "unmeasured": ["optional TLS128K-profile transfer check", "cheap-rule live comparator", "independent unseen tasks with guard tail", "natural-generation quality and exclusive latency attribution"]}
