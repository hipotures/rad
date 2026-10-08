#!/usr/bin/env python3
"""Fresh-context visual acceptance, deep-link reconstruction and actual UI regression."""
import argparse,datetime,hashlib,io,json,time
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from PIL import Image
from playwright.sync_api import sync_playwright
from common import REVIEW,load,save,digest

TITLE={"churn":"Swap volume","slots":"Physical VRAM slot ownership","residency":"Residency state","startup":"Process startup","oracle":"Current versus future","expert":"Layer","predictor":"AUC","lease":"Observed lifetimes","demand":"Working-set"}
PLOT={"churn":"Churn and required service","slots":"Physical slot turnover","residency":"Residency state","startup":"Startup set survival","oracle":"Aligned layer residency","expert":"Expert admission generations","predictor":"Predictive signal","lease":"Generation lifetime","demand":"expert demand"}

def metrics(png):
 im=Image.open(io.BytesIO(png)).convert('RGB');colored=0;colors=set()
 for r,g,b in im.getdata():
  if max(r,g,b)-min(r,g,b)>35 and max(r,g,b)>110:colored+=1;colors.add((r,g,b))
 return {'width':im.width,'height':im.height,'colored_chart_pixels':colored,'unique_saturated_colors':len(colors),'png_sha256':hashlib.sha256(png).hexdigest()}

def signature(page):
 text=page.evaluate('''()=>JSON.stringify({page:atlas.page,run:atlas.A.id,compare:atlas.B?.id,range:atlas.range,plots:atlas.charts.filter(c=>c.el.getBoundingClientRect().height>0).map(c=>({title:c.el.parentElement.querySelector('h3').innerText,data:c.el.data.map(t=>({name:t.name,type:t.type,x:t.x,y:t.y,z:t.z,base:t.base})),xr:c.el.layout.xaxis.range}))})''')
 return hashlib.sha256(text.encode()).hexdigest()

def ready(page):
 page.wait_for_function('window.atlas&&!atlas.busy',timeout=90000);page.wait_for_timeout(150)
 assert 'failed' not in page.locator('#loading').inner_text().lower(),page.locator('#notice').inner_text()

