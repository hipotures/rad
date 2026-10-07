# Qwen3.8-Flash-Next fresh runtime campaign

This directory is self-contained. `harness.py` starts and stops one isolated llama.cpp server per experiment group, emits exact commands/configuration, exact token-array prompts, raw streamed responses, raw server logs, telemetry, and normalized JSON records.

Formal lanes are only 32768, 65536, and 131072 tokens per slot. Sanity/startup checks are labeled separately and excluded from final performance tables.
