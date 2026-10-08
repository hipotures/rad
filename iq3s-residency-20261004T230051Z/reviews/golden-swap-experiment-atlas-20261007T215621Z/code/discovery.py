"""Read-only discovery over published metadata; never expose arbitrary files."""
from functools import lru_cache
import gzip,json
from pathlib import Path
from urllib.parse import urlencode

VIEWS=[('overview','Experiments'),('residency','Residency state'),('slots','Physical VRAM slots'),('churn','Swaps & churn'),('startup','Startup-set decay'),('expert','Expert lifecycle'),('oracle','CURRENT vs future'),('demand','Demand'),('classes','Physical size classes'),('predictor','AUC to outcomes'),('lease','Lease evidence')]
def read_asset(review,url):
 path=(review/url.lstrip('/')).resolve()
 if not path.is_relative_to((review/'evidence').resolve()):raise ValueError('Not a published evidence asset')
 with gzip.open(path,'rt') as f:return json.load(f)

def matches(catalog,run):
 identity=run.get('alignment_id')
 return [r for r in catalog['runs'] if identity and r['id']!=run['id'] and r.get('detail') and r.get('alignment_id')==identity]

def known_equal(a,b,key):
 return a[key]==b[key] if a.get(key) is not None and b.get(key) is not None else None

@lru_cache(maxsize=16)
def interesting(review_path,run_json):
 review=Path(review_path);run=json.loads(run_json)
 if not run.get('summary_url'):return {'run':run['id'],'evidence':'aggregate-only','interesting':[],'missing':'No retained chronological journal selected for this record.'}
 summary=read_asset(review,run['summary_url']);cols=summary['series_columns'];ai=cols.index('admissions');ei=cols.index('evictions')
 layers=sorted([{'layer':i,'gpu':int(i>=(run.get('split') or 24)),'admissions':sum(v[ai] for v in row),'evictions':sum(v[ei] for v in row),'byte_class':summary['initial_quality'][i]['byte_class']} for i,row in enumerate(summary['all_layer_series'])],key=lambda v:-v['admissions'])
 l=layers[0]['layer'];detail=read_asset(review,run['layer_url'].replace('{layer}',str(l)));gs=[dict(zip(detail['columns'],v)) for v in detail['generations']];counts={}
 for g in gs:
  if g['generation']>0 and g['publish_event'] is not None:counts[g['expert']]=counts.get(g['expert'],0)+1
 experts=sorted([{'layer':l,'expert':e,'admissions':n,'url':'/?'+urlencode({'view':'expert','run':run['id'],'layer':l,'expert':e,'focus':1})} for e,n in counts.items()],key=lambda x:-x['admissions'])[:12]
 return {'run':run['id'],'ranking':'Observed admissions only, not latency gain or optimal TTL labels.','layers':layers[:12],'experts':experts,'early_range':{'from':0,'to':min(128,run['windows']),'time':'window'},'windows':run['windows']}

def response(review,catalog,path,query):
 if path=='/api/views':return 200,{'views':[{'id':i,'title':t,'url':'/?view='+i} for i,t in VIEWS],'url_parameters':['view','run','compare','gpu','layer','class','expert','experts','from','to','time','smooth','metric','comparison','focus','snapshot','scope','limit','changed','counts']}
 if path=='/api/runs':
  runs=[r for r in catalog['runs'] if not query.get('task') or r['task']==query['task'][0]]
  keys=['id','campaign','task','policy','windows','detail','alignment_id','kind','evidence_quality','model','context','input','output','future']
  return 200,{'count':len(runs),'runs':[{k:r.get(k) for k in keys} for r in runs]}
 if path in ['/api/matches','/api/interesting']:
  rid=query.get('run',[''])[0];run=next((r for r in catalog['runs'] if r['id']==rid),None)
  if not run:return 404,{'error':'Unknown canonical run ID'}
  if path=='/api/matches':return 200,{'run':rid,'matches':[{'id':r['id'],'policy':r['policy'],'campaign':r['campaign'],'same_campaign':r['campaign']==run['campaign'],'same_binary':known_equal(r,run,'binary_sha256'),'same_attempt':known_equal(r,run,'attempt'),'same_logical_work':True} for r in matches(catalog,run)],'timing_caveat':'Logical equality alone does not establish contemporary paired timing; null means an identity is unavailable.'}
  return 200,interesting(str(review),json.dumps(run,sort_keys=True))
 return 404,{'error':'Unknown discovery endpoint'}
