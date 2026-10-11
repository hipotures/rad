#!/usr/bin/env python3
"""Smoke test of job5_replays.py on a synthetic upstream repository (seconds, no network, stdlib only).

Six toy packages exercise every path of the harness:
  pass      exits 0; writes kappa as a decimal string with a trailing zero (exact), a value 1e-19 away (close
            only) and b as 'a/10^24'; args use {BOOST}, which must arrive as $BOOST_INCLUDE
  gitattr   manifest lists an absent .gitattributes: the as-is attempt fails at the integrity assertion, the
            job 4 repair attempt passes and becomes the passing attempt
  changed   manifest mismatch with a changed file as well: repair is attempted but job 4 declines it
  fail      computes, then exits 3: no repair, not passed
  claim     supplier without kappa in its title: config claim b = 1326789535340266/10^18 must match a JSON
            number literal exactly (parsed as Decimal, not float)
  float     kappa as a JSON number with 17 significant digits that a float would round: exact must be false

usage: test_job5_smoke.py [--keep]
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job5_replays as J5  # noqa: E402

INTEGRITY = '''import hashlib, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
actual={p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.rglob('*')if p.is_file()and p!=ROOT/'MANIFEST.json'and '__pycache__'not in p.parts}
assert actual==read(ROOT/'MANIFEST.json'),'Package manifest mismatch'
'''

WRITE = '''out = Path(sys.argv[1]); out.mkdir(parents=True)
(out / 'RESULT.json').write_text({payload!r})
print('done'); sys.exit({code})
'''


def package(root, name, payload, code=0, integrity=False, manifest_extra=None, manifest_change=None, check_boost=False):
    d = root / 'research' / name
    d.mkdir(parents=True)
    src = INTEGRITY if integrity else 'import json, sys\nfrom pathlib import Path\n'
    if check_boost:
        src += "import os\nassert sys.argv[2:] == ['--boost-include', os.environ['BOOST_INCLUDE']], sys.argv\n"
    (d / 'verify.py').write_text(src + WRITE.format(payload=payload, code=code))
    (d / 'DATA.txt').write_text(f'{name} data\n')
    if integrity:
        m = {p.relative_to(d).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in d.rglob('*') if p.is_file()}
        for k in manifest_extra or []:
            m[k] = '0' * 64
        if manifest_change:
            m[manifest_change] = '1' * 64
        (d / 'MANIFEST.json').write_text(json.dumps(m))


def main():
    keep = '--keep' in sys.argv
    tmp = Path(tempfile.mkdtemp(prefix='job5-smoke-'))
    try:
        repo = tmp / 'upstream'
        repo.mkdir()
        k = '0.0013435180181173090'           # == 1343518018117309/10^18 exactly
        package(repo, 'pass', json.dumps({'kappa': k, 'kappa_next_grid': '0.0013435180181173091',
                                          'complex_lower': '1345325487149526878087/10^24'}), check_boost=True)
        package(repo, 'gitattr', json.dumps({'kappa': '1/1000'}), integrity=True, manifest_extra=['.gitattributes'])
        package(repo, 'changed', json.dumps({'kappa': '1/1000'}), integrity=True, manifest_extra=['.gitattributes'],
                manifest_change='DATA.txt')
        package(repo, 'fail', json.dumps({'kappa': '1/500'}), code=3)
        package(repo, 'claim', '{"b": 0.001326789535340266, "kappa": 0.0012}')
        package(repo, 'float', '{"kappa": 0.0013435180181173091}')
        for cmd in (['init', '-q'], ['add', '-A'], ['-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-q', '-m', 'toy']):
            subprocess.run(['git', '-C', str(repo), *cmd], check=True)
        sha = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
        title = 'Conditional κ = 0.001343518018117309: toy'
        entries = [
            dict(pr=1, title=title, entry='research/pass/verify.py', args=['{OUT}', '--boost-include', '{BOOST}']),
            dict(pr=2, title='Conditional kappa = 0.001: toy', entry='research/gitattr/verify.py', args=['{OUT}']),
            dict(pr=3, title='Conditional kappa = 0.001: toy', entry='research/changed/verify.py', args=['{OUT}']),
            dict(pr=4, title='Conditional κ = 0.002: toy', entry='research/fail/verify.py', args=['{OUT}']),
            dict(pr=5, title='Complex supplier b ≈ 1.327·10⁻³: toy', entry='research/claim/verify.py', args=['{OUT}'],
                 claim=dict(kind='complex_b', value='1326789535340266/1000000000000000000', source='toy')),
            dict(pr=6, title=title, entry='research/float/verify.py', args=['{OUT}']),
        ]
        for e in entries:
            e.update(sha=sha, author='toy', tier='whole-hosting', runner='python')
        cfg = tmp / 'cfg.json'
        cfg.write_text(json.dumps(dict(replays=entries)))
        run = tmp / 'run'
        env = dict(os.environ, BOOST_INCLUDE=str(tmp / 'fake-boost'))
        subprocess.run([sys.executable, '-B', str(HERE / 'job5_replays.py'), '--config', str(cfg), '--clone', str(repo),
                        '--work', str(run), '--python', sys.executable, '--jobs', '6', '--timeout-min', '1'],
                       check=True, env=env)
        rows = {r['pr']: r for r in json.loads((run / 'SUMMARY.json').read_text())['rows']}
        checks = {p: json.loads((run / 'checks' / f'pr-{p}.json').read_text()) for p in rows}
        failures = []

        def expect(cond, what):
            print(('ok   ' if cond else 'FAIL ') + what)
            if not cond:
                failures.append(what)

        r, c = rows[1], checks[1]
        expect(r['passed'] and r['passing_attempt'] == 'as-is' and not r['repair_attempted'], 'pass: as-is, no repair')
        expect(r['claim_exact'] and c['claim_exact_at'] == ['RESULT.json:kappa'], 'pass: trailing-zero decimal equals the title kappa')
        expect(c['claim_close_at'] == ['RESULT.json:kappa_next_grid=0.0013435180181173091'], 'pass: 1e-19 neighbour is close, not exact')
        expect(list(c['complex_b_values']) == ['1345325487149526878087/1000000000000000000000000'], 'pass: b parsed from a/10^24')
        r = rows[2]
        expect(not r['asis_passed'] and r['repair_attempted'] and r['repair_eligible'] and r['repair_passed']
               and r['passing_attempt'] == 'repair (job 4 deviation)' and r['claim_exact'], 'gitattr: as-is fails, repair passes')
        log = (run / 'repair' / 'logs' / 'pr-2.log').read_text()
        expect('# JOB4 DEVIATION' in log and 'remaining_equal=True' in log, 'gitattr: deviation line in repair log')
        expect((run / 'out' / f'pr-2-{sha[:12]}').exists() is False and (run / 'repair' / 'out' / f'pr-2-{sha[:12]}' / 'RESULT.json').exists(),
               'gitattr: as-is and repair outputs are separate')
        r = rows[3]
        expect(not r['passed'] and r['repair_attempted'] and r['repair_eligible'] is False, 'changed: repair declined by job 4')
        r = rows[4]
        expect(not r['passed'] and r['asis_exit'] == 3 and not r['repair_attempted'], 'fail: exit 3, no repair')
        r = rows[5]
        expect(r['passed'] and r['claim_kind'] == 'complex_b' and r['claim_exact'], 'claim: JSON number b matches exactly')
        r = rows[6]
        expect(r['passed'] and not r['claim_exact'] and r['claim_close'], 'float: 17-digit JSON number is close, not exact')
        expect(J5.exact('1/10**3') == Fraction(1, 1000) and J5.exact('3e-3') == Fraction(3, 1000)
               and J5.exact(Decimal('0.25')) == Fraction(1, 4) and J5.exact(0.25) is None and J5.exact(True) is None,
               'exact(): power, scientific, Decimal; floats and booleans refused')
        print(f"\n{len(failures)} failure(s)")
        return 1 if failures else 0
    finally:
        if keep:
            print('kept', tmp)
        else:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
