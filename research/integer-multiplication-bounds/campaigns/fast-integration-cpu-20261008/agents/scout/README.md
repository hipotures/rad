# Public-source scout

This directory records the CPU campaign's public-source observations and targeted proof criticism. It does not inspect the independent GPU campaign. The coordinating agent alone commits or pushes these files.

## Intake at 2026-10-08 12:43 UTC

The leading discovered public claim is [CrocSwap PR 37](https://github.com/CrocSwap/integer-mult-bounds/pull/37), Rohan Arun, head `cb86e50e9a07685068874d8e4174b2e6c209b95c`: conditional `kappa = 3850771033 / 10^14`. Its stated mechanism is icekylinx's PR 36 copied retained centers combined with James Chang's PR 34 reversed corner profiles at dimensions `(23,25)`. The PR was a draft at intake; its full integrated rerun remained pending. The claimed savings are not added to one another.

[PR 36](https://github.com/CrocSwap/integer-mult-bounds/pull/36), icekylinx, head `11817ccacb564bb7f98789c20dc11d3fece207e3`, claims `384569 / 10^10`. Its copied-center schedule changes the paid rank budget from `Wm-N+2L` to `Wm-N+L`; the transformed copy and rank-one endpoint corrections remain charged. Both recent claims retain RaD's completed-child semantic guard, arbitrary-coordinate routing, phase-cell Gaussian inverse and bulk resampling. They do not adopt Swapnil's segmented inverse.

[Swapnil Jain's round five](https://github.com/Swapnil-jain/integer-mult-kappa/tree/c2c2f279d93643e5ff3fe121a0fbc68e0e6f4007), committed at 12:38:33 UTC, claims `309575208081 / (2*10^16)`. It introduces a common flag basis, shared side circuit, side-role batching one level down and data-entrance corners. Its analytic stack separately contains longer digits, a segmented/recentered Toeplitz inverse, one chunk per axis, fine-bit exposure and permuted selected-bit swaps. Its Lean checks prove finite arithmetic statements under named analytic premises; they do not formalize the complete multiplication algorithm.

## What is already public

The leading balanced assembly already has semantic `C1=1` and permits `epsilon` approaching one. With `q = a_bit*(1-2h)` it chooses `epsilon=(1-h)/(1+q)`. Its scoped limit is `a_bit/(1+a_bit)`. The complex stopped-leaf condition `(1-beta)*a_complex > a_bit` survives, with `beta=1/20` and `a_complex=717/10^7`, but is not binding for this witness. The product row degree 2000 is explicitly charged. An isolated removal of the old `epsilon<1/2` ceiling is therefore not a new leading result.

The eligible intake was superseded by PR38, PR39 and PR40. [The live findings](live-findings.md) records exact heads, changed profiles and validation receipts. The pinned eligible PR40 science head is `43f59ff533598762cbc43a5e14af2bbbc76fabbd`, with `kappa=3.918734894e-5`, bit saving `783777693/(2*10^13)`, and readiness head `e3bf3ab0cb1ec48588e279b31a97e7a49c72f99e`. Its full checks support a conditional argument, not external acceptance.

At 13:48 a source audit identified the full-payload CRT rotations that survive an improved axis reversal. The coordinator withdrew the tentative stronger full composition. [The CRT review](crt-cost-review.md) proves the scoped ceiling `a/(1+a)` with those rotations retained and records a Hamming-weight discriminator showing that the true modular map is not a named-bit permutation. The new product gather, spatial locality, physical band-LU and deferred transform remain useful separately reviewed interfaces.

At 14:13 the inverse agent supplied a new independent-node CRT tree with guarded interval rotations. [The independent review](guarded-crt-review.md) supports its repeated-source BIT extension, dirty predicate loading, monotone padded splitting and physical bank accounting under the inherited tape primitives. This repairs the audited row if the completed schedules and exact repair boundaries are adopted. Full multiplication assembly remains the coordinator's responsibility.

The surviving physical rows include prefix movement, phase localization and phase boundaries, with savings `1-epsilon`, `1-epsilon-delta`, and `min(1-epsilon-delta,r-delta)`. A stronger full algorithm must change the limiting rows or improve the bit child-width moment.

## Records and recovery

- [Input manifest](input-manifest.json): public pinned commits, source snapshot paths, archive sizes/hashes, licenses and acquisition commands. Source snapshots are ignored execution inputs, not contents of the Git clone.
- [Intake](intake.json): PR metadata and public claim text as observed.
- [Fork heads](fork-heads.json): directly queried public fork branches at intake.
- [Analytic leads](analytic-leads.md): tensor packing, a proved regular Laurent estimate and explicit missing machine interfaces.
- [Deferred-reservoir criticism](deferred-reservoir-review.md): source-grounded review of the new equal-axis transform schedule.
- [Continuation reviews](all-cardinality-continuation-review.md): independent complete-profile enumeration and universal concavity exclusion for the coordinator's exported generic graph.
- [Global inverse locality review](global-locality-review.md): weighted lifted-kernel and principal-window criticism, including aliases.
- [Joint product and cap review](joint-interface-review.md): exact occupied order, metadata, cut exclusions and the explicitly conditional primitive cap.
- [Physical LU and long-record review](physical-lu-review.md): independent backward-error induction and address/precision/bank comparisons.
- [CRT audit](crt-cost-review.md): remaining payload rotations, exact scoped ceiling and primary literature follow-up.
- [Guarded CRT review](guarded-crt-review.md): independent criticism of the new arithmetic repair and its actual banks, scans and repair boundaries.
- [Round-six source receipt](swapnil-round6-source.json): compact selected source provenance for Swapnil's 14:01 public update.
- [Prime interval review](prime-interval-review.md): primary Baker–Harman–Pintz citation, distinct-prime supply and charged deterministic setup for the long-digit chooser.
- `observations/`: timestamped compact observations and differences.
- [refresh_public_sources.py](code/refresh_public_sources.py): one read-only `gh api` observation, with optional broader searches; it never fetches RaD branches or performs Git mutations.

Snapshots reside in `../../work/scout/snapshots/`. Reacquire any snapshot with `gh api repos/<repository>/tarball/<sha>`, then extract it outside the durable tree. Apache-2.0 applies to the two source repositories; imported RaD source notices identify CC0 material. Any copied source must retain its own notices and license.

To refresh the public watch from the repository root:

```bash
python3 research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/scout/code/refresh_public_sources.py --forks --search
```

No remote human acceptance or full formal verification is inferred from passing numerical, finite or Lean arithmetic checks.

The live watcher now lists PR metadata without requesting bodies, excludes new campaign-linked RaD entries and suspected derivatives, then fetches only eligible bodies. It never enumerates live hipotures forks. No independent campaign's new branch, source, result or bound is used for scientific comparison. Two earlier automatic raw list captures are quarantined in ignored work and explicitly excluded from publication in the input manifest; their excluded metadata was removed from the durable compact observations. The pinned eligible reference is PR40, without a claim that it is the current global best.
