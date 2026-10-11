#!/usr/bin/env python3
"""Move paid scalar producers using existing disjoint source partitions.

Avi Eisenberg's pinned PR62 interval graph and eumemic's PR57 binary joint
compiler are the baselines. A changed gate still pays one binary addition,
uses two existing nonzero disjoint source forms, and keeps its complete exact
scalar support. Its new actual signed frame contains its former frame and
fits every recipient. Global topology and every physical word are rebuilt.
This tests source partition changes absent from free unit-row matching.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import heapq
from itertools import combinations
import json
from pathlib import Path
import sys
import time

from check_compiled_witness import contained
import joint_region_search_v3 as region
import joint_signed_word_recompile as joint
from joint_word_check_v4 import check


class ReconstructedCircuit:
    def __init__(self, parent, changed_args, moved_owner, signals):
        self.inputs = parent.inputs
        v = len(self.inputs)
        active, todo = set(),list(parent.outputs.values())
        while todo:
            value = todo.pop()
            if value in active:
                continue
            active.add(value)
            todo.extend(changed_args[value] or ())
        assert set(range(1,v+1)) <= active
        remaining = {x:len(changed_args[x] or ()) for x in active}
        users = defaultdict(set)
        for x in active:
            for y in changed_args[x] or ():
                users[y].add(x)
        ready = [x for x in active if not remaining[x]]
        heapq.heapify(ready)
        ordered = []
        while ready:
            x = heapq.heappop(ready)
            ordered.append(x)
            for y in sorted(users[x]):
                remaining[y] -= 1
                if not remaining[y]:
                    heapq.heappush(ready,y)
        assert len(ordered)==len(active), 'Producer replacement creates a cycle'
        assert ordered[:v]==list(range(1,v+1))
        mapping = {old:new for new,old in enumerate(ordered,1)}
        self.args, self.core, self.union = [None],[0],[0]
        self.old_nodes, self.expected_signals, self.owner = {},{},{}
        for old in ordered:
            new = mapping[old]
            self.args.append(tuple(mapping[y] for y in changed_args[old]) if changed_args[old] else None)
            self.core.append(parent.core[old])
            self.union.append(parent.union[old])
            self.old_nodes[new] = old
            self.expected_signals[new] = signals[old]
            self.owner[new] = moved_owner[old]
        self.active = set(range(1,len(self.args)))
        self.outputs = {target:mapping[x] for target,x in parent.outputs.items()}
        self.additions = sum(self.args[x] is not None for x in self.active)
        self.h = len({i for triple in self.inputs for i in triple})

    def verify(self):
        """Exact positive-support induction, independent of binary synthesis."""
        source = {}
        for x in sorted(self.active):
            if self.args[x]:
                a,b = self.args[x]
                assert a<x and b<x
                assert not source[a]&source[b], 'Source partition is not disjoint'
                source[x] = source[a]|source[b]
                assert self.core[x] == self.core[a]&self.core[b]
                assert self.union[x] == self.union[a]|self.union[b]
            else:
                source[x] = 1<<(x-1)
                mask = sum(1<<i for i in self.inputs[x-1])
                assert self.core[x] == self.union[x] == mask
            assert source[x] == self.expected_signals[x]
        for (common,target),x in self.outputs.items():
            omitted = set(target)-{common}
            expected = sum(1<<i for i,t in enumerate(self.inputs)
                           if common in t and not omitted.intersection(t))
            assert source[x] == expected
        return dict(status='exact DAG, disjoint partitions, every scalar form, core/cover and all outputs PASS',
                    active_nodes=len(self.active),additions=self.additions,
                    outputs=len(self.outputs),primitive_sources=len(self.inputs),
                    valid_over_every_coefficient_field=True)


def replace_partitions(c, labels, old_owner, policy, budget):
    built = joint.build(c,labels,old_owner,'preserve-regions','original')
    _,blocks,uses,value_uses,_,signal,order,_ = built
    position = {g:i for i,g in enumerate(order)}
    lookup = defaultdict(list)
    for x in sorted(c.active):
        lookup[signal[x]].append(x)
    args = list(c.args)
    owner = dict(old_owner)
    users = defaultdict(set)
    for x in c.active:
        for y in args[x] or ():
            users[y].add(x)
    terminals = set(c.outputs.values())
    chosen,seen = [],set()
    counters = Counter()
    donor_order = order if policy=='early' else list(reversed(order))
    for g in donor_order:
        block = blocks[g]
        donor = old_owner[block['nodes'][0]]
        frame = labels[donor]
        for a,b in combinations(block['inputs'],2):
            counters['input_pairs'] += 1
            if signal[a]&signal[b]:
                counters['overlapping_source_supports'] += 1
                continue
            form = signal[a]|signal[b]
            if form not in lookup:
                counters['no_existing_scalar_form'] += 1
                continue
            for x in lookup[form]:
                if x in seen or x in terminals or not args[x]:
                    counters['protected_terminal_or_prior_replacement'] += 1
                    continue
                if set(args[x])=={a,b}:
                    counters['same_original_partition'] += 1
                    continue
                if owner[x]==donor:
                    counters['already_in_donor_region'] += 1
                    continue
                if not contained(labels[owner[x]],frame):
                    counters['former_frame_not_contained'] += 1
                    continue
                if not contained(labels[owner[a]],frame) or not contained(labels[owner[b]],frame):
                    counters['provider_frame_not_contained'] += 1
                    continue
                if any(not contained(frame,labels[owner[y]]) for y in users[x]):
                    counters['recipient_frame_not_contained'] += 1
                    continue
                old_args,former_owner = args[x],owner[x]
                for y in old_args:
                    users[y].remove(x)
                for y in (a,b):
                    users[y].add(x)
                args[x]=(a,b)
                owner[x]=donor
                seen.add(x)
                chosen.append(dict(value=x,old_args=old_args,new_args=[a,b],
                                   former_region=former_owner,new_region=donor,
                                   original_donor_step=position[g],
                                   source_count=signal[x].bit_count()))
                if budget and len(chosen)>=budget:
                    break
            if budget and len(chosen)>=budget:
                break
        if budget and len(chosen)>=budget:
            break
    for x in c.active:
        for y in args[x] or ():
            assert contained(labels[owner[y]],labels[owner[x]])
    fresh = ReconstructedCircuit(c,args,owner,signal)
    return fresh,chosen,dict(counters)


def evaluate(document, configuration, work):
    started = time.monotonic()
    name = '-'.join([document['id'],configuration['frame'],configuration['policy'],str(configuration['budget'])])
    target = work/'raw'/name
    target.mkdir(parents=True,exist_ok=False)
    saved = region.COMPILER.build
    try:
        c,old_blocks,old_owner,old_word,ordinary,signed,successors,closure,parent_digest = joint.prepare(document)
        labels = ordinary if configuration['frame']=='original' else joint.selected_frames(
            ordinary,signed,successors,configuration['frame'],0 if configuration['frame']=='maximal' else 18 if document['h']>10 else 4)[0]
        fresh,chosen,counters = replace_partitions(c,labels,old_owner,configuration['policy'],configuration['budget'])
        scalar = fresh.verify()
        region.COMPILER.build = lambda h:joint.build(fresh,labels,fresh.owner,'preserve-regions','original')
        compiled,word = region.COMPILER.compile_(document['h'],matching=True,reclaim=True,dirty=True)
        word = joint.canonicalize(word,document.get('Q',list(range(document['h']))))
        raw = (json.dumps(word,separators=(',',':'))+'\n').encode()
        path = target/'word.json.gz'
        with path.open('wb') as stream:
            with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0) as gz:
                gz.write(raw)
        independent = check(path,target/'signed-transitions.bin')
        result = dict(status='DISCOVERY changed disjoint source-partition DAG and full word both-dirty PASS',
                      case_id=name,configuration=dict(parent=document,**configuration),
                      compiled=compiled,independent=independent,scalar=scalar,
                      source_partition_changes=chosen,rejection_counts=counters,
                      original_active_nodes=len(c.active),pruned_old_gates=len(c.active)-len(fresh.active),
                      parent_word_sha256=parent_digest,word_path=str(path),word_sha256=sha256(raw).hexdigest(),
                      source_head='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',
                      limitations='Exact scalar identities hold over every field; finite dirty word is F2. Actual signed CRT profiles, full source geometry, recurrence and conditional gauge/tape realization remain separate.')
    except Exception as error:
        import traceback
        traceback.print_exc()
        result = dict(status='failed',case_id=name,configuration=dict(parent=document,**configuration),error=repr(error))
    finally:
        region.COMPILER.build = saved
    result.update(seconds=time.monotonic()-started,completed_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    (target/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(case_id=name,status=result['status'],R=result.get('compiled',{}).get('roles'),
                         replacements=len(result.get('source_partition_changes',[])),
                         pruned=result.get('pruned_old_gates'),seconds=result['seconds'],error=result.get('error'))),flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--parents',type=Path)
    parser.add_argument('--small',action='store_true')
    parser.add_argument('--h',type=int)
    parser.add_argument('--frame',choices=['original','core-single','maximal'],default='original')
    parser.add_argument('--policy',choices=['early','late'],default='early')
    parser.add_argument('--budget',type=int,default=32)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    joint.initialize(args.source,args.work)
    if args.small:
        parents = [dict(id='small-h10-baseline',h=10,configuration=dict(h=10,policy='baseline',rank_delta=1,sweeps=1,limit=0))]
        configurations = [dict(frame='original',policy='early',budget=8),
                          dict(frame='core-single',policy='late',budget=32)]
    else:
        parents = [p for p in json.loads(args.parents.read_text()) if args.h is None or p['h']==args.h]
        configurations = [dict(frame=args.frame,policy=args.policy,budget=args.budget)]
    result = dict(status='running',command=sys.argv,rows=[])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    for parent in parents:
        for config in configurations:
            result['rows'].append(evaluate(parent,config,args.work))
            args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat())
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':
    main()
