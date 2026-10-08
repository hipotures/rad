#!/usr/bin/env python3
"""Replace a bounded predecessor queue after its durable completion receipt."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,json,os,time

p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,required=True)
p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
assert a.command and a.command[0]=='--';command=a.command[1:];assert command
print(json.dumps(dict(phase='WAITING FOR PREDECESSOR',receipt=str(a.receipt),utc=datetime.now(timezone.utc).isoformat())),flush=True)
while not a.receipt.exists():time.sleep(1)
result=json.loads(a.receipt.read_text());assert result.get('status')=='COMPLETE',result.get('status')
print(json.dumps(dict(phase='PREDECESSOR COMPLETE; STARTING DISTINCT QUEUE',utc=datetime.now(timezone.utc).isoformat(),command=command)),flush=True)
os.execvp(command[0],command)
