# Configuration provenance

`campaign-manifest.json` is an archived manifest of the ORIGINAL IQ3/Q4 resident-mode comparison, including its historical unsupported Q4+resident+split outcome. It does not describe this broader sweep. `q4-manifest.json` contains the pinned four-shard model sizes/SHA256.

The current campaign objective is `../objective.txt`; each actual candidate has its own JSON, runtime JSON and startup/request evidence. Default native full-RAM arena is selected by omitting mmap/resident flags. Selected topology and tuning provenance is stored under `../raw/*-selection.json`.

`IQ3_S-best-runtime.json` preserves the existing verified IQ3 model/KV/MTP/GPU/split settings and changes only isolated port/log path. Q4 ready configs are emitted only after final measurements. Run one engine at a time; ready launchers do not start automatically.
