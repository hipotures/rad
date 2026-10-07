"""Finite logged owned command with flushed heartbeat; no implicit rebuild."""
import subprocess,sys,time
from common import *
if __name__=='__main__':
 label=sys.argv[1];cmd=sys.argv[2:];ledger('Command start',label=label,command=cmd)
 with Heartbeat(label,2),(W/'logs'/f'{label}.log').open('x') as f:
  r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=420)
 ledger('Command finish',label=label,exit_code=r.returncode);print('COMMAND_FINISH',label,r.returncode,flush=True);sys.exit(r.returncode)
