# Frontier batch 2026-10-11: results

Operator runs on the shared host (16 cores, 2 x RTX 4090, Python 3.14.7),
campaign commit `01db37d2` (jobs 1-3), the follow-up job 4 at `77950181` and
`213f503d`, and job 5 at `9eea85ed`, clean tree each time. All runs finished
with exit 0.

| Run | Wall time | Outcome |
|---|---|---|
| `20261011T202316Z-job1` | 10 s | `MODEL_CONSISTENT` |
| `20261011T202331Z-job2` | 23.6 min (15 parallel) | 34 of 39 replays pass |
| `20261011T205141Z-job3` | 49 s | E8 price validation matches #370 |
| `20261011T211954Z-job4`, `20261011T213109Z-job4` | 5.8 + 3.7 min | 5 of 5 repair replays pass (section 5) |
| `20261011T220322Z-job5` | 19.3 min (9 parallel) | 8 of 9 newer frontier packages pass, one after the job 4 repair (section 6) |

The evidence is in [evidence/](evidence/) as gzip copies; the full outputs and
worktrees stay in `RAD_WORK_ROOT` (see [Evidence](#evidence)).

## 1. Cross-copy hosting under single-stream registers (job 1)

**Question.** Is splitting one dirty helper residual across two data copies
(#448 lineage) a program of the fixed local word, when each register is bound
to one physical stream and streams form a direct sum?

**Method.** Exact small models (bit side q = 3, 5; complex side q = 2;
m up to 8) of the original program, whole-residual hosting (#442), every
single-register placement of a split residual, and a two-register control.

**Measured.**
- Whole hosting equals the original program in all 13 cases where the residual
  fits on one copy.
- 0 of 152 single-register cross-copy programs equal the original program
  (18 split cases).
- The two-register control equals the original program in all 18 cases.
  It is a different local word that uses one more helper per split residual.

## 2. Fresh replays of 39 pinned claims (job 2)

Each replay ran the author's own verifier in a fresh detached worktree at the
pinned SHA, with a fresh output directory and no network access needed.

**Measured.**
- 34 of 39 pass. 33 of them print the title kappa exactly in a receipt or
  their log. #442 matches it to the title's printed rounding (within 1e-6).
- No verifier modified its worktree.
- Non-`PASS` receipt statuses are only informational negative-control labels
  (for example `EXACT_CLEAN_FULL_WORD_DISCOVERY_NOT_ADMITTED`).
- The longest replay was #462 (22.9 min); the largest peak RSS was 1.3 GB (#491).
- **#450 passed.** A PR comment had predicted that it would not replay from a
  fresh clone.
- **5 failures, all by one author (Dugongue):** #471, #476, #478, #483, #492.
  Each stops in 0.2 s at its own package integrity check:
  `MANIFEST.json` lists `.gitattributes`, but the pinned commit does not contain
  it. The commits are titled "Add files via upload", and a browser upload
  drops dotfiles. Every other listed file matches its hash byte for byte. The
  missing file's content could not be recovered: no blob in the upstream clone
  has that hash, and about 68k candidate attribute files did not match either.
  These are packaging failures at the pinned SHA, not evidence about the
  mathematics. The highest of these claims, #492 at 1.29738e-3, is below #493.

| Tier | Replayed and passing (title kappa) | Not reproduced |
|---|---|---|
| E8, no hosting | #376, #433, #436, #438, #439, #482 (max 1.16886e-3) | |
| Whole-residual hosting | #434, #442, #444, #445, #451, #454, #456-#463, #465-#467, #470, #472, #473, #490, #491, **#493 (1.30353e-3)** | #471, #476, #478, #483, #492 (integrity) |
| Cross-copy hosting | #448, #450, #464 (arithmetic only), #469, **#480 (1.37255e-3)** | |

A pass means that the author's verifier reproduces the claimed number from the
pinned bytes. It does not review the mathematics, and it does not discharge the
conditional supplier, hosting and compiler interfaces that the packages
declare.

### Independent hosting ledger (agent, post hoc)

[`code/job2_hosting_ledger.py`](code/job2_hosting_ledger.py) reads every
distinct hosted template produced by the replays (68 templates, 67 parsed). It
uses no upstream code. It checks:
- the split ledger: residuals whose coordinates lie on more than one data copy;
- coordinate intervals per child and copy: disjoint and within the child's rank;
- that each hosted stage lies in the stored window;
- the windows themselves, re-derived from each template's own schedule.

The one template not parsed is #473's `kernel-whole9-borrowed-spectator-v1`,
whose rows have nine fields.

| Template | Hosted residuals | Split across two copies |
|---|---|---|
| #448 bit / complex | 5770 / 5040 | 1562 (27%) / 1715 (34%) |
| #450 (both variants), #469 | 8140 | 1807 (22%) |
| #480 bit | 62920 | 14612 (23%) |
| all 61 other templates (whole hosting, #434 ... #493, incl. their parents) | 4320 - 660660 | 0 |

Across all 67 parsed templates there were 0 interval overlaps, 0 intervals
outside a child's rank and 0 rows outside the stored window. The windows
re-derived from the schedule match the stored windows in every template whose
schedule names pairs and child indices. The two nine-stage complex templates
(#434/#442 and #448) do not, so they were not re-derived.

**Interpretation.** Every cross-copy claim in the batch rests on 22-34% of its
hosted residuals being split across two copies. Job 1 shows that such a split
is not a program of the fixed local word when a register belongs to one stream.
It becomes valid with a second register, which costs one more helper per split
residual, and no package prices that helper. The whole-hosting templates
contain no split and pass all ledger checks.

**Confidence.** High for the measured counts and ledger checks. Medium-high for
the conclusion that the cross-copy tier is unsupported as priced. Job 1 is our
exact model of the declared execution model. An execution model in which one
helper register serves two streams at no cost would need its own justification.
The batch does not refute such a model.

## 3. Lattice screen for #370's five-stage template (job 3)

Our price function reproduces #370's R865 saving exactly
(9.040728210936710e-4, deficit 120). The deficit is 4V - 5 n_cent h, and
`s_ub` is the saving bound at R = 0.

| System | V | n_cent | Deficit | s_ub | Break-even helpers per line vs E8 |
|---|---|---|---|---|---|
| E8 roots | 120 | 9 | 120 | 4.37e-3 | 13.6 (actual word: 7.2) |
| E7 roots | 63 | 7 | 7 | 5.5e-4 (< E8's actual saving) | - |
| Leech minimal | 98280 | 2599 (exact, all rows on GPU) | 81240 | 1.24e-3 | **1.29** |
| E6; D4-D24; A4-A12; E8 norm-4, norm-6, norm-2+4; BW16 | | | negative | 0 | - |

**Conclusion.**
- Within this template, only E8 and Leech have a usable positive deficit.
- E7 is bounded below E8's actual saving.
- Leech would have to beat E8's saving with at most 1.29 helpers per line,
  where E8 needs 7.2. We consider this implausible, but the batch does not
  prove it impossible.
- We recommend no further work on replacing the lattice unless a cheap helper
  construction for Leech appears.

## 4. Follow-up: what #493's kappa rests on (agent, post hoc)

A dependency check from the replay outputs and the pinned packages. The
mathematical audit of the hosting lemma was deliberately not pursued; see
below.

- **The complex supplier binds.** #493's README gives the bit side
  c = 1.565442e-3 and reports every composition as complex-bound. Its title
  kappa 1.303530097714685e-3 is the cap of #471's complex supplier
  (b = 1305231506267591/10^18). `code/cited.py` reads that b from #471's
  receipt and does not rebuild it.
- **#471 did not replay in job 2, but does with one deviation (job 4).** At its
  pinned SHA it fails its own integrity check (section 2). It passes once the
  absent `.gitattributes` is tolerated, and it recomputes this b (section 5).
- **Other claims use the same b.** The replay outputs of #473, #490 and #491
  carry the same `complex_lower` = 1305231506267591/10^18 as an input. #473's
  own README says that "fresh full default replay remains pending" for its
  complex supplier.
- **Highest claims that avoid #471** (they need no deviation):
  - #472 (1.292099559e-3) uses #458's b, and #458 replayed in this batch.
  - #493's own verifier prices its word with #458's b at 1.295523322678044e-3.
    That is an information value, not a title claim.
- **The hosting lemma (#442 §2) is unchecked.** The lemma rests on two inherited
  facts:
  - a dirty invocation acts on a helper stream as an exact coordinate factor,
    whatever the prior contents;
  - an idle child is a commuting product of coordinate factors.

  The authors state that the global operator identity is not replayed
  numerically. Upstream has no review or comment on #442. What this batch adds:
  - job 1's stream model (whole hosting valid in 13 of 13 cases);
  - the ledger (0 overlaps, windows re-derived), across all whole-hosting
    templates.

  Neither is a proof of the two inherited facts at full size. The user decided
  not to pursue that audit further in this batch.

## 5. Repair replays of the five integrity failures (job 4)

**Method.** Job 2's procedure is reused: a fresh detached worktree at the
pinned SHA, a fresh output directory and the author's `verify.py`. There is one
documented deviation. `code/job4_launcher.py` replaces the integrity assertion
in memory, so that the manifest key `.gitattributes` is tolerated only if the
file is absent. Any changed, extra or other missing file still fails, and the
worktree is not modified.

The launcher was unit-tested on a synthetic package: 1 accepted case and 4
rejected ones. A precheck compares each package with its manifest under the
verifier's own exclusion rule.

**Runs.**
- Run `20261011T211954Z-job4` (5 parallel, 5.8 min) passed 4 of 5.
- It skipped #483 because of a harness defect. The precheck excluded only the
  root `MANIFEST.json`, while #483's verifier excludes every file of that name.
  The defect was fixed in `213f503d`.
- Run `20261011T213109Z-job4` passed #483.

| PR | Title kappa | Result | Wall |
|---|---|---|---|
| #471 | 1.274548075945587e-3 | pass, exact | 277 s |
| #476 | 1.291542455423938e-3 | pass, exact | 277 s |
| #478 | 1.295508560071773e-3 | pass, exact | 278 s |
| #483 | 1.296606691405309e-3 | pass, exact | 221 s |
| #492 | 1.297375468897877e-3 | pass, exact | 329 s |

- **One difference in every package.** Each differs from its manifest only by
  the absent `.gitattributes` (log line `# JOB4 DEVIATION ...
  remaining_equal=True`). No worktree was modified.
- **The missing file cannot change the computation.** The manifest's hash of the
  absent `.gitattributes` (`48747480...`) equals the blob `** -text` found in
  other packages (`research/r715-basis-exchange84/` and two more). That line
  only tells Git not to normalise line endings. No package code reads the file.
  Without it, the repository root's `* text=auto eol=lf` applies. Every other
  package file is byte-identical to the author's manifest, so the verifiers ran
  on exactly the author's inputs. The same holds for #498 in job 5.
- **#471's b is recomputed, not copied.** Each package recomputes
  b = 1305231506267591/10^18. In #471, `code/assemble.py` certifies b from the
  complex profile built in the same run, then compares it with `EXPECTED.json`.

**Result.**
- With this single deviation, all 39 pinned claims of the batch reproduce with
  their authors' verifiers.
- The input that caps #493 and feeds #473, #490 and #491 is reproducible.
- The job 2 failures were a packaging defect, not a computational one.
- All results remain conditional on the authors' declared interfaces.

## 6. Fresh replays of the newer frontier (job 5)

**Question.** Do the nine frontier packages opened after job 2 was pinned
reproduce with their authors' verifiers? Which complex supplier does each claim
bind to? Does the hosting in their templates pass our independent ledger? The
packages are #484 and #495-#502, pinned on 2026-10-11 at 21:54 UTC.

**Method.**
- **Replays.** Job 2's procedure is unchanged: a fresh worktree, a fresh output
  directory and the author's entry point. A second attempt, job 4's repair
  replay, runs only if a package stops at its own integrity assertion. It is
  recorded separately under `repair/`.
- **Claim check.** `checks/pr-N.json` searches every output JSON under 5 MB for
  the claimed value. JSON numbers are parsed as exact decimals. The claim is the
  title kappa, or #484's b because #484 claims no kappa.
- **Ledger.** `code/job5_hosting_ledger.py` reuses job 2's checks. It adds
  #471's two layouts, #496's `pooled_slots` and a per-call owner summary.
- **Controls.** A synthetic smoke test passes 12 of 12 checks. The pooled audit
  flags 6 of 6 mutation controls (`analysis/ledger-mutations.txt`).

**Replays** (run `20261011T220322Z-job5`, 9 in parallel, 19.3 min):

| PR | Claim | Result | Binding side (exact lower bound) | Wall |
|---|---|---|---|---|
| #484 | b = 1.326789535340266e-3 (supplier only) | pass, exact | complex, its own b | 767 s |
| #495 | 1.307044366925301e-3 | pass, exact | complex (`binding_component`) | 193 s |
| #496 | 1.332077359286333e-3 | pass, exact | complex b = 133385415620840915601/10^23 (pooled #484 word) | 794 s |
| #497 | 1.325117552367841e-3 | pass, exact | complex b = 1326875818805153/10^18 (re-packed #484 word) | 836 s |
| #498 | 1.301970637653655e-3 | as-is: integrity failure; repair: pass, exact | bit c ~ 1.303668e-3; its complex b is #471's 1305231506267591/10^18 | 0.2 + 256 s |
| #499 (cross-copy) | 1.452948511251494e-3 | pass, exact | complex b = 1455062642351477/10^18 (cross-copy slot) | 416 s |
| #500 | 1.308501945841842e-3 | pass, exact (no `EXPECTED.json` at the pin) | complex b = 1310216366506891/10^18 (#471's footprint rule) | 761 s |
| #501 | 1.343518018117309e-3 | **fail** at its own source-word pin (below) | - | 817 s |
| #502 | 1.343518018117309e-3 | pass, exact | complex b = 1345325487149526878087/10^24 | 1131 s |

The bit side of #496, #497, #499 and #502 is #493's freshly rebuilt
c = 391360506745414227149/(2.5*10^23), about 1.565442e-3.

**#498: the same packaging defect as job 4.** Its manifest lists a
`.gitattributes` that the commit lacks. The job 4 deviation (log line
`remaining_equal=True`) is the only change, and with it the package passes
with the exact title kappa.

**#501: not reproduced from fresh sources.**
- **Where it stops.** The verifier stops in `apply-frame-map`, after both
  suppliers have passed. `apply_retime.py` requires the canonical-JSON SHA-256
  of the freshly built #484 `gauge80-kernel42` FULL-WORD to equal the pin in
  `data/RETIME-FRAMES.json.gz`, `52f89042...`.
- **Our builds agree with each other but not with the pin.** Six independent
  builds of that word in this run all give `6d5ce907...`: inside #484, #496,
  #497, #500, #501 and #502. Their portable CANONICAL-WORD hash `c85d1438...`
  is the one #484's own `EXPECTED.json` pins, and #484 passes.
- **The float hypothesis fails.** We tested whether last-bit float differences
  in the word's three report floats could explain the pin. No combination
  within ±8 ulps matches (4,913 tried).
- **The author's input differs.** The author's provenance names a macOS build,
  `/private/tmp/pr484-independent-full-proof/...`, with yet another file hash.
- **Cause unknown.** Most likely the frame map was frozen against a word that
  differs from the published #484 source. This is a diagnosis, not a proven
  cause (`code/job5_pr501_word_check.py`, `analysis/pr501-source-word.json`).
- **#502 reaches the same value independently.** It has the same kappa and the
  same paid profile, reached by a different frame transfer, and it passes.

**Ledger** (`analysis/hosting-ledger.txt`):
- **Overall.** 56 templates were read, 45 with a hosting section, of which 43
  were parsed. Across them there are 0 overlaps, 0 duplicate helpers, 0
  intervals outside a child's rank and 0 rows outside the stored or re-derived
  window. No window disagrees, and no owner entry repeats within a call.
- **#471's complex template now parses and is clean.** It was the one
  template job 2's ledger could not read, and it is the binding input of #493
  and #498. It has 43,120 slots, 0 cross-copy, and windows re-derived 12 of 12.
- **Cross-copy appears only where expected.** Its only occurrence is #494's
  complex template inside #499: 1,715 of 5,040 residuals, as in #448.
- **#496's pooled allocation, which #502 also uses, is clean.**
  - 40,320 helper occurrences, each hosted exactly once.
  - 35,280 of them (87.5%) on a family of another replica.
  - At most one helper per family per call.
  - Family numbering is consistent on every slot.
  - Every hosted child is tiled exactly: 5,392 fully hosted and 8,992 with a
    paid remainder.
  - Every slot lies inside the window re-derived from the cover-sweep schedule.
- **Several owners in one family are standard.** Within one call this is the
  norm in the bank templates of the main lineage and in #442's hosted bit
  templates (for example 8,916 shared families in #493's bit template). #471
  and #500 apply it to complex hosts: 9,160 and 9,576, at most 5-7 per family.
  It is not a new admission. Different routes give different cover classes,
  so the registers stay distinct.
- **Not parsed:**
  - #495's `complex-eleven-hosted-v1`, which has no slot rows;
  - #499's hybrid cross-copy template, which has 5-field rows;
  - #498's `nonroot-paired-whole-owner-v1`, which has owners only: 60,984
    coordinate-whole and 1,936 paired-rational. Its pairs are checked only by
    its author's verifier.

**Result.**
- **Top claim.** The top claim without cross-copy that reproduces here is
  #502 at 1.343518018117309e-3, 3.07% above #493.
- **What it rests on.**
  - #484's gauge/kernel word, conditional on #484's Lemma A (the global
    spectator realisation) and Lemma G;
  - #495's retiming;
  - #496's cross-replica pooled allocation, which passes our ledger;
  - #493's bit word.
- **Without Lemma G.** The best reproduced claim is #500 at
  1.308501945841842e-3. It uses #471's footprint rule, which is the standard
  bank mechanism.
- **Conditions.** Everything remains conditional on the authors' declared
  interfaces and on the hosting lemma (#442 §2), which is still unreviewed.
- **Newer claims not replayed.** During the run, #503, #504 and #505 appeared;
  #505 claims 1.357701757628940e-3.

## 7. Where the complex cost sits (agent, 2026-10-12)

The operator asked for computation on the asynchronous whole-owner mechanism (#505 and its lineage) rather than
another audit. Before building a search, the agent measured how much of the complex saving that mechanism controls.
All numbers come from published plans and from words built in job 5. They are agent analyses, not operator runs.

**First-order form of b.** The moment engine solves sum_r (r*n_r)/(m*W) * (m/r)^b = 1 with m = 73. To first
order this gives b = D / Phi, where D = m*W - rank mass is the deficit and Phi = sum_r r*n_r*ln(73/r). For #523's
published plan (`inputs/ASYNC112-PLAN.json` at a900f98b), D = 2,560 and Phi = 1,748,788. Their ratio,
1.4638707e-3, equals the plan's own `linear_saving` exactly.

**The asynchronous allocation governs 4.7% of Phi.** The allocation decides only the idle remainders. In #523
they are `{3:3354, 5:3270, 7:60, 48:230}` with Phi 81,564. The rest, 1,667,224 (95.3%), is 72 copies of the local
word's paid profile, which per call is about `{1:2531, 2:160, 3:530, 4:88, 5:298, 6:68}`. Rank-one children alone
are 44.7% of Phi, rank 3 is 22.7% and rank 5 is 19.0%. Three facts close off the allocation lever:
- #523's integer nomination stopped at a MIP gap of 5e-5;
- #520's open allocator reproduces #505's profile as the optimum, and on #507's widths it reaches the timing-free
  ceiling (all windows open);
- #514's notes report no gain from T = 16, K = 5, offsets 4/6/8/12 or modulo-4 overlap.

Even the unattainable floor, with all 37,872 units of leftover rank in untouched rank-48 ports, would raise b by at
most 3.9%.

**Frame timings of the local word.** Every A/B gate of a split-centre word carries a frame (a subspace of F_2^9).
Registers climb to it, and every climb is a paid child of rank Δdim. With gates and coefficients fixed, the frame
timing is free within the emitter's rules:
- every register's frames form an inclusion chain from its start frame to its final frame;
- registers enter the centres phase exactly at their centre frame or target level.

`code/job6_retime_search.py` replays this model and reproduces the stored `local_profile` of all 7 distinct
#484-lineage words built in job 5. In a 108 s probe, the annealer took unretimed #484 words down by 180-252 Phi.
One of them reached 23,249.83, which is exactly the value of #495's retimed word. The retimed #495 and #502 words
gained nothing. Frame retiming is therefore already exhausted on the words that #495/#501/#502 retimed. Whether it
is exhausted on #522's rank-sector factory and on #523/#527's 112-port words is what job 6 measures. Those words
contain gates whose frames were transferred rather than re-optimized.

**Job 6 result (operator run `20261012T014457Z-job6`, budget 8 h, stopped by the operator after 5.33 h of
search).**
- **Builds.** Both builds passed as-is with the exact title kappa in 235 s each (peak RSS 0.27 GB):
  #523 (0.001457945761723368) and #527 (0.001467289440740487, draft at pinning). #527 is the highest
  independently reproduced claim of this campaign; it carries the same inherited conditions as its lineage.
  They yield four new words: #514 (`baseline514`), #522 (`source522`), #523 (`base112`) and #527 (`base112`).
- **Search.** All five words, including the #502 control, passed the format gate. 15 annealers (3 per word)
  ran 13.0 billion moves and accepted 15.2 million of them, worse moves included, over 33 reheating cycles
  each. No annealer found any timing below its word's published one.

| Word | Published Phi of paid climbs | Best found | Moves | Accepted |
|---|---:|---:|---:|---:|
| #527 `base112` | 22,810.28 | 22,810.28 | 2.61e9 | 3.67e6 |
| #522 (`source522` in #527) | 23,093.29 | 23,093.29 | 2.60e9 | 3.00e6 |
| #523 `base112` | 22,976.06 | 22,976.06 | 2.61e9 | 3.10e6 |
| #514 (`baseline514` in #523) | 23,259.07 | 23,259.07 | 2.61e9 | 2.37e6 |
| #502 control | 23,269.31 | 23,269.31 | 2.55e9 | 3.06e6 |

The operator pressed Ctrl-C at 07:09 UTC, and the agent recorded the stop in `protocol.json` (`stopped_by_operator`).
The summary was rebuilt from the annealer records with `job6_retime_search.py --summarize`
(`search/SUMMARY-FROM-CHECKPOINTS.json`).

**Interpretation.**
- Measured: from unretimed #484 words, this search reaches the retimed optimum within seconds.
- Measured: on every newest word it finds nothing in billions of moves.
- Conclusion: the authors' timings are at least deep local optima for the move set used, which is plateau raise
  and lower with cascades, plus random intermediate frames. Frame retiming with a fixed gate sequence is not a
  route to a higher kappa in this lineage.
- Limitation: this is a search result, not an optimality proof. Moves that change the gate order, or the gates
  themselves, are outside it.

**Job 7 (built 2026-10-12, operator run pending).** With frames free, the gate order matters only through
admissibility. For a given frame assignment, each register's cost depends only on the set of frames it visits.
Reordering helps only if it admits a cheaper assignment that the original order forbids. That requires commuting
gates on some register whose frames should appear in the other order. `code/job7_reorder_search.py` moves a gate
next to a commuting neighbour on one of its registers, inside the window that commutation allows on all its
registers, and keeps job 6's frame moves. Toy words show the effect exists: in a random search, about 1 in 120
toy words admits a reorder that saves 2*Phi(1) - Phi(2) = 1.386 over the best fixed-order timing, and job 7 finds
it where job 6 cannot. On the real words a 2.7-minute probe (187 M moves, 24 M accepted gate moves) found nothing.
The operator's run will tell whether the newest words have any such slack.

Any gain a later search finds is only a candidate until the agent re-emits the word and passes the package's own checks:
the local replay of all columns, the Clifford phase lowering of every new edge, the owner audit with unchanged
helper widths, and both moment engines. The deeper lever, frame chains shared by more than two targets (#520 §3),
changes the gate sequence itself and is not part of job 6.

## Recommended next steps

1. #502 (1.343518e-3) is the top reproduced claim without cross-copy (job 5).
   #493 (1.30353e-3) and its binding input #471 also reproduce. Two items
   separate these tiers from a reviewed result:
   - #484's Lemma A and Lemma G, which are the review points its author names;
   - the idle-data hosting lemma (#442 §2), which is still unreviewed upstream
     and whose audit the user deferred.

   Further replays have diminishing value while new claims appear every 30-60
   minutes.
2. The cross-copy finding was posted upstream on 2026-10-11, on
   [#448](https://github.com/CrocSwap/integer-mult-bounds/pull/448#issuecomment-6113791847)
   and [#480](https://github.com/CrocSwap/integer-mult-bounds/pull/480#issuecomment-6113805810)
   ([texts](upstream-comments/)). The author accepted it and retitled #448,
   #480 and #494 as not established
   ([replies](upstream-comments/README.md#replies-checked-2026-10-11-2140-utc)).
3. The five Dugongue packages of job 4, and #498, would pass without any
   deviation if their commits included the `.gitattributes` listed in their
   manifests. This could be mentioned to the author; nothing has been posted.
4. #501's frame map pins a source word that a fresh build of the published
   #484 source does not produce. Our six builds agree with each other and with
   #484's own pin. This could be reported to #501's author with
   `analysis/pr501-source-word.json`; nothing has been posted.

5. Job 6 closes frame retiming with a fixed gate sequence for the newest words. The remaining freedom inside the
   current construction is the gate order: many gates commute, and a different order changes every register's
   frame chain. Job 7 searches commuting reorders jointly with frames; its operator run is pending. Beyond it lie
   the shared delivery chains of #520 §3, which change the gates themselves.

## Evidence

- `evidence/<run-id>/` holds gzip copies of each run's protocol, configs and
  logs, plus `archive-manifest.jsonl.gz` with the original sizes and hashes.
  For job 2 it also holds `SUMMARY.json`, the 39 records, 39 replay logs, 1,125
  receipt/result/audit JSON files from `out/` and `analysis/hosting-ledger.json`.
- Not published:
  - the 39 worktrees (11 GB): pinned upstream source, regenerable from
    `configs/job2-replays.json`;
  - bulk replay outputs (2.6 GB), including the hosted templates: regenerable
    by `./run.sh 2`, and their SHA-256 hashes are in the records.

  Both stay under
  `/srv/ai/work/rad/integer-multiplication-bounds/frontier-batch-20261011/runs/`.
- Ledger regeneration:
  `python3 code/job2_hosting_ledger.py --run <job2 run> --out <file>` (17 s).
- Job 5 publishes 318 files (0.57 MB gzip):
  - records, replay logs, `checks/`, `SUMMARY.json`;
  - receipt/result/audit/failure JSON from `out/` and `repair/out/`;
  - `analysis/`: the ledger, the mutation controls and the #501 diagnosis.

  Not published: the worktrees (1.7 GB) and bulk outputs (0.8 GB), which stay in
  the run directory. Regenerate them:
  - the run: `./run.sh 5`;
  - the ledger: `python3 code/job5_hosting_ledger.py --run <job5 run> --run <job4 runs> --out <file>` (10 s);
  - the controls: `python3 code/test_job5_ledger_mutations.py <#496 hosted template>` (2 s);
  - the #501 diagnosis: `python3 code/job5_pr501_word_check.py --run <job5 run> --out <file>` (2 s).
- Job 6 publishes 45 files (0.05 MB gzip):
  - protocol with the operator stop, configs, build and search logs;
  - the two build records, checks, logs and result/audit JSON;
  - `search/WORDS.json` and `search/SUMMARY-FROM-CHECKPOINTS.json`, with all 15 annealer records.

  The per-annealer files under `search/checkpoints/` (735 bytes each) are not copied separately, because the
  archive validator skips that directory name. Later runs use `search/annealer-states/`. Not published: the
  worktrees and build outputs (0.4 GB), including the five searched words. Rebuild them with `./run.sh 6 <hours>`;
  their SHA-256 hashes are in `search/WORDS.json`.
