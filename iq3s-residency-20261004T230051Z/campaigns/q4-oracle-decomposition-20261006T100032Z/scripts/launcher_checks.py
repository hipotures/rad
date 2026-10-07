"""Finite identity/config checks; no additional inference requests."""
import json
import subprocess
import sys
from pathlib import Path

from owned import C, run


def main():
    jobs = subprocess.check_output(
        ['nvidia-smi', '--query-compute-apps=pid', '--format=csv,noheader'],
        text=True, timeout=10).strip()
    assert not jobs, 'Refuse heavy validation concurrently with GPU work'
    rows = []
    for profile in ['32k', '128k', '256k']:
        for arm in ['current', 'FF', '64F', 'F64', '6464', 'F256']:
            wrapper = C / 'launchers/replay' / f'{arm}-{profile}.sh'
            subprocess.run(['bash', '-n', wrapper], check=True, timeout=10)
            label = f'launcher-check-{profile}-{arm}'
            directory = run(label, [wrapper, '--check'], timeout=180, area='tests')
            output = (directory / 'stdout.log').read_text()
            assert 'CHECK_PASS_NO_SERVER' in output
            assert 'EXPERIMENTAL_FORCED_WORK_REPLAY_NOT_NORMAL_SERVING' in output
            rows.append({'profile': profile, 'arm': arm, 'state': 'PASS',
                         'wrapper': str(wrapper), 'evidence': str(directory)})
    normal_rows = []
    normal_directory = C.parent / 'q4-live-oracle-20261006T040656Z' / 'launchers/control'
    for profile in ['32k', '128k', '256k']:
        wrapper = normal_directory / f'start-{profile}.sh'
        subprocess.run(['bash', '-n', wrapper], check=True, timeout=10)
        directory = run(f'unchanged-normal-check-{profile}', [wrapper, '--check'],
                        timeout=120, area='tests')
        assert 'VERIFIED_UNCHANGED_CONTROL' in (directory / 'stdout.log').read_text()
        normal_rows.append({'profile': profile, 'wrapper': str(wrapper),
                            'state': 'PASS', 'evidence': str(directory)})
    # Fail closed before model/tape loading if the expected binary hash differs.
    sandbox = C / 'tests/hash-refusal'
    (sandbox / 'scripts').mkdir(parents=True, exist_ok=False)
    (sandbox / 'git').mkdir()
    (sandbox / 'scripts/reproduce.py').write_text(
        (C / 'scripts/reproduce.py').read_text())
    identity = json.loads((C / 'git/oracle-decomposition-v2-identity.json').read_text())
    identity['binary_sha256'] = '0' * 64
    (sandbox / 'git/oracle-decomposition-v2-identity.json').write_text(
        json.dumps(identity, indent=2) + '\n')
    result = subprocess.run(
        [sys.executable, sandbox / 'scripts/reproduce.py', '--arm', 'FF',
         '--profile', '32k', '--check'], capture_output=True, text=True, timeout=30)
    (C / 'tests/launcher-hash-refusal.stdout.log').write_text(result.stdout)
    (C / 'tests/launcher-hash-refusal.stderr.log').write_text(result.stderr)
    assert result.returncode != 0 and 'AssertionError' in result.stderr
    assert 'CHECK_PASS_NO_SERVER' not in result.stdout
    assert not subprocess.check_output(
        ['nvidia-smi', '--query-compute-apps=pid', '--format=csv,noheader'],
        text=True, timeout=10).strip()
    value = {'state': 'PASS', 'rows': rows, 'unchanged_normal_rows': normal_rows,
             'hash_refusal': {'state': 'PASS', 'exit_code': result.returncode},
             'no_new_inference_requests': True,
             'scope': 'All retained wrappers identity/config/tape validation; measured coverage is separately reported.'}
    (C / 'tests/launcher-checks.json').write_text(json.dumps(value, indent=2) + '\n')
    print('LAUNCHER_CHECKS_PASS', len(rows), flush=True)


if __name__ == '__main__':
    main()
