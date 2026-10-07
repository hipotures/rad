# Q8 32K live profile — MEASURED IN PHASE 2

Profile window: 20 seconds during `EXP-001` 32K prompt processing.

- Process RSS: `132020332 KiB` (about `125.9 GiB`).
- Process CPU: about `106%`, approximately one exposed CPU core.
- Disk activity: no reads/writes and no major page faults in the observed window.
- CUDA0 SM utilization: commonly `90–96%` during active intervals.
- CUDA1: mostly idle between layer-split bursts.
- CUDA0 PCIe receive traffic: frequently about `12–13 GB/s`; transmit about `1.1–1.5 GB/s`.
- GPU topology: PHB/PCIe through the CPU; no NVLink.
- Host: Ryzen 9 7950X3D, one NUMA node, about 160 GB RAM.

Interpretation: the automatic layer-split placement is strongly affected by sequential GPU execution and host-to-GPU expert traffic. This motivates the already-planned manual MoE placement and expert-cache tests; it does not itself establish a winner.
