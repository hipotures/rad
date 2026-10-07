# Next causal predictor: conditional eviction risk, not generic popularity

This specification follows the completed bounded live experiment. It is not a trained predictor or a production change.

Candidate population: actual class-compatible, same-device, same-layer resident victims considered for a visible nonresident incoming action. Respect K24, physical slot classes, current/inflight readers, charged spare availability and native/external admission ownership. A candidate expert first demand must be visible within E64; incoming I>=64 valuation is dormant in the tested first-feasible scheduler. Smaller I changes eligibility/lead, not just retention valuation.

Available causal features: current router confidence/rank and batch assignments where causally available; actual recent use1/4/16/64 windows; native .7/4-window heat; resident age/last use/miss recurrence; sizeclass/device/layer; actual queue and staged/copy readiness; current/inflight protection; previous victim eviction/reload frequency; measured CPU-positive/mapped completion spans with overlap caveat. Do not use future routed IDs, future MTP acceptance or tape-end knowledge at inference.

Targets: risk and weighted cost of resident-victim demand while displaced before a replacement provides enough useful ready demand to amortize copying. Predict an uncertainty-aware lifetime/reuse distribution or calibrated eviction-risk class. It need not predict the exact farthest-next-use event chosen by a full oracle. Incoming benefit should count actual target-ready demand and repeated distinct invocation use, not merely published-before-target status. A joint action score subtracts copy/online planner costs and victim loss; do not sum overlapping runtime timers.

Units: main verifier routed-layer batch invocations (48/window), with event shape/speculation identity. Convert to lead milliseconds only using rolling measured physical progress, not a historical absolute timestamp. Unknown beyond finite horizon is censored, not never. At request end, lifetime labels without a guard tail are right-censored; avoid finite-4096-end privilege in deployable training.

Evaluation: task-level independent episodes/splits, freeze thresholds before holdout, and transactional fixed-work tests before ordinary generation. Check useful-copy recall, copy bytes, recurring promotions, victim reloads, totalCPU/mapped demand, ready/late usage, exposed measured latency and end-to-end requestwall. Do not select by hitrate or generic next-expert accuracy alone.

The concrete research intervention should be to rank or veto exchanges by calibrated victim-return risk when E64 incoming first-demand is already known/adequate. Existing deadline heuristic's computed reuse utility cannot demonstrate incoming lifetime value because it breaks before comparing feasible actions. A later reuse-aware scheduler would need a separate controlled design before claiming the incoming channel is unnecessary.

This proposed target is conditional on the study's privileged incoming E channel
and complete-current-window P protection. Neither becomes a free causal feature
in natural serving. A later runtime must obtain incoming candidates causally and
protect actually current/in-flight readers using its dependency/ownership state.
It must explicitly account for any remaining predicted future-protection hint.
The present decomposition isolates information roles under declared common
privileges; it does not validate a deployable predictor or permit a production
policy to read future router outputs.

## Observed decision basis

Incoming: I=64 is the smallest tested budget reproducing deterministic F/F decisions at unchanged E64 in the offline model and source tests. Its live median retention is75.96%, range -25.67% to94.05%, so an 80–90% performance-sufficiency claim is unresolved. I4/I16 shorten eligibility as well as value information and therefore do not isolate incoming lifetime. Victim: neither V64 at32K nor V256 in the larger profiles is sufficient under the tested policy/fallback. FULL is the only tested passing reference; the smallest sufficient finite V remains unmeasured. This is not proof that a causal predictor needs exact whole-request next-use, nor that every short-history victim policy fails. Interaction has signs +1181/-3150/-2575ms across blocks, not a stable linear law.

Observed absent demand, future-conditioned displacement duration and eventual readmission provide training labels only after the action. Negative labels near tape end remain censored without a guard tail. Weight losses by measured class copy payload and observed CPU/mapped costs with timer-overlap caveats; do not convert each miss into an assumed exclusive millisecond cost. A future learner requires new task-level calibration/holdout episodes, not these timing replicas.
