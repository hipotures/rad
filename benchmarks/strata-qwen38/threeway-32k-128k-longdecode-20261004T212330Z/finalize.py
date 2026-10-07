import json,hashlib,shutil,subprocess,time
from pathlib import Path
import analyze,enrich
R=Path(__file__).resolve().parent
s=json.loads((R/'summary.json').read_text());diag=[];invalid=[]
for p in [R/'raw/CURRENT-32K-VALIDATION-run1.json',*sorted((R/'raw').glob('*-32K-16K-run[123].json'))]:
 a=json.loads(p.read_text());a['raw_path']=str(p);a=enrich.enrich(a);a['headline_eligible']=False;a['summary_exclusion']='OPTIONAL_INCOMPLETE_FIXED_LENGTH_CONFIRMATION' if '16K' in p.name else 'ORIGINAL_WORKLOAD_NATURAL_EOS';a['decode_progression']=analyze.progression(a)
 if '16K' in p.name:diag.append(a)
 if not a['valid']:invalid.append(a)
s.update(primary_valid_count=18,optional_valid_count=sum(a['valid'] for a in diag),diagnostic_runs=diag,invalid_runs=invalid)
(R/'summary.json').write_text(json.dumps(s,indent=2));(R/'analysis/optional-progression.json').write_text(json.dumps(diag,indent=2))
dec=json.loads((R/'analysis/confirmation-decision.json').read_text());dec.update(outcome='INCOMPLETE_FIXED_LENGTH_COMPARISON_NATURAL_EOS',results=str(R/'analysis/confirmation-results.json'),invalid_outputs={'CURRENT':9689,'HELPER':13174},valid_outputs={'HELPER':[16384]},valid_three_run_medians=False,final_action='No prompt rewriting/repetition search; keep primary4096 matrix complete; optional diagnostic only')
(R/'analysis/confirmation-decision.json').write_text(json.dumps(dec,indent=2))
rec={'recommendation':'BASELINE_CURRENT_LAYER_SPLIT','reason':'For this shared repository long-output workload, currentK25/pcie0.28 wins4096-output median TG at both32K and128K and has the best PP/TTFT.32K late2K–4K helper/split estimates are nearly tied and the16K A/B is incomplete due natural EOS; no universal long-generation winner is claimed. Use current as the conservative frozen research reference, not proof that helper cannot win on other trajectories.128K API token-ID difference is explicitly documented.','config':str(R/'configs/CURRENT.json'),'source_HEAD':'6f32ec070f23ced9f50e704d854d775da52591ab','binary_sha256':'871bb3b8ff217b6c53b517e3a5f77504e86c74877d6c717050e2034d3098840d','scope':'Reference for upcoming residency research; no implementation authorized in this campaign'}
(R/'recommendation.json').write_text(json.dumps(rec,indent=2))
ref=R.parent/'iq3s-v0138-2x4090'
for f in ['model-provenance.json','environment.json']:shutil.copy2(ref/f,R/'git'/('v0138-'+f))
shutil.copy2(ref/'evidence/IQ3_S-SHA256SUMS',R/'git/IQ3_S-SHA256SUMS')
for name in ['HELPER','V0138','CURRENT']:
 c=json.loads((R/'configs'/f'{name}.json').read_text());cache=Path(c['cwd'])/'build-default/CMakeCache.txt';shutil.copy2(cache,R/'git'/f'{name}-current-CMakeCache.txt')
 # Current build cache may describe diagnostic rebuild; preserved original cache is additionally retained.
 if name=='CURRENT':
  for fn in ['control-configure-command.json','control-build-command.json']:
   shutil.copy2(R.parent/'pr578-dual4090-refresh-20261004T124028Z/git'/fn,R/'git'/('CURRENT-preserved-'+fn))
(R/'README.md').write_text('Reproduce analysis: run analyze.py, bursts.py, finalize.py, audit.py, report.py in this directory with the preserved control venv. Do NOT rerun driver.py unless explicitly launching a new campaign; completed cells skip, but source/environment/model guards must be reviewed. Raw requests/streams/footer logs and input IDs are immutable evidence. Optional16K lacks three valid results per configuration and is diagnostic only. Production/research reference: configs/CURRENT.json. All benchmark servers stopped.\n')
