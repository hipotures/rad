"""Regenerate paired medians, exact small-sample tests and CSVs from raw arms.

The A/B pair is the sole inferential unit; telemetry/tokens never inflate N.
"""
import argparse,collections,csv,hashlib,itertools,json,math,pathlib,random,statistics
C=pathlib.Path(__file__).resolve().parents[1]
def load(p):return json.loads(pathlib.Path(p).read_text())
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def quantile(xs,q):
 s=sorted(xs);i=(len(s)-1)*q;a=int(i);b=min(a+1,len(s)-1);return s[a]+(s[b]-s[a])*(i-a)
def distribution(xs):
 return {'n':len(xs),'median':statistics.median(xs),'min':min(xs),'max':max(xs),'q25':quantile(xs,.25),'q75':quantile(xs,.75),'IQR':quantile(xs,.75)-quantile(xs,.25)} if xs else None
def inference(xs,seed):
 logs=[math.log(x) for x in xs];n=len(logs);observed=abs(sum(logs)/n)
 outcomes=[abs(sum(s*v for s,v in zip(sign,logs))/n) for sign in itertools.product([-1,1],repeat=n)]
 permutation=sum(x>=observed-1e-14 for x in outcomes)/len(outcomes)
 pos=sum(x>1 for x in xs);neg=sum(x<1 for x in xs);nt=pos+neg
 sign_p=min(1,2*sum(math.comb(nt,k) for k in range(min(pos,neg)+1))/2**nt) if nt else 1
 rng=random.Random(seed);boot=[statistics.median(rng.choices(xs,k=n)) for _ in range(20000)]
 return {'transformation':'log(B/A)','statistic':'abs(mean(log(B/A)))','statistic_observed':observed,'two_sided_exact_signflip_p':permutation,'permutations':2**n,'sign_B_gt_A':pos,'sign_B_lt_A':neg,'ties':n-pos-neg,'two_sided_exact_sign_p':sign_p,'bootstrap_median_ratio_percentile95':[quantile(boot,.025),quantile(boot,.975)],'bootstrap_seed':seed,'bootstrap_resamples':20000,'assumptions':'Sign-flip requires exchangeable paired log differences under null; counterbalanced order reduces but cannot remove drift. Fixed repeated workload variants limit workload generality. Small sample intervals are descriptive support, not universal default safety.'}
def balanced_design_test(pairs):
 # Supplement the declared unrestricted sign-flip reference with assignments
 # that honor sixAB/sixBA, twoAB/twoBA per family, and first10 fiveAB/fiveBA.
 if len({p['point']['family'] for p in pairs})<3:return None
 families=['code','math','prose']*4
 groups=[[i for i,f in enumerate(families) if f==family] for family in ['code','math','prose']]
 assignments=[]
 for cs in itertools.product(*(itertools.combinations(g,2) for g in groups)):
  ab=set(itertools.chain.from_iterable(cs))
  if len(ab & set(range(10)))==5:assignments.append(ab)
 assert len(assignments)==108
 observed=abs(statistics.mean(math.log(p['B']['TG']/p['A']['TG']) for p in pairs))
 diffs=[(p['point']['pair']-1,math.log(p['B']['TG']/p['A']['TG'])*(1 if p['point']['order']=='AB' else -1)) for p in pairs]
 null=[abs(statistics.mean(d*(1 if index in ab else -1) for index,d in diffs)) for ab in assignments]
 return {'assignments':len(assignments),'two_sided_p':sum(v>=observed-1e-14 for v in null)/len(null),'statistic':observed,'constraints':'Full12 sixAB/sixBA, eachfamily2AB/2BA, prefix10 fiveAB/fiveBA. Observed chronological second/first logTG held fixed.','assumptions':'Sharp no-spin-effect null, exchangeable randomized order subject to declared constraints, no unmodeled cross-pair carryover. Fresh processes reduce cache-history carryover but OS/thermal/host effects can remain. Secondary design-respecting support; medians primary.'}
