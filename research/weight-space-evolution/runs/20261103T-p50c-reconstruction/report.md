# p50c reconstruction — report

**Outcome: pass.** All three published Qwen3.5-0.8B edits rebuild bit-exactly from `Qwen/Qwen3.5-0.8B@2fc06364…`.

| Run | Tensors | Changed bf16 entries | Base hashes | Edited hashes | Upstream `apply_edit.py` |
|---|---|---|---|---|---|
| p50c | 2 (`layers.{15,19}.mlp.down_proj.weight`) | 130,188 (64 columns each) | ok | ok | ok |
| p25c | 1 (`layers.15.self_attn.o_proj.weight`) | 262,144 | ok | ok | ok |
| p10c | 30 (low-rank form, rank-1 + fixups) | 72,986,982 | ok | ok | ok |

- Independent implementation (`wse.p50c`) and upstream script agree; Gold file sha256 equals the HF LFS hash.
- p50c delta is rank-1 per tensor (top singular value carries ≥ 99.999% of the delta energy) over exactly 64
  columns per tensor — consistent with "subtract the loop direction from 64 output columns".
- Imported as WSE patch `p-4b2661ed6f35` (lineage: Gold → patch); round trip hash-exact; Gold stays read-only.
- Text-only exports (as upstream evaluated): Gold `68194c7b…`, p50c `b42d7679…` (model.safetensors sha256).

Limitation: hash validity says nothing about benchmark scores; see `../20261103T-p50c-math500-bounded/`.
