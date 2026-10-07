"""Explicit schemas and request-local identity checks; vector position is never chronology."""
from pathlib import Path
import numpy as np
P_FIELDS=['generation','event','device','class','validation_begin','command_available','wait_begin','wait_end','cpu_begin','cpu_end','commit_end','worker_observed','metadata_submit','cuda_observed','ack_state','notify_unlock_return']
H_FIELDS=['event','hook_begin','publications_end','hook_end','flag_before','flag_after','plan_end','cpu_end','flag_b_before','flag_b_after','flag_cpu_before','flag_cpu_after']
P=np.dtype([(f,'<u8') for f in P_FIELDS]);H=np.dtype([(f,'<u8') for f in H_FIELDS]);G=np.dtype([(f,'<u8') for f in ['begin','end','ring','ordinal']])
def read_gpu(path):
 with Path(path).open('rb') as f:
  head=np.fromfile(f,'<u8',20);assert len(head)==20 and head[0]==1 and head[3]==11
  counts=list(map(int,head[5:16]));rows=[np.fromfile(f,G,min(n,int(head[2]))) for n in counts];assert not f.read(1),'Trailing GPU data'
 return {'header':head,'rows':rows,'counts':counts,'host_brackets':list(map(int,head[16:20])),'device':int(head[1]),'detail':bool(head[4]),'overflow':any(n>int(head[2]) for n in counts)}
def identity_check(prefix, version, expected=15672):
 errors=[];gpus=[read_gpu(str(prefix)+f'-gpu{d}-trace.bin') for d in [0,1]]
 for g in gpus:
  if g['overflow']:errors.append('GPU buffer overflow')
  if g['counts'][8]!=2:errors.append('Calibration count')
  expected_kinds=range(8) if version==1 else [0,1,2,4,7]
  for kind in expected_kinds:
   records=g['rows'][kind]
   if len(records)!=expected:errors.append(f'device{g["device"]} kind{kind} count')
   elif not (np.array_equal(records['ordinal'],np.arange(expected)) and np.array_equal(records['ring'],np.tile(np.arange(1,25),expected//24))):errors.append('Repeated graph/event identity alias')
   if np.any(records['end']<records['begin']):errors.append('Device timestamp reversal')
  for kind in [9,10]:
   if g['counts'][kind]!=653:errors.append('Window endpoint count')
 pub=np.fromfile(str(prefix)+'-publication-trace.bin',P);host=np.fromfile(str(prefix)+'-producer-trace.bin',H)
 if len(host)!=31344 or not np.array_equal(host['event'],np.arange(31344)):errors.append('Host event coverage/alias')
 if not np.array_equal(pub['generation'],np.arange(len(pub))):errors.append('Publication generation coverage')
 for x in pub:
  if not (x['validation_begin']<=x['command_available']<=x['worker_observed']<=x['metadata_submit']<=x['cuda_observed']<=x['ack_state']<=x['notify_unlock_return']):errors.append('Worker publication sequence')
  if not (x['wait_begin']<=x['wait_end']<=x['commit_end']):errors.append('Host ack sequence')
  if x['commit_end']>host[int(x['event'])]['publications_end']:errors.append('Publication after hook phase')
  if x['device']>1 or x['class']>2 or x['device']==1 and x['class']==2:errors.append('Worker physical class/device')
 return {'state':'PASS' if not errors else 'FAIL','errors':sorted(set(errors)),'pub_count':len(pub),'host_count':len(host),'gpu_counts':[g['counts'] for g in gpus],'overflow':any(g['overflow'] for g in gpus),'linked_wait_A_count':sum(g['counts'][0] for g in gpus),'expected_wait_A_count':31344,'version':version}
