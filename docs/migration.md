# Legacy workspace import

On 2026-10-07 the existing research workspace was connected to
`hipotures/rad`, preserving remote main history and its AGENTS.md/LICENSE.
The repository root became `/srv/ai/research`. The study directory and every
payload remained at its original absolute path; existing campaign evidence was
not rewritten or regenerated.

The former repository had four local branches and no remote. Its HEAD was
`175537747c8fbdb734176a7e03bf72b41f9e1b49`; Phase 0/Phase 1 and several later
campaigns were not yet committed there. A complete, verified `git bundle --all`
and the exact old .git directory, including index and local metadata, are
archived outside the new working tree:

```text
/srv/ai/repository-backups/rad-import-20261007T081726Z/
  legacy-history.bundle
  legacy.git/
  legacy-repository.json
  status-before.txt
  staged-before.patch
  unstaged-before.patch
```

[legacy-repository.json](legacy-repository.json) records the original refs,
bundle SHA256, remote starting commit and shared-object-store check. The old
uncommitted working files stayed in place. The original process-state change
is retained locally but excluded from the public snapshot.

No historical branches were force-pushed or merged into unrelated remote
history. The remote receives a curated snapshot of the working evidence,
including previously uncommitted campaign results. Large old summary dumps
and source/build trees remain local. The legacy archive is not itself stored
on GitHub; it preserves the history the user proposed replacing.

To inspect the old Git metadata without changing the new repository:

```bash
git --git-dir=/srv/ai/repository-backups/rad-import-20261007T081726Z/legacy.git log --all --oneline
git bundle list-heads /srv/ai/repository-backups/rad-import-20261007T081726Z/legacy-history.bundle
```

To recover the former history into a separate inspection checkout:

```bash
git clone /srv/ai/repository-backups/rad-import-20261007T081726Z/legacy-history.bundle /srv/ai/legacy-research-inspection
```

Runtime/source repositories nested in ignored storage remain independent Git
checkouts. The Phase 1 source commit is still
`20e1e10f6848f11ec5580fc5ec7f97ea5d4e520b`. No runtime launcher, weight file,
driver/host setting or scientific result was changed for this import.
