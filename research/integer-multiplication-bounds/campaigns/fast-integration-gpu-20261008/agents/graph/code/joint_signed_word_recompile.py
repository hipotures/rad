#!/usr/bin/env python3
"""Joint synthesis using signed frames constrained by an existing exact word.

Pinned interval DAG: Avi Eisenberg PR62. Pinned invertible binary compiler,
linear/partition matroid intersection and paid reclamation: eumemic PR57.
This experiment transfers actual-word signed address constraints back to
scalar nodes, optionally merges identical enlarged spaces, and synthesizes
a NEW invertible word. It does not replay a same-role address substitution
as if that were a new joint synthesis. Scalar-only positive labels and
pivot-only Gaussian reorderings are not used.
"""
import argparse
from collections import defaultdict, deque
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import heapq
from itertools import combinations
import json
from pathlib import Path
import sqlite3
import sys
import time

from check_compiled_witness import contained
import joint_region_search_v3 as region
from joint_word_positive_closure import extend
from joint_word_check_v4 import check

WORK = None
CACHE = {}


def initialize(source, work):
    global WORK
    WORK = Path(work)
    region.initialize(source, work)


def prepare(document):
    key = document['id']
    if key in CACHE:
        return CACHE[key]
    h = document['h']
    config = document['configuration']
    config = {k:v for k,v in config.items() if k != 'kind'}
    c, blocks, uses, value_uses, owner, signal, order, fits = region.build_regions(h, config)
    if document.get('word_path'):
        raw = gzip.decompress(Path(document['word_path']).read_bytes())
        assert sha256(raw).hexdigest() == document['word_sha256']
        original = json.loads(raw)
        receipt = json.loads(Path(document['source_recovery']).read_text())
        assert receipt['source_head'] == 'ad0f25ff7b23cff7f08ad237c2254e6ecf74257e'
        recovered_parent = receipt.get('source_parent_sha256', receipt.get('source_word_sha256'))
        assert recovered_parent == document['word_sha256']
    else:
        # Only bounded small controls construct their parent in this worker.
        saved = region.COMPILER.build
        region.COMPILER.build = lambda dimension: region.build_regions(dimension, config)
        _, original = region.COMPILER.compile_(h, matching=True, reclaim=True, dirty=True)
        region.COMPILER.build = saved
        raw = (json.dumps(original, separators=(',', ':'))+'\n').encode()
    assert original['h'] == h
    assert [tuple(f) for f in original['frames']] == [b['frame'] for b in blocks]
    maximal, closure = extend(original)
    signed = [maximal['frames'][i] for i in maximal['physical_region_address_aliases']]
    signed = [tuple((f[0], f[1], tuple(f[2]))) for f in signed]
    ordinary = []
    for core, cover in original['frames']:
        rank = 1 if core == cover else cover.bit_count()-core.bit_count()
        symbols = tuple(int(core>>i&1) for i in range(h)) if core == cover else tuple(
            1 if core>>i&1 else i+2 if cover>>i&1 else 0 for i in range(h))
        ordinary.append((rank, core, symbols))
    successors = [set() for _ in blocks]
    for role, before, after in original['events']:
        if before >= 0 and before != after:
            successors[before].add(after)
    value = (c, blocks, owner, original, ordinary, signed, successors, closure, sha256(raw).hexdigest())
    CACHE[key] = value
    return value


def selected_frames(ordinary, signed, successors, mode, threshold):
    chosen = set()
    for g, frame in enumerate(ordinary):
        if frame[0] < threshold:
            continue
        if mode == 'maximal' or mode == 'rank-suffix' or (
            mode == 'core-single' and frame[1].bit_count() == 1) or (
            mode == 'core-pair' and frame[1].bit_count() == 2):
            if signed[g] != frame:
                chosen.add(g)
    pending = deque(sorted(chosen))
    while pending:
        g = pending.popleft()
        for target in successors[g]:
            if target not in chosen and not contained(signed[g], ordinary[target]):
                chosen.add(target)
                pending.append(target)
    labels = [signed[g] if g in chosen else ordinary[g] for g in range(len(ordinary))]
    for g, targets in enumerate(successors):
        for target in targets:
            assert contained(labels[g], labels[target])
    return labels, len(chosen)


