#!/usr/bin/env python3
"""Joint interval compilation with distinct legal lifetime/reclamation policies.

Uses Avi Eisenberg's pinned interval graph and eumemic's joint compiler. These
variants change equal-rank region schedules and explicitly paid reclamation
choices, beyond the scoped one-strip and nine-piece scalar minima. Every word
is checked on the entire arbitrary-dirty basis in both orientations; actual
matrix profiles and conditional arithmetic remain separate acceptance gates.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import importlib.util
import inspect
import json
from pathlib import Path
import random
import subprocess
import sys
import time

sys.dont_write_bytecode = True


def worker(a):
    assert not a.work.exists()
    a.work.mkdir(parents=True)
    root = a.source.resolve()
    sys.path.insert(0, str(root/'scripts/experiments'))
    import binary_frame_compiler as compiler
    graph_file = root/'research/pair-assembly/pair_graph.py'
    assert sha256(graph_file.read_bytes()).hexdigest() == '3d47e89d2649c90800a276bdd0480131def50e0bdf92c122a19494b55bf17420'
    spec = importlib.util.spec_from_file_location('pinned_interval_graph', graph_file)
    graph = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(graph)
    compiler.graph = graph.graph
    if a.regions:
        sys.path.insert(0, str(Path(__file__).parents[1]/'agents/graph/code'))
        from joint_region_build_hook import install
        original_build = install(a.source, a.work, dict(h=a.h, policy='rank-first', rank_delta=1, sweeps=1, limit=256))
    else:
        original_build = compiler.build

    def build(h):
        built = original_build(h)
        c, blocks, uses, value_uses, owner, signal, old_order, contained = built
        rng = random.Random(a.seed+h)
        tie = {g: rng.random() for g in old_order}
        if a.order == 'reverse':
            order = sorted(old_order, key=lambda g: (blocks[g]['rank'], -min(blocks[g]['nodes'])))
        elif a.order == 'random':
            order = sorted(old_order, key=lambda g: (blocks[g]['rank'], tie[g]))
        elif a.order == 'fanout':
            order = sorted(old_order, key=lambda g: (blocks[g]['rank'], -len(blocks[g]['uses']), min(blocks[g]['nodes'])))
        else:
            order = old_order
        position = {g: i for i, g in enumerate(order)}
        for g, b in enumerate(blocks):
            assert all(position[owner[y]] < position[g] for y in b['inputs']), 'Region dependency reversed'
            assert all(position[g] < position[uses[u][1]] for u, _ in b['candidates']), 'Retained continuation chronology reversed'
        return c, blocks, uses, value_uses, owner, signal, order, contained

    compiler.build = build
    function = inspect.getsource(compiler.compile_)
    assert function.count('for s in sorted(retired):') == 1
    keys = {
        'original': 's',
        'reverse': '-s',
        'highest-rank': "(-blocks[frames[s]]['rank'], s)",
        'same-frame': "(frames[s]!=g, -blocks[frames[s]]['rank'], s)",
        'random': '(lifetime_key(s), s)',
    }
    function = function.replace('for s in sorted(retired):', 'for s in sorted(retired, key=lambda s: '+keys[a.reclaim]+'):')
    namespace = dict(compiler.__dict__)
    namespace['lifetime_key'] = lambda s: ((s*104729+a.seed*13007) % 2147483647)
    exec(compile(function, '<paid-lifetime-variant>', 'exec'), namespace)
    start = time.monotonic()
    result, word = namespace['compile_'](a.h, matching=True, reclaim=True, dirty=True)
    raw = (json.dumps(word, separators=(',', ':'))+'\n').encode()
    packed = a.work/'word.json.gz'
    with packed.open('wb') as f:
        with gzip.GzipFile(fileobj=f, mode='wb', mtime=0) as archive:
            archive.write(raw)
    del word
    from binary_frame_replay import replay
    replayed = replay(packed)
    assert replayed['roles'] == result['roles']
    row = dict(status='DISCOVERY: literal word and complete dirty basis independently replayed',
        h=a.h, order=a.order, reclamation=a.reclaim, seed=a.seed,
        source_revision='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',
        roles=result['roles'], compiled=result, independent_word=replayed,
        word=str(packed), word_sha256=sha256(raw).hexdigest(), gzip_sha256=sha256(packed.read_bytes()).hexdigest(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        elapsed_seconds=time.monotonic()-start,
        acceptance_pending='Actual rational word transitions/CRT, complete child histogram and independent assembly')
    (a.work/'result.json').write_text(json.dumps(row, indent=2)+'\n')
    print(json.dumps({k: row[k] for k in ('status', 'h', 'order', 'reclamation', 'seed', 'roles')}), flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--worker', action='store_true')
    p.add_argument('--regions', action='store_true', help='Apply the exact selective enlarged-region construction before lifetime synthesis.')
    p.add_argument('--h', type=int, choices=[23, 25])
    p.add_argument('--order', choices=['original', 'reverse', 'random', 'fanout'], default='original')
    p.add_argument('--reclaim', choices=['original', 'reverse', 'highest-rank', 'same-frame', 'random'], default='original')
    p.add_argument('--seed', type=int, default=2026100801)
    p.add_argument('--workers', type=int, default=3)
    a = p.parse_args()
    if a.worker:
        assert a.h
        return worker(a)
    assert not a.work.exists() and 1 <= a.workers <= 3
    a.work.mkdir(parents=True)
    jobs = [(h, order, policy, seed) for h in [23, 25]
        for order in ['original', 'reverse', 'random', 'fanout']
        for policy in ['original', 'highest-rank', 'same-frame', 'reverse', 'random']
        for seed in ([2026100881, 2026100887] if order == 'random' or policy == 'random' else [2026100881])]
    def execute(job):
        h, order, policy, seed = job
        name = f'h{h}-{order}-{policy}-s{seed}'
        work = a.work/name
        command = [sys.executable, '-u', __file__, '--worker', '--source', str(a.source), '--work', str(work),
            '--h', str(h), '--order', order, '--reclaim', policy, '--seed', str(seed)]
        if a.regions:
            command.append('--regions')
        with (a.work/(name+'.log')).open('wb') as log:
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            print(json.dumps(dict(status='COMPILER RUNNING', pid=process.pid, command=command)), flush=True)
            rc = process.wait()
        if rc:
            return dict(case_id=name, status='REJECTED', exit_code=rc, log=str(a.work/(name+'.log')))
        result = json.loads((work/'result.json').read_text())
        return dict(case_id=name, status=result['status'], h=h, roles=result['roles'], result=str(work/'result.json'))
    rows = []
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        pending = {pool.submit(execute, job): job for job in jobs}
        for future in as_completed(pending):
            rows.append(future.result())
            status = dict(utc=datetime.now(timezone.utc).isoformat(), completed=len(rows), total=len(jobs), workers=a.workers,
                accepted_for_further_profile=sum(x['status']!='REJECTED' for x in rows),
                best_roles={str(h): min((x['roles'] for x in rows if x.get('h')==h), default=None) for h in [23,25]})
            (a.work/'status.json').write_text(json.dumps(status, indent=2)+'\n')
            print(json.dumps(status), flush=True)
    (a.work/'results.json').write_text(json.dumps(dict(status='COMPLETE', rows=rows), indent=2)+'\n')


if __name__ == '__main__':
    main()
