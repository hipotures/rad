"""Phase-filtered lightweight telemetry; unavailable quantities remain null."""
from pathlib import Path
import json,argparse,numpy as np,datetime
from tape import Tape
C=Path(__file__).resolve().parents[1]
def analyze(label,tape):
 p=C/'raw'/label;t=Tape(tape);o=np.fromfile(p/'raw/observations.bin',t.obs_dtype)
 begin=int(o['begin_ns'][0])/1e9;end=int(o['end_ns'][-1])/1e9
 samples=[json.loads(x) for x in (p/'telemetry/run.jsonl').read_text().splitlines()]
 decode=[x for x in samples if begin<=x['monotonic']<=end]
 def stat(vals):
  v=[float(x) for x in vals if x is not None];return {'samples':len(v),'min':min(v),'median':float(np.median(v)),'mean':float(np.mean(v)),'max':max(v)} if v else None
 result={'label':label,'decode_monotonic_s':[begin,end],'decode_samples':len(decode),'system_cpu_pct':stat([x.get('system_cpu_pct') for x in decode]),'process_cpu_pct':stat([sum(y.get('cpu_pct',0) for y in x.get('processes',[])) for x in decode]),'cpu_steal_pct':stat([x.get('cpu_times_percent',{}).get('steal') for x in decode]),'ram_used_gib':stat([x.get('ram_used_gib') for x in decode]),'mem_available_gib':stat([x.get('mem_available_gib') for x in decode]),'rss_gib':stat([sum(y.get('rss_gib',0) for y in x.get('processes',[])) for x in decode]),'gpus':{},'PCIe_attribution':'Aggregate samples only; no event-level DMA bandwidth inferred. Missing counters are unknown.'}
 for d in [0,1]:
  g=[y for x in decode for y in x.get('gpus',[]) if int(y.get('index',-1))==d]
  result['gpus'][str(d)]={k:stat([y.get(k) for y in g]) for k in ['util_pct','power_w','vram_mib','sm_mhz','memory_mhz','temperature_c','pcie_generation','pcie_width','pcie_rx_kib_s','pcie_tx_kib_s']}
 offset=float(np.median([x['wall_time']-x['monotonic'] for x in samples]));pcie=[]
 for line in (p/'telemetry/pcie-dmon.log').read_text().splitlines():
  words=line.split()
  if len(words)!=5 or not words[0].isdigit():continue
  try:
   epoch=datetime.datetime.strptime(words[0]+' '+words[1],'%Y%m%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc).timestamp()
   if begin+offset<=epoch<=end+offset:pcie.append({'epoch':epoch,'device':int(words[2]),'rx_MB_s':float(words[3]),'tx_MB_s':float(words[4])})
  except ValueError:continue
 result['PCIe_decode_dmon']={str(d):{k:stat([x[k] for x in pcie if x['device']==d]) for k in ['rx_MB_s','tx_MB_s']} for d in [0,1]}
 result['PCIe_clock']='nvidia-smi dmon UTC wall timestamps at1s resolution; aligned using observed wall-minus-monotonic offset. Phase-edge samples can include neighboring work; no event-level saturation/attribution claim.'
 def io_delta(rows):
  if len(rows)<2:return None
  first={x['pid']:x for x in rows[0].get('processes',[])};last={x['pid']:x for x in rows[-1].get('processes',[])}
  return {str(pid):{key:last[pid][key]-first[pid][key] if key in last[pid] and key in first[pid] else None for key in ['read_bytes','read_count']} for pid in first.keys()&last.keys()}
 result['sampled_process_IO_decode_delta']=io_delta(decode);result['sampled_process_IO_whole_request_delta']=io_delta(samples)
 result['IO_caveat']='Per-process Linux I/O counters across available1Hz samples; decode edge gaps excluded. Physical read_bytes is not an expert-source attribution. Expert source is independently checked fullRAM ArenaExpertSource; logical expertfile reads from native/metric counters separate.'
 result['whole_request_samples']=len(samples)
 (C/'analysis'/f'{label}-system.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('label');a.add_argument('tape');v=a.parse_args();print(json.dumps(analyze(v.label,v.tape),indent=2))
