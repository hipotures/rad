"""Update root deliverables from persisted stage evidence; never run inference."""
import csv,json,pathlib,time
from lab import ROOT,save
latest={}
for line in (ROOT/'experiments.jsonl').read_text().splitlines():
 if line.strip():row=json.loads(line);latest[row['id']]=row
controls=json.loads((ROOT/'experiments/E002-controls/summary.json').read_text())
rows=[]
for c in controls:
 row={'experiment':'E002','variant':c['variant'],'profile':c['profile'],'valid':c['valid'],'attempted':c['attempted'],'raw_paths':c['runs']}
 for key in ['actual_input_tokens','PP','TG','TTFT_s','wall_s','mtp_acceptance_pct','mtp_accepted_per_window']:
  for stat,value in c[key].items():row[key+'_'+stat]=value
 rows.append(row)
deadline=json.loads((ROOT/'deadline.json').read_text())
save(ROOT/'summary.json',{'state':'IN_PROGRESS','elapsed_s':time.time()-deadline['start_epoch'],'deadline':deadline,'stage_states':latest,'measured_controls':rows,'candidate_ledger':json.loads((ROOT/'candidate-ledger.json').read_text()),'selection':'UNDECIDED: no confirmed runtime candidate yet','scope':'only total32768/131072 capacity; observed fixed4096output controls'})
with (ROOT/'summary.csv').open('w') as handle:
 writer=csv.DictWriter(handle,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
text=['# IQ3_S expert-residency research — interim report','','Status: IN_PROGRESS. Absolute deadline '+deadline['deadline_utc']+'. Original goal remains intact.','','## Fresh frozen controls','','|Total capacity|Actual input median|PP median|TG median(min/max)|TTFT median|Valid|','|---:|---:|---:|---:|---:|---:|']
for row in rows:text.append(f"|{'32768' if row['profile']=='32k' else '131072'}|{row['actual_input_tokens_median']}|{row['PP_median']}|{row['TG_median']}({row['TG_min']}/{row['TG_max']})|{row['TTFT_s_median']:.3f}|{row['valid']}/3|")
text+=['','Control rebuilt from frozen6f32ec0 with its own source/build; historical871bb3b8binary preserved. Same K25/PCIe0.28/MTP4/minp0.5/INT8/workers15, equal4096/64warmup, suffix/reuse0. Detailed provenance/tests/resource budgets: experiments/E001-evidence/report.md and experiments/E002-controls/report.md.','','## Completed diagnostic evidence','','Both repository traces and six independent task traces validate all demand/path/slot-publication totals. Exact frozen selector reproduces all promotions/float32 usage on32k and128k. See experiments/E003-diagnostics/report.md and E004-replay/v1/current-validation-*; diagnosis records preserve per-window progression and host-clock brackets. No diagnostic TG is promoted to a headline candidate result.','','## Research tree and remaining work','','Byte/queue replay, Expert-Jev linear/MLP/temporal evaluation, trace-supported runtime implementation, correctness, two-profile live confirmation and final audit remain. Candidate family dispositions are maintained in candidate-ledger.json. No claim of exhausted headroom or measured candidate gain is currently warranted.','','All old weights/checkouts/launchers/results remain preserved. New task-scoped work is under this repository only. Local source changes are reversible and unpublished.']
(ROOT/'report.md').write_text('\n'.join(text)+'\n')
print('root report/summary updated',flush=True)
