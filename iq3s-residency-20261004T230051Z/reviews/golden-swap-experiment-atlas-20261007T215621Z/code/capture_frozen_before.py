#!/usr/bin/env python3
"""Re-capture the immutable pre-review UI at a smaller device scale for Git."""
import argparse,datetime,hashlib,json,shutil,subprocess,tempfile,threading
from pathlib import Path
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
from common import REVIEW,REPO,save
from serve import Handler

def main(commit,work):
 work=work.resolve();work.mkdir(parents=True,exist_ok=False);prefix=str(REVIEW.relative_to(REPO))
 refs={}
 for name in ['index.html','app.js','styles.css']:
  content=subprocess.check_output(['git','show',commit+':'+prefix+'/site/'+name],cwd=REPO);(work/name).write_bytes(content);refs[name]=hashlib.sha256(content).hexdigest()
 class Frozen(Handler):
  def translate_path(self,path):
   from urllib.parse import urlsplit
   name=urlsplit(path).path
   if name in ['/','/index.html','/app.js','/styles.css']:return str(work/(name.lstrip('/') or 'index.html'))
   return super().translate_path(path)
  def log_message(self,*args):pass
 server=ThreadingHTTPServer(('127.0.0.1',0),Frozen);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 try:
  with sync_playwright() as p:
   b=p.chromium.launch(executable_path='/snap/bin/chromium',args=['--disable-gpu','--no-sandbox']);page=b.new_page(viewport={'width':1440,'height':960},device_scale_factor=.75)
   page.goto(f'http://127.0.0.1:{server.server_address[1]}/',wait_until='networkidle');page.wait_for_function('window.atlas&&!atlas.busy')
   for view in ['residency','churn','startup','expert','oracle','demand','classes','predictor']:
    page.locator('[data-page="'+view+'"]').click();page.wait_for_function('!atlas.busy')
   txt=page.locator('#content').inner_text();audit=json.loads((REVIEW/'results/visual-audit/before/visual-audit.json').read_text());original=next(v for v in audit['pages'] if v['page']=='predictor');sha=hashlib.sha256(txt.encode()).hexdigest();assert sha==original['content_hash'],(sha,original['content_hash'])
   out=REVIEW/'results/visual-audit/before/figures/screenshots/09-auc-outcomes-small-scale.png';page.evaluate('window.scrollTo(0,0)');page.screenshot(path=out,full_page=True);b.close()
  source=REVIEW/'results/visual-audit/before/figures/screenshots/09-auc-outcomes.png';raw=work/'original-full-resolution.png';shutil.copy2(source,raw)
  original['full_resolution_original']={'path':str(raw),'sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'bytes':raw.stat().st_size,'recovery':'Local original; same UI can be recaptured from frozen Git source. A complete full-page smaller-device-scale PNG is published.'};original['screenshot']=str(out.relative_to(REVIEW));original['device_scale_factor']=.75;save(REVIEW/'results/visual-audit/before/visual-audit.json',audit)
  save(REVIEW/'results/visual-audit/frozen-before-capture.json',{'state':'PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commit':commit,'source_hashes':refs,'content_sha256_exact_original_match':sha,'viewport_css_pixels':[1440,960],'device_scale_factor':.75,'screenshot':str(out.relative_to(REVIEW)),'bytes':out.stat().st_size,'full_resolution_original':original['full_resolution_original'],'new_gpu_runs':0})
  print('FROZEN_BEFORE_CAPTURE_PASS',out.stat().st_size,flush=True)
 finally:server.shutdown();server.server_close()
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--commit',default='3a6f011fa00dd9b0082475fe51b8b4b8d34712ca');a.add_argument('--work',type=Path,required=True);x=a.parse_args();main(x.commit,x.work)
