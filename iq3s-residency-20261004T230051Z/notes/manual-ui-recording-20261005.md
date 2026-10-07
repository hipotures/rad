# Durable Monitor recording for real prompts

Requested after the bounded P0/P1/P2 campaign was completed. The historical reports, data and provenance snapshots remain preserved. This changes only the local launcher/logging layer; the frozen source, executable, weights and inference settings are unchanged.

The UI at `http://192.168.100.207:8080/#monitor` uses `/metrics`. Upstream keeps 60 hardware samples and up to 500 completed request records in memory, with no durable metrics archive. The separate API-monitor retains at most 100 records in memory when enabled; it is not used by this recorder.

`scripts/record_ui_metrics.py` writes cached UI snapshots once per second to `metrics.jsonl` and flattened `metrics.csv`. `requests.jsonl` preserves each completed request's statistics once. `initial-snapshot.json` preserves the history still present on attachment. It does not reconstruct earlier live samples or perform inference, PSS/GPU polling, model changes or an engine patch. Raw API fields and unavailable/null values remain preserved; disk rates are system-wide and PCIe rates are the UI aggregate.

Both manual start scripts now attach the recorder automatically after READY and print `UI_MONITOR_LOGS`. Benchmark sessions remain unchanged. `record-ui.sh` can attach to an older running server without restarting it; Ctrl-C ends only recording. The recorder checks the server PID and creation identity and exits when that server exits. A session lock prevents duplicate recording.

The already running session `manual/20261005T133002Z` received a separate recorder at `telemetry/ui-monitor-20261005T134346.178408Z`. A three-sample read-only smoke saved valid JSONL/CSV with zero API errors, both GPU fields and the completed request recovered from the UI. The continuous recorder also saved snapshots without errors. The user server and its requests were not stopped.

Files remain under the manual session directory. Historical campaign end-state checks describe the completed research before the user's later manual server launch; this recorder belongs to that user session.
