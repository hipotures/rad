#!/usr/bin/env python3
"""Read-only checks of preserved source results, launchers and our static server."""
import argparse
import urllib.request
from common import *

def main(url):
    start=load(REVIEW/'provenance/starting-state.json')
    checks=[]
    for rel,sha in start['preserved_launchers'].items():
        assert digest(REPO/rel)==sha,rel
        checks.append(dict(path=rel,sha256=sha,state='UNCHANGED'))
    sources=load(REVIEW/'results/source-catalog.json')['sources']
    for s in sources:
        assert digest(s['path'])==s['sha256'],s['path']
    model=campaign('golden-swap-phase1')/'models/logistic.txt'
    assert digest(model)=='065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e'
    server=load(REVIEW/'server-status.json');pid=server['pid'];proc=Path('/proc')/str(pid)
    actual=proc.joinpath('cmdline').read_bytes().split(b'\0')
    assert str(REVIEW/'code/serve.py').encode() in actual
    fields=proc.joinpath('stat').read_text().rsplit(')',1)[1].split()
    assert int(fields[19])==int(server['process_start_ticks']),'PID identity changed'
    checks_http=[]
    for route,mime in [('/', 'text/html'),('/vendor/plotly.js?check=1','application/javascript'),
                       ('/site/data/catalog.json','application/json')]:
        # The catalog is served at /data/catalog.json by the static root.
        if route.startswith('/site/'):route=route[len('/site'):]
        with urllib.request.urlopen(url.rstrip('/')+route,timeout=10) as response:
            assert response.status==200
            assert mime in response.headers['Content-Type'],(route,response.headers)
            if 'plotly' in route:assert response.headers.get('Content-Encoding')=='gzip'
            checks_http.append(dict(route=route,status=200,mime=response.headers['Content-Type']))
    result=dict(state='PASS',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                preserved_launchers=checks,original_result_sources_unchanged=len(sources),
                frozen_checkpoint_sha256=digest(model),static_server=server,http=checks_http,
                gpu_benchmark_runs=0,serving_settings_changed=False,
                limitation='No model-weight rehash or claim of new natural-generation equivalence.')
    save(REVIEW/'results/integrity-validation.json',result)
    print('INTEGRITY_PASS',len(checks),'launchers;',len(sources),'original result sources;',url,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--url',default='http://127.0.0.1:8765/');main(p.parse_args().url)