def build(c, labels, old_owner, grouping, carrier_policy):
    groups, owner, signal, blocks = {}, {}, {}, []
    for x in sorted(c.active):
        frame = labels[old_owner[x]]
        key = frame if grouping == 'merge-aliases' else (frame, old_owner[x])
        if key not in groups:
            groups[key] = len(blocks)
            blocks.append(dict(nodes=[], frame=frame, inputs=set(), uses=[]))
        g = groups[key]
        owner[x] = g
        blocks[g]['nodes'].append(x)
        signal[x] = signal[c.args[x][0]]^signal[c.args[x][1]] if c.args[x] else 1<<(x-1)
        for y in c.args[x] or ():
            assert contained(labels[old_owner[y]], frame), 'Scalar dependency does not fit actual-word signed space'
    outgoing, incoming = [set() for _ in blocks], [set() for _ in blocks]
    for x in sorted(c.active):
        for y in c.args[x] or ():
            if owner[y] != owner[x]:
                blocks[owner[x]]['inputs'].add(y)
                outgoing[owner[y]].add(owner[x])
                incoming[owner[x]].add(owner[y])
    uses, value_uses = [], defaultdict(list)
    for g,b in enumerate(blocks):
        b['inputs'] = sorted(b['inputs'])
        b['source'] = not c.args[b['nodes'][0]]
        b['rank'] = b['frame'][0]
        for y in b['inputs']:
            u = len(uses)
            uses.append((y,g,None))
            value_uses[y].append(u)
            blocks[owner[y]]['uses'].append(u)
    for target,x in c.outputs.items():
        u = len(uses)
        uses.append((x,owner[x],target))
        value_uses[x].append(u)
        blocks[owner[x]]['uses'].append(u)
    remaining = [len(v) for v in incoming]
    ready = [(blocks[g]['rank'], min(blocks[g]['nodes']), g) for g in range(len(blocks)) if not remaining[g]]
    heapq.heapify(ready)
    order = []
    while ready:
        _,_,g = heapq.heappop(ready)
        order.append(g)
        for target in sorted(outgoing[g]):
            remaining[target] -= 1
            if not remaining[target]:
                heapq.heappush(ready,(blocks[target]['rank'],min(blocks[target]['nodes']),target))
    assert len(order) == len(blocks), 'Identical-address grouping creates a noncausal region cycle'
    position = {g:i for i,g in enumerate(order)}
    for g,b in enumerate(blocks):
        coeff = {y:1<<i for i,y in enumerate(b['inputs'])}
        if b['source']:
            assert len(b['nodes']) == 1
            coeff[b['nodes'][0]] = 1
        for x in b['nodes']:
            if c.args[x]:
                coeff[x] = coeff[c.args[x][0]]^coeff[c.args[x][1]]
        b['coeff'] = coeff
        b['outvalues'] = sorted({uses[u][0] for u in b['uses']})
        b['outbasis'] = region.COMPILER.basis(coeff[x] for x in b['outvalues'])
        b['candidates'],b['selected'] = [],set()
        if not b['source']:
            for i,y in enumerate(b['inputs']):
                if not region.COMPILER.independent(b['outbasis'],1<<i):
                    continue
                for u in value_uses[y]:
                    _,target,terminal = uses[u]
                    if position[g] < position[target] and contained(b['frame'],blocks[target]['frame']):
                        b['candidates'].append((u,i))
        if carrier_policy == 'large-rise':
            b['candidates'].sort(key=lambda item:(-blocks[uses[item[0]][1]]['rank'],item))
        elif carrier_policy == 'small-rise':
            b['candidates'].sort(key=lambda item:(blocks[uses[item[0]][1]]['rank'],item))
        elif carrier_policy == 'terminal-first':
            b['candidates'].sort(key=lambda item:(uses[item[0]][2] is None,item))
    return c,blocks,uses,value_uses,owner,signal,order,contained


def canonicalize(word, order):
    h = word['h']
    def mask(value):
        return sum(1<<order[i] for i in range(h) if value>>i&1)
    lookup, frames, aliases = {}, [], []
    for rank,core,symbols in word['frames']:
        moved = [0]*h
        for i in range(h):
            moved[order[i]] = symbols[i]
        frame = (rank,mask(core),tuple(moved))
        if frame not in lookup:
            lookup[frame] = len(frames)
            frames.append(frame)
        aliases.append(lookup[frame])
    word.update(frames=frames,frame_format='positive-signed-v1')
    word['ops'] = [(a,b,aliases[g]) for a,b,g in word['ops']]
    word['outputs'] = [(s,aliases[g],order[c],tuple(sorted(order[i] for i in t))) for s,g,c,t in word['outputs']]
    word['events'] = [(s,-1 if before<0 else aliases[before],aliases[after]) for s,before,after in word['events']]
    triples = list(combinations(range(h),3))
    index = {t:i for i,t in enumerate(triples)}
    labels = [index[tuple(sorted(order[i] for i in t))] for t in triples]
    inverse = [0]*len(labels)
    for i,j in enumerate(labels):
        inverse[j] = i
    word.update(source_permutation=order,source_label_permutation=labels,source_label_inverse=inverse)
    return word


