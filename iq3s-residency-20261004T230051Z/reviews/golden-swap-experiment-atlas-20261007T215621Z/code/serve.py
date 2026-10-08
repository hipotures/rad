#!/usr/bin/env python3
"""Serve the static Atlas and complete gzip assets; no GPU or experiment services."""
import argparse
import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import socket
import subprocess
import sys
import urllib.parse
from discovery import response

REVIEW=Path(__file__).resolve().parents[1]
REPO=REVIEW.parents[2]
CATALOG=json.loads((REVIEW/'site/data/catalog.json').read_text())
SOURCE_LINKS={r[k] for r in CATALOG['runs'] for k in ['source_result','report'] if r.get(k)}

def ipv4_addresses():
    result=set()
    try:
        for item in subprocess.check_output(['hostname','-I'],text=True,timeout=3).split():
            if '.' in item and not item.startswith('127.'):result.add(item)
    except (OSError,subprocess.SubprocessError):pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(),None,socket.AF_INET):
            if not info[4][0].startswith('127.'):result.add(info[4][0])
    except OSError:pass
    return sorted(result)

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed=urllib.parse.urlsplit(self.path)
        if parsed.path.startswith('/api/'):
            try:code,value=response(REVIEW,CATALOG,parsed.path,urllib.parse.parse_qs(parsed.query))
            except (OSError,ValueError,KeyError) as error:code,value=500,{'error':'Retained discovery data unavailable','detail':str(error)}
            body=json.dumps(value,separators=(',',':'),allow_nan=False).encode()
            self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body);return
        super().do_GET()

    def translate_path(self,path):
        path=urllib.parse.unquote(urllib.parse.urlsplit(path).path)
        if '\\' in path or '..' in Path(path).parts:return str(REVIEW/'not-found')
        if path in {'/gallery','/gallery/'}:return str(REVIEW/'site/gallery.html')
        if path=='/vendor/plotly.js':return str(REVIEW/'evidence/library-v1/plotly-2.35.2.txt.gz')
        if path.startswith('/evidence/'):
            base=REVIEW/'evidence';rel=path[len('/evidence/'):]
        elif path.startswith('/review/'):
            base=REVIEW;rel=path[len('/review/'):]
            if Path(rel).suffix not in {'.md','.json','.png','.txt','.py','.csv'}:return str(REVIEW/'not-found')
        elif path.startswith('/sources/'):
            base=REPO;rel=path[len('/sources/'):]
            allowed=('iq3s-residency-20261004T230051Z/campaigns/','iq3s-residency-20261004T230051Z/experiments/','docs/')
            if not rel.startswith(allowed) or Path(rel).suffix not in {'.md','.json','.py','.txt','.patch','.gz'}:
                return str(REVIEW/'not-found')
            if any(p in Path(rel).parts for p in ['src','source','.git','repos','models','inputs']):return str(REVIEW/'not-found')
            if 'raw' in Path(rel).parts and rel not in SOURCE_LINKS:return str(REVIEW/'not-found')
        else:
            base=REVIEW/'site';rel=path.lstrip('/') or 'index.html'
        candidate=(base/rel).resolve()
        if not candidate.is_relative_to(base.resolve()) or any(x.startswith('.') for x in Path(rel).parts):return str(REVIEW/'not-found')
        return str(candidate)

    def guess_type(self,path):
        if urllib.parse.urlsplit(self.path).path=='/vendor/plotly.js':return 'application/javascript; charset=utf-8'
        if str(path).endswith('.json.gz'):return 'application/json; charset=utf-8'
        if str(path).endswith('.jsonl.gz'):return 'application/x-ndjson; charset=utf-8'
        return mimetypes.guess_type(path)[0] or 'application/octet-stream'

    def end_headers(self):
        p=self.translate_path(self.path)
        if p.endswith('.gz') and Path(p).is_file():self.send_header('Content-Encoding','gzip')
        self.send_header('Cache-Control','no-cache')
        self.send_header('X-Content-Type-Options','nosniff')
        super().end_headers()

    def list_directory(self,path):
        self.send_error(404,'Directory listing is disabled');return None

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--host',default='0.0.0.0');p.add_argument('--port',type=int,default=8765)
    args=p.parse_args()
    try:server=ThreadingHTTPServer((args.host,args.port),Handler)
    except OSError as ex:raise SystemExit(f'Cannot bind {args.host}:{args.port}: {ex}')
    actual=server.server_address[1];urls=[f'http://{addr}:{actual}/' for addr in ipv4_addresses()]
    value={'pid':os.getpid(),'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'command':[sys.executable,*sys.argv],'host':args.host,'port':actual,'interfaces':ipv4_addresses(),'urls':urls,
           'process_start_ticks':Path('/proc/self/stat').read_text().split()[21],
           'identity_rule':'PID plus /proc start ticks and exact command; never use a historical PID alone.'}
    temp=REVIEW/'server-status.json.tmp';temp.write_text(json.dumps(value,indent=2)+'\n');temp.replace(REVIEW/'server-status.json')
    print(f'Golden Swap Experiment Atlas listening on {args.host}:{actual}',flush=True)
    for url in urls:print('Browser URL:',url,flush=True)
    print('Local health URL:',f'http://127.0.0.1:{actual}/',flush=True)
    try:server.serve_forever(poll_interval=.5)
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=='__main__':main()
