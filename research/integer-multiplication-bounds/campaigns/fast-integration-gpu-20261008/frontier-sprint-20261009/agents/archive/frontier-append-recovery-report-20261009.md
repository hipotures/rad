# Supplemental completed public observation recovery

The frontier owner confirmed that all five supplemental receipt inventories (092900Z, 094100Z, 095200Z, 100200Z and 101200Z) are frozen, complete and safe to archive. The earlier recovery inventory was also checked for omissions. Every listed current original was checked against its inventory size and SHA256 before selection. Raw intake/check/source/review/file receipts preserve observations rather than scientific authority.

Selection deduplicated whole original SHA256 identities against existing frontier archive manifests and within this append. [The selection receipt](frontier-append-selection-20261009.json) maps 161 already retained or duplicate paths to their archived identities; original role/path associations remain in the source inventories. [The frozen explicit paths list](frontier-append-frozen-paths-20261009.json) selects 35 new whole originals, 27,996,542 bytes. No file was split and no original or previous namespace was changed. Downloaded archives, extracted sources, private configuration, environments and symlinks were excluded.

The new namespace is `agents/frontier/evidence/completed-public-observations-20261009T101330Z`. Payload gzip bytes total 3,364,441; its manifest adds 4,024 bytes. [The verification receipt](frontier-append-verification-20261009.json) records the namespace's manifest hash and maximum individual size. `verify-text --check-originals` passed complete membership, both SHA256/size identities, gzip framing/CRC, UTF-8 and recognizable-credential checks. This validation did not rerun scientific experiments or re-read mutable GitHub metadata.

From the repository root:

```bash
S=research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008/frontier-sprint-20261009
python3 tools/archive_workspace.py verify-text --destination "$S/agents/frontier/evidence/completed-public-observations-20261009T101330Z" --check-originals
```

In a clone omit `--check-originals`. Recover an individual complete file using `gzip -dc` into a fresh destination with shell noclobber enabled; compare its SHA256 to `original_sha256` in `archive-manifest.jsonl.gz`. Packing used the explicit frozen list with `pack-text --source "$S" --paths-from "$S/agents/archive/frontier-append-frozen-paths-20261009.json"` and the fresh namespace above. Existing source acquisition manifests/file inventories preserve source reconstruction; they do not reconstruct historical mutable public observations, whose bytes are now archived.
