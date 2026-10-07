#!/usr/bin/env python3
"""Pinned manual import per upstream docs/UNSLOTH_Q4.md; no engine changes."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

BASE = Path(__file__).resolve().parent
REPO = Path('/srv/ai/strata')
OUT = Path('/srv/ai/models/strata/models/UD-Q4_K_XL')
REV = '38bb39ee97821de2c9009abb7e93950eec396e66'
OUT.mkdir(parents=True, exist_ok=True)
verified = []
for entry in json.loads((BASE / 'q4-manifest.json').read_text()):
    path = OUT / entry['file']
    url = f'https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/resolve/{REV}/UD-Q4_K_XL/{path.name}'
    print(f'Download {path.name}', flush=True)
    if not path.exists() or path.stat().st_size != entry['bytes']:
        subprocess.run(['curl', '--fail', '--location', '--retry', '5', '--continue-at', '-', '--output', str(path), url], check=True)
    h = hashlib.sha256()
    with path.open('rb') as stream:
        while block := stream.read(16 * 1024 * 1024):
            h.update(block)
    actual = h.hexdigest()
    result = dict(entry, actual_sha256=actual, actual_bytes=path.stat().st_size, url=url)
    verified.append(result)
    (BASE / 'results/raw/q4-sha256.json').write_text(json.dumps(verified, indent=2))
    if actual != entry['sha256'] or path.stat().st_size != entry['bytes']:
        sys.exit(f'SHA256/SIZE FAILED: {path.name}')
    print(f'SHA256 OK {path.name}', flush=True)
env = dict(os.environ, STRATA_GGUF_PY=str(REPO / 'third_party/llama.cpp/gguf-py'))
subprocess.run([str(REPO / '.venv/bin/python'), str(REPO / 'tools/iq_pack.py'), '--gguf', str(OUT / verified[0]['file']), '--out', '/srv/ai/models/strata/packs/ud-q4_k_xl', '--compat-bf16'], cwd=REPO, env=env, check=True)
assert not Path('/srv/ai/models/strata/packs/ud-q4_k_xl/experts.bin').exists()
print('Q4 pack prepared; multi-GPU resident runtime is unsupported at pinned HEAD.', flush=True)
