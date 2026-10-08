# Public-source intake and live scouting

Observed 2026-10-08 12:43:39 UTC. Public GitHub content was read through
`gh api`; no other RaD campaign files, new-branch source contents or
unpublished results were consumed, and no other execution host was contacted.
The scout has no CPU-bound execution allocation. Source snapshots are external,
immutable campaign inputs; [input-manifest.json](input-manifest.json) records
their obtainable commits, tarball hashes, locations and license hashes.
The snapshots and archives are read-only; generator/build replays must work
from a copy in the receiving agent's task-owned derived directory.

## Findings at intake

| Source / author | Pinned head | Public timestamp | Mechanism / claimed saving | Proof status and overlap |
| --- | --- | --- | --- | --- |
| [CrocSwap PR36](https://github.com/CrocSwap/integer-mult-bounds/pull/36), icekylinx, substantial OpenAI assistance | `11817ccacb564bb7f98789c20dc11d3fece207e3` | Updated 12:27:27 UTC | Copied retained centers replace local ranks `(r,h)` by `(r,h-r)`; two-stage mass `Wm-N+L`; bit factors `(25,23)`, complex `(28,28)`; conditional `kappa=384569/10^10` | Written scalar/frame/dirty-scratch lemma, exact incremental producer and moment checks; upstream interfaces remain hypotheses. Directly incorporates Paureel/#29 topology and correction, #31/#33 corners, #21/#23/RaD semantic and bulk transfer. |
| [CrocSwap PR37](https://github.com/CrocSwap/integer-mult-bounds/pull/37), Rohan Arun with OpenAI Codex | `cb86e50e9a07685068874d8e4174b2e6c209b95c` | Updated 12:39:52 UTC | PR36 centers composed with James Chang's reversed PR34 family at `(23,25)`; data profile `9*[1]+[21,17,481]`; conditional `kappa=3850771033/10^14` | Draft at intake; focused checks complete, integrated `make verify` pending. Claimed +0.132122792% versus PR36. Inherits full conditional setup/tape/analytic/assembly assumptions; no external expert or formal theorem acceptance. |
| [Swapnil round five](https://github.com/Swapnil-jain/integer-mult-kappa/tree/c2c2f279d93643e5ff3fe121a0fbc68e0e6f4007), Swapnil Jain with Claude assistance | `c2c2f279d93643e5ff3fe121a0fbc68e0e6f4007` | Commit 12:38:33 UTC | A common flag basis batches both auxiliary corners, centers and side residuals one level down; global-matching side graph `R=403248` at `h=47`; data-entrance run; conditional `kappa=309575208081/(2*10^16)` | Written equal-factor proof plus small exact / working-dimension modular checks. Lean checks arithmetic certificates with analytic premises, not the complete multiplication theorem or geometry. Retains Paureel motif, PR7 complex source frames, own analytic/routing stack. |
| [CrocSwap PR35](https://github.com/CrocSwap/integer-mult-bounds/pull/35), Dominik Scholz with OpenAI/Anthropic assistance | `9c345a2a11e5f4f3649f7c68214bf9a2a0a3fe9c` | Updated 12:37:15 UTC | Fixed local bases `I+J` at `(47,45)` replace generic internal profiles, retain data `48*[1]+[43,1933]`; conditional `kappa=16631776/10^12` | Claimed integrated validation complete, 183 regressions and exact bounded-minor reconstruction. Separate reusable fixed-basis result; adopts PR32 profiler and PR33/29 dependencies. |

At the 12:58:02 poll, the new [PR38](https://github.com/CrocSwap/integer-mult-bounds/pull/38)
by Dominik Scholz was found, head `cc794077f6c103e24ec0939be765cd1521239aab`,
updated 12:49:21 UTC. It composes copied centers with fixed I+J **original**
envelopes on the actual PR36 (25,23) graphs, giving conditional
`kappa=242889/6250000000=3.886224e-5`, bit saving
`19432631/500000000000`, and conservative data `26*[1]+[21,481]`.
It explicitly preserves all paid copies and physical accounting. Draft full
regression is pending; finite producer/CRT/moment/assembly checks are reported.
The pinned source and [fixed-basis interface map](fixed-basis-interface.md)
were sent promptly to the coordinator and computational agents.

At 13:04:26, new [PR39](https://github.com/CrocSwap/integer-mult-bounds/pull/39)
by Rohan Arun was found, head `50e54ece17afa4bd3cccd1927e9cdea5098038c2`,
updated 12:58:44 UTC. It fixes only the middle L25=I+J and leaves GL23 free
in reversed (23,25), retaining the second 17-block and claiming conditional
`kappa=971668963/25000000000000=3.886675852e-5`. Its source is pinned in
the manifest. [The scoped hybrid review](hybrid-basis-review.md) maps the
common-basis argument and changed-graph obligations. PR38 meanwhile became
ready at documentation/validation follow-up
`605323bab4ba330de3d1785dc5b3ecb14e8ab747`; its scientific sources remain
the pinned `cc794077...`.

At 13:15:27, PR39 became ready at validation-only follow-up
`70ae24129649f6d6d4ec6360962a80c3c42a38f1`; its scientific inputs remain
`50e54ece...`. The [receipt](validation-pr39.json) records the upstream
executable rerun. CrocSwap main separately advanced to
`1a74950ce5074b848243ba89d8022fbadba66105`, preserving a conditional
2^-30 checkpoint and crediting parallel contributions. Its new contribution
review explicitly treats the stronger submitted PRs as unaccepted claims,
since the full chains have not been audited there. The campaign must keep
its own conditional proof/review scope clear. A newly visible James Chang
A5 branch was inspected; it is earlier 11:20 UTC geometry, not a new
copied-center or graph rewrite. Details and citations are in
[supplementary-sources.json](supplementary-sources.json).

At13:25:27, ready [PR40](https://github.com/CrocSwap/integer-mult-bounds/pull/40)
by Rohan Arun was found at
`e3bf3ab0cb1ec48588e279b31a97e7a49c72f99e`, updated13:24:23 UTC.
It fixes BOTH I+J factors at reversed23/25 while retaining data
`9*[1]+[21,17,481]`, with final conditional
`kappa=1959367447/50000000000000=3.918734894e-5`.
The pinned snapshot, manuscript and code were sent to both computational
agents immediately. [The scoped both-fixed review](both-fixed-review.md)
maps the full finite data-family proof and changed-DAG obligations. Its
upstream receipt records full validation at research commit
`43f59ff533598762cbc43a5e14af2bbbc76fabbd`. No new full replay is attributed
to the scout, and no generic profile survives on either fixed axis.

At13:45:27, both default scientific heads and every allowed PR scientific
head were unchanged. PR40's metadata update changed no pinned source, and
allowed comments/reviews on PR38/39/40 supplied no new mathematical review.
The Colkitt public integration branch's new transfer-review document at
`731a70c67b0d82e3a86db11fc6c1777c579739bd` was acquired separately and
reported to the coordinator. It conditionally supports generic batching,
mixed-width row/volume recurrence and larger-child semantic induction;
selected geometry, bulk/tape and full analytic transfer remain open there.
It explicitly identifies itself as an assistant review, not human peer
review. The changed-DAG scalar E must still cover the actual new schedule.
Pinned citations and recovery are in the manifests.

At14:05:27, Swapnil's main advanced to round six
`f2176bc1124821bf17eb63725bd366d7bdc020a3`, committed14:01:26 UTC.
Its conditional final kappa is `3666565558019/10^17`; it adopts copied
centers and retained point totals, and adds a two-stage h24 complex
pair-exclusion producer with claimed complex saving
`36926111/(5*10^11)`. The snapshot is pinned and read-only. Its useful
producer lead is to reconstruct retained totals from reusable disjoint
active supports, trying two-/three-node covers then a greedy exact cover.
This is not a proven global-minimum set-cover algorithm. The lead was sent
to the graph agent; no saving in our graph is inferred. Its separate complex
construction/analytic stack remains an unadopted alternative. No unchanged
baseline replay was run.

At14:45:27, new [PR45](https://github.com/CrocSwap/integer-mult-bounds/pull/45)
by Alejandro Zarzuelo Urdiales supplies a scoped Gaussian parity/denominator
audit at `5e219f7b3513b092d3ee919a303db0f55a3a0a0e`. Selected sources and
provenance are pinned. [The scope review](gaussian-parity-scope-review.md)
checks the written arithmetic and distinguishes completed C-tensor returns
from the D-bit final normalization. The author reports69 Lean declarations
and finite arithmetic controls; the scout did not run either suite. This
changes no selected network or exponent. Another current producer derivative
discovered in the same poll is held under the provenance gate; its body and
source were not opened or mathematically consumed, and its discovery metadata
is omitted from the reduced poll.

PR37 physical invariants are `m=575`, `N=4073300`, `W=188181929`,
`L=2226400`, `s=Wm-N+L=108202762275`, maximum child 529, with all
4073300 paid endpoint corrections retained. Relative to PR36 it removes
`4N` width-one children and `2N` width-15 children and adds `2N` width-17
children. For `0<tau<1`, its moment change
`2N*(17^tau-15^tau-2)<0` follows directly by integrating
`tau*x^(tau-1)<1` from 15 to 17. The source README presents this general
profile inequality separately from rational moment certification.

At the 12:48:39 poll, PR37 advanced to
`2f7578affce416ad4b6c41f3438ebb734f66a899` and became ready for review.
GitHub's exact comparison lists only README/patch metadata and the new
[validation receipt](validation-pr37.json); the scientific source at the pinned
research commit is unchanged. The author reports full `make verify` finished
12:45:18 UTC, 182 tests, 18 historical patch checks, plus 12 focused tests.
This is a reported executable-validation improvement, not external theorem
review. There is no reason to change or restart the pinned experiment inputs.

## Actionable mathematical dependencies

The copied-center schedule is admissible only for a designated retained
terminal carrier with no later producer consumer. Its temporary stream must
be the complete role stream, spectators and control included; all scatter
reads leave the retained scalar unchanged. The rank-`r` temporary transform,
separate rank-one endpoint copy correction, scalar charge, copy/read/erase
cost and source/sink frame cancellation all remain charged. Merely replacing
histogram entries without these contracts would not certify a new graph.

Swapnil's flag mechanism is structurally distinct. On `F tensor F`, the first
`h` rows of a common basis correspond to `U R_i V^T`, and the last `h` inverse
columns to `U^{-T} C_i V^{-1}`. Prefix-square `R_i` and suffix-square `C_i`
force both corner families lower triangular. The pairing constraints are
solved before completing the ambient basis. This can merge `h` corner
singletons into one width-`h` call; it should not be combined by multiplying
headline savings.

The written flag proof is equal-dimension only. A rectangular extension needs
independent row/inverse-column prescriptions through the larger factor,
exact pairing and completion, both auxiliary corner sizes, the one-level-down
side profiles, both data-entrance profiles, and the copied rank-one complements
in the same admissible family. The square support proof does not automatically
establish those conditions at `(23,25)`. Similarly, a fixed `I+J` specialization
must establish the data corners rather than invoke a generic open-set argument
after all local freedom has been removed.

The geometry agent independently derived a shifted rectangular flag extension.
Interface inspection shows its auxiliary and ordinary-local batching already
overlaps PR37's controlled basis. In particular, the PR37 boundary is a sparse
specialization of that flag family. A lower delta-Hessenberg data corner plus
a rank-one term gives the same first run of width a-2; any extra saving needs
the full data profile, especially the second 17-block. A scout's initial
unshifted rectangular support suggestion ignored the last-a inverse-column
offset and was explicitly withdrawn before testing. No improvement is
attributed to that incorrect prescription.

## Scout method and continuation

[scout_poll.py](scout_poll.py) records both default heads, all active/recent PR
heads, linked fork identities and one public repository search. Raw API
responses stay in the campaign external `raw/scout/<UTC>/` tree; compact
timestamped metadata is retained under `polls/`. Poll approximately every ten
minutes until explicit campaign closing, compare changed heads, and inspect new
mathematical mechanisms before alerting the coordinator. Snapshots already in
use remain pinned; a public update does not alter running input identities.
The user's14:24 indefinite extension is preserved in
[extension-protocol.json](extension-protocol.json), without resetting the
original start or rewriting the historical initial deadline.

The [new-basis algebra review](new-basis-algebra-review.md) independently
derives the selected negative rank-one basis, actual lines and centers, and
original-envelope rank bounds. The [data classification review](new-data-classification-review.md)
assesses the exact169 exceptional profiles and complete source-index audit.
These scoped reviews do not assert a new headline bound or full theorem.

To preserve campaign independence, every mutable branch and new PR of the
RaD public fork is excluded from source acquisition and compact poll interpretation.
Only its completed historical source20 commit
`4f8d6c8272b5ff307a0da51df545ec3cd96a8b6e` is retained. Initial broad public
API listings exposed mutable reference/submission metadata before the
exclusion gate was added. Those acquisitions are immutable external
provenance, but the reduced poll exports omit that metadata, and future raw
PR retention filters it before interpretation. No source content or
unpublished result from those branches was opened or used. This omission is
explicit; the
compact exports do not claim to preserve every raw API field.
New public derivatives referring to current RaD producer work are held
outside the consumed source set until their originating campaign is
confirmed as this GPU campaign. [The exclusion record](independence-exclusions.json)
preserves that scope without incorporating their mathematical contents.

Only the campaign coordinator performs Git index, branch, commit and push
operations. All new scout-authored durable files stay in `agents/scout/`.
