# UD-Q4_K_XL manual server, 128K

This launcher uses the preserved, unchanged Strata v0.1.32 default binary and Q4 production settings from `/srv/ai/benchmarks/strata-qwen38/q4-v0132/configs/production-Q4.json`. It is separate from the IQ3_S P1 baseline and does not apply the IQ3_S-only pool experiment. The context limit is changed from 262144 to 131072. Startup/session paths, bind address, and port are separate from prior benchmark files.

Model: Unsloth Qwen3.8-Flash-Next UD-Q4_K_XL, revision `38bb39ee97821de2c9009abb7e93950eec396e66`. Existing four native GGUF shards and the existing BF16-compatible dense pack are reused. No download, weight conversion, engine patch, or experts.bin creation occurs.

Settings: GPU0+GPU1, layer split K=24, full resident RAM arena, auto expert cache, K8V4 KV, prefill 16384, workers 12, PCIe fraction 0.28, MTP spec 3/min-p 0.3. Preserved Q4 production defaults for prompt reuse and suffix lookup are retained; this is an interactive launcher, not a new controlled benchmark.

```bash
cd /srv/ai/research/iq3s-residency-20261004T230051Z/variants/ud-q4-k-xl
./start-128k.sh --host 0.0.0.0 --port 8080
```

Ctrl-C stops the server and owned engine. From a second terminal, `./stop.sh` stops only this launcher's recorded process identity. Stop any other GPU model first. `./logs.sh` follows the current session's saved logs. Manual starts show both logs in the foreground and record cached UI metrics at 1 Hz under `manual/<timestamp>/telemetry/ui-monitor/`.

```bash
OPENCODE_CONFIG=/home/user/.config/opencode/strata-ud-q4-128k.json \
opencode -m strata/qwen3.8-flash-next-ud-q4_k_xl
```

Run OpenCode in the project directory. The configuration uses localhost:8080; on another client computer, copy it and change `baseURL` to `http://192.168.100.207:8080/v1`. The configured model context is 131072 and output budget 8192. Model choice is verified from `/v1/models` during launcher validation, not inferred from the filename.
