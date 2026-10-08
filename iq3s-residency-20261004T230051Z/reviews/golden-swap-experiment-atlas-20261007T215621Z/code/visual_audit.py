#!/usr/bin/env python3
"""Capture actual UI navigation, full pages, focused charts and numeric plot specs."""
import argparse
import datetime
import hashlib
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from common import REVIEW, save

PAGES=[('overview','experiments'),('residency','residency'),('churn','churn'),('startup','startup'),
       ('expert','expert'),('oracle','current-future'),('demand','demand'),('classes','size-classes'),
       ('predictor','auc-outcomes'),('lease','lease'),('slots','physical-slots')]

def main(url,output,specs,chromium):
    output=output.resolve();specs=specs.resolve()
    if output.exists():raise SystemExit('Refuse an existing visual audit namespace')
    output.mkdir(parents=True);specs.mkdir(parents=True,exist_ok=False)
    shots=output/'figures/screenshots';shots.mkdir(parents=True)
    all_errors=[];console=[];requests=[];records=[];previous=None;start=time.monotonic()
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=chromium,headless=True,args=['--disable-gpu','--no-sandbox'])
        page=browser.new_page(viewport={'width':1440,'height':960},device_scale_factor=1)
        page.on('pageerror',lambda e:all_errors.append(str(e)))
        page.on('console',lambda m:console.append(m.text) if m.type=='error' else None)
        page.on('requestfailed',lambda r:requests.append({'url':r.url,'error':r.failure}))
        page.goto(url,wait_until='networkidle')
        page.wait_for_function('window.atlas && !atlas.busy',timeout=60000)
        # Preserve default behavior: no expert/B automatically selected to hide empty views.
        for i,(name,label) in enumerate(PAGES,1):
            before_errors=len(all_errors);before_console=len(console);before_requests=len(requests)
            page.locator(f'#tabs [data-page="{name}"]').click()
            page.wait_for_function('window.atlas && !atlas.busy',timeout=60000)
            page.wait_for_timeout(200)
            visible=page.evaluate("""() => {
              const c=document.querySelector('#content'),plots=[...c.querySelectorAll('.js-plotly-plot')];
              return {state:atlas.page,title:c.querySelector('h2')?.innerText||null,
                intro:[...c.querySelectorAll('.intro')].map(e=>e.innerText),text:c.innerText,
                loading:document.querySelector('#loading').innerText,notice:document.querySelector('#notice').innerText,
                viewport:{width:innerWidth,height:innerHeight,scrollY},document:{height:document.documentElement.scrollHeight,width:document.documentElement.scrollWidth},
                plots:plots.map(el=>{const b=el.getBoundingClientRect();return {
                  title:el.closest('.card')?.querySelector('h3')?.innerText,
                  visibly_rendered:b.width>0&&b.height>0,traces:el.data.length,types:[...new Set(el.data.map(d=>d.type))],
                  axes:[...el.querySelectorAll('.g-xtitle,.g-ytitle')].map(e=>e.textContent),
                  legends:[...el.querySelectorAll('.legendtext')].map(e=>e.textContent),
                  bounds:{x:b.x,y:b.y,width:b.width,height:b.height},point_count:el.data.reduce((n,d)=>n+(d.x?.length||0),0)
                };})};
            }""")
            digest=hashlib.sha256(visible['text'].encode()).hexdigest()
            screenshot=shots/f'{i:02d}-{label}.png'
            page.screenshot(path=screenshot,full_page=True)
            page.screenshot(path=shots/f'{i:02d}-{label}-viewport.png')
            focused=[]
            cards=page.locator('#content .card').filter(has=page.locator('.js-plotly-plot'))
            # Each first two charts plus key later plots are inspected independently.
            indexes=list(range(min(2,cards.count())))
            if name in ['startup','oracle','predictor','lease'] and cards.count()>2:indexes.append(cards.count()-1)
            for j in indexes:
                card=cards.nth(j);collapsed=card.evaluate("e=>{const d=e.closest('details');if(d&&!d.open){d.open=true;return true;}return false;}");path=shots/f'{i:02d}-{label}-chart-{j+1:02d}.png'
                card.screenshot(path=path);focused.append(str(path.relative_to(REVIEW)));
                if collapsed:card.evaluate("e=>e.closest('details').open=false")
            for j in range(page.locator('.js-plotly-plot').count()):
                spec=page.locator('.js-plotly-plot').nth(j).evaluate("""el=>({
                  title:el.closest('.card')?.querySelector('h3')?.innerText,
                  data:el.data.map(d=>{const out={};for(const k of ['type','mode','name','x','y','z','base','width','orientation','stackgroup','nbinsx','colorscale','zmin','zmax','line','marker'])if(d[k]!=null)out[k]=d[k];return out;}),
                  layout:{xaxis:el.layout.xaxis,yaxis:el.layout.yaxis,barmode:el.layout.barmode,shapes:el.layout.shapes},
                  run:atlas.A?.id,compare:atlas.B?.id,layer:document.querySelector('#layer').value,
                  representation:'Exact plotted numeric coordinates; long hover text omitted. Full generations/service available in published layer assets.'
                })""")
                save(specs/f'{i:02d}-{label}-plot-{j+1:02d}.json',spec)
            record=dict(page=name,navigation_worked=visible['state']==name,content_changed=previous!=digest,
                plot_count=len(visible['plots']),visible_plot_count=sum(x['visibly_rendered'] for x in visible['plots']),plot_titles=[x['title'] for x in visible['plots']],
                visible_errors=[x for x in [visible['notice'],visible['loading']] if 'fail' in x.lower()],
                console_errors=console[before_console:],exceptions=all_errors[before_errors:],request_failures=requests[before_requests:],
                screenshot=str(screenshot.relative_to(REVIEW)),focused_screenshots=focused,
                human_readability='PENDING_VISUAL_INSPECTION',reason='Screenshots must be inspected before classification.',
                visible=visible,content_hash=digest,previous_content_hash=previous)
            records.append(record);previous=digest
            save(output/'visual-audit.json',dict(state='CAPTURED_NOT_YET_VISUALLY_CLASSIFIED',url=url,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),pages=records,all_console_errors=console,all_exceptions=all_errors,elapsed_s=time.monotonic()-start))
            print('[VISUAL AUDIT]',name,'graphs',len(visible['plots']),'title',visible['title'],'screenshot',screenshot.name,'elapsed',round(time.monotonic()-start),'s',flush=True)
        browser.close()

if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--url',default='http://192.168.100.207:8765/')
    a.add_argument('--output',type=Path,required=True);a.add_argument('--specs',type=Path,required=True);a.add_argument('--chromium',default='/snap/bin/chromium');args=a.parse_args();main(args.url,args.output,args.specs,args.chromium)
