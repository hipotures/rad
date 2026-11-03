# Editor final report — session phaseC-seaquest-v3S-e3 (model output, condensed by operator)

> Operator notes: condition S (source + permitted self-simulation). Interrupted by the API rate limit and resumed.

Submitted **p-e16dae33cb40**: one entry, b3[4] ("down" bias) 244 → 242. 2/6 passes, 12/25 sandbox runs.

**Diagnosis (weights, own simulator).** Up/down-only controller (simulator action mix: fire 79%, down 10.7%, up 10.5%;
column 5, facing left). h1: row (0–8), divers (9–15), central danger (16–23), "low oxygen & diver" (24), left danger
(25–31); h2: per-row conjunctions for fire/up/down with −3 penalty for danger in the target row; one surfacing unit.
Simulator (150 episodes, Gold 54.0, length ≈ 1,450): ~70% of deaths fish/sub collisions, rest mostly bullets; most
fatal steps are vertical moves into an occupied row, the rest right-side arrivals. Idle-state flaw: with no steering
unit active the logits are fire 1.8, down 4, up 0 → "down" ≈ 87% → drift into danger that the −3 penalty cannot stop
(it acts on already-off units). Bonus cannot be targeted (gauge merges oxygen and diver bars).

**Edit.** b3[4] − 2 → idle down/fire ≈ 0.47/0.47 (from 0.87/0.10); deliberate moves (+30–60 logits) unaffected.
Simulator: longer episodes (1,384 → 1,574), more surfacings, slightly more oxygen deaths.

| Source | Δ vs Gold (SE) | 95% CI |
|---|---|---|
| dev pass 1 (Gold 50.86, cand. 53.48) | +2.62 (1.62) | [−0.53, 5.69] |
| dev pass 2 | +5.16 (1.68) | [1.92, 8.64] |
| simulator, 600 paired: down bias −1 / −2 / −4 | +3.6 (1.85) / +4.8 (2.0) / +4.2 (2.1) | – |

Rejected in the simulator only: veto units by repurposing left-danger units (26 vs 56); spare h2 veto units (39–47 vs
55); left-danger weights ×2/×3/×0.5 (54.6/31.6/40.7); earlier right-side detection (38–44 vs 51); danger penalty
×0.5/×1.5 (12/22); down bias +2 (45); fire bias +3 (46). Value −2 chosen in the simulator before dev passes.
Closest to a rule: comparing a few hand-chosen settings in the simulator (permitted in condition S).
