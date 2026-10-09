# Completed PR168 complement evidence recovery

The complement lane confirmed that all five directories selected in [the frozen list](complements-frozen-paths-20261009.json) were complete and immutable. This archive preserves 70 whole JSON files (35,118,154 original bytes), including both coherent context exports, controls and failed orientation variants, frame/move lists, orientation choices and the full fused component candidate. The negative result is that these orientation batches added no improvement beyond component descent; see the lane's [scientific report](../complements/pr168-fused-orientation-report.md). No scientific acceptance is implied by this recovery audit.

The new namespace is `agents/complements/evidence/completed-pr168-complements-20261009T104300Z`. Its gzip payload is 3,578,480 bytes and its manifest is 5,130 bytes. Every complete gzip is smaller than 10 MiB. [The verification receipt](complements-archive-verification-20261009.json) records manifest SHA256, exact scope and maximum size. `verify-text --check-originals` passed: complete namespace membership, gzip framing/CRC, UTF-8, recognizable credentials, compressed/original sizes and SHA256 all checked. Originals were unchanged; no experiments were rerun or scientific/checker/source-plan hashes edited.

Both context `source/` trees were excluded. The owner confirmed these contain copied certificates/reference frames/pairs and an immutable source-script symlink, with no unique authored transformation. Their reconstruction uses retained context pins, full generated exports, existing input manifests and `prepare_context.py`. No downloaded repository, environment, bytecode, symlink, tarball or private configuration was copied into the archive.

From the repository root:

```bash
S=research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008/frontier-sprint-20261009
python3 tools/archive_workspace.py verify-text --destination "$S/agents/complements/evidence/completed-pr168-complements-20261009T104300Z" --check-originals
```

Omit `--check-originals` in a clone. To recover a whole file, use `gzip -dc` into a fresh location with shell noclobber enabled, then compare SHA256 with its manifest entry. Archive creation used `pack-text --source "$S/work/complements" --paths-from "$S/agents/archive/complements-frozen-paths-20261009.json"` and the new destination above; never rerun packing into an existing namespace.

This completed scoped E1 construction/negative-evidence milestone is separate from the placement/public-observation historical archive milestone. It is also separate from the current winner certification: the frozen component candidate is retained as research evidence, not an independent final paid-composition claim.
