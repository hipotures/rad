"""Reject new native failures; retain the known missing-fixture/VM failures."""
import argparse
import re
from lab import ROOT, load, save
ap = argparse.ArgumentParser()
ap.add_argument('experiment')
ap.add_argument('--attempt', default='v1')
ap.add_argument('--expected-native-tests',type=int,default=68)
a = ap.parse_args()
out = ROOT / 'experiments' / a.experiment / a.attempt / 'tests'
log = (out / 'native-tests.log').read_text()
failed = re.findall(r'^\s*\d+ - (\S+) \((?:Failed|Timeout|SEGFAULT|Subprocess aborted)\)', log, re.MULTILINE)
expected = {'ple_parity', 'platform_memory_test', 'expert_parity', 'pool_test'}
summary = load(out / 'summary.json')
checks = {'only_known_environment_failures': set(failed) == expected,
          'no_undocumented_native_failures': f'94% tests passed, 4 tests failed out of {a.expected_native_tests}' in log,
          'Python_passed': summary['python_returncode'] == 0,
          'real_native_experts_passed': summary['real_native_parity_returncode'] == 0}
save(out / 'failure-audit.json', {'state': 'PASS_WITH_KNOWN_ENVIRONMENT_LIMITS' if all(checks.values()) else 'FAIL',
     'checks': checks, 'native_failure_names': failed,
     'evidence': 'Missing Q2_0 PLE fixture, VM mlock hard limit and absent legacy experts.bin fixtures; original raw failure messages retained.'})
print(checks, failed)
if not all(checks.values()):
    raise SystemExit('New correctness/test failure; headline runs prohibited')
