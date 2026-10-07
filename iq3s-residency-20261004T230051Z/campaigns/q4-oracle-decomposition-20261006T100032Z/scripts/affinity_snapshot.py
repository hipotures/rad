"""Read-only thread affinity observation; no affinity or scheduler changes."""
import datetime
import json
import os
from pathlib import Path

import psutil

C = Path(__file__).resolve().parents[1]


def main():
    status = json.loads((C / 'STATUS.json').read_text())
    label = status['running']['label']
    record_path = C / 'raw' / label / 'raw/native-process.json'
    if not record_path.exists():
        print('WAIT_NATIVE_READY', label, flush=True)
        return
    record = json.loads(record_path.read_text())
    process = psutil.Process(record['pid'])
    assert abs(process.create_time() - record['created']) < .1
    assert Path(process.exe()).resolve() == Path(record['executable']).resolve()
    threads = []
    for thread in process.threads():
        try:
            threads.append({
                'tid': thread.id,
                'name': Path(f'/proc/{process.pid}/task/{thread.id}/comm').read_text().strip(),
                'allowed_cpus': sorted(os.sched_getaffinity(thread.id)),
                'cumulative_user_s': thread.user_time,
                'cumulative_system_s': thread.system_time,
            })
        except (FileNotFoundError, ProcessLookupError):
            threads.append({'tid': thread.id, 'state': 'EXITED_DURING_SNAPSHOT'})
    value = {'label': label, 'pid': process.pid,
             'observed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'method': 'One read-only /proc+affinity snapshot; no profiling or changes',
             'threads': threads,
             'caveat': 'Generic thread names do not prove individual thread role. '
                       'Role inheritance is separately audited in the source.'}
    path = C / 'analysis' / (label + '-thread-affinity.json')
    assert not path.exists()
    path.write_text(json.dumps(value, indent=2) + '\n')
    print('AFFINITY_SNAPSHOT', label, len(threads), flush=True)


if __name__ == '__main__':
    main()
