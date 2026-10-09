#!/usr/bin/env python3
"""Independent adversarial checks; every publication operation is in-memory.

No real Git write, GitHub query, fork, push, PR command, or publishing CLI runs.
The author fixture is imported solely to supply synthetic local input/backend.
"""
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

PUBLICATION_CODE = Path(__file__).resolve().parents[2] / 'publication' / 'code'
sys.path.insert(0, str(PUBLICATION_CODE))
import publication_runtime as runtime
from test_publication import Fixture, FakeRunner


class IndexMutationRunner(FakeRunner):
    """A successful pinned checker adds an unexpected file to the index."""
    def run(self, args, **kwargs):
        result = super().run(args, **kwargs)
        if args[:2] == ['python3', 'tests/inherited.py']:
            self.extra_staged_path = 'unrelated.py'
        return result


class IndependentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='independent-publication-',
                                                   dir=os.environ.get('PUBLICATION_REVIEW_WORK'))
        self.fixture = Fixture(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_successful_checker_cannot_add_staged_paths(self):
        self.fixture.persist()
        runner = IndexMutationRunner(self.fixture)
        publisher = runtime.Publisher(self.fixture.package, self.fixture.workspace, runner)
        publisher.spec['synthetic_test_only'] = False
        runner.publisher = publisher
        with self.assertRaisesRegex(runtime.Stop, 'allowlist|staged|index'):
            publisher.execute('publish')
        self.assertEqual(runner.writes, [], 'Checker index mutation must stop before any mock GitHub write')

    def test_successful_checker_cannot_change_index_blob_or_mode(self):
        for mutation in ('blob', 'mode'):
            publisher, runner = self.fixture.publisher()
            original = runner.run
            def run(args, **kwargs):
                result = original(args, **kwargs)
                if args[:2] == ['python3', 'tests/inherited.py']:
                    name = publisher.spec['changes'][0]['path']
                    if mutation == 'blob':
                        runner.index_blobs[name] = b'changed index, unchanged working bytes'
                    else:
                        runner.index_modes[name] = '100755'
                return result
            runner.run = run
            with self.assertRaises(runtime.Stop):
                publisher.execute('publish')
            self.assertEqual(runner.writes, [])

    def test_corrupted_commit_bytes_stop_before_push(self):
        publisher, runner = self.fixture.publisher()
        original = runner.run
        def run(args, **kwargs):
            result = original(args, **kwargs)
            if args[0] == 'git' and 'commit' in args:
                runner.index_blobs[publisher.spec['changes'][0]['path']] = b'bad committed bytes'
            return result
        runner.run = run
        with self.assertRaisesRegex(runtime.Stop, 'Committed publication bytes'):
            publisher.execute('publish')
        self.assertFalse(any(call[:2] == ['git', 'push'] for call in runner.calls))
        self.assertFalse(any(call[:3] == ['gh', 'pr', 'create'] for call in runner.calls))

    def test_corrupted_remote_content_stops_before_pr(self):
        publisher, runner = self.fixture.publisher()
        original = runner.run
        def run(args, **kwargs):
            result = original(args, **kwargs)
            if args[:2] == ['git', 'push']:
                name = publisher.spec['changes'][0]['path']
                runner.certificates[('fixture-user/integer-mult-bounds', self.fixture.submit_sha,
                                     name)] = b'corrupted remote candidate'
            return result
        runner.run = run
        with self.assertRaisesRegex(runtime.Stop, 'fingerprint changed'):
            publisher.execute('publish')
        self.assertFalse(any(call[:3] == ['gh', 'pr', 'create'] for call in runner.calls))

    def test_changed_default_branch_stops_before_writes(self):
        publisher, runner = self.fixture.publisher()
        original = runner.run
        def run(args, **kwargs):
            if args[:3] == ['gh', 'api', 'repos/' + runtime.UPSTREAM]:
                return b'{"full_name":"CrocSwap/integer-mult-bounds","default_branch":"changed"}'
            return original(args, **kwargs)
        runner.run = run
        with self.assertRaisesRegex(runtime.Stop, 'default branch changed'):
            publisher.execute('publish')
        self.assertEqual(runner.writes, [])

    def test_inconsistent_active_state_and_missing_claim_close_gate(self):
        for mutation in ('closed', 'merged', 'absent'):
            publisher, runner = self.fixture.publisher()
            if mutation == 'closed':
                runner.prs[0]['state'] = 'closed'
            elif mutation == 'merged':
                runner.prs[0]['merged_at'] = '2026-10-09T00:00:00Z'
            else:
                runner.prs = []
            with self.assertRaises(runtime.Stop):
                publisher.execute('publish')
            self.assertEqual(runner.writes, [])

    def test_changed_certified_upper_bound_claim_stops_before_writes(self):
        publisher, runner = self.fixture.publisher()
        rule = publisher.spec['frontier_rules']['claims'][0]
        rule['certified_upper_bound'], rule['exact_kappa'] = rule['exact_kappa'], None
        runner.prs[0]['body'] += ' New stronger value.'
        with self.assertRaisesRegex(runtime.Stop, 'body changed'):
            publisher.execute('publish')
        self.assertEqual(runner.writes, [])

    def test_downloaded_corrupt_dependency_never_reaches_check(self):
        data = b'# pinned synthetic dependency\n'
        item = {'path': 'inherited/source.py', 'sha256': runtime.digest(data), 'mode': 0o644,
                'before_sha256': None, 'acquire': {
                    'repository': 'source/integer-mult-bounds', 'ref': '5' * 40,
                    'path': 'inherited/source.py', 'decoded_sha256': runtime.digest(data)}}
        self.fixture.spec['changes'].append(item)
        publisher, runner = self.fixture.publisher()
        runner.certificates[('source/integer-mult-bounds', '5' * 40, item['path'])] = b'# corrupted\n'
        with self.assertRaisesRegex(runtime.Stop, 'fingerprint changed'):
            publisher.execute('publish')
        self.assertFalse(any(call[0] == 'python3' for call in runner.calls))
        self.assertEqual(runner.writes, [])

    def test_duplicate_marker_with_changed_content_is_not_success(self):
        publisher, runner = self.fixture.publisher()
        candidate = copy.deepcopy(runner.prs[0])
        candidate.update(number=888, body=publisher.marker, user={'login': 'fixture-user'},
                         html_url=f'https://github.com/{runtime.UPSTREAM}/pull/888')
        candidate['head'] = {'sha': self.fixture.submit_sha,
                             'repo': {'full_name': 'fixture-user/integer-mult-bounds'}}
        runner.closed.append(candidate)
        for item in publisher.spec['changes']:
            runner.certificates[('fixture-user/integer-mult-bounds', self.fixture.submit_sha,
                                 item['path'])] = b'changed candidate, same marker'
        with self.assertRaisesRegex(runtime.Stop, 'fingerprint changed'):
            publisher.execute('publish')
        self.assertEqual(runner.writes, [])

    def test_duplicate_marker_with_changed_mode_is_not_success(self):
        publisher, runner = self.fixture.publisher()
        candidate = copy.deepcopy(runner.prs[0])
        candidate.update(number=888, body=publisher.marker, user={'login': 'fixture-user'},
                         html_url=f'https://github.com/{runtime.UPSTREAM}/pull/888')
        candidate['head'] = {'sha': self.fixture.submit_sha,
                             'repo': {'full_name': 'fixture-user/integer-mult-bounds'}}
        runner.closed.append(candidate)
        runner.remote_mode_mutation = True
        with self.assertRaisesRegex(runtime.Stop, 'Remote candidate file mode'):
            publisher.execute('publish')
        self.assertEqual(runner.writes, [])

    def test_truncated_remote_tree_stops_before_pr(self):
        publisher, runner = self.fixture.publisher()
        original = runner.run
        def run(args, **kwargs):
            if args[:2] == ['gh', 'api'] and '/git/trees/' in args[2]:
                return json.dumps({'truncated': True, 'tree': []}).encode()
            return original(args, **kwargs)
        runner.run = run
        with self.assertRaisesRegex(runtime.Stop, 'tree is truncated or unresolved'):
            publisher.execute('publish')
        self.assertFalse(any(call[:3] == ['gh', 'pr', 'create'] for call in runner.calls))

    def test_fork_api_failure_is_not_treated_as_missing_fork(self):
        publisher, runner = self.fixture.publisher()
        runner.fail_prefix = ['gh', 'api', 'repos/fixture-user/integer-mult-bounds']
        with self.assertRaises(runtime.CommandFailure):
            publisher.execute('publish')
        self.assertEqual(runner.writes, [])
        self.assertFalse(any(call[:3] == ['gh', 'repo', 'fork'] for call in runner.calls))

    def test_failed_pr_and_malformed_success_output_never_report_success(self):
        for output in (b'', b'https://github.com/other/repo/pull/999\n',
                       b'https://github.com/CrocSwap/integer-mult-bounds/pull/999\nwarning\n'):
            publisher, runner = self.fixture.publisher()
            original = runner.run
            def run(args, **kwargs):
                if args[:3] == ['gh', 'pr', 'create']:
                    return output
                return original(args, **kwargs)
            runner.run = run
            with self.assertRaisesRegex(runtime.Stop, 'no unambiguous actual URL'):
                publisher.execute('publish')
            self.assertFalse(any(message.startswith('Created pull request:') for message in runner.messages))

    def test_submission_has_unique_branch_and_no_force_or_upstream_push(self):
        publisher, runner = self.fixture.publisher()
        publisher.execute('publish')
        checkout = next(call for call in runner.calls if call[:3] == ['git', 'checkout', '-b'])
        self.assertRegex(checkout[3], r'^submission/synthetic-fixture-7{12}-[0-9a-f]{12}$')
        pushes = [call for call in runner.calls if call[:2] == ['git', 'push']]
        self.assertEqual(len(pushes), 1)
        self.assertEqual(pushes[0][3], 'submission')
        self.assertFalse(any('--force' in item or item.startswith('+') for item in pushes[0]))
        remote = next(call for call in runner.calls if call[:3] == ['git', 'remote', 'add'])
        self.assertEqual(remote[-1], 'https://github.com/fixture-user/integer-mult-bounds.git')


if __name__ == '__main__':
    unittest.main(verbosity=2)
