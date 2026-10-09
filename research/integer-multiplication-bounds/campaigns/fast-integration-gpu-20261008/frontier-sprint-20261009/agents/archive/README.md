# Completed evidence recovery audit

This lane preserves completed historical placement, scoped complement experiments and frozen public observations. It does not certify a scientific construction or alter a checker, source plan or original evidence. The coordinator alone stages, commits and pushes these artifacts.

## Verified namespaces

See [machine-readable verification](archive-verification-20261009.json) for exact namespace membership, aggregate sizes, manifest SHA256 identities and original-scope verification. Placement ownership confirmed that every recorded original was frozen; later additions to its work root are outside the snapshot. Frontier ownership checked every one of the 152 selected receipts against the frozen [recovery inventory](../frontier/evidence-recovery.json), and future observations use new paths. Intermediate/unassessed frontier receipts remain historical evidence rather than scientific authority.

The archived originals are whole UTF-8 JSON/JSONL/log/text files. Each complete gzip is strictly smaller than 10 MiB. No source was split or overwritten. Downloaded tarballs, extracted repositories, environments, bytecode, symlinks and private configuration are outside these archives. Frontier source archive recovery remains documented in the eight acquisition manifests identified by its recovery inventory.

## Verification and recovery

From the repository root, set the sprint location and verify each namespace listed in the verification receipt:

```bash
S=research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008/frontier-sprint-20261009
python3 tools/archive_workspace.py verify-text --destination "$S/agents/placement/evidence/completed-placement-20261009T074650Z" --check-originals
python3 tools/archive_workspace.py verify-text --destination "$S/agents/frontier/evidence/completed-public-observations-20261009T092300Z" --check-originals
```

A clone can use these commands without `--check-originals`; that checks archive identity, complete membership, gzip framing/CRC, UTF-8 and recognizable credential formats without requiring the original host paths. Host verification with `--check-originals` passed and additionally matched original sizes and SHA256 identities. This is archival validation, not an experiment rerun.

Recover an individual file into a fresh destination; do not overwrite an original:

```bash
set -o noclobber
gzip -dc -- "$S/agents/frontier/evidence/completed-public-observations-20261009T092300Z/work/frontier/20261009T073500Z/main-README-md.json.gz" > /tmp/rad-frontier-main-readme-recovered.json
sha256sum /tmp/rad-frontier-main-readme-recovered.json
```

Compare the result with `original_sha256` in that namespace's `archive-manifest.jsonl.gz`. Gzip readback recovers exact retained bytes even when the original host evidence is lost. These archives preserve historical observations which cannot be reproduced by polling GitHub again; source retrieval and experimental reconstruction still require their existing manifests and instructions.
