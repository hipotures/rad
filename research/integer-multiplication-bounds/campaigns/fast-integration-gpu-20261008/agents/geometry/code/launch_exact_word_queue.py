#!/usr/bin/env python3
"""Replenish one exact mathematical queue after a durable predecessor receipt.

Input transition files may be produced concurrently by independent source-only
compiler checks. This launcher consumes no compute slot while waiting and never
interrupts a useful predecessor.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    assert args.command and args.command[0] == '--'
    command = args.command[1:]
    assert command
    inputs = json.loads(args.input.read_text())
    announced = 0.0
    while True:
        predecessor = None
        try:
            predecessor = json.loads(args.receipt.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        missing = [row['transitions'] for row in inputs
                   if not Path(row['transitions']).exists()]
        ready = False
        if predecessor is not None:
            status = predecessor['status'].upper()
            assert not status.startswith(('FAIL', 'ERROR', 'ABORT')), status
            ready = status.startswith(('PASS', 'COMPLETE'))
            if ready:
                assert not predecessor.get('failures')
                if not missing:
                    break
        if time.monotonic() - announced >= 60:
            print(json.dumps(dict(status='WAITING FOR VALUABLE PREDECESSOR',
                utc=datetime.now(timezone.utc).isoformat(),
                predecessor_complete=ready,
                missing_transitions=missing, command=command)), flush=True)
            announced = time.monotonic()
        time.sleep(1)
    print(json.dumps(dict(status='STARTING DISTINCT EXACT WORD QUEUE',
        utc=datetime.now(timezone.utc).isoformat(), command=command)), flush=True)
    os.execvp(command[0], command)


if __name__ == '__main__':
    main()
