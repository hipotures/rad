#!/usr/bin/env python3
"""Export exact important plotted data/specs from deterministic deep links."""
import argparse,datetime,json,time
from pathlib import Path
from playwright.sync_api import sync_playwright
from common import REVIEW,load,save

def main(base,out):
 out=out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();records=[]
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/snap/bin/chromium',args=['--disable-gpu','--no-sandbox']);page=b.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  for row in load(REVIEW/'results/curated-views.json'):
   page.goto(base.rstrip('/')+row['path'],wait_until='networkidle');page.wait_for_function('window.atlas&&!atlas.busy',timeout=90000)
   specs=page.evaluate('''()=>atlas.charts.filter(c=>c.el.getBoundingClientRect().height>0).map(c=>({title:c.el.parentElement.querySelector('h3').innerText,data:c.el.data,layout:c.el.layout,run:atlas.A.id,compare:atlas.B?.id,range:atlas.range,source_summary:atlas.A.summary_url,source_layer:atlas.A.layer_url.replace('{layer}',document.querySelector('#layer').value)}))''')
   record={'name':row['name'],'url':page.url,'selected_filters':row['selected_filters'],'representation':'Complete exact visible Plotly data and layout; not independent latency measurements. Generation/service asset provenance remains in each source summary.','plots':specs}
   save(out/(row['name']+'.json'),record);records.append({'name':row['name'],'plots':len(specs),'bytes':(out/(row['name']+'.json')).stat().st_size})
   print('[PLOT EXPORT]',row['name'],len(specs),'plots','elapsed',round(time.monotonic()-start),'s',flush=True)
  assert not errors,errors;b.close()
 save(out/'export-manifest.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'new_gpu_runs':0,'elapsed_s':time.monotonic()-start})
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--url',default='http://192.168.100.207:8765');a.add_argument('--output',type=Path,required=True);x=a.parse_args();main(x.url,x.output)
