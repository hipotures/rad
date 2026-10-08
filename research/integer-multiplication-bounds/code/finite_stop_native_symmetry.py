#!/usr/bin/env python3
"""Guarded cleanup of currently profiled overdue native symmetry attempts.

Historical PID records are not authority. This command requires unchanged
live process births/parents and a fresh native sample of every active worker
in each affected pool. It refuses cleanup if any productive stage is present.
Completed scientific files are never rewritten or removed.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time


def live(pid):
    p=Path('/proc')/str(pid);stat=(p/'stat').read_text();fields=stat[stat.rfind(')')+2:].split()
    return dict(pid=pid,parent_pid=int(fields[1]),start_ticks=int(fields[19]),
        cpu_seconds=(int(fields[11])+int(fields[12]))/os.sysconf('SC_CLK_TCK'),
        elapsed_seconds=time.monotonic()-int(fields[19])/os.sysconf('SC_CLK_TCK'),
        cmdline=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode())


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--profile',type=Path,required=True)
    ap.add_argument('--output-directory',type=Path,required=True);args=ap.parse_args()
    assert not args.output_directory.exists();args.output_directory.mkdir(parents=True)
    original=json.loads(args.profile.read_text());workers=original['workers'];known={x['pid']:x for x in workers}
    before=[]
    for old in workers:
        now=live(old['pid'])
        assert now['start_ticks']==old['start_ticks'] and now['parent_pid']==old['parent_pid']
        assert 'multiprocessing.spawn' in now['cmdline'] and now['elapsed_seconds']>300
        before.append(now)
    for parent in {x['parent_pid'] for x in before}:
        command=live(parent)['cmdline'];assert 'finite_complex_' in command and '--run-dir' in command
        children=(Path('/proc')/str(parent)/'task'/str(parent)/'children').read_text().split()
        for child in children:
            now=live(int(child))
            if 'multiprocessing.spawn' in now['cmdline'] and now['cpu_seconds']>2 and now['cpu_seconds']/now['elapsed_seconds']>.1:
                assert now['pid'] in known, 'A productive or unprofiled active worker forbids broken-pool cleanup'
    record=dict(status='Guarded live cleanup pending fresh stage verification',started_utc=datetime.now(timezone.utc).isoformat(),
        live_processes_before=before,minimum_native_symmetry_sample_fraction=.9,
        scope='Individually overdue preprocessing attempts only; all active affected-pool workers must pass the same fresh native guard')
    output=args.output_directory/'guarded-stop.json';output.write_text(json.dumps(record,indent=2)+'\n')
    binary=args.output_directory/'fresh.perf.data'
    command=['perf','record','-o',str(binary),'-p',','.join(str(x['pid']) for x in before),'-F','49','--','sleep','2']
    with (args.output_directory/'perf-record.log').open('w') as log:
        result=subprocess.run(command,stdout=log,stderr=log,timeout=15)
    assert result.returncode==0
    result=subprocess.run(['perf','report','--stdio','--no-children','--sort','pid,dso,symbol','-g','none',
        '-i',str(binary),'--percent-limit','0'],capture_output=True,text=True,timeout=15)
    assert result.returncode==0;(args.output_directory/'fresh-perf-report.txt').write_text(result.stdout)
    totals={x['pid']:0.0 for x in before};symmetry=dict(totals)
    for line in result.stdout.splitlines():
        m=re.match(r'\s*([\d.]+)%\s+(\d+):',line)
        if not m:continue
        percentage,pid=float(m.group(1)),int(m.group(2));totals[pid]=totals.get(pid,0)+percentage
        if 'HighsSymmetryDetection' in line:symmetry[pid]=symmetry.get(pid,0)+percentage
    for worker in before:
        pid=worker['pid'];assert totals[pid]>0
        worker['fresh_native_symmetry_fraction']=symmetry[pid]/totals[pid]
        assert worker['fresh_native_symmetry_fraction']>=.9, 'A productive verification or other stage must not be ended'
    record.update(status='Fresh individual live-native guards PASS',live_processes_before=before)
    output.write_text(json.dumps(record,indent=2)+'\n')
    actions=[]
    for old in before:
        try:now=live(old['pid'])
        except FileNotFoundError:
            actions.append(dict(pid=old['pid'],action='Already ended by affected executor cleanup after an earlier guarded termination'));continue
        assert now['start_ticks']==old['start_ticks'] and now['parent_pid']==old['parent_pid']
        os.kill(now['pid'],signal.SIGTERM)
        actions.append(dict(pid=now['pid'],action='SIGTERM after individually verified overdue native preprocessing',live_identity_before_signal=now))
    record.update(status='Terminal guarded overdue-native attempt cleanup PASS',actions=actions,
        completed_utc=datetime.now(timezone.utc).isoformat(),historical_record_is_not_live_process_authority=True)
    output.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(status=record['status'],individually_guarded=len(before))),flush=True)


if __name__=='__main__':main()
