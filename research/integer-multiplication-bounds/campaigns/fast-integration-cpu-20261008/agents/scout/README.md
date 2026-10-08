# Public-source scout

This directory records the CPU campaign's public-source observations and targeted proof criticism. It does not inspect the independent GPU campaign. The coordinating agent alone commits or pushes these files.

## Intake at 2026-10-08 12:43 UTC

The leading discovered public claim is [CrocSwap PR 37](https://github.com/CrocSwap/integer-mult-bounds/pull/37), Rohan Arun, head `cb86e50e9a07685068874d8e4174b2e6c209b95c`: conditional `kappa = 3850771033 / 10^14`. Its stated mechanism is icekylinx's PR 36 copied retained centers combined with James Chang's PR 34 reversed corner profiles at dimensions `(23,25)`. The PR was a draft at intake; its full integrated rerun remained pending. The claimed savings are not added to one another.

[PR 36](https://github.com/CrocSwap/integer-mult-bounds/pull/36), icekylinx, head `11817ccacb564bb7f98789c20dc11d3fece207e3`, claims `384569 / 10^10`. Its copied-center schedule changes the paid rank budget from `Wm-N+2L` to `Wm-N+L`; the transformed copy and rank-one endpoint corrections remain charged. Both recent claims retain RaD's completed-child semantic guard, arbitrary-coordinate routing, phase-cell Gaussian inverse and bulk resampling. They do not adopt Swapnil's segmented inverse.

[Swapnil Jain's round five](https://github.com/Swapnil-jain/integer-mult-kappa/tree/c2c2f279d93643e5ff3fe121a0fbc68e0e6f4007), committed at 12:38:33 UTC, claims `309575208081 / (2*10^16)`. It introduces a common flag basis, shared side circuit, side-role batching one level down and data-entrance corners. Its analytic stack separately contains longer digits, a segmented/recentered Toeplitz inverse, one chunk per axis, fine-bit exposure and permuted selected-bit swaps. Its Lean checks prove finite arithmetic statements under named analytic premises; they do not formalize the complete multiplication algorithm.

## What is already public

The leading balanced assembly already has semantic `C1=1` and permits `epsilon` approaching one. With `q = a_bit*(1-2h)` it chooses `epsilon=(1-h)/(1+q)`. Its scoped limit is `a_bit/(1+a_bit)`. The complex stopped-leaf condition `(1-beta)*a_complex > a_bit` survives, with `beta=1/20` and `a_complex=717/10^7`, but is not binding for this witness. The product row degree 2000 is explicitly charged. An isolated removal of the old `epsilon<1/2` ceiling is therefore not a new leading result.

The intake was superseded during the campaign by PR 38 and then PR 39. [The live findings](live-findings.md) records the exact heads, changed profiles and later validation receipts; PR 39 claims `kappa=3.886675852e-5` and was ready for review by the 13:11 observation.

The surviving physical rows include prefix movement, phase localization and phase boundaries, with savings `1-epsilon`, `1-epsilon-delta`, and `min(1-epsilon-delta,r-delta)`. A stronger full algorithm must change the limiting rows or improve the bit child-width moment.

## Records and recovery

- [Input manifest](input-manifest.json): public pinned commits, source snapshot paths, archive sizes/hashes, licenses and acquisition commands. Source snapshots are ignored execution inputs, not contents of the Git clone.
- [Intake](intake.json): PR metadata and public claim text as observed.
- [Fork heads](fork-heads.json): directly queried public fork branches at intake.
- [Analytic leads](analytic-leads.md): tensor packing, a proved regular Laurent estimate and explicit missing machine interfaces.
- [Deferred-reservoir criticism](deferred-reservoir-review.md): source-grounded review of the new equal-axis transform schedule.
- [Continuation reviews](all-cardinality-continuation-review.md): independent complete-profile enumeration and universal concavity exclusion for the coordinator's exported generic graph.
- `observations/`: timestamped compact observations and differences.
- [refresh_public_sources.py](refresh_public_sources.py): one read-only `gh api` observation, with optional broader searches; it never fetches RaD branches or performs Git mutations.

Snapshots reside in `../../work/scout/snapshots/`. Reacquire any snapshot with `gh api repos/<repository>/tarball/<sha>`, then extract it outside the durable tree. Apache-2.0 applies to the two source repositories; imported RaD source notices identify CC0 material. Any copied source must retain its own notices and license.

To refresh the public watch from the repository root:

```bash
python3 research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/scout/refresh_public_sources.py --forks --search
```

No remote human acceptance or full formal verification is inferred from passing numerical, finite or Lean arithmetic checks.
