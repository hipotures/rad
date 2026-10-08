#!/usr/bin/env python3
"""Freeze one telemetry continuation after its own natural deadline.

This watcher reads the terminal marker; it neither samples hardware nor
signals a process.  Original protocol and telemetry bytes remain unchanged.
"""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import time


def row(path):
    return dict(path=str(path),bytes=path.stat().st_size,
        sha256=sha256(path.read_bytes()).hexdigest())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--protocol',type=Path,required=True)
    p.add_argument('--inventory',type=Path,required=True)
    a=p.parse_args();assert not a.inventory.exists()
    config=json.loads(a.protocol.read_text());deadline=datetime.fromisoformat(config['sampling_deadline'].replace('Z','+00:00'))
    marker=Path(config['logs'])/'execution.log'
    while datetime.now(timezone.utc)<deadline:
        time.sleep(min(30,(deadline-datetime.now(timezone.utc)).total_seconds()))
    limit=time.monotonic()+20
    while True:
        text=marker.read_text()
        if '"status": "terminal"' in text:break
        assert time.monotonic()<limit,'No natural terminal marker; original data left active and untouched'
        time.sleep(0.2)
    data=Path(config['output']);rows=[json.loads(line) for line in data.read_text().splitlines()]
    assert rows and all(datetime.fromisoformat(x['utc'])<deadline for x in rows)
    results=a.protocol.parent/'results';results.mkdir(exist_ok=True)
    summary=dict(status='Terminal natural telemetry continuation',completed_utc=datetime.now(timezone.utc).isoformat(),
        first_sample_utc=rows[0]['utc'],last_sample_utc=rows[-1]['utc'],sample_count=len(rows),
        source_sha256=config['source_sha256'],sampling_deadline=config['sampling_deadline'],
        active_campaign_deadline=config['active_authorized_deadline'],interval_seconds=config['interval_seconds'],
        peak_sampled_campaign_rss_sum_bytes=max(x['sampled_campaign_rss_sum_bytes'] for x in rows),
        observed_process_cpu_delta_seconds=sum(x['observed_process_cpu_delta_seconds'] for x in rows),
        raw=row(data),natural_terminal_marker=row(marker),
        original_protocol_sha256=sha256(a.protocol.read_bytes()).hexdigest(),
        no_process_termination_or_campaign_restart=True,
        scope='Read-only snapshots; system metrics include unrelated work and short process CPU may be missed')
    result=results/'closure.json';assert not result.exists();result.write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    report=a.protocol.parent/'report.md';assert not report.exists()
    report.write_text('# Natural telemetry continuation closure\n\n'
        'The unchanged read-only sampler reached its own 09:59 UTC deadline and emitted its terminal marker. '
        'No process was signalled, no worker was interrupted and the campaign was not restarted. '
        'The original active protocol remains preserved as the launch record; closure.json records its natural terminal state.\n\n'
        f"The continuation has {len(rows)} complete samples, from {rows[0]['utc']} through {rows[-1]['utc']}. "
        f"Its raw JSONL is {data.stat().st_size} bytes with SHA {summary['raw']['sha256']}. "
        'The full raw text and terminal execution log are listed in the final frozen inventory for complete gzip publication. '
        'System metrics include unrelated work; snapshot CPU misses processes finishing between samples and must be read with per-run measurements.\n')
    topic=[a.protocol,result,report,Path(__file__)]
    inventory=dict(status='Frozen complete natural telemetry continuation',topic_files=[row(x) for x in topic],
        external_files=[row(data),row(marker)],original_live_bytes_unchanged=True)
    a.inventory.parent.mkdir(parents=True,exist_ok=True);a.inventory.write_text(json.dumps(inventory,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(status=summary['status'],inventory=str(a.inventory),inventory_sha256=sha256(a.inventory.read_bytes()).hexdigest(),sample_count=len(rows),raw=summary['raw'])),flush=True)


if __name__=='__main__':main()
