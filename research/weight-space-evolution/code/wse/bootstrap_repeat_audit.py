"""Describe dev repeat variability without changing frozen sampling, scores or candidate selection."""
import collections
import json
from pathlib import Path

from .bootstrap_prepare import TOPIC


def audit(raw):
    groups=collections.defaultdict(list)
    for p in sorted(Path(raw).glob('*__dev.summary.json')):
        rec=json.loads(p.read_text())
        if 'error' not in rec:groups[rec['editor_id']].append(rec)
    comparisons=[]
    for eid,recs in groups.items():
        if len(recs)<2:continue
        first=recs[0]
        def rows(rec):
            return {(r['id'],r['tier'],r['sample']):(r['text'],r.get('final_text'),r['recovery'])
                    for r in (json.loads(s) for s in (Path(raw)/(rec['job_id']+'.jsonl')).read_text().splitlines())}
        ref=rows(first)
        for rec in recs[1:]:
            other=rows(rec)
            if set(ref)!=set(other):raise ValueError('repeat grids differ')
            comparisons.append({'editor_id':eid,'first_job':first['job_id'],'repeat_job':rec['job_id'],
                'same_gpu':rec['worker']==first['worker'],'first_worker':first['worker'],'repeat_worker':rec['worker'],
                'samples':len(ref),'identical_texts':sum(ref[k][:2]==other[k][:2] for k in ref),
                'identical_scores':sum(ref[k][2]==other[k][2] for k in ref),
                'mean_recovery_repeat_minus_first':sum(other[k][2]-ref[k][2] for k in ref)/len(ref)})
    return {'role':'observed dev repeat diagnostic, not a new benchmark or a parent feedback channel',
            'comparisons':comparisons}


def main():
    raw=TOPIC/'work/raw/20261103T-phaseD-bootstrap-execution'
    result=audit(raw)
    out=TOPIC/'runs/20261103T-phaseD-bootstrap-execution/results/dev_repeat_audit.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
