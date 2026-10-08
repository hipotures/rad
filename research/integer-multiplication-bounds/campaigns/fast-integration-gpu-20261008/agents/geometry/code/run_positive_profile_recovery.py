#!/usr/bin/env python3
"""Sequential one-slot source-recovered actual-frame profile validations."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import argparse
import json
import subprocess
import sys
import time

from refresh_geometry_status import refresh

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=Path, required=True)
parser.add_argument('--work', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--live-output', type=Path)
args = parser.parse_args()
assert not args.work.exists() and not args.output.exists()
args.work.mkdir(parents=True)
configs = json.loads(args.input.read_text())
rows = []
started = time.monotonic()
for config in configs:
    source_receipt = Path(config['source_receipt'])
    source = json.loads(source_receipt.read_text())
    assert 'PASS' in source['status']
    weighted = source.get('weighted_selected')
    if weighted is not None and Path(weighted['fixture']).resolve() == Path(config['expected']).resolve():
        assert weighted['fixture_sha256'] == sha256(Path(config['expected']).read_bytes()).hexdigest()
        producer = weighted['producer']
    else:
        producer = source['producer']
    case = args.work/config['case_id']
    case.mkdir()
    receipt = case/'receipt.json'
    command = [sys.executable, '-u', str(Path(__file__).with_name('reproduce_positive_profile.py')),
               '--dag', producer['dag_path'], '--selected', producer['witness_path'],
               '--expected', config['expected'], '--source-receipt', str(source_receipt),
               '--work', str(case/'rebuild'), '--output', str(receipt)]
    with (case/'run.log').open('wb') as log:
        child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        (case/'process.json').write_text(json.dumps(dict(pid=child.pid, command=command,
            started_utc=datetime.now(timezone.utc).isoformat()), indent=2)+'\n')
        print(json.dumps(dict(status='SOURCE PROFILE RECOVERY RUNNING', pid=child.pid, case=config['case_id'])), flush=True)
        assert child.wait() == 0, config
    row = json.loads(receipt.read_text())
    rows.append(dict(case_id=config['case_id'], h=row['h'], basis=row['basis'], status=row['status'],
        receipt=str(receipt), receipt_sha256=sha256(receipt.read_bytes()).hexdigest()))
    status = dict(utc=datetime.now(timezone.utc).isoformat(), completed=len(rows), total=len(configs),
        workers=1, elapsed_seconds=time.monotonic()-started)
    (args.work/'status.json').write_text(json.dumps(status, indent=2)+'\n')
    print(json.dumps(status), flush=True)
    if args.live_output:
        refresh(args.work, args.live_output, 'Fresh chosen actual-frame source recovery; new public54 enlarged matrices and transpose matching')
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(dict(status='PASS SOURCE-ONLY ACTUAL PROFILE RECOVERY', rows=rows,
    utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.monotonic()-started,
    input_sha256=sha256(args.input.read_bytes()).hexdigest(),
    source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()), indent=2)+'\n')
