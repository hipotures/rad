"""Read-only progress watcher; never stops work or synchronizes CUDA."""
import time,psutil,json
from pathlib import Path
C=Path(__file__).resolve().parents[1]
while True:
 active=[p for p in psutil.process_iter(['cmdline']) if any(Path(a).name=='campaign_live.py' for a in p.info['cmdline'] or [])]
 x=json.loads((C/'progress.json').read_text());print('[HEARTBEAT]',json.dumps({k:x.get(k) for k in ['utc','step','task','arm','version','phase','completed','remaining','elapsed_s','remaining_s','next_action','eta_range_s']}),flush=True)
 if not active:break
 time.sleep(25)
