# Resource status

Initial live observation (2026-10-08 approximately 12:44 UTC): 16 online usable CPU slots; RAM 173014831104 bytes total and 168750166016 bytes available; disk 560257011712 bytes available. Both RTX4090 devices idle, each 24564MiB total VRAM and 1MiB in use. Unrelated host processes consume under 3% of one CPU in the initial process snapshot; preserve them.

Initialization is source/proof-bound. Allocations: graph8 CPU slots, geometry6, coordinator2; all native BLAS/OpenMP worker threads restricted to1. A read-only monitor records process identities, deltas, memory/disk and both GPUs once each minute in external raw evidence. Coordinator reviews it at most three minutes apart and after batch changes. CPU worker count is not inference from the physical CPU model.
