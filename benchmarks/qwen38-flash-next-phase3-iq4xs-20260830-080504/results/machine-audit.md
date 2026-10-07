# Phase 3 machine audit

Recorded for the Phase 3 campaign and rechecked after the unplanned reboot on 2026-08-30 UTC.

- GPU 0: NVIDIA GeForce RTX 4090, 24,564 MiB, PCIe maximum Gen4 x16.
- GPU 1: NVIDIA GeForce RTX 4090, 24,564 MiB, PCIe maximum Gen4 x16.
- Driver: 595.84; NVIDIA runtime reports CUDA 13.2.
- CUDA toolkit: 13.3 (`nvcc` 13.3.73).
- Topology: PHB between GPUs; no NVLink.
- Idle link state at audit: Gen1 x8 on both GPUs; maximum Gen4 x16.
- CPU: AMD Ryzen 9 7950X3D 16-Core Processor.
- Exposed CPUs: 16; one thread per core; AVX2 and AVX-512 feature flags exposed.
- NUMA nodes: 1.
- RAM: 156 GiB total, approximately 153 GiB available after reboot verification.
- Swap: none.
- `/srv/ai`: 1.9 TiB total, 1.1 TiB available after reboot verification.
- `/srv/ai` guest filesystem: `virtiofs`; physical backing device is not exposed to the VM.
- No `llama-server` or `llama-bench` process remained after the campaign.

Commands used included `nvidia-smi`, `nvidia-smi topo -m`, `lscpu`, `free -h`, `df -h /srv/ai`, `numactl --hardware`, and CUDA compiler/runtime version queries.