def main(base,out,publish_curated=False):
 out=out.resolve()
 if out.exists():raise SystemExit('Refuse existing acceptance output namespace')
 out.mkdir(parents=True);shots=(REVIEW/'figures/curated') if publish_curated else out/'figures/curated';shots.mkdir(parents=True,exist_ok=True)
 source_hashes={str(p.relative_to(REVIEW)):digest(p) for p in [REVIEW/'site/app.js',REVIEW/'site/review_views.js',REVIEW/'site/styles.css',REVIEW/'site/index.html']};rows=load(REVIEW/'results/curated-views.json');records=[];start=time.monotonic();errors=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/snap/bin/chromium',headless=True,args=['--disable-gpu','--no-sandbox'])
  for row in rows:
   context=browser.new_context(viewport={'width':1440,'height':1000},device_scale_factor=1);page=context.new_page();err=[];console=[]
   page.on('pageerror',lambda e:err.append(str(e)));page.on('console',lambda m:console.append(m.text) if m.type=='error' else None)
   url=base.rstrip('/')+row['path'];page.goto(url,wait_until='networkidle');ready(page);q=row['selected_filters'];observed=page.evaluate('({page:atlas.page,run:atlas.A.id,compare:atlas.B?.id,range:atlas.range})')
   assert observed['page']==q['view'] and observed['run']==q['run'],observed
   if q.get('compare'):assert observed['compare']==q['compare'],observed
   if 'from' in q and 'to' in q:assert observed['range']==[float(q['from']),float(q['to'])],observed
   for key,node in [('gpu','gpu'),('layer','layer'),('class','byteClass'),('expert','expert'),('time','time'),('smooth','smooth')]:
    if key in q:assert page.input_value('#'+node)==str(q[key]),(key,page.input_value('#'+node),q)
   title=page.locator('#content h2').first.inner_text();assert TITLE[q['view']] in title,(title,q)
   visible=page.locator('#content .js-plotly-plot:visible');titles=visible.evaluate_all("es=>es.map(e=>e.parentElement.querySelector('h3').innerText)");assert any(PLOT[q['view']] in t for t in titles),(q,titles)
   plot_png=visible.first.screenshot();pm=metrics(plot_png);assert pm['colored_chart_pixels']>150 and pm['unique_saturated_colors']>10,pm
   assert not err and not console,(err,console);assert not page.locator('#notice').inner_text(),page.locator('#notice').inner_text()
   sig=signature(page);normalized=page.url;page.evaluate('window.scrollTo(0,0)');page.wait_for_timeout(50);assert page.locator('#content h2').first.bounding_box()['y']>=0;page.screenshot(path=shots/(row['name']+'.png'),full_page=True)
   # A separate empty-cache browser context must reconstruct the same plotted data.
   second=browser.new_context(viewport={'width':1440,'height':1000});fresh=second.new_page();fresh_errors=[];fresh.on('pageerror',lambda e:fresh_errors.append(str(e)));fresh.goto(normalized,wait_until='networkidle');ready(fresh);assert signature(fresh)==sig,(row['name'],'URL round-trip numeric state mismatch');assert not fresh_errors
   records.append({'name':row['name'],'state':'PASS_STRUCTURAL_AND_PIXELS_PENDING_HUMAN_REVIEW','url':url,'normalized_url':normalized,'run':q['run'],'filters':q,'title':title,'plot_titles':titles,'plot_count_visible':visible.count(),'chart_pixels':pm,'screenshot':str((shots/(row['name']+'.png')).relative_to(REVIEW)),'numeric_plot_sha256':sig,'url_roundtrip':'PASS','console_errors':console,'exceptions':err})
   second.close();context.close();save(out/'acceptance.json',{'state':'CAPTURING','curated':records,'elapsed_s':time.monotonic()-start})
   print('[VISUAL ACCEPTANCE]',len(records),'/',len(rows),row['name'],'chart pixels',pm['colored_chart_pixels'],'elapsed',round(time.monotonic()-start),'s',flush=True)
  # Reproduce the operator's aggregate-only path through actual controls.
  context=browser.new_context(viewport={'width':1440,'height':1000});page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(base,wait_until='networkidle');ready(page);page.select_option('#runA','q4-multigpu--32k-layer-split-1');ready(page);agg=[]
  for view in ['residency','churn','startup','expert','oracle']:
   page.locator('[data-page="'+view+'"]').click();ready(page);text=page.locator('#content').inner_text();assert view in parse_qs(urlsplit(page.url).query)['view'];agg.append({'page':view,'title':page.locator('#content h2').first.inner_text(),'content_sha256':hashlib.sha256(text.encode()).hexdigest()});(out/'figures').mkdir(exist_ok=True);page.screenshot(path=out/'figures'/(view+'-aggregate-after.png'))
  assert len({r['content_sha256'] for r in agg})==5
  page.locator('#openDetailed').click();ready(page);assert page.evaluate('!!atlas.A.summary_url');page.locator('[data-page="churn"]').click();ready(page)
  # Actual zoom event changes the URL; a fresh page restores the range.
  page.evaluate("Plotly.relayout(atlas.charts[0].el, {'xaxis.range':[12,36]})");page.wait_for_function('atlas.range?.[0]===12');zoom_url=page.url;assert parse_qs(urlsplit(zoom_url).query)['from']==['12'];assert parse_qs(urlsplit(zoom_url).query)['to']==['36']
  page.reload(wait_until='networkidle');ready(page);assert page.evaluate('atlas.range[0]===12&&atlas.range[1]===36')
  page.locator('#reset').click();ready(page);assert page.evaluate('atlas.range===null')
  assert page.input_value('#timeFrom')=='0' and page.input_value('#timeTo')==str(page.evaluate('atlas.A.windows'))
  assert 'from' not in parse_qs(urlsplit(page.url).query)
  page.locator('#theme').click();ready(page);assert page.locator('html').evaluate('e=>e.classList.contains("light")')
  # Pan and hover operate on the rendered Plotly graph, not just application state.
  page.evaluate("Plotly.relayout(atlas.charts[0].el,{dragmode:'pan'});Plotly.Fx.hover(atlas.charts[0].el,[{curveNumber:0,pointNumber:16}])");assert page.locator('.hoverlayer').count()>0
  for view in ['startup','demand','classes','residency','churn']:page.locator('[data-page="'+view+'"]').click()
  ready(page);assert page.evaluate("atlas.page==='churn'");assert 'Churn and required service' in page.locator('#content h3').first.inner_text()
  assert not errors,errors;context.close()
  gallery_context=browser.new_context(viewport={'width':1440,'height':1000},device_scale_factor=.6);page=gallery_context.new_page()
  page.goto(base.rstrip('/')+'/gallery',wait_until='networkidle');page.wait_for_function('document.querySelectorAll(".gallery article").length===12');assert page.locator('.gallery a').count()==12
  page.evaluate('document.querySelectorAll(".gallery img").forEach(i=>i.loading="eager")')
  page.wait_for_function('Array.from(document.querySelectorAll(".gallery img")).every(i=>i.complete&&i.naturalWidth>0)')
  assert 'Twelve selected views' in page.locator('header').inner_text()
  page.screenshot(path=out/'figures/gallery.png',full_page=True)
  gallery_context.close();browser.close()
 assert len({r['chart_pixels']['png_sha256'] for r in records})==len(records),'Duplicate rendered curated charts'
 assert source_hashes=={path:digest(REVIEW/path) for path in source_hashes},'Application source changed during browser capture'
 result={'source_hashes':source_hashes,'state':'PASS_STRUCTURAL_PIXELS_AND_ROUNDTRIP_PENDING_DIRECT_IMAGE_REVIEW','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'curated':records,'aggregate_navigation':agg,'zoom_url_roundtrip':'PASS','reset_controls_and_url':'PASS','rapid_navigation':'PASS','light_theme':'PASS','gallery_cards':12,'console_errors':errors,'elapsed_s':time.monotonic()-start,'gpu_rendering':'disabled','limitations':'Pixel checks supplement, not replace, direct screenshot readability inspection.'};save(out/'acceptance.json',result)
 print('VISUAL_ACCEPTANCE_CAPTURE_COMPLETE',len(records),round(time.monotonic()-start,1),'s',flush=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--url',default='http://192.168.100.207:8765');a.add_argument('--output',type=Path,required=True);a.add_argument('--publish-curated',action='store_true',help='Explicitly regenerate the gallery PNG derivatives; default leaves published figures unchanged.');x=a.parse_args();main(x.url,x.output,x.publish_curated)
