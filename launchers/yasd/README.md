# Local YASD installation

YASD 1.1.0 is installed in an isolated venv at `/srv/ai/yasd/.venv`. The user command `/home/user/.local/bin/yasd` forwards arguments to this installation. No Strata engine or model is changed.

```bash
yasd --server http://127.0.0.1:8080 --requests all
```

For a remote Strata server:

```bash
yasd --server http://192.168.100.207:8080 --requests all
```

YASD reads `/health`, `/metrics`, and `/v1/status`. It does not include SQLite storage. Its optional `--debug NEW_FILE.jsonl` writes raw replies on UI frames, so repeated samples may occur. Use a fresh path because YASD opens debug files for writing. For a future independent SQLite collector, poll cached API data around 1 Hz and deduplicate completed request rows; do not launch PSS/GPU polling separately.

The Q4 128K launcher already saves cached Monitor metrics and completed request summaries in `variants/ud-q4-k-xl/manual/<timestamp>/telemetry/ui-monitor/`. YASD itself has not been left running. Run it after the model server is READY.
