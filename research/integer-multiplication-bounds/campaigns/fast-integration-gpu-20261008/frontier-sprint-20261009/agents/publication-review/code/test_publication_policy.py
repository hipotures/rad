#!/usr/bin/env python3
"""Independent exact 1% policy audit. All Git/GitHub writes are in-memory.

Final-guard tests isolate submit() after mocked preparation to reach its second
frontier check even when the candidate would fail the earlier production guard.
This is test-only Python object construction, never a real publishing CLI.
"""
import copy
import json
import os
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

PUBLICATION_CODE = Path(__file__).resolve().parents[2] / 'publication' / 'code'
sys.path.insert(0, str(PUBLICATION_CODE))
import build_publication as builder
import publication_runtime as runtime
from test_publication import Fixture


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='policy-audit-',
                                               dir=os.environ.get('PUBLICATION_REVIEW_WORK'))
        self.fixture = Fixture(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def values(top):
        exact = Fraction(101, 100) * top
        return [(exact - Fraction(1, 10**30), False), (exact, True),
                (exact + Fraction(1, 10**30), True)]

    def set_comparison(self, spec, source_kind):
        if source_kind == 'retained':
            top = Fraction(3, 5000)
            spec['frontier_rules']['retained_main']['exact_kappa'] = str(top)
        else:
            top = Fraction(1, 2000)
            if source_kind == 'rounded_upper_bound':
                rule = spec['frontier_rules']['claims'][0]
                rule['exact_kappa'] = None
                rule['certified_upper_bound'] = str(top)
                rule['assessment_scope'] = 'Synthetic conservative bound for rounded claim'
        return top

    def sync_retained_certificate(self, publisher, runner):
        retained = publisher.spec['frontier_rules']['retained_main']
        data = json.dumps({'kappa': retained['exact_kappa']}).encode()
        source = retained['certificate_sources'][0]
        source['decoded_sha256'] = runtime.digest(data)
        runner.certificates[(source['repository'], source['ref'], source['path'])] = data

    def test_builder_below_equal_above_exact_active_bound_and_retained(self):
        for kind in ('active_exact', 'rounded_upper_bound', 'retained'):
            spec = copy.deepcopy(self.fixture.spec)
            top = self.set_comparison(spec, kind)
            for candidate, allowed in self.values(top):
                spec['exact_kappa'] = str(candidate)
                if allowed:
                    builder.validate_spec(copy.deepcopy(spec), self.fixture.payload)
                else:
                    with self.assertRaisesRegex(runtime.Stop, 'below the exact 1%'):
                        builder.validate_spec(copy.deepcopy(spec), self.fixture.payload)

    def test_initial_execution_guard_below_equal_above_all_comparison_kinds(self):
        for kind in ('active_exact', 'rounded_upper_bound', 'retained'):
            top = self.set_comparison(copy.deepcopy(self.fixture.spec), kind)
            for candidate, allowed in self.values(top):
                publisher, runner = self.fixture.publisher()
                self.set_comparison(publisher.spec, kind)
                self.sync_retained_certificate(publisher, runner)
                publisher.spec['exact_kappa'] = str(candidate)
                if allowed:
                    result = publisher.execute('--dry-run')
                    self.assertEqual(result['frontier']['minimum_required_kappa'],
                                     str(Fraction(101, 100) * top))
                else:
                    with self.assertRaisesRegex(runtime.Stop, 'below the exact 1%'):
                        publisher.execute('publish')
                    self.assertFalse(any(call[:2] == ['git', 'clone'] for call in runner.calls))
                self.assertEqual(runner.writes, [])

    def test_final_submit_guard_below_equal_above_all_comparison_kinds(self):
        for kind in ('active_exact', 'rounded_upper_bound', 'retained'):
            top = self.set_comparison(copy.deepcopy(self.fixture.spec), kind)
            for candidate, allowed in self.values(top):
                publisher, runner = self.fixture.publisher()
                self.set_comparison(publisher.spec, kind)
                self.sync_retained_certificate(publisher, runner)
                publisher.spec['exact_kappa'] = str(candidate)
                publisher.authenticate()
                publisher.prepare()
                fork = publisher.own_fork()
                if allowed:
                    result = publisher.submit(fork, {})
                    self.assertFalse(result['duplicate'])
                    body = (publisher.workspace / 'pull-request-body.md').read_text()
                    self.assertIn(str(Fraction(101, 100) * top), body)
                else:
                    with self.assertRaisesRegex(runtime.Stop, 'below the exact 1%'):
                        publisher.submit(fork, {})
                    self.assertFalse(any(call[:3] == ['gh', 'pr', 'create'] for call in runner.calls))
                self.assertTrue(any(call[:2] == ['git', 'push'] for call in runner.calls))

    def test_absent_weaker_and_noncanonical_policy_fails_builder_initial_and_final(self):
        for value in (None, '0', '1/1000', '1/101', '2/200'):
            spec = copy.deepcopy(self.fixture.spec)
            if value is None:
                spec.pop('minimum_relative_improvement')
            else:
                spec['minimum_relative_improvement'] = value
            with self.assertRaisesRegex(runtime.Stop, 'immutably require at least 1%'):
                builder.validate_spec(spec, self.fixture.payload)
            publisher, runner = self.fixture.publisher()
            if value is None:
                publisher.spec.pop('minimum_relative_improvement')
            else:
                publisher.spec['minimum_relative_improvement'] = value
            with self.assertRaisesRegex(runtime.Stop, 'at least 1% relative'):
                publisher.execute('publish')
            self.assertEqual(runner.calls, [], 'Invalid policy must stop before even authentication')
            publisher, runner = self.fixture.publisher()
            publisher.authenticate()
            publisher.prepare()
            if value is None:
                publisher.spec.pop('minimum_relative_improvement')
            else:
                publisher.spec['minimum_relative_improvement'] = value
            with self.assertRaisesRegex(runtime.Stop, 'at least 1% relative'):
                publisher.submit(publisher.own_fork(), {})
            self.assertFalse(any(call[:3] == ['gh', 'pr', 'create'] for call in runner.calls))

    def test_final_current_top_head_body_or_unknown_claim_change_stops(self):
        for change in ('head', 'body', 'unknown'):
            publisher, runner = self.fixture.publisher()
            original = runner.run
            def run(args, **kwargs):
                # On the final fresh open-page read after the mock push, mutate
                # current observations without changing immutable frozen rules.
                if args[:2] == ['gh', 'api'] and 'pulls?state=open' in args[2] and runner.remote_commit:
                    if change == 'head':
                        runner.prs[0]['head']['sha'] = '8' * 40
                    elif change == 'body':
                        runner.prs[0]['body'] += ' Increased final claim.'
                    else:
                        item = copy.deepcopy(runner.prs[0])
                        item['number'] = 9999
                        runner.prs.append(item)
                return original(args, **kwargs)
            runner.run = run
            with self.assertRaises(runtime.Stop):
                publisher.execute('publish')
            self.assertTrue(any(call[:2] == ['git', 'push'] for call in runner.calls))
            self.assertFalse(any(call[:3] == ['gh', 'pr', 'create'] for call in runner.calls))

    def test_global_push_destination_rewrite_stops_before_remote_write(self):
        publisher, runner = self.fixture.publisher()
        runner.rewrite_remote = True
        with self.assertRaisesRegex(runtime.Stop, 'rewrites submission destination'):
            publisher.execute('publish')
        self.assertFalse(any(call[:2] == ['git', 'push'] for call in runner.calls))
        self.assertFalse(any(call[:3] == ['gh', 'pr', 'create'] for call in runner.calls))

    def test_live_score_threshold_is_dynamic_exact_fraction(self):
        # Alleged latest score is fixture arithmetic only; not a verified live PR.
        top = Fraction(6105562, 10**10)
        threshold = top * Fraction(101, 100)
        self.assertEqual(threshold, Fraction(616661762, 10**12))
        publisher, runner = self.fixture.publisher()
        rule = publisher.spec['frontier_rules']['claims'][0]
        rule['exact_kappa'] = str(top)
        data = json.dumps({'kappa': str(top)}).encode()
        source = rule['certificate_source']
        source['decoded_sha256'] = runtime.digest(data)
        runner.certificates[(source['repository'], source['ref'], source['path'])] = data
        publisher.spec['exact_kappa'] = str(threshold)
        result = publisher.frontier(runner.prs)
        self.assertEqual(result['minimum_required_kappa'], str(threshold))
        self.assertEqual(result['maximum'], str(top))
        self.assertEqual(result['achieved_relative_improvement'], '1/100')
        self.assertEqual(runner.writes, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
