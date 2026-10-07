"""One pre-reserved repair: use existing incoming count for a matched copy-cost veto."""
import pathlib,shutil,hashlib,time,subprocess
from common import *
# Wait is on a verified live owned leaf, not a ledger or expired observation.
pid=2374538;stat=pathlib.Path('/proc')/str(pid)/'stat';expected=stat.read_text().split()[21] if stat.exists() else None
while stat.exists():
 row=stat.read_text().split()
 if row[21]!=expected or row[2]=='Z':break
 progress(2,'HEARTBEAT awaiting v1 competition before guard repair',owned_cpu_pid=pid);time.sleep(20)
no_gpu();assert (C/'results/offline-competition.json').exists();assert not (C/'results/offline-reserved.json').exists(),'Reserved evaluation already exposed; refuse policy repair'
v1=C/'versions/risk-only-v1';v1.mkdir(parents=True,exist_ok=False)
for f in ['scripts/offline.cpp','scripts/offline_campaign.py','scripts/prepare_offline.py','source/runtime/include/strata/research/q4_oracle.hpp','source/runtime/include/strata/research/q4_victim_model.hpp','results/offline-competition.json','models/selection.json']:
 src=C/f
 if src.exists():dest=v1/f;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
(C/'results/offline').rename(v1/'offline-results');(C/'results/offline').mkdir()
if (C/'models/selection.json').exists():(C/'models/selection.json').unlink()
rows=load(v1/'results/offline-competition.json');diagnosis=[]
for task in [t for t in load(P0/'benchmark-manifest.json')['tasks'] if t['split']=='calibration']:
 rr=[r for r in rows if r['task']==task['task_id']];cur=next(r for r in rr if r['policy']=='current')
 for policy in ['native','recency','logistic','tree']:
  a=next(r for r in rr if r['policy']==policy and r['threshold']==.2);b=next(r for r in rr if r['policy']==policy and r['threshold']==.5);diagnosis.append({'task':task['task_id'],'policy':policy,'nonlocal_ratio':(a['cpu']+a['mapped'])/(cur['cpu']+cur['mapped']),'copy_ratio':a['copied_bytes']/cur['copied_bytes'],'thresholds_same_actions':all(a[k]==b[k] for k in ['cpu','mapped','issued','copied_bytes']),'rejections':a['rejections']})
save(C/'results/guard-diagnosis-v1.json',diagnosis);ledger('Bounded pre-reserved repair justified: risk-only guard was effectively inactive; improved miss counts carried excessive churn/copy traffic. Add common amortization veto using already computed oracle incoming count, predicted victim risk and prefix rate. Native/recency receive matched veto. Incoming E64/order/first-feasible ranking and physical allocator unchanged. Cost proxy assumes40us net gain per demanded entry (not measured exclusive latency); staging25GB/s+H2D13.2GB/s copy cost. No new models or fit; no reserved result viewed.',version='cost-guard-v2',evidence='results/guard-diagnosis-v1.json')
p=C/'source/runtime/include/strata/research/q4_victim_model.hpp';s=p.read_text();needle=' size_t memory_bytes()const'
s=s.replace(needle,''' double expected_entries16(int l,int e,int at,int policy,const float* heat){int k=l*512+e;double wi=at/48.,dt=wi-std::max(0,updated[l]);double rate=policy==1?std::max(0.f,heat[k])*.089168735:.5*(fast[k]*std::exp(-dt/4)/4+slow[k]*std::exp(-dt/64)/64);auto p=risk(l,e,at,policy,heat);return p[2]*std::max(1.,16*rate);}\n'''+needle);p.write_text(s)
p=C/'source/runtime/include/strata/research/q4_oracle.hpp';s=p.read_text();s=s.replace('damage=causal_policy?0:victim_view.count(l*512+v,current+1,utility_end,current);double utility=', 'damage=causal_policy?0:victim_view.count(l*512+v,current+1,utility_end,current);if(causal_policy){double victim_loss=scorer.expected_entries16(l,v,current,causal_policy,heat);double copy_entries=(double(blobs[l])/25e9+double(blobs[l])/13.2e9)/40e-6;if(double(uses)<copy_entries+victim_loss){++scorer.rejections;continue;}}double utility=');p.write_text(s)
(C/'patches/risk-only-to-cost-guard-v2.diff').write_bytes(subprocess.check_output(['git','diff'],cwd=C/'source/runtime'))
