"""Initialize the persistent laboratory; never reset the absolute deadline."""
import datetime as dt
import hashlib
import json
import pathlib
import shutil
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent
START = 1791154851
DEADLINE = START + 10 * 3600
def iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat()
def write(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2) + "\n")

if (ROOT / "deadline.json").exists():
    raise SystemExit("Laboratory already initialized; deadline must not be reset")
for d in ("references", "sources", "scripts", "experiments", "variants", "workloads", "analysis", "builds", "src", "git", "logs"):
    (ROOT / d).mkdir()
goal = pathlib.Path("/home/user/.codex/attachments/a5813aec-1bce-41ee-a156-8b2f58e16d71/pasted-text-1.txt")
shutil.copy2(goal, ROOT / "GOAL.md")
write("deadline.json", {"start_epoch": START, "start_utc": iso(START), "deadline_epoch": DEADLINE, "deadline_utc": iso(DEADLINE), "consolidation_start_epoch": DEADLINE-2700, "source": "active goal creation time; includes initial read/setup", "goal_sha256": hashlib.sha256(goal.read_bytes()).hexdigest()})
write("STATUS.json", {"state": "RUNNING", "completed": [], "running": "E001 evidence/source audit", "pending": ["E002 fresh controls at true context limits", "E003 demand/critical-path diagnosis", "E004 byte-aware replay/reference schedules", "E005 Expert-Jev linear/MLP evaluation", "bounded runtime candidates and correctness", "two-profile confirmation", "final report and cleanup"], "next_exact_action": "Inspect preserved evidence, frozen source and runtime admission; build clean control from 6f32ec0", "deadline_utc": iso(DEADLINE), "excluded": [], "current_winners": {}})
(ROOT / "STATUS.md").write_text(f"# Research status\n\nRUNNING: evidence and frozen-source audit.\n\nStart: {iso(START)}. Hard deadline: {iso(DEADLINE)}. Consolidation begins 45 minutes before the deadline.\n\nNext: prepare frozen-base clean control and correctly budgeted 32K/128K workloads. Read GOAL.md and STATUS.json after every resumption.\n")
(ROOT / "README.md").write_text("# IQ3_S expert-residency laboratory\n\nPrimary reference: frozen Strata 6f32ec070f23ced9f50e704d854d775da52591ab, layer split K=25, PCIe fraction 0.28. Only 32768 and 131072 total-context profiles are in scope. Existing weights and campaigns remain read-only.\n\nRead GOAL.md, deadline.json and STATUS.json before continuing. Experiment protocols, attempts, negatives and runnable variants are retained separately. No automatic deployment, push or PR.\n")
(ROOT / "DECISIONS.md").write_text("# Decisions\n\n- D001: use exactly frozen CURRENT base; build clean control and candidates separately. Historical helper/v0.1.38 are explanatory references only.\n- D002: honor total context limits and budget 4096 output plus runtime headroom; freeze tokenizer-rendered workloads before speed runs.\n- D003: do not interpret 99% reported hit rate as local VRAM coverage. Audit disjoint dispatch categories first.\n- D004: reuse hardware characterization rather than repeat its campaign.\n")
write("sources.json", {"local_references": [], "external_sources": [], "downloads": []})
(ROOT / "experiments.jsonl").write_text(json.dumps({"id": "E001", "state": "RUNNING", "question": "What is the frozen reference provenance, fair context budget, counter semantics and existing evidence?", "started_utc": iso(START), "path": "experiments/E001-evidence"}) + "\n")
e = ROOT / "experiments/E001-evidence"
e.mkdir()
(e / "protocol.md").write_text("# E001: evidence and source audit\n\nInspect all four required campaigns, actual configs/raw/token IDs, frozen baseline and toolchain. Identify admission reserve, cache accounting and diagnostic hooks. No inference algorithm changes. Completion requires saved source/reference manifest and a plan grounded in dispatch/cost evidence.\n")
(ROOT / ".gitignore").write_text("src/\nbuilds/\n.venv/\n__pycache__/\n*.pyc\nexperiments/**/raw/\nexperiments/**/logs/\nexperiments/**/traces/\nexperiments/**/checkpoints/\nworkloads/token-ids/\nsources/vendor/\n")
subprocess.run(["git", "init", "-b", "research"], cwd=ROOT, check=True)
subprocess.run(["git", "add", "."], cwd=ROOT, check=True)
subprocess.run(["git", "-c", "user.name=Local Research", "-c", "user.email=research@localhost", "commit", "-m", "Record research objective, absolute deadline and initial protocol"], cwd=ROOT, check=True)
print(ROOT)
print(iso(DEADLINE))
