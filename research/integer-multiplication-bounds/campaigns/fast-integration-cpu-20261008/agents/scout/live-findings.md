# Actionable public changes

This ledger records new mathematical or proof-status changes rather than every unchanged observation. All times are UTC on 2026-10-08. Public claims remain conditional and are not accepted as a complete theorem solely from their checks.

| Observed | Source and author | Pinned head | Mechanism / claimed saving | Proof status at observation |
| --- | --- | --- | --- | --- |
| 12:43 | [PR 36](https://github.com/CrocSwap/integer-mult-bounds/pull/36), icekylinx | `11817ccacb564bb7f98789c20dc11d3fece207e3` | Copied retained-center schedule, `(25,23)` bit graph; `kappa=3.84569e-5` | Written conditional proof and finite reconstructions; inherited unchanged checks reused |
| 12:43 | [PR 37](https://github.com/CrocSwap/integer-mult-bounds/pull/37), Rohan Arun | `cb86e50e9a07685068874d8e4174b2e6c209b95c` | PR 36 plus reversed `(23,25)` corners, data `9*[1]+[21,17,481]`; `kappa=3.850771033e-5` | Draft; full inherited rerun pending |
| 12:43 | [Swapnil round five](https://github.com/Swapnil-jain/integer-mult-kappa/tree/c2c2f279d93643e5ff3fe121a0fbc68e0e6f4007), Swapnil Jain | `c2c2f279d93643e5ff3fe121a0fbc68e0e6f4007` | Common flag, cheaper side circuit, finer side/data batching; `kappa=309575208081/(2*10^16)` | Finite arithmetic checked in Lean under explicit analytic premises; full algorithm conditional |
| 12:53 | [PR 38](https://github.com/CrocSwap/integer-mult-bounds/pull/38), Dominik Scholz | `cc794077f6c103e24ec0939be765cd1521239aab` | PR 36 plus fixed `I+J` local bases, complete original-envelope transitions; data `26*[1]+[21,481]`; bit `a=19432631/(5*10^11)`, final `kappa=3.886224e-5` | Draft; producer/moment/common-basis checks passed, full inherited rerun pending |
| 12:53 | PR 37, Rohan Arun | `2f7578affce416ad4b6c41f3438ebb734f66a899` | Scientific construction unchanged; validation receipt added | Ready for review; claims 182 inherited tests, 12 focused tests and 18 historical patch checks passed |
| 13:02 | [PR 39](https://github.com/CrocSwap/integer-mult-bounds/pull/39), Rohan Arun | `50e54ece17afa4bd3cccd1927e9cdea5098038c2` | Only middle `L25=I+J`, common generic rational `L23`, reversed data `9*[1]+[21,17,481]`; bit `a=3886826921/10^14`, final `kappa=3.886675852e-5` | Draft; portable replay and 10 focused controls passed; full inherited rerun pending |
| 13:02 | PR 38, Dominik Scholz | `605323bab4ba330de3d1785dc5b3ecb14e8ab747` | Scientific construction unchanged; validation receipt added | Ready; claims 170 inherited tests, both selected producer rebuilds and 19 patch checks passed |
| 13:11 | PR 39, Rohan Arun | `70ae24129649f6d6d4ec6360962a80c3c42a38f1` | Scientific construction unchanged; validation receipt added at 13:05:47 | Ready; claims 192 inherited tests, 10 focused controls and 18 patch checks passed |
| 13:21 | [PR 40](https://github.com/CrocSwap/integer-mult-bounds/pull/40), Rohan Arun | `43f59ff533598762cbc43a5e14af2bbbc76fabbd` | Both local bases `I+J`, complete original-envelope h23/h25 profiles, reversed data `9*[1]+[21,17,481]`; bit `a=783777693/(2*10^13)`, final `kappa=3.918734894e-5` | Draft; fresh h23 replay, 11 controls and finite geometry passed; full inherited rerun pending |
| 13:30 | PR 40, Rohan Arun | `e3bf3ab0cb1ec48588e279b31a97e7a49c72f99e` | Scientific construction unchanged; validation receipt added at 13:24:23 | Ready; reports 203 inherited tests, a fresh full 4,073,300-pair replay and 18 historical patch checks at science commit `43f59ff533598762cbc43a5e14af2bbbc76fabbd` |

All PRs in this table retain Apache-2.0 notices; their imported RaD interfaces retain CC0 notices. PR 36 credits Paureel, Swapnil Jain, Zhihao Chen, Rohan Arun, Dominik Scholz and earlier producers for distinct dependencies. PR 37/38/39 compositions inherit those mechanisms rather than independently adding their exponent savings.

The broader direct fork/search intake also found [platypii's Lean project](https://github.com/platypii/integer-mult-bounds-lean), whose public head moved through finite optimized-circuit and forward-frame proofs. It is work in progress; no new leading algorithmic bound was identified there. [Fernando's independent TypeScript report](https://github.com/fernandoeeu/integer-mult-bounds/blob/097b96a7eba8/independent/ts/prs/REPORT.md) checks finite earlier PRs through 16 and expressly leaves analytic obligations open. It does not review PRs 36–39.

At 13:21, CrocSwap main changed to `1a74950ce5074b848243ba89d8022fbadba66105`, Douglas R. Colkitt, committed at 13:10:58. Its separate ternary checkpoint claims `2^-30`. [Its contribution review](https://github.com/CrocSwap/integer-mult-bounds/blob/1a74950ce5074b848243ba89d8022fbadba66105/docs/research/contribution-review.md) records stronger submissions as unverified, states that it has not reproduced or independently audited their full tape/precision chains, and does not treat them as accepted. This is a proof-status update, not a mathematical exclusion of those claims.

The initial source snapshots and PR 38/39 snapshots are listed in [input-manifest.json](input-manifest.json). Readiness-only follow-up heads are identified above and in the observation files; no duplicate whole snapshot is necessary where scientific files are unchanged.

At 13:30, platypii's public Lean head was `57652088e3adf0c1aa7714803b6b270d5eaaa236` (commit 13:29:29), adding sparse optimized invocation and instruction bounds. No new full analytic theorem or stronger numerical saving was identified in that change. CrocSwap main and Swapnil main were unchanged at this poll.

At 14:07, Swapnil Jain's main advanced to
[`f2176bc1124821bf17eb63725bd366d7bdc020a3`](https://github.com/Swapnil-jain/integer-mult-kappa/commit/f2176bc1124821bf17eb63725bd366d7bdc020a3),
committed at 14:01:26 UTC. Round six claims
`kappa=3666565558019/10^17`, with bit saving `36667/10^9` at `h=23`
and complex saving `36926111/(5*10^11)` at `h=24`. The changed mechanism
adopts PR36's copied centres, then replaces direct centre wires by retained
point totals built from existing side roles. Copies pay rank `h-1`, originals
pay rank `1`, and centre roles leave `W`. The complex side adopts the copied
centre and whole-residual batching schedules. A new Lean round-six file checks
finite moments and assembly arithmetic under the earlier analytic premises.
These are conditional public claims; no new proof of the arithmetic CRT
payload cost was identified in the changed files. The pinned eligible PR40
reference has the larger bit saving; this update does not require replacing
its primitive in the CPU composition. Source licensing is Apache-2.0 with
the prior-work notices retained. A compact selected source snapshot and exact
archive identity are recorded in [swapnil-round6-source.json](swapnil-round6-source.json).

At the same poll platypii's public head was
`69f017a0e88129ea227d5d399904c062923f4e03`, committed at 14:05:29 UTC,
with local-projector and reused-boundary finite proofs. No complete analytic
multiplier theorem was identified. New campaign-linked and suspected derivative
branches remained metadata-only quarantines and were not used in the science.

At 14:53 the eligible new [PR45](https://github.com/CrocSwap/integer-mult-bounds/pull/45)
by Alejandro Zarzuelo Urdiales was pinned at
`5e219f7b3513b092d3ee919a303db0f55a3a0a0e`, submitted at 14:35:44 UTC.
Its self-contained Gaussian parity audit identifies the exact legality
condition for division by `1+i`, retains the shared parity defect bit, and
distinguishes the sharp completed `C`-tensor denominator `ceil(D/2)` from
the normalized `H0` denominator, which remains `D` bits in the worst case.
The author reports 69 Lean finite arithmetic/lattice statements under Lean
4.31 and exact Python controls. These statements do not formalize the full
network, tape costs or analytic multiplier. The contribution explicitly
credits historical PR23's completed-child semantic work and the established
Gaussian denominator literature; no new campaign-linked RaD input was used
in this intake. No changed full assembly exponent or arithmetic CRT cost
was claimed. Ten selected files, totaling 72,087 bytes, are recorded in
[pr45-source.json](pr45-source.json), with Apache-2.0 and author notices
retained. The community integration branch and unrelated repository files
were not downloaded.

The scout replayed that selected Python exact-control file without changes;
all 3,721 division, 13,122 pair, 72 tensor and 36 normalized tensor cases
passed, including denominator sharpness and four negative controls.
[pr45-controls.json](pr45-controls.json) records the pinned source hash and
counts. Lean was not compiled by this scout. The replay adds bounded evidence
only and changes no full-multiplier claim.

At 15:11 the public watch retained unchanged eligible CrocSwap, Swapnil and
PR40 heads. Newly associated branches for excluded PR44, PR46 and PR47 remain
metadata-only quarantines. The watcher now carries exclusions forward,
filters references transitively through known excluded derivatives, and
omits their fork branches from actionable changes. No scientific source or
bound from those branches enters this campaign.

At 15:21 CrocSwap main moved to
`0605a24a28836168ad29d6239b46064b892298fc`, Douglas R. Colkitt,
committed at 15:18:13 UTC, with metadata headline "Publish audited community
bound with contributor attribution". That aggregate new publication is
metadata only here; its mathematical contents, bound and audit conclusions
were not consumed. Eligible PR39, PR37, PR36, PR32, PR24, PR18 and PR10 changed
to closed at 15:18:19 UTC with unchanged scientific heads. These status changes
do not establish acceptance of the pinned PR40 primitive or change the CPU
composition's named assumptions. The watcher now requests head metadata
through GraphQL, without the source patches included by a REST commit response.
# 2026-10-08 16:03 UTC: eligible metadata follow-up

The 15:45 broad scout and 15:58 refresh found no new eligible scientific input needed by the active CPU construction. Swapnil round six remains pinned at `f2176bc1124821bf17eb63725bd366d7bdc020a3`. New aggregate-main and campaign-linked PR mathematics remain quarantined; recent Platypii theorem headlines are metadata only and supply no scientific premise.

Eligible historical [PR2](https://github.com/CrocSwap/integer-mult-bounds/pull/2), Bortlesboat, advanced to `ff505ea9f6d5528cf2e2aba02e1db85471ff9bf4` at 15:36:13 UTC. Metadata identifies a two-parent integration of its old `1c200af99d348de496d78274de3584339dcf02e3` review packet with eligible public checkpoint `1a74950ce5074b848243ba89d8022fbadba66105` from 13:10:58. The PR body is unchanged; its substantive global-pair alignment is already present in the pinned native `aligned_points` interface. No new source snapshot, mathematical gain or external acceptance is inferred. This intake does not consume the later aggregate main.
