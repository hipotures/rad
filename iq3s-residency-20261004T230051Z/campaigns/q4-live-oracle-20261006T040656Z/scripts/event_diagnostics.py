"""Derived host-timeline diagnostics; timers are overlapping observations, not additive model stages."""
from pathlib import Path
import json,argparse,numpy as np
from inspect_oracle import L,E,N
from tape import Tape
C=Path(__file__).resolve().parents[1]
def stat(x):
 x=np.asarray(x,dtype=float);return dict(zip(['count','sum_ms','median_us','p95_us','max_us'],[len(x),float(x.sum())/1e6,float(np.median(x))/1e3,float(np.quantile(x,.95))/1e3,float(x.max())/1e3])) if len(x) else None
def analyze(label,tape):
 p=C/'raw'/label;t=Tape(tape);a=np.fromfile(p/'raw/oracle-layers.bin',L);e=np.fromfile(p/'raw/oracle-admissions.bin',E)
 mask=np.arange(40)[None,:]<a['n'][:,None];cpu=np.any((a['path']==-1)&mask,axis=1);mapped=np.any((a['path']==1)&mask,axis=1)
 dt=(a['cpu_end']-a['plan_end']).astype(np.int64)
 out={'label':label,'host_quant_group_compute_completion_span':{'CPU_positive':stat(dt[cpu]),'all_no_CPU':stat(dt[~cpu]),'mapped_positive':stat(dt[mapped])},'scope_caveat':'CPU span includes activation quantization/job construction/native CPU completion. It is not an isolated wait, and overlaps GPU work. No CPU/mapped/GPU timers are summed.', 'future_lead':{},'copy_lifetimes':{}}
 pub=e[e['publish_ns']>0]
 if len(e):
  targets=a['begin'][np.clip(e['target'],0,len(a)-1)];out['future_lead']={'logical_invocations':{'min':int(np.min(e['target']-e['trigger'])),'median':float(np.median(e['target']-e['trigger'])),'p95':float(np.quantile(e['target']-e['trigger'],.95)),'max':int(np.max(e['target']-e['trigger']))},'issue_to_actual_target':stat(targets.astype(np.int64)-e['issue_ns'].astype(np.int64)),'queue_before_staging':stat(e['stage_begin'].astype(np.int64)-e['issue_ns'].astype(np.int64))}
  out['copy_lifetimes']={'published':len(pub),'ready_publications':int(np.count_nonzero(pub['published_at']<=pub['target'])),'late_publications':int(np.count_nonzero(pub['published_at']>pub['target'])),'never_used':int(np.count_nonzero(e['uses']==0)),'one_use':int(np.count_nonzero(e['uses']==1)),'multiple_uses':int(np.count_nonzero(e['uses']>1)),'max_uses':int(e['uses'].max()),'total_uses':int(e['uses'].sum()),'victim_absent':int(e['victim_uses'].sum()),'per_class':{str(b):{'issued':int(np.count_nonzero(e['bytes']==b)),'bytes':int(e['bytes'][e['bytes']==b].sum()),'uses':int(e['uses'][e['bytes']==b].sum()),'victim_absent':int(e['victim_uses'][e['bytes']==b].sum())} for b in [3072000,3584000,3993600]},'tail_censoring':'No recorded guard tail. Future victim-use after tape end is unknown in reality but full oracle uses known finite ending; no global upper bound.'}
 (C/'analysis'/f'{label}-event-diagnostics.json').write_text(json.dumps(out,indent=2)+'\n');return out
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('label');a.add_argument('tape');v=a.parse_args();print(json.dumps(analyze(v.label,v.tape),indent=2))
