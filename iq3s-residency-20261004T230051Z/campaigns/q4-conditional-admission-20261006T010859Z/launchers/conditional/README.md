# conditional

Experimental pre-copy conditional admission. Consult report for deployment recommendation/output trajectory limitations.

K24/PCIe.28/pool100us/15workers/spec4/.5/INT8/kv32768/prefillauto/suffix0/reuse0. One foreground server. Defaultlocalhost:8080. Full binary/source/model/config checks and GPU/port conflict refusal; no build/download/update. Logs and UI snapshots retained. Ctrl-C stops owned server.

```bash
./start-32k.sh --host 0.0.0.0 --port 8080
./start-128k.sh --host 0.0.0.0 --port 8080
./start-256k.sh --host 0.0.0.0 --port 8080
./stop.sh
./reproduce.sh --profile 128k --port 18144
```

Run one launcher at a time. `--check` no inference; `--smoke` launches64-output request and stops. Reproducer onlyafter campaigncomplete;3fresh servers, identicalwarmup,one requesteach,no retries. Normal user launchers untouched.
