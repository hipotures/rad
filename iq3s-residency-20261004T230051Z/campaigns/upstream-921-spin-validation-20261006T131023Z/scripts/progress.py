"""Lightweight, bounded45-second supervision; prints progress without inference."""
import datetime,json,pathlib,time
C=pathlib.Path(__file__).resolve().parents[1]
start=time.monotonic();deadline=json.loads((C/'timing.json').read_text())['deadline_monotonic']
while time.monotonic()<deadline:
 state=json.loads((C/'STATUS.json').read_text())
 counts={cell:len(list((C/'raw'/cell).glob('*/pair.json'))) for cell in ['IQ3_S-32k','IQ3_S-128k','Q4-32k','Q4-128k']}
 log=C/'campaign-resumed.log'
 with log.open('rb') as f:
  f.seek(0,2);size=f.tell();f.seek(max(0,size-1600));lines=f.read().decode(errors='replace').splitlines()
 print(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':state['state'],'valid_pairs':counts,'latest':lines[-3:]}),flush=True)
 if state['state'] in ['MATRIX_COMPLETE','NEEDS_PROTOCOL_AUDIT','MEASUREMENT_CUTOFF','COMPLETE']:break
 time.sleep(45)
