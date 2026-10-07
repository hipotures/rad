"""Validate installed YASD parsing using preserved real Q4 API responses."""
import asyncio
import json
import pathlib
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from yasd import StrataCollector

root = pathlib.Path('/srv/ai/research/iq3s-residency-20261004T230051Z/variants/ud-q4-k-xl')
evidence = sorted((root/'validation').iterdir())[-1]
bodies = {endpoint: json.loads((evidence/name).read_text()) for endpoint, name in
          [('/health', 'health.json'), ('/metrics', 'metrics.json'), ('/v1/status', 'status.json')]}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps(bodies[urlsplit(self.path).path]).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass


async def validate(port):
    collector = StrataCollector(f'http://127.0.0.1:{port}')
    collector._session = collector._make_session()
    try:
        snapshot = await collector._fetch_and_parse()
        assert snapshot.loaded
        assert snapshot.model == 'qwen3.8-flash-next-ud-q4_k_xl'
        assert snapshot.max_context == 131072
        assert snapshot.draft_n == 53 and snapshot.draft_n_accepted == 39
        assert len(snapshot.gpus) == 2
        result = {'state': 'PASS', 'kind': 'HTTP replay of preserved real Strata responses; not a live inference run',
                  'fixture': str(evidence), 'model': snapshot.model, 'max_context': snapshot.max_context,
                  'gpu_count': len(snapshot.gpus), 'mtp_proposed': snapshot.draft_n,
                  'mtp_accepted': snapshot.draft_n_accepted, 'request_rows': len(snapshot.requests)}
        pathlib.Path(__file__).with_name('verification.json').write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(result))
    finally:
        await collector.stop()


server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    asyncio.run(validate(server.server_port))
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
