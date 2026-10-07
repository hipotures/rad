---
license: apache-2.0
base_model: Qwen/Qwen3.8-Flash-Next
tags:
- llama.cpp
- speculative-decoding
- mtp
- gguf
- qwen
---

# Qwen 3.8 Flash Next - MTP Draft Speculative Model (GGUF)

This repository provides working MTP (Multi-Token Prediction) draft models in GGUF format for **Qwen 3.8 Flash Next** (and experimental architectures with hyper-connections / QSA / Hadamard KV rotations), powered by [cafe-llama.cpp](https://github.com/quimmedes/cafe-llama.cpp).

## Compatible Engine

This MTP model requires the fork implementation supporting hyper-connection hidden states, QSA Hadamard KV rotation, and MTP layer graph generation:
- **Repository**: [https://github.com/quimmedes/cafe-llama.cpp](https://github.com/quimmedes/cafe-llama.cpp)

- ```
  git clone --single-branch --branch main https://github.com/quimmedes/cafe-llama.cpp
  
- ```

## Available Files

- `mtp-Qwen3.8-Flash-Next-Q4_K_M.gguf`: Quantized Q4_K_M MTP draft model (~2.65 GB) - *Recommended*
- `mtp-Qwen3.8-Flash-Next-Q6_K.gguf`: Quantized Q6_K MTP draft model (~3.24 GB)
- `mtp-Qwen3.8-Flash-Next-Q8_0.gguf`: Quantized Q8_0 MTP draft model (~3.94 GB)
- `mtp-Qwen3.8-Flash-Next-BF16.gguf`: Full precision BF16 MTP draft model (~7.40 GB)

## Usage with llama.cpp / llama-server

Run `llama-server` or `llama-cli` with `--spec-type draft-mtp` and point `-md` to your preferred MTP file.
Setting `--spec-draft-n-max 2` provides optimal acceptance rate (~50-70%) for a 1-layer MTP draft head:

```bash
llama-server   -m Qwen3.8-Flash-Next-UD-IQ3_XXS-00001-of-00003.gguf   -md mtp-Qwen3.8-Flash-Next-Q4_K_M.gguf   --spec-type draft-mtp   --spec-draft-n-max 2   -ngl 999   -hmoe   -fa on   -ctk q8_0 -ctv q8_0 -kvu   -c 8192 -b 1024 -ub 128
```

### CLI Example:

```bash
llama-cli   -m Qwen3.8-Flash-Next-UD-IQ3_XXS-00001-of-00003.gguf   -md mtp-Qwen3.8-Flash-Next-Q4_K_M.gguf   --spec-type draft-mtp   --spec-draft-n-max 2   -ngl 999   -hmoe   -fa on   -ctk q8_0 -ctv q8_0   -p "Explain quantum entanglement simply."
```
