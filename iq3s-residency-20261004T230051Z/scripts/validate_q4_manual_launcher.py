"""One load/health/generation smoke for the Q4 launcher; no benchmark sweep."""
import datetime
import json
import pathlib
import signal
import subprocess
import time
import urllib.request

from lab import ROOT, api, load, save


def main():
    variant = ROOT/'variants/ud-q4-k-xl'
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    evidence = variant/'validation'/stamp
    evidence.mkdir(parents=True, exist_ok=False)
    url = 'http://127.0.0.1:18088'
    proc = None
    result = {'state': 'RUNNING', 'port': 18088, 'benchmark': False}
    try:
        with (evidence/'launcher.log').open('x') as output:
            proc = subprocess.Popen([str(variant/'start-128k.sh'), '--host', '127.0.0.1', '--port', '18088'],
                                    stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
            start = time.monotonic()
            while time.monotonic()-start < 900:
                if proc.poll() is not None:
                    raise RuntimeError('Launcher failed; inspect '+str(evidence/'launcher.log'))
                health = api(url, '/health')
                if health and health.get('loaded') and health.get('status') == 'ok':
                    break
                time.sleep(1)
            else:
                raise RuntimeError('Smoke startup timeout')
            result['load_to_health_s'] = time.monotonic()-start
            save(evidence/'health.json', health)
            models = api(url, '/v1/models')
            save(evidence/'models.json', models)
            assert health['model'] == 'qwen3.8-flash-next-ud-q4_k_xl'
            assert health['max_context'] == 131072
            payload = {'model': health['model'], 'messages': [{'role': 'user', 'content':
                       'Write a numbered list of 30 short practical tips for reading Python tracebacks. '
                       'Begin with the first tip; do not call tools.'}],
                       'temperature': 0, 'max_tokens': 64, 'stream': False}
            save(evidence/'smoke-request.json', payload)
            req = urllib.request.Request(url+'/v1/chat/completions', data=json.dumps(payload).encode(),
                                         headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=180) as response:
                reply = json.load(response)
            save(evidence/'smoke-response.json', reply)
            time.sleep(2)
            status, metrics = api(url, '/v1/status'), api(url, '/metrics?requests=all')
            save(evidence/'status.json', status)
            save(evidence/'metrics.json', metrics)
            result.update(state='PASS', usage=reply.get('usage'), finish_reason=reply['choices'][0].get('finish_reason'),
                          manual_attempt=load(variant/'owned-process.json')['attempt'],
                          timings=status.get('last_timings') if status else None)
    except BaseException as exc:
        result.update(state='FAIL', error=repr(exc))
        raise
    finally:
        if proc and proc.poll() is None:
            proc.send_signal(signal.SIGTERM)
            proc.wait(timeout=45)
        result['launcher_exit_code'] = proc.returncode if proc else None
        result['port_closed'] = api(url, '/health') is None
        result['remaining_gpu_processes'] = subprocess.check_output(
            ['nvidia-smi', '--query-compute-apps=pid,process_name', '--format=csv,noheader'], text=True).strip()
        save(evidence/'result.json', result)
        print('VALIDATION', evidence, json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