def csvwrite(path,rows):
 if not rows:path.write_text('');return
 fields=list(dict.fromkeys(k for r in rows for k in r))
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fields);w.writeheader();w.writerows(rows)
metrics={'TG':'TG','wall':'wall_s','CPU':'decode_cpu_pct','PP':'PP','TTFT':'TTFT_s','process_CPU':'decode_process_cpu_vm_pct'}
def aggregate(pairs,seed):
 out={'valid_pairs':len(pairs),'identical_outputs':sum(p['audit']['output_ids_identical'] for p in pairs),'arm':{},'paired':{},'orders':{},'routing':{}}
 for name,key in metrics.items():
  out['arm'][name]={arm:distribution([p[arm][key] for p in pairs]) for arm in ['A','B']}
  xs=[p['B'][key]/p['A'][key] for p in pairs];out['paired'][name]={**distribution(xs),'B_higher':sum(x>1 for x in xs),'B_lower':sum(x<1 for x in xs),'ties':sum(x==1 for x in xs),'ratio_of_arm_medians':out['arm'][name]['B']['median']/out['arm'][name]['A']['median']}
  if name=='TG':out['paired'][name]['inference']=inference(xs,seed)
 for order in ['AB','BA']:
  ps=[p for p in pairs if p['point']['order']==order]
  out['orders'][order]={'n':len(ps),'TG_ratio':distribution([p['B']['TG']/p['A']['TG'] for p in ps]),'wall_ratio':distribution([p['B']['wall_s']/p['A']['wall_s'] for p in ps])}
 out['balanced_design_randomization']=balanced_design_test(pairs)
 for key in ['local_pct','cpu_pct','mapped_pct','local_vram_entries','cpu_fallback_entries','mapped_nonlocal_gpu_entries','all_routed_entries','mtp_acceptance_pct','mtp_accepted_per_window','cpu_experts_per_layer_window','cpu_entries_per_layer_window','CPU_completion_ms_per_window','pool_plus_plan_ms_per_window','decode_cpu_steal_pct','decode_s','pp_s','decode_process_cpu_cores_pct']:
  out['routing'][key]={arm:distribution([p[arm][key] for p in pairs if p[arm].get(key) is not None]) for arm in ['A','B']}
 return out

