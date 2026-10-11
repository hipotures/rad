# Our mechanisms versus the current upstream frontier, 2026-10-11

## Question

This is step 3 of the re-baselining plan. Do any of our accepted mechanisms
still add value on the constructions now at the upstream frontier? And which
next direction has the highest information value?

The inputs are the frozen snapshot from
[the frontier inventory](../20261011T1916Z-upstream-frontier-inventory/report.md),
the pinned upstream package `research/five-stage-gen4-banks` at `12a4934d`,
and our accepted records in `campaigns/fast-integration-gpu-20261008/` and its
`frontier-sprint-20261009/`.

## Correction to the inventory report

The inventory report gave our best result as about 5.14e-5. That is wrong.
5.14e-5 was only the first fast-integration campaign. The frontier sprint of
2026-10-09 then accepted
**`61728289/100000000000` = 6.1728289e-4**, which is:
- 0.853 x the reviewed upstream main (7.2357e-4)
- 0.450 x the highest open claim (#480)

That sprint candidate was built on PR168/PR170 sources and stayed below the
public leader when it was accepted. The inventory report and topic README are
corrected in the same commit.

## How kappa is assembled

The final witness is bounded by the binding supplier:
`kappa < min(b, c) / (1 + min(b, c))`, where `b` is the complex supplier's
native saving and `c` is the bit supplier's. Finite backoffs and bootstrap
depth decide how close a package gets to that ceiling. Three sources confirm
this:
- PR275's finite-assembly theorem
- our sprint's ceiling analysis
- the explicit "bit binds" / "complex binds" statements in current PRs

So any gain has to raise the **binding** supplier, or both. Polishing the slack
supplier changes nothing.

## Where upstream gains came from

`code/upstream_frontier_tiers.py` orders the title-stated claims by creation
time and keeps every claim that raised the running maximum
([record-steps.csv](results/record-steps.csv), 109 rows). From kappa 1e-4
onward there were 57 record steps, with a median step of +1.06%. The 35 steps
below 2% add up to only about 6% of the total log-gain. Most of the gain came
from structural steps:

| Step | PR | Mechanism | Share of log-gain since 1e-4 |
|---|---|---|---|
| +143.5% | #130 | Three-stage Cayley covers | 0.33 |
| +32.0% | #114 | Shared completed cores and physical frames | 0.10 |
| +17.4% | #376/#433 | E8 split centres | 0.06 |
| +14.6% | #262 | Bit word's own retained ledger (unreviewed, CI none) | 0.05 |
| +14.2% | #137 | Padded triple covers | 0.05 |
| +11.4% | #434 | Hosting-selected kernel (idle-data hosting) | 0.04 |
| +10.4% | #168 | Annealed modules and terminal sinks | 0.04 |
| +6.5% | #373 | E8 bit word with E8 complex unit, seven-stage | 0.02 |

Frame retiming and reset-type polish on current words now gains:
- +0.097% for PR279's concave descent
- +0.016% for #374's coupled complex retiming
- +0.21% for #469's gate-frame retiming
- +0.41% for #438's early resets

## Frontier tiers and their assumptions

Each open title-stated claim above main (173) is assigned a tier ([tiers.json](results/tiers.json)). The
assignment uses body markers, inherited through referenced PRs, and counted
only from the PR that introduced the mechanism (E8 from #360, hosting from #434).

| Tier | Open claims | Range | CI success | Assumption status |
|---|---|---|---|---|
| Pre-E8 (paired-cube / bank words) | 72 | 7.24e-4 to 8.34e-4 | 34 | Main's interfaces; unreviewed above main |
| E8 words, no hosting | 70 | 8.04e-4 to 1.139e-3 | 36 | Main's interfaces plus new E8 units; unreviewed |
| Idle-data hosting | 31 | 1.139e-3 to 1.3726e-3 | 8 | **Additional idle-data hosting assumption**; #434 calls its operator extension inherited and not proved by the finite audits |

Inside the hosting tier, the leading line (#448 -> #450 -> #464/#469 -> #480,
1.33e-3 to 1.37e-3) adds **cross-copy hosting**, which is disputed:

- #451 (chafreaky) publishes `research/cross-family-residual-obstruction`. For
  q=3, m=2 the operators `D_(a+b) ⊕ I` and `D_a ⊕ D_b` have different traces
  (90 vs 54; complex analogue 4+2i vs 4+4i). This contradicts #448's stated
  coordinate-permutation derivation.
- #453 (rohanarun) reproduced the obstruction. It now marks its own
  cross-copy gain as "not currently established".
- higherbeing (#448) replies that the obstruction compares single-residual
  placements, not complete programs. They added a toy check (q=3, m=2) showing
  that both complete programs equal the original children. They state that the
  open point is the interface itself: may a residual's route land in two
  families?
- #450 does not replay from a fresh clone. Two pinned evidence logs are
  untracked, as reported in a comment; the claimed kappa reportedly passes once
  they are restored.
- PR275 (lydakis) shows that #442's independent hosted bit audit accepts two
  deliberate mutations, a deleted terminal exchange and a zeroed bridge
  coefficient. Literal F2 replay catches both. PR275 adds a guard, and the
  published construction itself is not alleged invalid.

Without cross-copy hosting, the best open claims are:
- #473 (1.29563e-3)
- #472 (1.29210e-3)
- #456 (1.26656e-3), the best with full CI success. Its author's sibling PRs
  #457, #459 and #466 report full replays of 25-30 minutes each

## Our mechanisms against current upstream

Details and sources are in [mechanism-map.json](results/mechanism-map.json).

| Our mechanism | Our best record | Upstream state on current words | Expected value now |
|---|---|---|---|
| Positive-frame networks (PR51) | 4.17e-5, +1.01% | E8 form makes every frame nondegenerate | none, subsumed |
| Pair-block networks, interval joint compilation, matrix-weighted allocation, source coframes | 5.14e-5 | Construction families replaced by covers, paired cubes, E8 | none, obsolete |
| Binary physical-lifetime program | part of 6.17e-4 | Recycled registers, early resets, helper reuse (#150, #426, #437, #438) | <=0.5% per step, crowded |
| Complex fusion/alias/frame placement, moment-aware selection | +0.77% over PR161 | Common-frame, concave-descent, coupled and gate-frame retiming (PR244, PR279, #374, #469), F2 fusion (#210) | <=0.3% per step, crowded |
| Terminal-sink placement | plateau | #168, #182 | small |
| Signed synthesis, structural local circuits | negative | Structural gains came from new word families | n/a |
| Independent exact verification | every accepted candidate | Scarce. 173 claims above main are unreviewed; errors keep surfacing ad hoc (#450, #451/#453, PR275) | decides validity of the 1.13e-3 to 1.37e-3 tiers |

## Interpretation

- **Measured:** structural changes produced the large upstream gains: covers,
  shared cores, paired cubes, E8 units, split centres and hosting. Polish of
  the kind we built produced the small ones.
- **Conclusion:** none of our construction mechanisms is a plausible source of
  a meaningful gain on the current words. Each has an upstream counterpart
  that is already applied, at about 0.3-0.5% per step. Several contributors
  apply such polish within hours of each new word. Porting our polish would
  most likely yield sub-percent, quickly superseded results. It would also
  inherit the hosting assumption if done on the top words.
- **Conclusion:** our reusable advantage is independent exact verification.
  Upstream is short of it, and the top tier currently rests on an unreviewed
  extra assumption plus a disputed cross-copy step.
- **Hypothesis (untested):** new lattice or root-system word families could
  produce the next structural jump, as E8 did. No PR mentions the Leech
  lattice, Barnes-Wall BW16, K12 or E6, while E7 and D4 appear only as
  sub-structures of E8 words.

## Recommended next step

Ranked by information value per effort:

1. **Adjudicate cross-copy hosting.** Write an independent exact checker for
   the complete-program identity in the actual interface model. Use our own
   address-space model, not higherbeing's toy. Cover q=3, m=2, then the actual
   rank-8/rank-9 residual widths. This settles whether 1.33e-3 to 1.37e-3 is
   real or whether the frontier is about 1.296e-3, and it is publishable either
   way.
2. **Independently replay the top cross-copy-free claim**, #456 (or #473 once
   its CI finishes). Sibling full runs are reported at 25-30 minutes. Check
   the idle-data hosting window condition with our own code, alongside the
   finite and assembly checks.
3. **Structural bet:** screen a non-E8 lattice word family (BW16, K12 or
   Leech-derived lines) with the E8 bit-word producer's cost model before any
   full construction. Highest upside, lowest prior probability.

Porting our polish mechanisms to current words is not recommended.

## Confidence and limitations

- Tiers come from keyword markers inherited through references. They are
  indicators, not verified properties. The cross-copy dispute is summarized
  from PR bodies and comments, and I did not reproduce either side.
- All upstream kappa values and step percentages are self-reported. None was
  replayed here.
- The mechanism map compares by mechanism class. I did not check line by line
  whether a specific variant of ours differs from its upstream counterpart.
