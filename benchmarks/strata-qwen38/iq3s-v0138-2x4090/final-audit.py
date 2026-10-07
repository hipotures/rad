from pathlib import Path
import json,re,hashlib,datetime,statistics,subprocess
R=Path(__file__).parent;s=json.loads((R/'summary.json').read_text());nonces=[];checks=[]
pcie=[]
for line in (R/'telemetry/IQ3S-v0138-pcie-dmon.log').read_text().splitlines():
 parts=line.split()
 if len(parts)!=5 or not parts[0].isdigit():continue
 try:pcie.append({'wall':datetime.datetime.strptime(' '.join(parts[:2]),'%Y%m%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc).timestamp(),'GPU':int(parts[2]),'RX_MB_s':float(parts[3]),'TX_MB_s':float(parts[4])})
 except ValueError:pass
for a in s['measured_raw']:
 tag=a['repeat_tag'];base=R/'raw'/f'IQ3S-v0138-{tag}'
 payload=json.loads(Path(str(base)+'-request.json').read_text());stream=json.loads(Path(str(base)+'-stream.json').read_text());log=Path(str(base)+'-engine.log').read_text()
 nonce=re.search(r'\[bench run ([0-9a-f]+)\]',payload['messages'][0]['content'])[1];nonces.append(nonce)
 assert payload['temperature']==0 and payload['max_tokens']==256 and payload['reasoning_effort']=='none'
 assert a['usage']['prompt_tokens']==a['actual_prompt_tokens_tokenizer']==a['target_prompt_tokens']
 assert a['usage']['completion_tokens']==256 and a['finish_reasons']==['length'] and a['cache_reused_tokens']==0 and a['status']=='OK' and a['abort'] is None and not a['tool_call_events']
 assert a['selected_layer_split_K']==25 and a['GPU0_slots']==10112 and a['GPU1_slots']==8376
 assert a['Strata_HEAD']==s['Strata_HEAD'] and a['Strata_version']=='0.1.38' and a['model_revision']=='ed59f92082b1e93c0e96d60a8b11aab089b52f09'
 assert 'strata serve: prompt ' in log and '256 generated' in log
 assert Path(str(base)+'-response.txt').read_text()==a['text'] and not stream['tool_call_events']
 samples=[json.loads(line) for line in Path(a['telemetry_file']).read_text().splitlines()];offset=samples[0]['wall_time']-samples[0]['monotonic']
 a['PCIe_aggregates']={}
 for phase,lo,hi in [('prefill',a['t_start_monotonic_s'],a['t_first_monotonic_s']),('decode',a['t_first_monotonic_s'],a['t_end_monotonic_s'])]:
  a['PCIe_aggregates'][phase]={}
  for i in [0,1]:
   vals=[x for x in pcie if x['GPU']==i and lo+offset<=x['wall']<=hi+offset]
   a['PCIe_aggregates'][phase][str(i)]={'samples':len(vals),'RX_MB_s_mean':statistics.mean(x['RX_MB_s'] for x in vals) if vals else None,'TX_MB_s_mean':statistics.mean(x['TX_MB_s'] for x in vals) if vals else None}
 a['PCIe_sampling_note']='nvidia-smi dmon1Hz, UTCsecond granularity; phase alignment approximate ±1s, sparse decode samples. Bandwidth counters not expert-specific.'
 Path(str(base)+'.json').write_text(json.dumps(a,indent=2)+'\n')
 checks.append({'raw':str(base)+'.json','payload_sha256':hashlib.sha256(Path(str(base)+'-request.json').read_bytes()).hexdigest(),'nonce':nonce,'status':'VALID_256_OUTPUT_ZERO_REUSE_EXACT_ACTUAL_TOKENS'})
assert len(set(nonces))==12
assert not subprocess.check_output(['git','status','--porcelain'],cwd='/srv/ai/strata-v0.1.38',text=True).strip()
apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader'],text=True);assert not apps.strip()
s['independent_audit']={'status':'PASS','measured_count':12,'unique_measured_nonce_count':12,'per_request':checks,'model_files_unchanged':s['model_stat_unchanged'],'clean_upstream_checkout':True,'GPU_apps_after':apps,'PSS_sampling':'Only before/after timed request, no live PSS read;1Hz sampler source preserved.'}
s['decode_system_cpu_peak_all_runs']=max(a['telemetry_aggregates']['decode']['system_cpu_pct_peak'] for a in s['measured_raw'])
(R/'summary.json').write_text(json.dumps(s,indent=2)+'\n');(R/'evidence/independent-final-audit.json').write_text(json.dumps(s['independent_audit'],indent=2)+'\n')
print('PASS:12valid measured requests,12different nonces,exactactualtokens,256output,zero reuse,clean checkout,both GPUsfree')
