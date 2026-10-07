"""Diagnostic-only bounded episodes. Preserve natural EOS; never turn them into headline medians."""
import argparse,json,pathlib,time
from lab import ROOT,Session,save,deadline
ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['profiles','episodes']);ap.add_argument('--profiles',nargs='+',choices=['32k','128k'],default=['32k','128k']);ap.add_argument('--attempt',default='v5');ap.add_argument('--port',type=int,default=18132);ap.add_argument('--variant',default='diagnostic-v5');ap.add_argument('--experiment',default='E003-diagnostics');ap.add_argument('--reproduction',action='store_true',help='Explicit later replay after the active campaign deadline');a=ap.parse_args()
if a.reproduction and time.time()<=deadline():raise RuntimeError('Active deadline remains binding; later replay only')
variant=a.variant
if a.mode=='profiles':
 for profile in a.profiles:
  path=ROOT/'experiments'/a.experiment/a.attempt/profile
  if path.exists():raise RuntimeError('Existing attempt; refuse overwrite')
  save(path/'protocol.json',{'variant':variant,'profile':profile,'question':'full demand and publication accounting; diagnostic only','requests':['same saved4096/64 warmup',profile+'-run1'],'attempt':a.attempt,'port':a.port,'measured_repetitions':1,'headline':False})
  with Session(variant,profile,path,port=a.port,budgeted=not a.reproduction) as s:
   warm=s.request('warmup','warmup','warmup')
   if warm['state']!='VALID':raise RuntimeError('Invalid warmup')
   rec=s.request(profile+'-run1','trace-run1','diagnostic')
   save(path/'results.json',{'runs':[rec],'headline':False,'question':'dispatch/timing/accounting diagnosis; free-generation overhead comparison limited by trajectory'})
elif a.mode=='episodes':
 path=ROOT/'experiments'/a.experiment/a.attempt/'episodes'
 if path.exists():raise RuntimeError('Existing attempt; refuse overwrite')
 episodes=['dev-code','dev-math','cal-prose','hold-code','hold-structured','hold-math']
 save(path/'protocol.json',{'profile':'32k','episode_order':episodes,'split':'whole independent task/document; no benchmark nonce variants included','max_output_per_episode':1024,'natural_EOS':'retained and allowed for development traces','fresh_server':True,'warmup':'same64outputsavedinput','no_headline_speed_claim':True})
 with Session(variant,'32k',path,port=a.port,budgeted=not a.reproduction) as s:
  warm=s.request('warmup','warmup','warmup');assert warm['state']=='VALID'
  results=[]
  for n,name in enumerate(episodes,2):
   r=s.request(name,name,'predictor-episode');r['trace_request_number']=n;results.append(r)
   save(path/'results.json',{'runs':results,'headline':False,'whole_episode_split':True})
