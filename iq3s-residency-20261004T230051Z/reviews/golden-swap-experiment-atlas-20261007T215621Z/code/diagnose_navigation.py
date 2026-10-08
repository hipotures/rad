"""Reproduce aggregate-only navigation and exercise retained matched replay UI."""
import argparse, json, hashlib, datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
from common import REVIEW as R

def main(url,output):
 out=output.resolve();(out/'figures').mkdir(parents=True,exist_ok=False);rows=[]
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/snap/bin/chromium',args=['--disable-gpu','--no-sandbox'])
  page=b.new_page(viewport={'width':1440,'height':960});errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
  page.goto(url,wait_until='networkidle');page.wait_for_function('window.atlas&&!atlas.busy')
  agg=page.evaluate('atlas.catalog.runs.find(r=>!r.detail).id');page.select_option('#runA',agg);page.wait_for_function('!atlas.busy')
  for name in ['residency','churn','startup','expert','oracle']:
   page.locator('[data-page="'+name+'"]').click();page.wait_for_function('!atlas.busy');page.wait_for_timeout(100)
   text=page.locator('#content').inner_text();fn=out/'figures'/('aggregate-'+name+'.png');page.screenshot(path=fn,full_page=True)
   rows.append({'page':name,'run':agg,'title':page.locator('#content h2').inner_text(),'text_sha256':hashlib.sha256(text.encode()).hexdigest(),'plots':page.locator('.js-plotly-plot').count(),'screenshot':str(fn.relative_to(R))})
  page.select_option('#runA','golden-swap-phase2--code-archive-block1-REPLAY_CURRENT');page.wait_for_function('!atlas.busy');page.locator('#match').click();page.wait_for_function('!atlas.busy');page.wait_for_timeout(100)
  fn=out/'figures'/'matched-current-oracle.png';page.screenshot(path=fn,full_page=True)
  matched=page.evaluate('({page:atlas.page,A:atlas.A.id,B:atlas.B?.id,plots:atlas.charts.length,notice:document.querySelector("#notice").innerText})');b.close()
 (out/'diagnosis.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'aggregate_navigation':rows,'identical_content_on_all_pages':len(set(r['text_sha256'] for r in rows))==1,'matching_button':matched,'exceptions':errs},indent=2)+'\n')
 print(json.dumps({'aggregate':agg,'identical':len(set(r['text_sha256'] for r in rows))==1,'match':matched,'errors':errs}),flush=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--url',default='http://192.168.100.207:8765/');a.add_argument('--output',type=Path,required=True);x=a.parse_args();main(x.url,x.output)
