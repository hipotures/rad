# First evidence checkpoint

The archive `evidence/first-batch-20261009` preserves 26 complete text files as observed when it was packed. Streaming decompression, hashes, UTF-8 and credential/CRC checks pass. The supplied PDF extraction, completed historical E1 profiles, initial public receipts and exact scalar/moment baseline evidence are retained.

The complement lane subsequently added checks to `agents/complements/results/pr161-orientations-three-pass.json`, so checking that archive against the current original correctly reports a difference. The gzip bytes remain an immutable earlier observation, not the final updated receipt. Its manifest identifies the captured source SHA-256. A later evidence checkpoint will retain the completed current receipt. No candidate acceptance is inferred from this intermediate snapshot.

The original failed initial `gh api --slurp` intake produced an empty local file and was replaced by an explicitly named paginated v2 receipt; the empty file is not presented as evidence.
