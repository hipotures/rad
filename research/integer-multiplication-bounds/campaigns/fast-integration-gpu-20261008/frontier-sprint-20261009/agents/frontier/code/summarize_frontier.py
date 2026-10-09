#!/usr/bin/env python3
"""Preserve a manually assessed frontier, binding each statement to gh receipts.

The lower-claim envelope is a scoped manual assessment of current bodies, not
an automated title parser or mathematical certification of those submissions.
"""
import argparse
import base64
import collections
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

sys.set_int_max_str_digits(0)
ROOT = Path(__file__).resolve().parents[3]


def read(path):
    return json.loads(path.read_text())


def decoded(path):
    return base64.b64decode(read(path)['content']).decode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--intake', type=Path, required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--lower-envelope-assessed', action='store_true', required=True)
    args = parser.parse_args()
    args.intake = args.intake.resolve()
    args.sources = args.sources.resolve()
    intake = read(args.intake)
    assert intake['complete']
    sources = args.sources
    manifest = read(sources / 'manifest.json')
    assert manifest['complete']
    assert intake['default_commit'] == manifest['default_commit']
    open_prs = sum(intake['open_pages'], [])
    if any(pr['number'] > 161 for pr in open_prs):
        raise RuntimeError('New PR beyond original assessment: source-aware manual update required; never reuse the old envelope')
    closed_prs = sum(intake['closed_pages'], [])
    selected = json.loads(decoded(sources / 'main-selected-result-json.json'))
    claims = []
    scope = ('Retained #144 analytic, semantic, ordinary-leaf, uniform-recursion, '
             'weighted-child, completed-core sharing and fixed-tape interfaces; '
             'finite/written conditional witness, not an unconditional theorem.')
    for pr in sorted(open_prs, key=lambda pr: pr['number'], reverse=True):
        number = pr['number']
        row = {'pr': number, 'url': pr['html_url'], 'author': pr['user']['login'],
               'head_sha': pr['head']['sha'], 'state': pr['state'], 'draft': pr['draft'],
               'merged': bool(pr['merged_at']), 'updated_at': pr['updated_at'],
               'title': pr['title'], 'body_sha256': hashlib.sha256((pr['body'] or '').encode()).hexdigest(),
               'title_sha256': hashlib.sha256(pr['title'].encode()).hexdigest(), 'exact_kappa': None, 'certificate_source': None,
               'construction_family': 'Historical retained conditional construction; see pinned body',
               'conditional_assumptions': 'Inherited interfaces as stated in pinned body; not independently certified here',
               'evidence_observed': ['Current body, title and source-head metadata in complete paginated intake'],
               'comparability': 'No stronger final kappa seen in current body; historical source not recertified',
               'conservative_comparison_upper_bound': '13/25000',
               'bound_basis': 'Manual body assessment: lower final-kappa claims are below 0.00052, with wide allowance for rounded titles and body/title drift',
               'author_reported_reproduction': 'Not individually classified',
               'hosted_checks': 'Not inspected in this source receipt',
               'scoped_lean_coverage': 'No new result-specific formal coverage claimed by this scout',
               'maintainer_review': 'Not inspected or established for this current head'}
        if number in (161, 160):
            current = read(sources / f'pr{number}-metadata.json')
            assert current['head']['sha'] == pr['head']['sha'], 'Head changed: refresh source receipts'
            cert = json.loads(decoded(sources / f'pr{number}-certificate.json'))
            Fraction(cert['kappa'])
            row.update(exact_kappa=cert['kappa'], certificate_source={
                'path': 'certificates/paired-cube-network.json', 'repository': pr['head']['repo']['full_name'],
                'ref': pr['head']['sha'], 'receipt': str((sources / f'pr{number}-certificate.json').relative_to(ROOT)),
                'decoded_sha256': hashlib.sha256(decoded(sources / f'pr{number}-certificate.json').encode()).hexdigest()},
                construction_family=('Paired-cube complex merged outputs with annealed pair modules, physical frames and late-read reuse; annealed p12 paired-cube bit supplier; phase stop 1e-9' if number == 161 else 'Paired-cube p11 searched bit pair module composed with unchanged #157 physical complex supplier'),
                conditional_assumptions=scope,
                comparability='Comparable conditional retained-framework claim; unreviewed, included in publication threshold',
                conservative_comparison_upper_bound=None, bound_basis='Exact final kappa in pinned certificate, reconciled with current body',
                author_reported_reproduction=('Completed focused checks, maintainer entry-point tests and full make verify, reported by author; not freshly reproduced by this scout' if number == 161 else 'Completed focused bit regeneration/checker/moment and make paired-cube-verify, reported by author; broader reproduction not claimed complete'),
                maintainer_review='No PR review records at source observation; retained predecessor review does not review this head')
            runs = [run for page in read(sources / f'pr{number}-checks.json') for run in page['check_runs']]
            row['hosted_checks'] = {'observed_utc': manifest['completed_utc'], 'head_sha': pr['head']['sha'],
                'total': len(runs), 'summary': {str(k): v for k,v in collections.Counter((run['status'], run['conclusion']) for run in runs).items()},
                'scope': 'Named GitHub check runs, not independent human review or full multiplication formalization',
                'receipt': str((sources / f'pr{number}-checks.json').relative_to(ROOT))}
            row['evidence_observed'].append('Decoded exact certificate and current-head check runs; comments, files and PR review collection')
        elif number == 158:
            row.update(exact_kappa='1111463/2000000000', certificate_source={
                'path': 'research/paired-cube-toll-edge/verify.py', 'repository': pr['head']['repo']['full_name'],
                'ref': pr['head']['sha'], 'receipt': str((sources/'pr158-verify-py.json').relative_to(ROOT))},
                construction_family='Retained #157 paired cubes with re-instantiated atom exponent on exact toll edge',
                conditional_assumptions=scope, conservative_comparison_upper_bound=None,
                bound_basis='Exact body rational plus inspected source-bound verifier; no separate static final certificate',
                comparability='Comparable conditional retained-framework claim; included even without hosted checks',
                author_reported_reproduction='Author reports focused stdlib verifier reproducing predecessor, strict toll, 47 constraints and seven margins',
                hosted_checks='No upstream check runs observed in source receipt')
        elif number in (154, 101, 90):
            row.update(conservative_comparison_upper_bound=None, bound_basis='No new exponent claim; verification or documentation change', comparability='No new final-kappa claim')
        claims.append(row)
    leader = next(row for row in claims if row['pr'] == 161)
    reviewed = {'pr': selected['source_pr'], 'author': 'icekylinx', 'head_sha': selected['reviewed_head'],
                'retained_at_main_sha': intake['default_commit'], 'state': 'closed', 'draft': False, 'merged': True,
                'exact_kappa': selected['kappa'], 'certificate_source': selected['certificate'],
                'construction_family': 'Paired cubes and shared completed cores', 'conditional_assumptions': selected['scope'],
                'evidence_observed': ['Main selected-result record, README, written round-six maintainer review and validation receipt'],
                'review_scope': 'Scoped maintainer finite-construction, arithmetic and written dependency audit; not independent human peer review or a full formal proof',
                'integration_repairs': selected['integration_repairs'],
                'source_receipts': str(sources.relative_to(ROOT))}
    history = []
    for pr in sorted(closed_prs, key=lambda pr: pr['number'], reverse=True):
        history.append({'pr': pr['number'], 'author': pr['user']['login'], 'head_sha': pr['head']['sha'],
                        'state': pr['state'], 'merged': bool(pr['merged_at']), 'draft': pr['draft'], 'title': pr['title'],
                        'disposition': ('Excluded: current body explicitly says false data led to bad verification' if pr['number']==156 else
                                        'Excluded: closed spoof submission; sole five-line file explicitly intended to fool AI progress trackers; no mathematical certificate' if pr['number']==159 else
                                        'Superseded by #161, explicit #161 body; closed, retained historical claim' if pr['number'] in (155,157) else
                                        'Closed historical claim retained; see pinned body for withdrawal or review'),
                        'evidence': 'Complete closed-page receipt; for #159 also work/receipts/pr159-files.json'})
    result = {'schema_version': 1, 'observed_utc': intake['completed_utc'],
              'source_evidence_observed_utc': manifest['completed_utc'],
              'upstream': 'CrocSwap/integer-mult-bounds', 'default_branch': intake['repository']['default_branch'],
              'default_commit': intake['default_commit'], 'collection_complete': True,
              'open_pages': len(intake['open_pages']), 'open_count': len(open_prs), 'drafts_included': True,
              'intake_receipt': str(args.intake.relative_to(ROOT)),
              'intake_sha256': hashlib.sha256(args.intake.read_bytes()).hexdigest(),
              'highest_active_comparable_public_claim': {'pr':161,'head_sha':leader['head_sha'],'exact_kappa':leader['exact_kappa']},
              'strongest_completed_reported_reproduction': {'pr':161,'head_sha':leader['head_sha'],'exact_kappa':leader['exact_kappa'],
                  'evidence_kind':'Author-reported full make verify plus 45 current-head hosted checks; scout did not independently rerun mathematics'},
              'retained_maintainer_reviewed_result': reviewed,
              'publication_comparison_threshold': leader['exact_kappa'],
              'comparison_resolved': True,
              'resolution_scope': 'Current public numerical claims in complete intake, inspected leader certificates and manually bounded lower bodies; no global optimality or independent validity certification of every PR',
              'lower_claim_envelope': '13/25000', 'claims': claims, 'closed_history': history,
              'limitations': ['Observation is time-bounded; refresh before freeze and handoff',
                             'Inherited analytic and transfer interfaces remain assumptions',
                             'Main selected record establishes retained review; empty GitHub review arrays are not a substitute for written maintainer review',
                             'PR160 old 628fcab source-hash CI failure is historical and cannot be attributed to da338531 current head',
                             'No newly submitted final-kappa result is proved by inherited scoped Lean packages alone']}
    assert Fraction(result['publication_comparison_threshold']) > Fraction(reviewed['exact_kappa'])
    assert Fraction(result['publication_comparison_threshold']) > Fraction(result['lower_claim_envelope'])
    (ROOT/'public-frontier.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key: result[key] for key in ['observed_utc','open_count','default_commit','publication_comparison_threshold','comparison_resolved']}))


if __name__ == '__main__':
    main()
