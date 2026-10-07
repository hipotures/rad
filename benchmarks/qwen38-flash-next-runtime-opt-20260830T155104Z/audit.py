#!/usr/bin/env python3
"""Capture the campaign's machine and selected-source audit without mutation."""

import datetime
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent

COMMANDS = {
    "date_utc": ["date", "-u", "+%FT%TZ"],
    "uname": ["uname", "-a"],
    "os_release": ["bash", "-lc", "cat /etc/os-release"],
    "lscpu": ["lscpu"],
    "cpu_flags": ["bash", "-lc", "sed -n 's/^flags[[:space:]]*: //p' /proc/cpuinfo | head -1"],
    "memory": ["free", "-h"],
    "meminfo": ["bash", "-lc", "cat /proc/meminfo"],
    "numa_hardware": ["numactl", "--hardware"],
    "numastat": ["numastat"],
    "gpu_query": ["nvidia-smi", "--query-gpu=index,name,uuid,pci.bus_id,memory.total,memory.free,memory.used,driver_version,pstate,power.draw,utilization.gpu", "--format=csv"],
    "gpu_topology": ["nvidia-smi", "topo", "-m"],
    "gpu_processes": ["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv"],
    "nvidia_smi": ["nvidia-smi"],
    "nvcc": ["nvcc", "--version"],
    "cuda_packages": ["bash", "-lc", "dpkg -l | rg 'cuda-toolkit|libcudart|nvidia-driver'"],
    "mount_srv_ai": ["findmnt", "-T", "/srv/ai", "-o", "TARGET,SOURCE,FSTYPE,OPTIONS,SIZE,USED,AVAIL"],
    "block_devices": ["lsblk", "-o", "NAME,TYPE,SIZE,MODEL,FSTYPE,MOUNTPOINTS"],
    "disk_usage": ["df", "-hT", "/srv/ai"],
    "source_commit": ["git", "-C", "/srv/ai/llama.cpp-qwen4exp", "rev-parse", "HEAD"],
    "source_status": ["git", "-C", "/srv/ai/llama.cpp-qwen4exp", "status", "--short", "--branch"],
    "server_version": ["/srv/ai/llama.cpp-qwen4exp/build-cuda-sm89/bin/llama-server", "--version"],
    "server_devices": ["/srv/ai/llama.cpp-qwen4exp/build-cuda-sm89/bin/llama-server", "--list-devices"],
    "cmake_cache": ["bash", "-lc", "rg '^(CMAKE_BUILD_TYPE|CMAKE_CUDA_ARCHITECTURES|GGML_CUDA|GGML_CUDA_GRAPHS|GGML_NATIVE|GGML_OPENMP|GGML_BLAS|CMAKE_CXX_COMPILER):' /srv/ai/llama.cpp-qwen4exp/build-cuda-sm89/CMakeCache.txt"],
    "server_help": ["/srv/ai/llama.cpp-qwen4exp/build-cuda-sm89/bin/llama-server", "--help"],
    "qwen_support": ["bash", "-lc", "rg -n 'QWEN4EXP|qwen4exp|Qwen3.8-Flash-Next' /srv/ai/llama.cpp-qwen4exp/{src,include,convert_hf_to_gguf.py,examples,docs,tools} | head -300"],
    "cuda_graph_source": ["bash", "-lc", "sed -n '1248,1270p' /srv/ai/llama.cpp-qwen4exp/ggml/src/ggml-cuda/common.cuh; sed -n '2540,2590p' /srv/ai/llama.cpp-qwen4exp/ggml/src/ggml-cuda/ggml-cuda.cu"],
    "model_files": ["bash", "-lc", "find /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-IQ4XS/UD-IQ4_XS -maxdepth 1 -type f -printf '%f %s bytes\\n' | sort"],
}


def main():
    results = {"captured_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "commands": {}}
    text = []
    for name, command in COMMANDS.items():
        completed = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, timeout=120)
        entry = {"command": command, "exit_code": completed.returncode, "output": completed.stdout}
        results["commands"][name] = entry
        text.extend([f"===== {name} =====", "$ " + " ".join(command), completed.stdout.rstrip(), ""])
    (ROOT / "raw" / "audit.txt").write_text("\n".join(text))
    (ROOT / "raw" / "audit.json").write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
