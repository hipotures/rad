#!/usr/bin/env python3
"""Exercise the actual HTTP dashboard in a software-rendered desktop browser."""
import argparse
import datetime
import json
import time
from playwright.sync_api import sync_playwright
from common import *
from compact_assets import expand

def main(url,chromium):
    errors=[];console=[];checks=[];start=time.monotonic()
    def check(name,detail=None):
        checks.append({'check':name,'state':'PASS','detail':detail});print('[BROWSER]',name,'elapsed',round(time.monotonic()-start),'s',flush=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=chromium,headless=True,args=['--disable-gpu','--no-sandbox'])
        page=browser.new_page(viewport={'width':1680,'height':1050},device_scale_factor=1)
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('console',lambda m:console.append({'type':m.type,'text':m.text}) if m.type in ['error','warning'] else None)
        def ready():
            page.wait_for_function('window.atlas && !atlas.busy',timeout=60000)
            assert not page.locator('#loading').inner_text().endswith('failed'),page.locator('#notice').inner_text()
        def tab(name):
            page.locator(f'#tabs [data-page="{name}"]').click();ready()
            n=page.locator('.js-plotly-plot').count();assert n>0 or name=='overview',(name,page.locator('#notice').inner_text())
            check('page '+name,{'charts':n})
        def select(id,value):page.select_option('#'+id,str(value));ready()
        def screenshot(name):
            out=REVIEW/'figures'/name;out.parent.mkdir(exist_ok=True);page.screenshot(path=out)
        page.goto(url,wait_until='networkidle');ready()
        assert page.title()=='Golden Swap Experiment Atlas'
        assert page.locator('tbody tr').count()==335
        check('overview and catalog',{'experiments':12,'run_records':335})
        screenshot('overview.png')
        ids=page.evaluate("atlas.catalog.runs.filter(r=>r.campaign.startsWith('golden-swap-phase2')&&r.task==='code-archive'&&r.detail).map(r=>({id:r.id,policy:r.policy}))")
        bypolicy={r['policy']:r['id'] for r in ids}
        select('runA',bypolicy['ORACLE_IN_HISTORY_TC']);select('runB',bypolicy['REPLAY_CURRENT'])
        for name in ['residency','churn','startup','expert','oracle','demand','classes','predictor','lease']:
            tab(name)
            if name in ['residency','startup','predictor','lease']:screenshot(name+'.png')
        tab('residency')
        select('gpu',1);assert page.input_value('#layer')=='24';check('GPU ownership restricts selected layer')
        select('byteClass',3584000);assert int(page.input_value('#layer')) in [30,46,47];check('physical class filter')
        select('layer',47)
        expert=page.evaluate('atlas.layerA.demand[0][1]');page.fill('#expert',str(expert));page.locator('#expert').dispatch_event('change');ready()
        tab('expert');assert str(expert) in page.locator('h2').first.inner_text();check('expert drill-down',{'layer':47,'expert':expert})
        select('byteClass','');select('gpu','');select('layer',0);page.fill('#expert','');page.locator('#expert').dispatch_event('change');ready()
        tab('residency');page.fill('#expertSubset','3,17,100-120');page.locator('#expertSubset').dispatch_event('change');ready();check('expert subset filter')
        page.fill('#expertSubset','');page.locator('#expertSubset').dispatch_event('change');ready()
        page.evaluate("Plotly.relayout(atlas.charts[0].el, {'xaxis.range':[5,22]})")
        page.wait_for_function("atlas.charts.filter(c=>c.timelike).every(c=>c.el.layout.xaxis.range[0]===5&&c.el.layout.xaxis.range[1]===22)")
        check('linked zoom')
        page.evaluate("Plotly.relayout(atlas.charts[0].el,{dragmode:'pan'})");check('pan mode')
        page.evaluate("Plotly.Fx.hover(atlas.charts[0].el,[{curveNumber:0,pointNumber:0}])")
        assert page.locator('.hoverlayer').count()>0;check('hover rendering')
        page.click('#reset');page.wait_for_function('atlas.range===null');check('zoom reset')
        select('time','event');assert page.evaluate("atlas.charts[0].el.layout.xaxis.title.text")== 'Routed-layer invocation';check('routed invocation units')
        select('time','percent');check('percentage time units');select('time','window')
        select('runA',bypolicy['REPLAY_CURRENT']);select('runB',bypolicy['ORACLE_FULL']);tab('oracle');screenshot('current-vs-full-oracle.png')
        assert page.evaluate('atlas.A.alignment_id===atlas.B.alignment_id');check('current / full-oracle exact tape alignment')
        assert any('similarity to' in t.lower() for t in page.locator('h3').all_text_contents());check('whole-model future-reference similarity')
        select('comparison','difference');assert 'A − B' in page.evaluate('atlas.charts[0].el.data[0].name');check('paired difference mode')
        select('comparison','absolute');select('globalMetric','nonlocal');tab('residency');check('global nonlocal map')
        page.click('#theme');ready();assert page.locator('html').evaluate('e=>e.classList.contains("light")');check('light theme');page.click('#theme');ready()
        select('policy','REPLAY_CURRENT');assert page.locator('#runA option').count()<335;check('policy filter');select('policy','')
        select('task','math-inventory');assert page.locator('#runA option').count()<335;check('task / run switching');select('task','')
        select('source','RFC8259-JSON');assert page.locator('#runA option').count()>0;check('source group filter');select('source','')
        legacy=page.evaluate("atlas.catalog.runs.find(r=>r.campaign==='IQ3_S-E004-replay'&&r.policy==='future-nextuse'&&r.detail).id")
        select('runA',legacy);select('runB','');tab('residency');check('legacy modeled replay view')
        select('runA',bypolicy['ORACLE_IN_HISTORY_TC']);tab('residency')
        layer=page.evaluate('({columns:atlas.layerA.columns,generation_count:atlas.layerA.generations.length,demand_count:atlas.layerA.demand.length,path_totals:atlas.layerA.demand.reduce((a,r)=>a.map((v,i)=>v+r[i+2]),[0,0,0,0])})')
        original_path=work_root()/'derived/browser-v1/runs'/bypolicy['ORACLE_IN_HISTORY_TC']/'layer-0.json'
        if original_path.exists():original=load(original_path)
        else:
            original=load(REVIEW/'evidence/browser-v1/runs'/bypolicy['ORACLE_IN_HISTORY_TC']/'layer-0.json.gz')
            original['demand']=expand(load(REVIEW/original['demand_url'].lstrip('/')),original)
        assert layer['generation_count']==len(original['generations']) and layer['demand_count']==len(original['demand'])
        assert layer['path_totals']==[sum(r[i] for r in original['demand']) for i in range(2,6)];check('browser exact compact decoding',layer)
        page.locator('#provenance').evaluate('e=>e.open=true');assert 'source' in page.locator('#provenanceContent').inner_text().lower();check('provenance panel')
        exported=page.evaluate("async()=>{const s=await Plotly.toImage(atlas.charts[0].el,{format:'svg',width:800,height:400});return s.startsWith('data:image/svg+xml');}");assert exported;check('SVG chart export')
        exported=page.evaluate("async()=>{const s=await Plotly.toImage(atlas.charts[0].el,{format:'png',width:800,height:400});return s.startsWith('data:image/png');}");assert exported;check('PNG chart export')
        browser.close()
    result={'state':'PASS' if not errors else 'FAIL','url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'checks':checks,'page_exceptions':errors,'console_messages':console,'elapsed_s':time.monotonic()-start,
            'browser':chromium,'gpu_rendering':'disabled; no inference service used'}
    save(REVIEW/'results/browser-validation.json',result)
    assert not errors,errors
    assert not [m for m in console if m['type']=='error'],console
    print('BROWSER_VALIDATION_PASS',len(checks),'checks',flush=True)

if __name__=='__main__':
    q=argparse.ArgumentParser(description=__doc__);q.add_argument('--url',default='http://127.0.0.1:8765/');q.add_argument('--chromium',default='/snap/bin/chromium');a=q.parse_args();main(a.url,a.chromium)
