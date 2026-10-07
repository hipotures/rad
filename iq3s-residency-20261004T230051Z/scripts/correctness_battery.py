"""Greedy preserved battery: save all answers, completion state and divergence evidence."""
import argparse, difflib, json, pathlib, re, subprocess
from lab import ROOT, Session, save, load
from diagnostic_logs import has_nonfinite_failure
ap=argparse.ArgumentParser();ap.add_argument('--variant',required=True);ap.add_argument('--experiment',required=True);ap.add_argument('--attempt',default='v1');ap.add_argument('--reference');ap.add_argument('--port',type=int,default=18132)
a=ap.parse_args();out=ROOT/'experiments'/a.experiment/a.attempt/'correctness'/a.variant
if out.exists():raise RuntimeError('Correctness attempt exists')
out.mkdir(parents=True);save(out/'protocol.json',{'kind':'diagnostic, not headline speed','cases':'saved prior 10 prompts; frozen input IDs','reference':a.reference,'NaN':'STRATA_DBG_NAN=1 only for this session; synchronized debug checks not used in speed','limits':'No teacher-forced logits or true output IDs claimed; frontend text/reasoning and finish state compared. Greedy divergence must be investigated, not automatically called harmless.'})
summary=[]
with Session(a.variant,'32k',out,port=a.port,diagnostic_env={'STRATA_DBG_NAN':'1'}) as session:
    # Explicit diagnostic setting only; lab clears inherited debug state.
    # Engine checks are additionally audited from its normal failure/output logs.
    warm=session.request('warmup','warmup','warmup')
    if warm['state']!='VALID':raise RuntimeError('Warmup invalid')
    for n in range(1,11):
        name=f'case{n}';r=session.request(name,name,'correctness',ROOT/'workloads/correctness-manifest.json')
        text=r.get('text','');reason=r.get('reasoning','');log=(out/'raw'/f'{name}-engine.log').read_text() if (out/'raw'/f'{name}-engine.log').exists() else ''
        finite_error=has_nonfinite_failure(log)
        rec={'case':n,'state':r['state'],'generated':r.get('actual_output_tokens'),'finish_reason':r.get('finish_reason'),'application_status':r.get('application_status'),'nonfinite_reported':finite_error,'empty_answer':not text.strip(),'output_sha256':r.get('output_text_sha256'),'same_input_ids':None,'same_visible_output':None,'first_diverging_character':None}
        if a.reference:
            ref=load(pathlib.Path(a.reference)/'raw'/f'{name}.json')
            old=ref.get('reasoning','')+'\0'+ref.get('text','');new=reason+'\0'+text
            rec['same_input_ids']=r['payload']['input_ids_sha256']==ref['payload']['input_ids_sha256']
            rec['same_visible_output']=old==new
            rec['first_diverging_character']=next((i for i,(x,y) in enumerate(zip(old,new)) if x!=y),min(len(old),len(new)) if old!=new else None)
            (out/'raw'/f'{name}-text.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='control',tofile=a.variant)))
        summary.append(rec);save(out/'summary.json',summary)
        if r['state']=='FAILED' or finite_error:raise RuntimeError('Real runtime correctness failure; stop battery')
    # Exercise the frozen variant's owned-process stop launcher as part of flow.
    subprocess.run([str(ROOT/'variants'/a.variant/'stop.sh')],check=True)
print(json.dumps(summary,indent=2),flush=True)
