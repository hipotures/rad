"""Finite final evidence inventory; run only after all GPU work, never modify old campaign data."""
from pathlib import Path
import json,hashlib,time,subprocess
C=Path(__file__).resolve().parents[1]
if __name__=='__main__':
 assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True,timeout=15).strip(),'GPU conflict'
 rows=[];start=time.monotonic()
 for directory in ['raw','tapes','inputs','configs','tests','phase-a','phase-b','phase-c','git']:
  for p in sorted((C/directory).rglob('*')):
   if not p.is_file() or p.is_symlink() or any(x in p.parts for x in ['__pycache__','Testing']):continue
   if p.name=='fixture' or 'inventory' in p.name:continue
   assert time.monotonic()-start<600,'Finite inventory timeout';h=hashlib.sha256()
   with p.open('rb') as f:
    while block:=f.read(8*1024**2):h.update(block)
   rows.append({'path':str(p.relative_to(C)),'bytes':p.stat().st_size,'sha256':h.hexdigest()})
   if len(rows)%50==0:print('INVENTORY_PROGRESS',len(rows),round(time.monotonic()-start,1),flush=True)
 (C/'analysis/evidence-inventory.json').write_text(json.dumps({'files':rows,'elapsed_s':time.monotonic()-start,'scope':'All retained raw attempts including invalid/pilots; tapes/sidecars/input manifests/configs/tests/source-build provenance; existing model weights and old campaigns not mutated or rehashed'},indent=2)+'\n');print('INVENTORY_COMPLETE',len(rows),round(time.monotonic()-start,2),flush=True)
