"""Read-only observation of an already-running identity-checked campaign parent."""
import argparse, psutil
from common import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pid', type=int, required=True)
    parser.add_argument('--created', type=float, required=True)
    parser.add_argument('--timeout', type=int, default=5000)
    args = parser.parse_args()
    started = time.monotonic()
    while time.monotonic() - started < args.timeout:
        try:
            process = psutil.Process(args.pid)
            assert abs(process.create_time() - args.created) < .01, 'PID identity changed'
            if process.status() == psutil.STATUS_ZOMBIE:
                break
            assert any('campaign_live.py' in x for x in process.cmdline()), 'Unexpected parent command'
        except psutil.NoSuchProcess:
            break
        print('HEARTBEAT observed parent alive', args.pid, json.dumps(load(C / 'progress.json')), flush=True)
        time.sleep(25)
    else:
        raise RuntimeError('Observation timeout; no work terminated or restarted')
    print('OBSERVED PARENT TERMINAL; inspect execution records and log for scientific outcome', flush=True)
