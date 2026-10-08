#!/usr/bin/env python3
"""Read-only bounded campaign telemetry; no process-control authority.

System utilization includes unrelated work. Campaign process identification
uses task paths transiently, and records only PID/start identity and resource
counters, never command lines, environment variables or credentials. Snapshot
CPU deltas miss processes which finish between samples; per-run time logs are
the complementary measurements.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import time


def processes(markers):
    rows = []
    for proc in Path('/proc').iterdir():
        if not proc.name.isdecimal():
            continue
        try:
            cmd = (proc/'cmdline').read_bytes()
            if not any(marker.encode() in cmd for marker in markers):
                continue
            stat = (proc/'stat').read_text()
            fields = stat[stat.rfind(')')+2:].split()
            row = {'pid':int(proc.name), 'start_ticks':int(fields[19]),
                   'cpu_user_ticks':int(fields[11]), 'cpu_system_ticks':int(fields[12]),
                   'rss_bytes':int(fields[21])*os.sysconf('SC_PAGE_SIZE'),
                   'threads':int(fields[17])}
            rows.append(row)
        except (OSError,ValueError,IndexError):
            continue
    return rows


def snapshot(work_root, previous, clock_ticks):
    stamp = datetime.now(timezone.utc)
    memory = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key,value,*_ = line.split()
        if key[:-1] in {'MemTotal','MemAvailable','SwapTotal','SwapFree'}:
            memory[key[:-1]+'_bytes'] = int(value)*1024
    own = processes([str(work_root),'fast-integration-gpu-20261008'])
    delta = 0
    for row in own:
        identity = (row['pid'],row['start_ticks'])
        ticks = row['cpu_user_ticks']+row['cpu_system_ticks']
        if identity in previous:
            delta += max(0,ticks-previous[identity])
        previous[identity] = ticks
    disk = os.statvfs(work_root)
    command = ['nvidia-smi','--query-gpu=index,name,utilization.gpu,memory.used,memory.free,power.draw',
               '--format=csv,noheader,nounits']
    try:
        query = subprocess.run(command,check=False,capture_output=True,text=True,timeout=15)
        gpu = {'exit_code':query.returncode,'csv':query.stdout.strip()}
    except (OSError,subprocess.TimeoutExpired) as exc:
        gpu = {'unavailable':type(exc).__name__}
    return {'utc':stamp.isoformat(), 'load_average':os.getloadavg(), 'memory':memory,
            'disk_available_bytes':disk.f_bavail*disk.f_frsize,
            'campaign_processes':own,'sampled_campaign_rss_sum_bytes':sum(p['rss_bytes'] for p in own),
            'observed_process_cpu_delta_seconds':delta/clock_ticks,
            'work_root_bytes':sum(f.stat().st_size for f in work_root.rglob('*') if f.is_file()),
            'gpu_system_metrics':gpu,
            'scope':'Read-only snapshots; system load/GPU metrics include unrelated work; short processes may be missed'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work-root',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--deadline',required=True)
    parser.add_argument('--interval',type=float,default=60)
    args = parser.parse_args()
    deadline = datetime.fromisoformat(args.deadline.replace('Z','+00:00'))
    assert deadline.tzinfo is not None and args.interval >= 10
    args.output.parent.mkdir(parents=True,exist_ok=True)
    previous = {}
    ticks = os.sysconf('SC_CLK_TCK')
    with args.output.open('x') as out:
        while datetime.now(timezone.utc) < deadline:
            row = snapshot(args.work_root,previous,ticks)
            out.write(json.dumps(row)+'\n')
            out.flush()
            remaining = (deadline-datetime.now(timezone.utc)).total_seconds()
            if remaining <= 0:
                break
            time.sleep(min(args.interval,remaining))
    print(json.dumps({'status':'terminal','output':str(args.output),'deadline_utc':deadline.isoformat()}),flush=True)


if __name__ == '__main__':
    main()
