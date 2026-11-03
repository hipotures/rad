"""Minimal weight-space editing laboratory (Gold registry, patches, sandbox, budgeted evaluation).

No gradient-based code lives here: candidates are produced only by explicit numerical edits.
"""
import os
from pathlib import Path

TOPIC_ROOT = Path(__file__).resolve().parents[2]


def work_root() -> Path:
    """Execution root for large/transient payloads: the topic's ignored work/ directory (override: WSE_WORK_ROOT).

    Never defaults to /tmp (RAM-backed on the reference host)."""
    p = Path(os.environ.get("WSE_WORK_ROOT") or (TOPIC_ROOT / "work"))
    p.mkdir(parents=True, exist_ok=True)
    return p
