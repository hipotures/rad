#!/usr/bin/env python3
"""Bounded visual edge checks and fully loaded gallery capture over HTTP."""
import argparse,datetime,json,time
from pathlib import Path
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright
from common import REVIEW,save

def main(base,out):
 out=out.resolve()
 if out.exists():raise SystemExit('Refuse existing validation namespace')
 out.mkdir(parents=True);fig=out/'figures';fig.mkdir();rows=[];errors=[];start=time.monotonic()
 run='golden-swap-phase2--code-archive-block1-REPLAY_CURRENT'
 full='golden-swap-phase2--code-archive-block1-ORACLE_FULL'
 cases=[
  ('gpu1-slots',dict(view='slots',run=run,gpu=1,layer=46,**{'class':3584000},scope='all',limit=12,changed=1,focus=1,snapshot=1)),
  ('state-difference',dict(view='residency',run=run,compare=full,layer=3,comparison='difference',experts='3,17,100-120',**{'from':262,'to':358},focus=1,snapshot=1)),
  ('percent-time',dict(view='churn',run=run,time='percent',**{'from':0,'to':25},smooth=4,counts='share',focus=1,snapshot=1)),
  ('lease-thresholds',dict(view='lease',run=run,layer=3,initial=0,short=8,long=128,snapshot=1))]
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/snap/bin/chromium',headless=True,args=['--disable-gpu','--no-sandbox'])
  for name,q in cases:
   context=b.new_context(viewport={'width':1440,'height':1000});page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(base.rstrip('/')+'/?'+urlencode(q),wait_until='networkidle');page.wait_for_function('window.atlas&&!atlas.busy',timeout=90000)
   assert not page.locator('#notice').inner_text(),page.locator('#notice').inner_text()
   title=page.locator('#content h2').first.inner_text();plots=page.locator('.js-plotly-plot:visible');assert plots.count()>0
   if name=='gpu1-slots':
    labels=page.evaluate('atlas.charts[0].el.layout.yaxis.ticktext');assert len(labels)==12 and all(v.startswith('GPU1') for v in labels),labels
   if name=='state-difference':
    value=page.evaluate('({y:atlas.charts[0].el.data[0].y,z:atlas.charts[0].el.data[0].z.flat(),r:atlas.range})')
    assert value['y']==[3,17,*range(100,121)];assert min(value['z'])>=-1.000001 and max(value['z'])<=1.000001 and any(v for v in value['z']);assert value['r']==[262,358]
   if name=='percent-time':
    assert page.input_value('#time')=='percent';assert page.evaluate('atlas.range')==[0,25]
    ys=page.evaluate('atlas.charts[0].el.data.slice(4).flatMap(d=>d.y)');assert min(ys)>=0 and max(ys)<=100
   if name=='lease-thresholds':
    assert not page.locator('#includeInitial').is_checked()
    assert page.input_value('#shortLife')=='8' and page.input_value('#longLife')=='128'
   url=page.url;page.reload(wait_until='networkidle');page.wait_for_function('!atlas.busy',timeout=90000);assert page.url==url
   screenshot=fig/(name+'.png');page.screenshot(path=screenshot,full_page=name!='lease-thresholds')
   rows.append({'name':name,'state':'PASS','url':url,'title':title,'plot_titles':plots.evaluate_all('es=>es.map(e=>e.parentElement.querySelector("h3").innerText)'), 'screenshot':str(screenshot.relative_to(REVIEW))});context.close();print('[VISUAL EDGE]',name,'PASS',round(time.monotonic()-start),'s',flush=True)
  context=b.new_context(viewport={'width':1440,'height':1000},device_scale_factor=.6);page=context.new_page();page.goto(base.rstrip('/')+'/gallery',wait_until='networkidle')
  page.wait_for_function('document.querySelectorAll(".gallery article").length===12');page.evaluate('document.querySelectorAll(".gallery img").forEach(i=>i.loading="eager")');page.wait_for_function('Array.from(document.querySelectorAll(".gallery img")).every(i=>i.complete&&i.naturalWidth>0)')
  assert 'Twelve selected views' in page.locator('header').inner_text();page.screenshot(path=fig/'gallery-published.png',full_page=True);assert (fig/'gallery-published.png').stat().st_size<1048576
  context.close();b.close()
 assert not errors,errors
 save(out/'validation.json',{'state':'PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cases':rows,'gallery_images_loaded':12,'gallery_png':str((fig/'gallery-published.png').relative_to(REVIEW)),'gallery_device_scale':.6,'exceptions':errors,'gpu_rendering':'disabled'})
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--url',default='http://192.168.100.207:8765');a.add_argument('--output',required=True,type=Path);x=a.parse_args();main(x.url,x.output)
