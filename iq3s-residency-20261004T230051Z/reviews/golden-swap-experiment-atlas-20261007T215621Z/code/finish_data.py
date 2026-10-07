"""Attach truthful metadata/provenance to the frozen identity-based trajectory selection."""
import re
from common import *

def main():
    catalog=load(REVIEW/'site/data/catalog.json')
    manifest_path=campaign('golden-swap-phase0')/'benchmark-manifest.json'
    tasks={x['task_id']:x for x in load(manifest_path)['tasks']}
    extra_sources={str(manifest_path):reference(manifest_path)}
    source_paths={x['path']:x for x in load(REVIEW/'results/source-catalog.json')['sources']}
    for r in catalog['runs']:
        if r['campaign']=='IQ3_S-E004-replay':r['model_revision']=None
        p=REPO/r['source_result'];r['source_result_sha256']=source_paths.get(str(p),reference(p))['sha256']
        match=re.search(r'(2026\d{4})T(\d{6})Z',r['campaign'])
        r['date']=f'{match[1][:4]}-{match[1][4:6]}-{match[1][6:8]} {match[2][:2]}:{match[2][2:4]}:{match[2][4:]} UTC' if match else 'Historical predecessor; see original report'
        task=tasks.get(r['task'])
        if task:
            for field,key in [('source_group','source_group'),('context','context_limit'),('input','actual_input_tokens'),('profile','profile')]:
                if r.get(field) is None or field=='source_group':r[field]=task.get(key)
            r['source_provenance']={k:task.get(k) for k in ['source_revision','source_sha256','license','split','prior_evaluation_exposure']}
        elif 'rfc8259' in r['task']:r['source_group']='RFC8259-JSON';r['context']=32768
        elif 'repository' in r['task'] or r['campaign'].startswith(('q4-live-oracle','q4-oracle-decomposition','q4-residency-v2')):r['source_group']='historical-repository-source'
        if r.get('raw_dir'):
            cfg_path=Path(r['raw_dir'])/'config.json';cfg=load(cfg_path);extra_sources[str(cfg_path)]=reference(cfg_path)
            args=cfg.get('args',[])
            for flag in ['--max-context','--max-total-context']:
                if flag in args:r['context']=int(args[args.index(flag)+1])
            r['configuration_sha256']=digest(cfg_path)
            r['startup_options']={k:args[args.index(k)+1] for k in ['--expert-profile','--layer-split','--gpu-layers','--kv','--kv-resident','--expert-cache'] if k in args and args.index(k)+1<len(args)}
            r['startup_inactive_options']=[k for k in ['--peer-device','--expert-cache-per-layer','--expert-profile-save'] if k not in args]
            r['source_sha']=cfg.get('source_sha',r.get('source_sha'));r['binary_sha256']=cfg.get('binary_sha256',r.get('binary_sha256'))
        elif r.get('trace_prefix'):
            folder=Path(r['trace_prefix']).parent
            valid=folder/'trace-validation.json'
            if valid.exists():
                v=load(valid);extra_sources[str(valid)]=reference(valid)
                r['output']=v.get('output_tokens',r.get('output'))
            rf=folder/'results.json'
            if rf.exists():
                v=load(rf);rows=v.get('runs',[]) if isinstance(v,dict) else []
                if rows:
                    r['input']=rows[0].get('actual_input_tokens',r.get('input'));r['output']=rows[0].get('actual_output_tokens',rows[0].get('output_tokens',r.get('output')))
                extra_sources[str(rf)]=reference(rf)
        identity=CAMPAIGNS/r['campaign']/'configs/runtime-identity.json'
        if identity.exists():
            q=load(identity);extra_sources[str(identity)]=reference(identity)
            # Per-request binary/version wins; old Phase 4 v1 must not be relabeled v2.
            if not r.get('source_sha'):r['source_sha']=q.get('source_sha')
            if not r.get('binary_sha256'):r['binary_sha256']=q.get('binary_sha256')
        r['workload_semantics']='retained simulated residency, fixed recorded demand' if r['kind']=='SIMULATION' else 'full-work fixed replay' if r.get('tape_path') and r['policy']!='NATURAL_CURRENT' else 'natural native observation / aggregate measurement'
    save(REVIEW/'site/data/catalog.json',catalog)
    inputs=load(REVIEW/'input-manifest.json');src={x['path']:x for x in inputs['sources']}
    src.update(source_paths);src.update(extra_sources)
    for p in load(work_root()/'derived/browser-v1/predictor.json')['provenance']:src[p['path']]=p
    inputs['sources']=list(src.values());save(REVIEW/'input-manifest.json',inputs)
    save(REVIEW/'results/metadata-enrichment.json',{'state':'PASS','selection_changed':False,'sources':len(src),
         'rule':'Task manifest and exact per-request args enrich missing fields. Per-request version identities precede campaign final binary.'})

if __name__=='__main__':main()
