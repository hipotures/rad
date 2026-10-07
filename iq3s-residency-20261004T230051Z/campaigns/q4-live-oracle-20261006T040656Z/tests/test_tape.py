"""Structural regression checks; reject altered schedules, counts, routes and truncation."""
import sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from tape import Tape,WINDOW,HEADER
import numpy as np
p=Path(sys.argv[1]);t=Tape(p);assert t.validate()['state']=='PASS';checks=[]
with tempfile.TemporaryDirectory(dir=p.parent) as temp:
 for mode in ['truncate','extra-byte']:
  d=p.read_bytes();q=Path(temp)/mode;q.write_bytes(d[:-1] if mode=='truncate' else d+b'!')
  try:Tape(q)
  except (AssertionError,ValueError):checks.append(mode)
  else:raise AssertionError(mode)
 for field,value in [('T',5),('accepted',4),('position',1),('emitted_before',99)]:
  t=Tape(p);t.ws=t.ws.copy();t.ws[1][field]=value;assert t.validate()['state']=='FAIL';checks.append(field)
 t=Tape(p);t.ws=t.ws.copy();t.ws[1]['routes']['ids'][0,0]=513;assert t.validate()['state']=='FAIL';checks.append('expert-ID')
print('PASS',checks)