def main():
 global C
 ap=argparse.ArgumentParser();ap.add_argument('--require-complete',action='store_true');ap.add_argument('--root',type=pathlib.Path,help='Analyze an isolated replay instead of the original');a=ap.parse_args()
 if a.root:C=a.root.resolve()
 orders=load(C/'orders/all.json');ledger=load(C/'invalid-pair-ledger.json');invalidpaths={x['path'] for x in ledger};rows=[];arms=[];summaries=[];familyrows=[];allpairs=[];cells={};baseline_repeats=[]
 for ci,cell in enumerate(orders):
  pairs=[]
  for path in sorted((C/'raw'/cell).glob('*/pair.json')):
   pj=load(path);assert pj['state']=='VALID';pp=path.parent;assert str(pp) not in invalidpaths,'INVALID INCLUDED'
   point=load(pp/'protocol.json');audit=load(pp/'audit.json');assert audit['state']=='PASS';assert set(audit['environment_diff'])=={'STRATA_POOL_SPIN_US'}
   A=load(pp/'A/raw/measured.json');B=load(pp/'B/raw/measured.json')
   assert A['state']==B['state']=='VALID';assert A['actual_output_tokens']==B['actual_output_tokens']==4096;assert A['input_ids_sha256']==B['input_ids_sha256'];assert A['context']==B['context'];assert A['regime']==B['regime']
   for arm,r in [('A',A),('B',B)]:
    ids=pathlib.Path(r['output_ids_path']);assert hashlib.sha256(ids.read_bytes()).hexdigest()==r['output_ids_sha256'],'OUTPUT FILE HASH'
    assert hashlib.sha256(pathlib.Path(r['input_ids_path']).read_bytes()).hexdigest()==r['input_ids_sha256'],'INPUT FILE HASH'
    cleanup=load(pp/arm/'cleanup.json');assert not cleanup['children_alive'] and not cleanup['gpu_jobs'] and not cleanup['parent_alive']
   p={'point':point,'audit':audit,'A':A,'B':B,'path':str(pp),'cell':cell};pairs.append(p);allpairs.append(p)
   row={'cell':cell,'regime':A['regime'],'context':A['context'],'pair':point['pair'],'order':point['order'],'family':point['family'],'payload_variant':point['payload_variant'],'replacement':point.get('replacement',False),'input_ids_sha256':A['input_ids_sha256'],'output_ids_identical':audit['output_ids_identical'],'first_divergence_zero_based':audit['first_output_divergence_zero_based'],'path':str(pp)}
   for name,key in metrics.items():
    row[name+'_A']=A[key];row[name+'_B']=B[key];row[name+'_ratio_B_over_A']=B[key]/A[key];row[name+'_paired_delta_pct']=100*(B[key]/A[key]-1)
   for key in ['started_monotonic','decode_s','pp_s','actual_input_tokens','actual_output_tokens','finish_reason','mtp_proposed','mtp_accepted','verify_windows','mtp_acceptance_pct','mtp_accepted_per_window','local_vram_entries','cpu_fallback_entries','mapped_nonlocal_gpu_entries','all_routed_entries','local_pct','cpu_pct','mapped_pct','cpu_experts_per_layer_window','cpu_entries_per_layer_window','CPU_completion_ms_per_window','pool_plus_plan_ms_per_window','decode_cpu_steal_pct','output_ids_sha256','decode_process_cpu_cores_pct']:
    row[key+'_A']=A.get(key);row[key+'_B']=B.get(key)
   for arm,r in [('A',A),('B',B)]:
    ar={k:v for k,v in r.items() if isinstance(v,(str,int,float,bool)) or v is None};ar.update(cell=cell,pair=point['pair'],family=point['family'],order=point['order'],path=str(pp/arm))
    native_manifest=load(pp/arm/'raw/native-manifest.json')
    ar.update(binary_sha256=native_manifest['binary_sha256'],source_sha=native_manifest['source_sha'],model_manifest_sha256=native_manifest['model_manifest_sha256'],layer_split=native_manifest['resolved']['--layer-split'],pcie_fraction=native_manifest['resolved']['--pcie-frac'],pool_workers=native_manifest['resolved']['--pool-workers'],MTP_spec=native_manifest['resolved']['--spec'],MTP_spec_min_p=native_manifest['resolved']['--spec-min-p'],KV=native_manifest['resolved']['--kv'],KV_resident_requested=native_manifest['resolved']['--kv-resident'],KV_resident_effective=native_manifest['capacity']['kv_resident'],expert_slots=native_manifest['capacity']['expert_slots'],physical_expert_capacity_pct=100*native_manifest['capacity']['expert_slots']/24576,affinity=json.dumps(native_manifest['affinity']),spin_environment='ABSENT' if arm=='A' else '100')
    for phase in ['prefill','decode']:
     for gpu,v in r['telemetry'][phase]['gpus'].items():
      for key,val in v.items():
       if isinstance(val,(str,int,float)) or val is None:ar[f'{phase}_gpu{gpu}_{key}']=val
     for key in ['samples','ram_mean_gib','native_rss_mean_gib','swap_max_bytes']:ar[f'{phase}_{key}']=r['telemetry'][phase].get(key)
    arms.append(ar)
   rows.append(row)
  assert len(pairs)<=12
  if a.require_complete:assert len(pairs)>=10,(cell,len(pairs),'MINIMUM10')
  if not pairs:continue
  s=aggregate(pairs,921100+ci);cells[cell]=s;s['regime']=pairs[0]['A']['regime'];s['context']=pairs[0]['A']['context'];s['families']={}
  primary={'Regime':s['regime'],'Context':s['context'],'Valid pairs':len(pairs),'A default TG median':s['arm']['TG']['A']['median'],'B 100us TG median':s['arm']['TG']['B']['median'],'Median paired TG delta pct':100*(s['paired']['TG']['median']-1),'Median paired wall delta pct':100*(s['paired']['wall']['median']-1),'CPU A':s['arm']['CPU']['A']['median'],'CPU B':s['arm']['CPU']['B']['median'],'Median paired CPU delta pct':100*(s['paired']['CPU']['median']-1),'B wins':s['paired']['TG']['B_higher'],'Identical outputs':s['identical_outputs']}
  for name,v in s['paired'].items():
   for key in ['min','max','q25','q75','IQR','ratio_of_arm_medians']:primary[f'{name}_paired_{key}']=v[key]
  for name,v in s['arm'].items():
   for arm,d in v.items():
    for key in ['median','min','max','q25','q75','IQR']:primary[f'{name}_{arm}_{key}']=d[key]
  primary.update(s['paired']['TG']['inference']);summaries.append(primary)
  if s['balanced_design_randomization']:primary['balanced_design_randomization_p']=s['balanced_design_randomization']['two_sided_p']
  for fi,family in enumerate(['code','math','prose']):
   ps=[p for p in pairs if p['point']['family']==family]
   if not ps:continue
   fs=aggregate(ps,921200+ci*3+fi);s['families'][family]=fs
   familyrows.append({'Regime':s['regime'],'Context':s['context'],'Workload':family,'Pairs':len(ps),'TG paired median delta pct':100*(fs['paired']['TG']['median']-1),'Wall paired median delta pct':100*(fs['paired']['wall']['median']-1),'CPU paired median delta pct':100*(fs['paired']['CPU']['median']-1),'Identical outputs':fs['identical_outputs'],'B wins':fs['paired']['TG']['B_higher']})
   variants=collections.defaultdict(list)
   for p in ps:variants[p['point']['payload_variant']].append(p)
   for variant,vs in variants.items():
    if len(vs)<2:continue
    for arm in ['A','B']:
     for p,q in itertools.combinations(vs,2):
      xs=load(p[arm]['output_ids_path']);ys=load(q[arm]['output_ids_path'])
      baseline_repeats.append({'cell':cell,'family':family,'variant':variant,'arm':arm,'pair1':p['point']['pair'],'pair2':q['point']['pair'],'identical':xs==ys,'first_divergence_zero_based':next((i for i,(x,y) in enumerate(zip(xs,ys)) if x!=y),None)})
 csvwrite(C/'pairs.csv',rows);csvwrite(C/'requests.csv',arms);csvwrite(C/'summary.csv',summaries);csvwrite(C/'families.csv',familyrows)
 result={'campaign':str(C),'protocol':load(C/'protocol.json'),'cells':cells,'baseline_repeat_checks':baseline_repeats,'invalid_pairs':ledger,'valid_pair_total':len(allpairs),'identical_pair_total':sum(p['audit']['output_ids_identical'] for p in allpairs),'trajectory_counter_parity':{k:sum(p['audit']['counters_identical'][k] for p in allpairs) for k in ['mtp_proposed','mtp_accepted','verify_windows','all_routed_entries','local_vram_entries','cpu_fallback_entries','mapped_nonlocal_gpu_entries']},'pairs_are_experimental_units':True}
 # Descriptive demand relationship only; no regression or pseudo-independent N.
 demand=sorted(allpairs,key=lambda p:(p['A']['cpu_experts_per_layer_window']+p['B']['cpu_experts_per_layer_window'])/2)
 bins=[]
 for b in range(4):
  ps=demand[len(demand)*b//4:len(demand)*(b+1)//4]
  if ps:bins.append({'quartile':b+1,'pairs':len(ps),'CPU_experts_per_layer_window':distribution([(p['A']['cpu_experts_per_layer_window']+p['B']['cpu_experts_per_layer_window'])/2 for p in ps]),'TG_ratio':distribution([p['B']['TG']/p['A']['TG'] for p in ps]),'regime_counts':dict(collections.Counter(p['A']['regime'] for p in ps))})
 result['CPU_demand_descriptive_quartiles']={'bins':bins,'limitation':'Model, context and workload covary; pooled descriptive bins do not estimate a causal demand slope. Within-cell/family paired medians remain primary.'}
 save(C/'summary.json',result);save(C/'raw-statistics.json',result)
 lines=['| Regime | Context | Valid pairs | A default TG median | B 100us TG median | Median paired TG Δ | Median paired wall Δ | CPU A | CPU B | Median paired CPU Δ | B wins / pairs |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
 for s in summaries:
  lines.append(f"| {s['Regime']} | {s['Context']} | {s['Valid pairs']} | {s['A default TG median']:.2f} | {s['B 100us TG median']:.2f} | {s['Median paired TG delta pct']:+.2f}% | {s['Median paired wall delta pct']:+.2f}% | {s['CPU A']:.2f}% | {s['CPU B']:.2f}% | {s['Median paired CPU delta pct']:+.2f}% | {s['B wins']}/{s['Valid pairs']} |")
 lines+=['','| Regime | Context | Workload | Pairs | TG paired median Δ | Wall paired median Δ | CPU paired median Δ | Identical outputs |','|---|---:|---|---:|---:|---:|---:|---:|']
 for s in familyrows:lines.append(f"| {s['Regime']} | {s['Context']} | {s['Workload']} | {s['Pairs']} | {s['TG paired median delta pct']:+.2f}% | {s['Wall paired median delta pct']:+.2f}% | {s['CPU paired median delta pct']:+.2f}% | {s['Identical outputs']}/{s['Pairs']} |")
 lines+=['','| Regime | Context | Local % A/B | CPU entries A/B | Mapped entries A/B | MTP % A/B |','|---|---:|---:|---:|---:|---:|']
 for s in cells.values():
  def med(key,fmt):return '/'.join(format(s['routing'][key][arm]['median'],fmt) for arm in ['A','B'])
  lines.append(f"| {s['regime']} | {s['context']} | {med('local_pct','.2f')} | {med('cpu_fallback_entries',',.0f')} | {med('mapped_nonlocal_gpu_entries',',.0f')} | {med('mtp_acceptance_pct','.2f')} |")
 (C/'tables.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps({'valid_pairs':{cell:s['valid_pairs'] for cell,s in cells.items()},'paired_TG_gain_pct':{cell:round(100*(s['paired']['TG']['median']-1),3) for cell,s in cells.items()},'identical_outputs':result['identical_pair_total'],'invalid_pairs':len(ledger)},indent=2))
if __name__=='__main__':main()
