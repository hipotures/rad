"""Run the preserved Q4 production runtime with a separate 128K manual profile."""
import argparse
import datetime
import hashlib
import json
import os
import pathlib
import signal
import socket
import subprocess
import time

import psutil

from lab import ROOT, api, load, owned_stop, save
from record_ui_metrics import MonitorRecorder

VARIANT = 'ud-q4-k-xl'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--check', action='store_true', help='Validate files/config without starting a server')
    args = parser.parse_args()
    cfg = load(ROOT/'variants'/VARIANT/'128k.json')
    if hashlib.sha256(pathlib.Path(cfg['exe']).read_bytes()).hexdigest() != cfg['binary_sha256']:
        raise RuntimeError('Preserved Q4 binary SHA256 mismatch')
    actual_head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=cfg['cwd'], text=True).strip()
    if actual_head != cfg['source_sha']:
        raise RuntimeError('Preserved Q4 source HEAD mismatch')
    options = dict(zip(cfg['args'][::2], cfg['args'][1::2]))
    for key in ['--pack', '--native', '--expert-profile', '--mtp']:
        if not pathlib.Path(options[key]).exists():
            raise RuntimeError('Missing '+key+': '+options[key])
    if not pathlib.Path(cfg['tokenizer']).is_dir():
        raise RuntimeError('Missing tokenizer directory')
    for shard in cfg['model_shards']:
        if pathlib.Path(shard['path']).stat().st_size != shard['bytes']:
            raise RuntimeError('Q4 shard size differs from preserved SHA256 manifest: '+shard['path'])
    if args.check:
        print('CONFIG_CHECK OK', cfg['model_name'], 'max_context', options['--max-context'],
              'split', cfg['layer_split'], 'source', actual_head, flush=True)
        return
    if psutil.virtual_memory().available < 110*1024**3:
        raise RuntimeError('Need at least 110 GiB MemAvailable for this Q4 full-RAM-arena profile')
    if subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid', '--format=csv,noheader'], text=True).strip():
        raise RuntimeError('GPU compute processes are active; stop the other model before starting Q4')
    with socket.socket() as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        probe.bind((args.host, args.port))

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    attempt = ROOT/'variants'/VARIANT/'manual'/stamp
    for name in ['logs', 'raw', 'telemetry']:
        (attempt/name).mkdir(parents=True, exist_ok=False)
    cfg.update(host=args.host, port=args.port, log=str(attempt/'logs/engine.log'))
    save(attempt/'config.json', cfg)
    env = {key: value for key, value in os.environ.items() if not key.startswith('STRATA_')}
    env.update(cfg['env'])
    command = [cfg['python'], '-m', 'serve.server', '--engine', 'strata', '--config',
               str(attempt/'config.json'), '--host', args.host, '--port', str(args.port)]
    stopping = False

    def stop_requested(*_):
        nonlocal stopping
        stopping = True

    for signum in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(signum, stop_requested)
    proc = follower = recorder = None
    url = f'http://127.0.0.1:{args.port}'
    started = time.monotonic()
    with (attempt/'logs/server.log').open('x') as output:
        try:
            (attempt/'logs/engine.log').touch()
            print('RESOLVED_CONFIG', json.dumps(cfg), flush=True)
            print('LOGS', attempt/'logs', flush=True)
            proc = subprocess.Popen(command, cwd=cfg['cwd'], env=env, stdout=output,
                                    stderr=subprocess.STDOUT, start_new_session=True)
            created = psutil.Process(proc.pid).create_time()
            record = {'pid': proc.pid, 'create_time': created, 'attempt': str(attempt), 'command': command}
            save(ROOT/'variants'/VARIANT/'owned-process.json', record)
            save(attempt/'process.json', dict(record, environment=cfg['env']))
            follower = subprocess.Popen(['tail', '-n', '+1', '-f', '--sleep-interval=0.2',
                                         str(attempt/'logs/server.log'), str(attempt/'logs/engine.log')])
            ready = False
            while not stopping and proc.poll() is None:
                if psutil.virtual_memory().available < 12*1024**3:
                    raise RuntimeError('RAM_ABORT: MemAvailable below 12 GiB; stopping owned Q4 process')
                if not ready:
                    health = api(url, '/health')
                    if health and health.get('loaded') and health.get('status') == 'ok':
                        if health.get('model') != cfg['model_name'] or health.get('max_context') != 131072:
                            raise RuntimeError('Loaded model/context differs from Q4 128K config')
                        startup = {'cold_start_s': time.monotonic()-started, 'health': health,
                                   'metrics': api(url, '/metrics'), 'status': api(url, '/v1/status')}
                        save(attempt/'raw/startup.json', startup)
                        recorder = MonitorRecorder(url, attempt/'telemetry/ui-monitor', proc.pid,
                                                   created, attempt/'config.json').start()
                        print('UI_MONITOR_LOGS', attempt/'telemetry/ui-monitor', flush=True)
                        print('READY', VARIANT, '128k', round(startup['cold_start_s'], 2), flush=True)
                        print('HTTP', url, '(bind '+args.host+':'+str(args.port)+')', flush=True)
                        ready = True
                    elif time.monotonic()-started > 900:
                        raise RuntimeError('Q4 startup timed out after 900 seconds')
                time.sleep(1)
            if not stopping and proc.returncode not in (0, -signal.SIGTERM):
                raise RuntimeError('Q4 server exited with code '+str(proc.returncode))
        except BaseException as exc:
            save(attempt/'failure.json', {'error': repr(exc), 'elapsed_s': time.monotonic()-started})
            raise
        finally:
            if recorder:
                recorder.close()
            if proc:
                owned_stop(proc.pid, created)
                proc.wait(timeout=5)
            if follower:
                follower.terminate()
                try:
                    follower.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    follower.kill()
                    follower.wait()
            save(attempt/'stopped.json', {'elapsed_s': time.monotonic()-started,
                                         'server_returncode': proc.returncode if proc else None})


if __name__ == '__main__':
    main()
