#!/usr/bin/env python3
"""Atomic progress and append-only observations under the immutable clock."""
from pathlib import Path
import json,sys,time,datetime,os,threading
C=Path(__file__).resolve().parents[1];R=C/json.loads((C/'active-run.json').read_text())['run']
lock=threading.Lock()
def update(step,status,message,**kw):
 with lock:
  clock=json.loads((R/'clock.json').read_text());elapsed=time.monotonic()-clock['start_monotonic'];remaining=max(0,clock['budget_s']-elapsed)
  old=json.loads((C/'progress.json').read_text()) if (C/'progress.json').exists() else {}
  state=dict(old,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),step=step,status=status,message=message,elapsed_s=elapsed,remaining_s=remaining,eta='unknown',execution_run=str(R),clock=clock);state.update(kw)
  tmp=C/'progress.json.tmp';tmp.write_text(json.dumps(state,indent=2)+'\n');os.replace(tmp,C/'progress.json')
  with (C/'progress.jsonl').open('a') as f:f.write(json.dumps(state)+'\n')
  (C/'STATUS.md').write_text(f"# Phase 4 execution status\n\nStep {step}/5 — {message}\n\nElapsed {elapsed/60:.1f} min; remaining {remaining/60:.1f} min; ETA {state['eta']}.\n\n```json\n"+json.dumps(state,indent=2)+"\n```\n")
  print('PHASE4_PROGRESS '+json.dumps(state),flush=True)
if __name__=='__main__':update(int(sys.argv[2]) if len(sys.argv)>2 else 1,'RUNNING',sys.argv[1] if len(sys.argv)>1 else 'Status')
