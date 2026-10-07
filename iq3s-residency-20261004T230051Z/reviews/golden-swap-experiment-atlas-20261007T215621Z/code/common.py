"""Small, portable helpers for a read-only retrospective derivation."""
import datetime
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess

REVIEW = Path(__file__).resolve().parents[1]
REPO = REVIEW.parents[2]
STUDY = REVIEW.parents[1]
CAMPAIGNS = STUDY / "campaigns"
DEFAULT_WORK = REPO.parent / 'work/rad/golden-swap-experiment-atlas' / REVIEW.name.rsplit('atlas-',1)[-1]

def work_root():
    return Path(os.environ.get("RAD_WORK_ROOT", DEFAULT_WORK))

def load(path):
    path=Path(path)
    if path.suffix=='.gz':
        with gzip.open(path,'rt',encoding='utf-8') as f:return json.load(f)
    return json.loads(path.read_text())

def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n")
    tmp.replace(path)

def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

_references = {}
def reference(path):
    path = Path(path).absolute()
    stat=path.stat();key=(str(path),stat.st_size,stat.st_mtime_ns)
    if key not in _references:
        _references[key]={"path": str(path), "repo_path": str(path.relative_to(REPO)) if path.is_relative_to(REPO) else None,
                          "bytes": stat.st_size, "sha256": digest(path)}
    return _references[key]

def campaign(prefix):
    return next(p for p in sorted(CAMPAIGNS.glob(prefix + "-*")) if "reproduction" not in p.name and (p/'report.md').exists())

def status(stage, message, **kwargs):
    value = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "stage": stage,
             "message": message, "gpu_inference_runs": 0, **kwargs}
    save(REVIEW / "progress.json", value)
    with (REVIEW / "progress.jsonl").open("a") as f:
        f.write(json.dumps(value) + "\n")
    (REVIEW / "STATUS.md").write_text("# Atlas status\n\n" + message + "\n\n" + value["utc"] + "\n")
    print("[ATLAS]", stage, message, flush=True)

def id_for(campaign_name, label):
    import re
    return re.sub(r"[^a-zA-Z0-9_-]", "-", campaign_name.split("-2026")[0] + "--" + label)
