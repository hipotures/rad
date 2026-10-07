"""Persist the existing Strata Monitor API without inference or hardware polling."""
import argparse
import collections
import csv
import datetime
import fcntl
import hashlib
import json
import os
import pathlib
import signal
import threading
import time
import urllib.request
import psutil

ROOT = pathlib.Path(__file__).resolve().parents[1]

def read(path):
    return json.loads(pathlib.Path(path).read_text())

class MonitorRecorder:
    def __init__(self, url, output, owner_pid, owner_created, config_path=None, max_samples=0):
        self.url, self.output = url.rstrip('/'), pathlib.Path(output)
        self.owner_pid, self.owner_created = owner_pid, owner_created
        self.config_path, self.max_samples = config_path, max_samples
        self.stop_event = threading.Event()
        self.output.mkdir(parents=True, exist_ok=False)
        self.lock = (self.output.parent/'.ui-monitor.lock').open('a')
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.lock.close()
            raise RuntimeError('A Monitor recorder already follows this server session')
        self.thread = threading.Thread(target=self.run, name='ui-monitor-recorder', daemon=True)

    def start(self):
        self.thread.start()
        return self

    def close(self):
        self.stop_event.set()
        self.thread.join(timeout=6)

    def fetch(self, path):
        headers = {}
        key = os.environ.get('STRATA_UI_MONITOR_API_KEY')
        if key:
            headers['Authorization'] = 'Bearer '+key
        req = urllib.request.Request(self.url+path, headers=headers)
        with urllib.request.urlopen(req, timeout=2) as response:
            return json.load(response)

    def owner_alive(self):
        try:
            p = psutil.Process(self.owner_pid)
            return abs(p.create_time()-self.owner_created) < .1 and p.status() != psutil.STATUS_ZOMBIE
        except psutil.Error:
            return False

    def run(self):
        samples, errors, recovered_requests = 0, 0, 0
        metadata = {'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    'url': self.url, 'server_pid': self.owner_pid, 'server_create_time': self.owner_created,
                    'config_path': str(self.config_path) if self.config_path else None,
                    'interval_s': 1, 'source': 'Cached /metrics?requests=all and /v1/status used by the UI',
                    'limitations': ['Collection begins at attachment; earlier live samples are not reconstructed.',
                                    'Initial snapshot preserves the UI history still available at attachment.',
                                    'Disk rates are system-wide, not logical expert SSD reads.',
                                    'PCIe RX/TX are the UI aggregate across both GPUs.',
                                    'Request MTP/cache statistics appear after completion, as exposed by Strata.',
                                    'The two API snapshots are sequential, not an atomic cross-endpoint sample.',
                                    'No prompt/answer text, PSS sampling, CUDA calls or extra GPU polling.']}
        (self.output/'metadata.json').write_text(json.dumps(metadata, indent=2)+'\n')
        seen, order = set(), collections.deque()
        fields = ['time_utc', 'server_time', 'state', 'phase', 'prompt_tokens', 'generated', 'max_tokens',
                  'elapsed_s', 'live_TG_tok_s', 'cumulative_TG_tok_s', 'PP_tok_s', 'CPU_pct',
                  'RAM_used_bytes', 'RAM_total_bytes', 'PCIe_RX_MiB_s', 'PCIe_TX_MiB_s',
                  'disk_read_MiB_s', 'disk_write_MiB_s']
        for gpu in (0, 1):
            fields.extend(f'GPU{gpu}_{name}' for name in ('util_pct', 'VRAM_bytes', 'power_w', 'temp_c'))
        try:
            with (self.output/'metrics.jsonl').open('x') as raw, (self.output/'metrics.csv').open('x', newline='') as flat, \
                 (self.output/'requests.jsonl').open('x') as requests:
                writer = csv.DictWriter(flat, fieldnames=fields, lineterminator='\n')
                writer.writeheader()
                while not self.stop_event.is_set() and self.owner_alive():
                    begin = time.monotonic()
                    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    try:
                        metric = self.fetch('/metrics?requests=all')
                        status = self.fetch('/v1/status')
                        if samples == 0:
                            (self.output/'initial-snapshot.json').write_text(json.dumps({'at': stamp, 'metrics': metric, 'status': status}, indent=2)+'\n')
                        snapshot = {k: v for k, v in metric.items() if k not in ('history', 'requests')}
                        raw.write(json.dumps({'at': stamp, 'metrics': snapshot, 'status': status}, separators=(',', ':'))+'\n')
                        for request in reversed(metric.get('requests', [])):
                            digest = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
                            if digest in seen:
                                continue
                            seen.add(digest); order.append(digest)
                            if len(order) > 2000:
                                seen.remove(order.popleft())
                            requests.write(json.dumps({'observed_at': stamp, 'request': request}, separators=(',', ':'))+'\n')
                            recovered_requests += 1
                        live, hw = metric.get('live', {}), metric.get('hardware', {})
                        row = {'time_utc': stamp, 'server_time': metric.get('time'), 'state': live.get('state'),
                               'phase': live.get('phase'), 'prompt_tokens': live.get('prompt_tokens'),
                               'generated': live.get('generated'), 'max_tokens': live.get('max_tokens'),
                               'elapsed_s': live.get('elapsed_s'), 'live_TG_tok_s': live.get('tok_s'),
                               'cumulative_TG_tok_s': live.get('tok_s_mean'), 'PP_tok_s': live.get('prefill_tok_s_mean'),
                               'CPU_pct': hw.get('cpu'), 'RAM_used_bytes': hw.get('ram_used'),
                               'RAM_total_bytes': hw.get('ram_total'), 'PCIe_RX_MiB_s': hw.get('gpu_pcie_rx_mb'),
                               'PCIe_TX_MiB_s': hw.get('gpu_pcie_tx_mb'), 'disk_read_MiB_s': hw.get('disk_read_mb'),
                               'disk_write_MiB_s': hw.get('disk_write_mb')}
                        for gpu in hw.get('gpus', []):
                            idx = gpu.get('index')
                            if idx in (0, 1):
                                for name, key in [('util_pct', 'util'), ('VRAM_bytes', 'mem_used'), ('power_w', 'power'), ('temp_c', 'temp')]:
                                    row[f'GPU{idx}_{name}'] = gpu.get(key)
                        writer.writerow(row)
                        raw.flush(); flat.flush(); requests.flush()
                        samples += 1
                    except Exception as exc:
                        errors += 1
                        with (self.output/'errors.jsonl').open('a') as error:
                            error.write(json.dumps({'at': stamp, 'error': repr(exc)})+'\n')
                    if self.max_samples and samples >= self.max_samples:
                        break
                    self.stop_event.wait(max(0, 1-(time.monotonic()-begin)))
        finally:
            (self.output/'finished.json').write_text(json.dumps({'samples': samples, 'errors': errors,
                                                              'completed_request_rows': recovered_requests,
                                                              'finished_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}, indent=2)+'\n')
            self.lock.close()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant', default='p1-baseline')
    parser.add_argument('--max-samples', type=int, default=0)
    args = parser.parse_args()
    owner = read(ROOT/'variants'/args.variant/'owned-process.json')
    attempt = pathlib.Path(owner['attempt'])
    cfg = read(attempt/'config.json')
    out = attempt/'telemetry'/('ui-monitor-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    recorder = MonitorRecorder(f'http://127.0.0.1:{cfg["port"]}', out, owner['pid'], owner['create_time'], attempt/'config.json', args.max_samples)
    for name in (signal.SIGINT, signal.SIGTERM):
        signal.signal(name, lambda *_: recorder.stop_event.set())
    (out/'recorder-process.json').write_text(json.dumps({'pid': os.getpid(), 'create_time': psutil.Process().create_time()}, indent=2)+'\n')
    print('UI_MONITOR_LOGS', out, flush=True)
    recorder.run()

if __name__ == '__main__':
    main()
