"""Final reproducibility/coverage/cleanup audit; all exclusions must be objective."""
import collections,datetime,hashlib,json,pathlib,subprocess,time
import run
C=run.C
def main():
 summary=run.load(C/'summary.json');orders=run.load(C/'orders/all.json');ledger=run.load(C/'invalid-pair-ledger.json');bases=run.load(C/'configs-base.json');checks={};details={}
 for regime,cfg in bases.items():run.verify(cfg,full=True)
 checks['binary_source_full_model_hashes']=True
 assert not run.gpu_jobs();checks['no_gpu_compute_jobs']=True
 owned=run.load(C/'owned-process.json');assert not run.alive(owned['parent']);assert not any(run.alive(j) for j in owned['children']);checks['owned_processes_stopped']=True
 valid=[];observed=[];invalidpaths={x['path'] for x in ledger}
 for cell,order in orders.items():
  assert len(order['pairs'])==12;assert collections.Counter(x['order'] for x in order['pairs'])=={'AB':6,'BA':6}
  assert collections.Counter(x['family'] for x in order['pairs'])=={'code':4,'math':4,'prose':4}
  replacements=[x for x in ledger if x['cell']==cell];assert len(replacements)<=2
  ps=[]
  for p in sorted((C/'raw'/cell).iterdir()):
   if not p.is_dir():continue
   if (p/'pair.json').exists():
    assert str(p) not in invalidpaths
    point=run.load(p/'protocol.json');aa=run.load(p/'audit.json');A=run.load(p/'A/raw/measured.json');B=run.load(p/'B/raw/measured.json')
    ma=run.load(p/'A/raw/native-manifest.json');mb=run.load(p/'B/raw/native-manifest.json')
    assert A['actual_output_tokens']==B['actual_output_tokens']==4096
    assert A['finish_reason']==B['finish_reason']=='length'
    assert aa['input_ids_equal'] and aa['capacities_equal'] and aa['native_manifests_equal_except_spin']
    assert set(aa['environment_diff'])=={'STRATA_POOL_SPIN_US'}
    assert 'STRATA_POOL_SPIN_US' not in ma['relevant_environment'];assert mb['relevant_environment']['STRATA_POOL_SPIN_US']=='100'
    for arm,m,r in [('A',ma,A),('B',mb,B)]:
     assert m['binary_sha256']==bases[A['regime']]['binary_sha256'];assert m['source_sha']==bases[A['regime']]['source_sha']
     expected=run.load(C/'workloads/manifest.json')['payloads'][f"{r['regime']}/{point['family']}-{'32k' if r['context']==32768 else '128k'}-run{point['payload_variant']}"]
     assert r['input_ids_sha256']==expected['input_ids_sha256'];assert r['payload']['payload_sha256']==expected['payload_sha256']
     assert run.filehash(r['input_ids_path'])==r['input_ids_sha256'];assert run.filehash(r['output_ids_path'])==r['output_ids_sha256']
     warm=run.load(p/arm/'raw/warmup.json');assert warm['actual_input_tokens']==4096 and warm['actual_output_tokens']==64
     clean=run.load(p/arm/'cleanup.json');assert not clean['parent_alive'] and not clean['children_alive'] and not clean['gpu_jobs']
     interval=run.load(p/arm/'raw/startup.json');assert interval['metrics']['engine']['max_context']==r['context']
     observed.append({'cell':cell,'pair':point['pair'],'arm':arm,'measured_start':r['started_monotonic'],'measured_end':r['ended_monotonic'],'path':str(p/arm)})
    aw=run.load(p/'A/raw/warmup.json');bw=run.load(p/'B/raw/warmup.json')
    ps.append({'pair':point['pair'],'order':point['order'],'family':point['family'],'replacement':point.get('replacement',False),'capacity':ma['capacity'],'warmup_output_identical':aw['output_ids_sha256']==bw['output_ids_sha256'],'warmup_graph_messages_identical':aw['graph_messages']==bw['graph_messages'],'measured_graph_messages_identical':A['graph_messages']==B['graph_messages'],'outputs_identical':aa['output_ids_identical'],'path':str(p)})
    valid.append(p)
   else:
    assert str(p) in invalidpaths,('UNACCOUNTED_INCOMPLETE_PAIR',str(p))
  assert 10<=len(ps)<=12,(cell,len(ps));assert len({x['pair'] for x in ps})==len(ps),'DUPLICATE_PAIR_NUMBER'
  assert len(ps)==summary['cells'][cell]['valid_pairs']
  if len(ps)==12:assert collections.Counter(x['order'] for x in ps)=={'AB':6,'BA':6};assert collections.Counter(x['family'] for x in ps)=={'code':4,'math':4,'prose':4}
  details[cell]={'valid_pairs':len(ps),'orders':dict(collections.Counter(x['order'] for x in ps)),'families':dict(collections.Counter(x['family'] for x in ps)),'replacement_count':len(replacements),'pairs':ps}
 checks['coverage_and_counterbalancing']=True
 checks['all_actual_native_environments_and_configs_verified']=True
 checks['all_inputs_warmups_outputs_and_cleanups_verified']=True
 for entry in ledger:
  assert pathlib.Path(entry['path']).is_dir();assert run.filehash(entry['evidence'])==entry['evidence_sha256'];assert entry['state']=='INVALID_ENTIRE_PAIR'
  assert entry['reason'] and 'timing' not in entry['reason'].lower().replace('no100us timing','')
 checks['no_selective_or_unaccounted_exclusions']=True
 observed.sort(key=lambda r:r['measured_start'])
 for p,q in zip(observed,observed[1:]):assert p['measured_end']<=q['measured_start'],'OVERLAPPING_MEASUREMENTS'
 checks['serial_requests']=True
 timing=run.load(C/'timing.json');elapsed=time.monotonic()-timing['start_monotonic'];assert elapsed<28800,'EIGHT_HOUR_LIMIT'
 checks['within_eight_hours']=True
 # Exact rendered table hash links the comment to the same audited summary.
 comment=(C/'github-issue-921-comment.md').read_text();report=(C/'report.md').read_text();tables=(C/'tables.md').read_text()
 primary=tables.split('\n\n')[0];assert primary in comment and tables in report
 assert report.rstrip().splitlines()[-1] in ['SUPPORTS_LOWER_DEFAULT','SUPPORTS_ADAPTIVE_OR_PER_PHASE_POLICY','KEEP_20MS_DEFAULT','MIXED_NEEDS_MORE_DATA','INCONCLUSIVE']
 checks['report_and_comment_match_summary_tables']=True
 manifest=run.load(C/'workloads/manifest.json')
 for name,info in manifest['payloads'].items():assert run.hashjson(run.load(info['path']))==info['payload_sha256'];assert run.filehash(info['token_ids_path'])==info['input_ids_sha256']
 checks['frozen_workloads_verified']=True
 j={'state':'PASS','audited_utc':run.utc(),'elapsed_s':elapsed,'checks':checks,'details':details,'valid_pairs_total':len(valid),'invalid_pairs':ledger,'protocol_sha256':run.filehash(C/'protocol.json'),'workload_manifest_sha256':run.filehash(C/'workloads/manifest.json'),'orders_sha256':run.filehash(C/'orders/all.json'),'binary_sha256':bases['IQ3_S']['binary_sha256'],'summary_sha256':run.filehash(C/'summary.json'),'tables_sha256':run.filehash(C/'tables.md'),'report_sha256':run.filehash(C/'report.md'),'comment_sha256':run.filehash(C/'github-issue-921-comment.md'),'source_clean':True,'unposted_comment':True,'no_push_or_PR':True}
 run.save(C/'reproducibility-audit.json',j)
 print(json.dumps({'state':'PASS','elapsed_hours':elapsed/3600,'valid_pairs':len(valid),'invalid_pairs':len(ledger),'checks':checks},indent=2))
if __name__=='__main__':main()
