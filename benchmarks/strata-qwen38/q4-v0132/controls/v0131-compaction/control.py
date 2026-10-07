"""Read-only old-runtime comparison required by upgrade table, never oldcampaign writes."""
import run as r,workloads as w,json,time
R=r.ROOT;NEW=R.parents[1];done=R/'raw/control-done.json'
assert json.loads((NEW/'raw/phase-compaction-terminal.json').read_text())['status']=='COMPLETE'
assert not done.exists(),'Already complete: read existing evidence'
assert not list((R/'raw').glob('COMPACTION-v0131-control-*-request.json')),'Partial attempt must be preserved before restart'
label='COMPACTION-v0131-control';cfg=json.loads((R/'configs'/f'{label}.json').read_text());rows=[]
with r.Session(label,cfg) as session:
 smoke=session.request(8000,64,'smoke','smoke');assert smoke['text'].strip() and smoke['draft_tokens']>0
 for target in [127000,250000]:
  source=NEW/'raw'/f'COMPACTION-FINAL-v0132-{target}-request.json';payload=json.loads(source.read_text());new=json.loads((NEW/'raw'/f'COMPACTION-FINAL-v0132-{target}.json').read_text());assert session.run.count(payload['messages'])==new['actual_prompt_tokens']
  rec=w.request(session,payload['messages'],payload['max_tokens'],str(target),kind='compaction',exact_payload=payload);assert rec['status']=='OK' and rec['generated_tokens']<=4096
  rec['comparison_request_source']=str(source);r.c.save(R/'raw'/f'{label}-{target}.json',rec);rows.append(rec)
r.c.save(done,{'status':'COMPLETE','runs':rows,'scope':'New upgrade comparison namespace only; immutableoldbinary/weights. Two exactnewcompactionpayloads with oldbest config, NOT_CONTROLLED_A_B if configs differ. Originalq4-max-sweep campaign untouched and frozen.'})
(NEW/'raw/phase-compaction-old-control-terminal.json').write_text(json.dumps({'status':'COMPLETE','ended':time.time(),'directory':str(R)}))