def evaluate(config):
    started = time.monotonic()
    document = config['parent']
    case = '-'.join([document['id'],config['mode'],str(config['threshold']),config['grouping'],config['carrier']])
    target = WORK/'raw'/case
    target.mkdir(parents=True,exist_ok=False)
    original_build = region.COMPILER.build
    try:
        c,old_blocks,old_owner,old_word,ordinary,signed,successors,closure,parent_digest = prepare(document)
        labels,changed = selected_frames(ordinary,signed,successors,config['mode'],config['threshold'])
        assignment = [(x,labels[old_owner[x]],old_owner[x] if config['grouping']=='preserve-regions' else None) for x in sorted(c.active)]
        digest = sha256(json.dumps((assignment,config['carrier']),separators=(',',':')).encode()).hexdigest()
        with sqlite3.connect(WORK/'claims.sqlite',timeout=30) as db:
            try:
                db.execute('INSERT INTO claims VALUES(?,?,?)',(document['h'],digest,case))
                db.commit()
                prior = None
            except sqlite3.IntegrityError:
                prior = db.execute('SELECT case_id FROM claims WHERE h=? AND digest=?',(document['h'],digest)).fetchone()[0]
        if prior is not None:
            result = dict(status='deduplicated identical complete signed assignment and carrier policy',case_id=case,configuration=config,duplicate_of=prior)
        else:
            region.COMPILER.build = lambda h:build(c,labels,old_owner,config['grouping'],config['carrier'])
            compiled,word = region.COMPILER.compile_(document['h'],matching=True,reclaim=True,dirty=True)
            word = canonicalize(word,document.get('Q',list(range(document['h']))))
            raw = (json.dumps(word,separators=(',',':'))+'\n').encode()
            path = target/'word.json.gz'
            with path.open('wb') as stream:
                with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0) as gz:
                    gz.write(raw)
            independent = check(path,target/'signed-transitions.bin')
            result = dict(status='new joint synthesis on actual-word signed frames full source/address/bothdirty PASS',
                          case_id=case,configuration=config,compiled=compiled,independent=independent,
                          scalar=c.verify(),parent_word_sha256=parent_digest,word_path=str(path),
                          word_sha256=sha256(raw).hexdigest(),assignment_sha256=digest,
                          enlarged_parent_regions=changed,old_regions=len(old_blocks),
                          new_regions=compiled['stats']['regions'],source_head='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',
                          limitations='DISCOVERY finite word. Exact actual signed matrix CRT, full source-pair geometry and complete recurrence/assembly must be checked before accepting an exponent.')
    except Exception as error:
        result = dict(status='failed',case_id=case,configuration=config,error=repr(error))
    finally:
        region.COMPILER.build = original_build
    result.update(seconds=time.monotonic()-started,completed_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    (target/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(case_id=case,status=result['status'],R=result.get('compiled',{}).get('roles'),
                         new_regions=result.get('new_regions'),seconds=result['seconds'],error=result.get('error'))),flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--parents',type=Path)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=6)
    parser.add_argument('--small',action='store_true')
    parser.add_argument('--preflight',action='store_true')
    parser.add_argument('--seed-claims',nargs='+',type=Path,default=[])
    parser.add_argument('--previous-output',type=Path)
    parser.add_argument('--previous-total',type=int,default=288)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    with sqlite3.connect(args.work/'claims.sqlite') as db:
        db.execute('CREATE TABLE claims(h INTEGER,digest TEXT,case_id TEXT,PRIMARY KEY(h,digest))')
        for previous in args.seed_claims:
            for row in json.loads(previous.read_text())['rows']:
                if row.get('assignment_sha256') and row.get('compiled'):
                    db.execute('INSERT OR IGNORE INTO claims VALUES(?,?,?)',
                               (row['compiled']['h'],row['assignment_sha256'],'prior:'+str(previous)+':'+row['case_id']))
    if args.small:
        parents = [dict(id='small-h10-baseline',h=10,configuration=dict(h=10,policy='baseline',rank_delta=1,sweeps=1,limit=0))]
        modes = [('core-single',4),('maximal',0)]
        carriers = ['original']
    else:
        assert args.parents
        parents = json.loads(args.parents.read_text())
        modes = [('core-single',18)] if args.preflight else [('core-single',18),('core-pair',18),('rank-suffix',18),('maximal',0)]
        carriers = ['original'] if args.preflight else ['original','large-rise','small-rise','terminal-first']
    configurations = [dict(parent=p,mode=mode,threshold=threshold,grouping=grouping,carrier=carrier)
                      for mode,threshold in modes for p in parents
                      for grouping in (['merge-aliases'] if args.preflight else ['merge-aliases','preserve-regions']) for carrier in carriers]
    pending,active = list(configurations),{}
    result = dict(status='running',command=sys.argv,configurations=configurations,rows=[])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    with ProcessPoolExecutor(max_workers=args.workers,initializer=initialize,initargs=(args.source,args.work)) as pool:
        while pending or active:
            previous = max(0,args.previous_total-len(json.loads(args.previous_output.read_text())['rows'])) if args.previous_output else 0
            capacity = args.workers-min(args.workers,previous)
            while pending and len(active)<capacity:
                configuration = pending.pop(0)
                active[pool.submit(evaluate,configuration)] = configuration
            done,_ = wait(active,timeout=.5,return_when=FIRST_COMPLETED) if active else (set(),set())
            if not active:
                time.sleep(.2)
            for future in done:
                active.pop(future)
                row = future.result()
                result['rows'].append({k:v for k,v in row.items() if k not in ('independent','scalar')})
                tmp = args.output.with_suffix('.tmp')
                tmp.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
                tmp.replace(args.output)
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat())
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
