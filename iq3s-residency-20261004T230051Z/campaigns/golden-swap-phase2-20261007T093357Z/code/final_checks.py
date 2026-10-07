"""Check retained table consistency and document links without rerunning a point."""
import csv, hashlib, math, re, statistics
from common import *

if __name__ == '__main__':
    no_gpu()
    modules = list((C / 'code').glob('*.py'))
    for path in modules:
        compile(path.read_text(), str(path), 'exec')
    rows = load(C / 'results/live-attempts.json')
    main = [r for r in rows if r.get('kind') == 'main']
    assert len(main) == 48 and all(r['valid'] for r in main)
    expected_tokens = {'code-archive': 2048, 'math-inventory': 2048,
                       'text-websocket': 1773, 'mixed-chinook': 2048}
    paired = load(C / 'results/paired-blocks.json')
    main_pairs = [r for r in paired if r['task'] in expected_tokens]
    assert len(main_pairs) == 24
    for p in main_pairs:
        group = [r for r in main if r['task'] == p['task'] and r['block'] == p['block']]
        assert len(group) == 4
        current = next(r for r in group if r['arm'] == 'REPLAY_CURRENT')
        full = next(r for r in group if r['arm'] == 'ORACLE_FULL')
        candidate = next(r for r in group if r['arm'] == p['arm'])
        assert math.isclose(candidate['tok_s'] * candidate['decode_s'], expected_tokens[p['task']], rel_tol=1e-12)
        assert math.isclose(p['TG_ratio'], candidate['tok_s'] / current['tok_s'], rel_tol=1e-12)
        assert math.isclose(p['wall_ratio'], candidate['wall_s'] / current['wall_s'], rel_tol=1e-12)
        saving = current['decode_s'] - full['decode_s']
        expected = (current['decode_s'] - candidate['decode_s']) / saving if saving > 0 else None
        assert p['retention'] == expected
    summaries = {(r['task'], r['arm']): r for r in load(C / 'results/main-summary.json')}
    with (C / 'results/primary-table.csv').open(newline='') as f:
        table = list(csv.DictReader(f))
    assert len(table) == 16 and len({(r['task'], r['arm']) for r in table}) == 16
    for r in table:
        s = summaries[r['task'], r['arm']]
        assert int(r['valid']) == int(r['attempts']) == 3
        for field in ['tok_s', 'paired_TG_pct', 'paired_wall_pct', 'retention']:
            assert math.isclose(float(r[field + '_median']), s[field]['median'], rel_tol=1e-12, abs_tol=1e-12)
        if r['arm'] in ['ORACLE_IN_HISTORY_TC', 'ORACLE_IN_LOGISTIC_TC']:
            points = [p for p in main_pairs if (p['task'], p['arm']) == (r['task'], r['arm'])]
            criterion = (statistics.median(1-p['decode_ratio'] for p in points) > .03
                         and sum(p['decode_ratio'] < 1 for p in points) >= 2
                         and statistics.median(p['wall_ratio'] for p in points) <= 1.01
                         and sum(p['wall_ratio'] > 1.03 for p in points) < 2)
            assert s['meets_gain_criterion'] == criterion
    links = []
    for document in [C/'README.md', C/'report.md', C/'reproduce.md']:
        for target in re.findall(r'\]\(([^)]+)\)', document.read_text()):
            if target.startswith(('http:', 'https:', '#')):
                continue
            path = (document.parent / target.split('#', 1)[0]).resolve()
            assert path.exists(), (document, target)
            links.append(str(path.relative_to(C.resolve())))
    model_sha = hashlib.sha256((C/'models/logistic.txt').read_bytes()).hexdigest()
    assert model_sha == '065afa1eec792a5dc2408165d3ecf0206eccce27ccca23da09b4855a5a3a229e'
    save(C/'tests/final-result-consistency.json', {
        'state': 'PASS', 'python_modules_compiled': len(modules),
        'main_points': len(main), 'paired_candidate_rows_checked': len(main_pairs),
        'primary_csv_rows_checked': len(table), 'local_document_links_checked': len(links),
        'actual_token_denominators': expected_tokens, 'frozen_checkpoint_sha256': model_sha,
        'scope': 'Retained-result arithmetic, frozen criterion, CSV/JSON and link consistency; no new timing attempt.'})
    ledger('Final result consistency PASS', main_points=len(main), primary_csv_rows=len(table))
    print('FINAL_RESULT_CONSISTENCY_PASS', flush=True)
