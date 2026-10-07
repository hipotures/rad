"""Read-only revalidation of the completed matrix; write a new review each run."""
import datetime
import hashlib
import json
import re
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
summary = json.loads((ROOT / "summary.json").read_text())
checks, cells, seen, warmups = {}, [], set(), []
pattern = (
    r"strata serve: prompt (\d+) tokens = (\d+) reused \+ (\d+) read in "
    r"(\d+) ms \(([\d.]+) tok/s\), (\d+) generated in (\d+) ms "
    r"\(([\d.]+) tok/s\)"
)
footer_rounding_differences = []
for cell in summary["cells"]:
    rows = [json.loads(Path(p).read_text()) for p in cell["raw_paths"]]
    label = cell["config"] + "-" + cell["context"]
    checks[label + "-three-valid"] = len(rows) == 3 and all(
        row["valid"] and row["generated_tokens"] == 4096
        and row["requested_generated_tokens"] == 4096
        and row["cache_reused_tokens"] == 0 and row["finish_reason"] == "length"
        for row in rows
    )
    for path, row in zip(cell["raw_paths"], rows):
        assert path not in seen
        seen.add(path)
        file = Path(path)
        request = json.loads(file.with_name(file.stem + "-request.json").read_text())
        canonical = json.dumps(request, sort_keys=True, separators=(",", ":"))
        assert hashlib.sha256(canonical.encode()).hexdigest() == row["payload_sha256"]
        ids = Path(row["input_token_provenance"]["token_ids_path"])
        assert hashlib.sha256(ids.read_bytes()).hexdigest() == row["input_token_provenance"]["input_ids_sha256"]
        assert len(json.loads(ids.read_text())) == row["actual_prompt_tokens"]
        matches = re.findall(pattern, file.with_name(file.stem + "-engine.log").read_text())
        assert len(matches) == 1
        prompt, reused, read, pp_ms, pp, output, tg_ms, tg = matches[0]
        assert int(prompt) == row["actual_prompt_tokens"] and int(reused) == 0 and int(output) == 4096
        # API uses fractional milliseconds; the footer prints integer milliseconds.
        # Require exact agreement with the raw API timing source and allow 0.1 tok/s
        # rounding differences against the separately formatted footer.
        assert row["pp_tps"] == row["timings"]["prompt_per_second"]
        assert row["tg_tps"] == row["timings"]["predicted_per_second"]
        assert abs(float(pp) - row["pp_tps"]) < 0.15
        assert abs(float(tg) - row["tg_tps"]) < 0.15
        if float(pp) != row["pp_tps"] or float(tg) != row["tg_tps"]:
            footer_rounding_differences.append({"raw": path, "API_PP": row["pp_tps"], "footer_PP": float(pp), "API_TG": row["tg_tps"], "footer_TG": float(tg)})
        args = row["full_config"]["args"]
        common = {"--spec": "4", "--spec-min-p": "0.5", "--kv": "int8", "--kv-resident": "32768", "--max-context": "262144", "--pool-workers": "15", "--suffix-draft": "0", "--prompt-cache": "0", "--prefill": "auto"}
        assert all(args[args.index(k) + 1] == v for k, v in common.items())
        if cell["config"] != "HELPER":
            assert row["full_config"]["layer_split"] == "25"
        if cell["config"] == "CURRENT":
            assert args[args.index("--pcie-frac") + 1] == "0.28"
        assert request["temperature"] == 0
    for key in ["pp_tps", "tg_tps", "ttft_s"]:
        assert abs(statistics.median(row[key] for row in rows) - cell[key]) < 1e-9
    cells.append({key: cell[key] for key in ["config", "context", "actual_prompt_tokens", "pp_tps", "tg_tps", "tg_tps_min", "tg_tps_max", "ttft_s"]})
    warmup = json.loads((ROOT / "raw" / (label + "-warmup.json")).read_text())
    assert warmup["valid"] and warmup["cache_reused_tokens"] == 0
    warmups.append((warmup["actual_prompt_tokens"], warmup["generated_tokens"], warmup["payload_sha256"], warmup["input_token_provenance"]["input_ids_sha256"]))

checks["six-cells-18-unique-primary-raw"] = len(cells) == 6 and len(seen) == 18
checks["identical-warmup-input-output-hashes"] = len(set(warmups)) == 1 and warmups[0][:2] == (4096, 64)
checks["raw-footer-payload-ids-settings-medians"] = True
for name in ["CURRENT", "HELPER", "V0138"]:
    config = json.loads((ROOT / "configs" / (name + ".json")).read_text())
    checks[name + "-binary-hash"] = hashlib.sha256(Path(config["exe"]).read_bytes()).hexdigest() == config["binary_sha256"]
checks["model-stat-unchanged"] = all(
    Path(item["path"]).stat().st_size == item["size"]
    and Path(item["path"]).stat().st_mtime_ns == item["mtime_ns"]
    for item in json.loads((ROOT / "git/model-files-before.json").read_text())
)
apps = subprocess.check_output(["nvidia-smi", "--query-compute-apps=pid,process_name", "--format=csv,noheader"], text=True)
checks["no-gpu-compute-process"] = not apps.strip()
checks["required-artifacts-present"] = all((ROOT / p).is_file() for p in ["report.md", "summary.json", "summary.csv", "STATUS.md", "STATUS.json"])
assert all(checks.values()), checks
stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
result = {
    "status": "PASS", "timestamp_UTC": stamp, "checks": checks,
    "cells_recomputed_from_raw": cells, "measurements_added": 0,
    "existing_results_overwritten": False,
    "API_footer_rounding_differences": footer_rounding_differences,
    "review_repair": "First review assertion incorrectly required bit-exact API/footer rounding agreement. Preserved raw API rates and integer-millisecond footer differ by 0.1 PP tok/s in two rows. No measurement or runtime changed.",
    "limitations": ["128K CURRENT input IDs differ from older APIs", "Progression uses bracketed 1 Hz client timestamps", "No interval cache/MTP identity counters in headline binaries", "Optional16K fixed-length comparison incomplete after natural EOS"],
}
target = ROOT / "analysis" / ("independent-review-" + stamp + ".json")
with target.open("x") as handle:
    json.dump(result, handle, indent=2)
print(json.dumps({"status": "PASS", "review_path": str(target), "checks": checks, "raw_medians": cells}, indent=2))
