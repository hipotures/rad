"""Finite owned subprocess with observable heartbeats and fresh logs."""
import argparse,signal,subprocess,time,psutil,os
from common import *
a=argparse.ArgumentParser();a.add_argument('label');a.add_argument('--timeout',type=int,required=True);a.add_argument('command',nargs=argparse.REMAINDER);v=a.parse_args();cmd=v.command
if cmd and cmd[0]=='--':cmd=cmd[1:]
assert cmd
log=W/'logs'/(v.label+'.log');ledger('Owned command START',label=v.label,command=cmd,timeout=v.timeout)
with log.open('x') as f:
 p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);created=psutil.Process(p.pid).create_time();save(W/'tmp'/(v.label+'-process.json'),{'pid':p.pid,'created':created,'command':cmd});start=time.monotonic();last=start
 while p.poll() is None:
  now=time.monotonic()
  if now-start>v.timeout:
   owner=psutil.Process(p.pid);assert abs(owner.create_time()-created)<.1;os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(20)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait(10)
   raise TimeoutError(v.label)
  if now-last>=25:
   r=load(C/'progress.json') if (C/'progress.json').exists() else {};print('HEARTBEAT',v.label,'PID',p.pid,'alive',r,flush=True);last=now
  time.sleep(1)
ledger('Owned command END',label=v.label,exit_code=p.returncode,elapsed_s=time.monotonic()-start);print('COMMAND END',v.label,p.returncode,flush=True);raise SystemExit(p.returncode)
