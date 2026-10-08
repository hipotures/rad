#!/usr/bin/env python3
"""Bounded campaign telemetry; no scheduling or process control."""
import argparse
import csv
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import time


def snapshot(root):
    processes = []
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():
            continue
        try:
            command = (proc / 'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
            cwd = (proc / 'cwd').resolve()
            if str(root) not in command and root.name not in command and not cwd.is_relative_to(root):
                continue
            stat = (proc / 'stat').read_text().rsplit(')', 1)[1].split()
            status = dict(line.split(':', 1) for line in (proc / 'status').read_text().splitlines() if ':' in line)
            processes.append({'pid': int(proc.name), 'ppid': int(stat[1]),
                              'cpu_ticks': int(stat[11]) + int(stat[12]),
                              'threads': int(status.get('Threads', '0')),
                              'rss_kib': int(status.get('VmRSS', '0 kB').split()[0]),
                              'state': status.get('State', '').strip(),
                              'name': status.get('Name', '').strip(), 'command': command[:500].strip()})
        except (OSError, ValueError):
            continue
    mem = dict(line.split(':', 1) for line in Path('/proc/meminfo').read_text().splitlines())
    cpu = [int(x) for x in Path('/proc/stat').read_text().splitlines()[0].split()[1:]]
    return {'utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'monotonic': time.monotonic(),
            'cpu_ticks': cpu, 'cpu_count': len(os.sched_getaffinity(0)),
            'mem_available_kib': int(mem['MemAvailable'].split()[0]),
            'disk_free_bytes': shutil.disk_usage(root).free,
            'task_processes': processes,
            'compact_result_files': sum(1 for p in root.rglob('*.json') if '/work/' not in str(p) and '/evidence/' not in str(p))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--deadline')
    parser.add_argument('--run-id', default='legacy')
    parser.add_argument('--compact-output', type=Path)
    parser.add_argument('--interval', type=float, default=150)
    args = parser.parse_args()
    root = args.root.resolve()
    raw = root / 'work' / ('telemetry' if args.run_id == 'legacy' else 'telemetry-' + args.run_id)
    raw.mkdir(parents=True, exist_ok=True)
    deadline = dt.datetime.fromisoformat(args.deadline.replace('Z', '+00:00')) if args.deadline else None
    previous = None
    tick_hz = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
    csv_path = args.compact_output or root / 'results' / 'resources.csv'
    fields = ['utc', 'system_busy_cpu_slots', 'observed_task_cpu_slots', 'task_processes',
              'task_threads', 'task_rss_kib', 'mem_available_kib', 'disk_free_bytes', 'compact_result_files']
    with (raw / 'observations.jsonl').open('x') as output, csv_path.open('x', newline='') as compact:
        writer = csv.DictWriter(compact, fieldnames=fields)
        writer.writeheader()
        while True:
            current = snapshot(root)
            system = observed = None
            if previous:
                elapsed = current['monotonic'] - previous['monotonic']
                cpu_delta = [a-b for a,b in zip(current['cpu_ticks'], previous['cpu_ticks'])]
                system = round((sum(cpu_delta[:8]) - cpu_delta[3] - cpu_delta[4]) / tick_hz / elapsed, 3)
                prior = {p['pid']: p for p in previous['task_processes']}
                delta = sum(max(0, p['cpu_ticks'] - prior[p['pid']]['cpu_ticks']) for p in current['task_processes'] if p['pid'] in prior)
                observed = round(delta / tick_hz / elapsed, 3)
            current['system_busy_cpu_slots'] = system
            current['observed_task_cpu_slots'] = observed
            output.write(json.dumps(current, separators=(',', ':')) + '\n')
            output.flush()
            writer.writerow({'utc': current['utc'], 'system_busy_cpu_slots': system,
                             'observed_task_cpu_slots': observed, 'task_processes': len(current['task_processes']),
                             'task_threads': sum(p['threads'] for p in current['task_processes']),
                             'task_rss_kib': sum(p['rss_kib'] for p in current['task_processes']),
                             'mem_available_kib': current['mem_available_kib'], 'disk_free_bytes': current['disk_free_bytes'],
                             'compact_result_files': current['compact_result_files']})
            compact.flush()
            print(json.dumps({key: current[key] for key in ['utc', 'system_busy_cpu_slots', 'observed_task_cpu_slots', 'mem_available_kib', 'disk_free_bytes', 'compact_result_files']}), flush=True)
            previous = current
            remaining = (deadline - dt.datetime.now(dt.timezone.utc)).total_seconds() if deadline else float('inf')
            if remaining <= 0:
                break
            time.sleep(min(args.interval, remaining))


if __name__ == '__main__':
    main()
