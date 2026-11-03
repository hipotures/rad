"""Audit complete final pairings and summarize the unchanged frozen endpoint across four parents."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import sqlite3

from . import patch, registry
from . import pd2_report as R
from .bootstrap_prepare import TOPIC
from .tensors import sha256_array


def state_identity(pid):
    names=sorted({t['name'] for p in patch.lineage(pid) for t in patch.load_patch(p)['tensors']})
    state=patch.materialize(patch.load_patch(pid)['gold_id'],pid,names)
    gold=registry.manifest(patch.load_patch(pid)['gold_id'])
    pairs=[(n,sha256_array(state[n][1])) for n in names if sha256_array(state[n][1])!=gold['tensors'][n]['sha256']]
    return hashlib.sha256(json.dumps(pairs).encode()).hexdigest()


def read_rows(raw, split, editors, expected_instances):
    out=[]
    for eid in editors:
        path=raw/(eid+'__'+split+'.jsonl')
        rows=[json.loads(line) for line in path.read_text().splitlines()]
        keys={(r['id'],r['tier'],r['sample']) for r in rows}
        if len(rows)!=expected_instances*16 or len(keys)!=len(rows):
            raise ValueError('incomplete or duplicated final sample grid')
        if any(r['editor_id']!=eid or r['tier'] not in ('T0','T1','T2','T2P') or r['sample'] not in range(4) for r in rows):
            raise ValueError('unexpected editor/tier/sample identity')
        if out:
            refkeys={(r['id'],r['tier'],r['sample']) for r in out if r['editor_id']==editors[0]}
            if keys!=refkeys:raise ValueError('unpaired candidate grid')
        out+=rows
    return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);a=ap.parse_args();root=Path(a.root)
    plan=json.loads((root/'final-plan.json').read_text())
    if not (root/'final-complete.json').exists():raise RuntimeError('final workers not complete')
    raw=TOPIC/'work/raw'/plan['campaign']
    protocol=json.loads((TOPIC/'configs/phaseD_v2/protocol_v2_frozen.json').read_text());cells=set(protocol['primary_cells'])
    parents=list(plan['sealed']);available=[sid for sid,pid in plan['sealed'].items() if pid!='FAILURE']
    result={'benchmark':'phaseD-v2','parent_model':'gpt-6.1-sol','parent_effort':'medium',
            'primary_hypothesis_family':parents,'splits':{},'lineages':{},'parent_resources':{},'worker_audits':{}}
    for sid,pid in plan['sealed'].items():
        result['lineages'][sid]={'patch_id':pid}
        if pid!='FAILURE':
            rec=patch.load_patch(pid)
            result['lineages'][sid].update(lineage=patch.lineage(pid),state_sha256=state_identity(pid),
                          changed_entries_in_last_patch=rec['changed_entries_total'],delta_l2_last_patch=rec['delta_l2_total'])
    result['distinct_final_states']=len({r['state_sha256'] for r in result['lineages'].values() if 'state_sha256' in r})
    editors=[e['editor_id'] for e in plan['editors']]
    for split in plan['splits']:
        rows=read_rows(raw,split,editors,protocol['manifests'][split]['n'])
        primary_rows=[r for r in rows if r['editor_id'] in ['E0']+available]
        endpoints=R.primary_endpoint(primary_rows,'E0',cells)
        # Failed sessions remain hypotheses (p=1); do not reduce the correction family after failure.
        pvals={sid:endpoints.get(sid,{}).get('p_boot',1.0) for sid in parents}
        adjusted=R.holm(pvals)
        for sid in parents:
            endpoints.setdefault(sid,{'status':'parent failure','mean_diff':None,'ci95':[None,None]})
            endpoints[sid]['p_holm']=adjusted[sid]
            endpoints[sid]['positive_significant']=bool(endpoints[sid]['mean_diff'] is not None and
                       endpoints[sid]['mean_diff']>0 and adjusted[sid]<0.05)
        stats={}
        for eid in editors:
            er=[r for r in rows if r['editor_id']==eid]
            stats[eid]={'all':R.cell_stats(er),'primary':R.cell_stats([r for r in er if f"{r['family']}/{r['tier']}" in cells]),
                        'cells':{cell:R.cell_stats([r for r in er if f"{r['family']}/{r['tier']}"==cell])
                                 for cell in sorted({f"{r['family']}/{r['tier']}" for r in er})}}
            summary=json.loads((raw/(eid+'__'+split+'.summary.json')).read_text())
            stats[eid]['resources']={'generation':summary['gen'],'transition':summary['transition'],'score_s':summary['score_s']}
        contrasts={}
        for sid in available:
            arows=[r for r in rows if r['editor_id']==sid and f"{r['family']}/{r['tier']}" in cells]
            ref=[r for r in rows if r['editor_id']=='E0' and f"{r['family']}/{r['tier']}" in cells]
            valid={(r['id'],r['tier'],r['sample']) for r in ref if r['valid']}
            jointly_valid=[r for r in arows if r['valid'] and (r['id'],r['tier'],r['sample']) in valid]
            matched=plan['matched_controls'][sid]['editor_id']
            null=[r for r in rows if r['editor_id']==matched and f"{r['family']}/{r['tier']}" in cells]
            contrasts[sid]={'jointly_valid_vs_E0':R.paired(jointly_valid,ref,with_p=True),
                            'vs_matched_random':R.paired(arows,null,with_p=True),
                            'note':'Secondary contrasts; no additional gate threshold is asserted.'}
        result['splits'][split]={'verified_sample_grid':True,'instances_per_editor':protocol['manifests'][split]['n'],
                                 'primary_endpoint':endpoints,'editors':stats,'secondary_contrasts':contrasts}
    with sqlite3.connect(root/'ledger.sqlite') as db:
        result['tool_counts']={sid:json.loads(counts) for sid,counts in db.execute('SELECT id,counts FROM sessions')}
    for sid in parents:
        rows=[json.loads(s) for s in (root/'logs'/f'{sid}-parent.jsonl').read_text().splitlines()]
        usage=[r['usage'] for r in rows if r.get('type')=='turn.completed']
        threads=[r['thread_id'] for r in rows if r.get('type')=='thread.started']
        result['parent_resources'][sid]={'thread_ids':threads,'usage_records':usage}
    for campaign in ('20261103T-phaseD-bootstrap-execution',plan['campaign']):
        records=[json.loads(p.read_text()) for p in (TOPIC/'work/raw'/campaign).glob('worker-*.json')]
        if len(records)!=2 or not all(r['final_audit']['ok'] for r in records):raise RuntimeError('worker final Gold audit missing or failed')
        result['worker_audits'][campaign]=[{'worker':r['worker'],'audit':r['final_audit'],'final_memory':r['final_memory'],
                                            'startup_s':r['startup_s'],'wall_s':r['wall_s']} for r in records]
    result['frozen_primary_positive']=any(v['positive_significant'] for v in result['splits']['test']['primary_endpoint'].values())
    out=TOPIC/'runs/20261103T-phaseD-bootstrap-execution/results'
    (out/'final_analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'distinct_states':result['distinct_final_states'],'test_primary':result['splits']['test']['primary_endpoint']},indent=2))


if __name__=='__main__':main()
