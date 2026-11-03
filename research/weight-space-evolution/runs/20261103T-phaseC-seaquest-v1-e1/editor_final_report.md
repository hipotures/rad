# Editor final report (model output, as delivered; lightly reformatted)

Source: final message of the editor subagent (Claude Opus 5.5, Claude Code general-purpose subagent), session
`phaseC-seaquest-v1-e1`, 2026-11-03. Content preserved with light formatting changes; claims are the editor's and are evaluated in
[report.md](report.md).

---

## Weight-editor report — Seaquest, phaseC-seaquest-v1-e1

**Submission status: NOT SUBMITTED** — the lab disappeared before I could run `lab.sh submit`. `/home/user/work/rad/weight-space-evolution/lab.sh` and the whole `weight-space-evolution` directory now return "No such file or directory" (the harness may have terminated the session at the wall-clock limit or for another reason). I did not look anywhere else on the machine. **Intended submission: `p-38e02409d21a` (edit B)** — if the session can be restored, run `lab.sh submit p-38e02409d21a`. None of my edits beat Gold significantly.

### 1. Diagnosis (what limits Gold)
Gold behaviour (read from weights + hand-built probes): never moves sideways (left/right logits −100), sits at column 5 facing left and fires left; dodges danger in its own row at cols 4–7, refuses to step into an adjacent row with danger at cols 4–7, steps toward rows with danger at cols 0–3 (to shoot) and toward divers; climbs to surface when oxygen < 60 and it carries ≥1 diver (gauge col 8 lit, col 2 off).
Evidence from dev passes:
- Score ≈ survival: corr(score, length) = 0.98 over 300 Gold episodes; mean length ≈1355, reward rate ≈0.037/step. Deaths are collisions, not oxygen.
- A death cluster at the first low-oxygen climb: ~6–8% of all episodes end at steps 141–152 with score 0–5, right after the "oxygen<60" climb begins. Moving the trigger to oxygen<40 (edit B) shifted that cluster by the predicted amount (to steps 164–176), confirming the link.
- Surfacing also raises difficulty (enemies spawn/move faster), which increases reward rate *and* death risk — so survival and reward-rate changes tended to cancel.
- Traces with "sticky"-repeat steps showed some deaths from repeated "up" near the surface (surfacing without a diver / moving into a dangerous row).
- Gold's left-side "attack" pull (also toward rows with only an enemy bullet) is useful: removing it lowered score (edit D), likely because a bullet from the left implies a sub that will shoot again.

### 2. Edits tested
- **B (p-38e02409d21a, intended submission):** climb trigger oxygen<60 → oxygen<40. W1 unit 24: gauge row-9 col-2 weight −6→0, col-1 0→−6 (2 entries). Idea: fewer risky climbs and slower difficulty ramp.
- **C (p-a745712c1f39):** danger units W1[:,16..23]: col-7 reward weight −3→0, col-8 danger weight 2→4 and reward −1.8→−3.8 (24 entries). Idea: treat column-7 enemies as blocking during the low-oxygen climb.
- **D (p-2c6337e46fac):** left-attack units W1[:,25..31]: danger 6→3, reward 0→4, bias −3→−4 (63 entries). Idea: stop approaching rows that hold only an enemy bullet.
All edits verified on hand-built observations (2,640 boards for C/D) to change only the intended situations.

### 3. Dev results (paired vs Gold, 300 episodes each)
| Pass | Network | Result |
|---|---|---|
| 1 | Gold only | mean 49.8 |
| 2 | B | −0.38 ± 3.31 (CI [−7.2, 6.1]); +6.5% length, −7% reward rate |
| 3 | C | −12.7 ± 2.9 (CI [−18.3, −6.9]) — clearly worse |
| 4 | D | −6.2 ± 2.5 (CI [−11.2, −1.2]) — worse |
| 5 | B (repeat) | +3.56 ± 3.36 (CI [−3.0, 10.0]); +15% length |
| 6 | not used | lab gone |
Pooled B ≈ +1.6 ± 2.4 — consistent with no effect.

### 4. Uncertainty and rules
- B is my best guess but statistically indistinguishable from Gold; survival gains may be offset by lower reward rate. C and D are clearly harmful.
- Exact collision causes unknown (traces record only the sub's own state, not enemy positions).
- Budgets: 5/6 passes, 16/25 sandbox runs. One pass came from a careless shell one-liner when proposing B (a later status check still showed one pass used). Two failed calls (a path the lab couldn't find; a mistyped candidate id) used no budget.
- Time: probably near or past the ~60-minute target.
- Rules: no gradients, fitting or random search; every edit hand-written from weight analysis. Used only `lab.sh`; wrote only in the scratch folder (now gone with the lab directory).
- Outstanding: the required `submit` call did not happen.
