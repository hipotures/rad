#!/usr/bin/env python3
"""Discover cross-region carriers synthesized from several incoming signals.

Scalar interval graph: Avi Eisenberg, PR62. Joint invertible binary synthesis,
linear/partition matroid intersection and paid reclamation: eumemic, PR57.
This extension offers exact nonunit input rows that equal a future scalar
signal. Every selected row occupies a distinct independent physical capacity;
the literal XOR word, transfers and retirement costs are retained in full.
Results are finite F2 DISCOVERY witnesses, not certified exponents.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import argparse
import gzip
from hashlib import sha256
import inspect
from itertools import combinations
import json
from pathlib import Path
import sys
import time

from check_compiled_witness import contained
import joint_region_search_v3 as region
import joint_signed_word_recompile as joint
from joint_word_check_v4 import check


def linear_rank(rows):
    """Independent elimination used only by the carrier receipt auditor."""
    pivots = {}
    for original in rows:
        row = original
        while row:
            pivot = row.bit_length()-1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


def build_candidates(c, labels, owner, grouping, policy, degree, protection):
    built = joint.build(c, labels, owner, grouping, policy)
    c, blocks, uses, value_uses, owner, signal, order, fits = built
    position = {g:i for i,g in enumerate(order)}
    protected = {}
    for value, indices in value_uses.items():
        protected[value] = min(indices, key=lambda u:(
            len(order) if uses[u][2] is not None else position[uses[u][1]], u))
    by_signal = defaultdict(list)
    for value in sorted(c.active):
        by_signal[signal[value]].append(value)
    discovery = Counter()
    for g,b in enumerate(blocks):
        # The third edge field is now an actual row mask, including unit rows.
        b['candidates'] = [(u,1<<i) for u,i in b['candidates']]
        prior = set(b['candidates'])
        if b['source'] or degree < 2:
            continue
        for size in range(2, min(degree,len(b['inputs']))+1):
            for indices in combinations(range(len(b['inputs'])),size):
                row = sum(1<<i for i in indices)
                discovery['input_combinations'] += 1
                if not region.COMPILER.independent(b['outbasis'],row):
                    discovery['dependent_on_desired_rows'] += 1
                    continue
                form = 0
                for i in indices:
                    form ^= signal[b['inputs'][i]]
                if not form:
                    discovery['zero_source_form'] += 1
                    continue
                values = by_signal.get(form,())
                if not values:
                    discovery['not_an_existing_scalar_form'] += 1
                    continue
                discovery['existing_source_form_combinations'] += 1
                for value in values:
                    for u in value_uses[value]:
                        _, target, terminal = uses[u]
                        if protection == 'first-use' and protected[value] == u:
                            discovery['protected_first_use'] += 1
                            continue
                        receiver_step = len(order) if terminal is not None else position[target]
                        if position[g] >= receiver_step:
                            discovery['noncausal'] += 1
                            continue
                        if not fits(b['frame'],blocks[target]['frame']):
                            discovery['frame_not_contained'] += 1
                            continue
                        edge = (u,row)
                        if edge not in prior:
                            prior.add(edge)
                            b['candidates'].append(edge)
                            discovery['new_nonunit_edges'] += 1
        if policy == 'large-rise':
            b['candidates'].sort(key=lambda item:(-blocks[uses[item[0]][1]]['rank'],item))
        elif policy == 'small-rise':
            b['candidates'].sort(key=lambda item:(blocks[uses[item[0]][1]]['rank'],item))
        elif policy == 'terminal-first':
            b['candidates'].sort(key=lambda item:(uses[item[0]][2] is None,item))
    return built, dict(discovery)


def install_compiler(built, protection):
    namespace = dict(region.COMPILER.__dict__)
    matcher = inspect.getsource(region.COMPILER.match)
    for old,new in [('1<<edges[f][2]','edges[f][2]'),
                    ('1<<edges[e][2]','edges[e][2]'),('1<<i','i')]:
        assert old in matcher
        matcher = matcher.replace(old,new)
    exec(compile(matcher,'<literal-row-matroid>','exec'),namespace)
    compiler = inspect.getsource(region.COMPILER.compile_)
    # inspect reads pinned disk source, so repeat the small-control-only
    # reporting extension already used by joint_region_search_v3.initialize.
    compiler = compiler.replace('baseline_pr48_roles={23:36432,25:48329}[h]',
                                'baseline_pr48_roles={23:36432,25:48329}.get(h)')
    compiler = compiler.replace('slots=[];frames=[];ops=[];events=[];',
                                'carrier_records=[];region_entries=[];slots=[];frames=[];ops=[];events=[];')
    old = "b=blocks[g];outuses=[u for u in b['uses']if u not in right];outvalues=sorted({uses[u][0]for u in outuses});assert outvalues==b['outvalues']"
    new = old
    if protection == 'all-paid-retirement':
        new = "b=blocks[g];outuses=[u for u in b['uses']if u not in right];outvalues=b['outvalues']"
    new += ";region_entries.append(dict(region=g,step=step,op_offset=len(ops),frame=b['frame'],input_roles=[]))"
    assert old in compiler
    compiler = compiler.replace(old,new)
    old = "assert len(set(ins))==len(ins)"
    assert old in compiler
    compiler = compiler.replace(old,old+";region_entries[-1]['input_roles']=list(zip(b['inputs'],ins))")
    old = "_,u,i=edges[e];r=1<<i;assert independent(echelon,r)"
    assert old in compiler
    compiler = compiler.replace(old,"_,u,i=edges[e];r=i;assert independent(echelon,r)")
    old = "elif kind=='carry':assign[key]=s;assert slots[s]==signal[uses[key][0]]"
    assert old in compiler
    compiler = compiler.replace(old,old+";carrier_records.append(dict(donor_region=g,use=key,value=uses[key][0],row=edges[right[key]][2],physical_slot=s,op_offset=len(ops),inputs=tuple(b['inputs']),frame=b['frame']))")
    if protection == 'all-paid-retirement':
        old = "output_slots=[];output_records=[];scatter=[0]*v;J=[]"
        assert old in compiler
        # This lies after each region's use assignment and inside the loop.
        compiler = compiler.replace(old," for x,s in value_slots.items():\n   if x not in used:retired.add(s)\n "+old)
    old = "frames=[b['frame']for b in blocks],events=events)"
    assert old in compiler
    compiler = compiler.replace(old,"frames=[b['frame']for b in blocks],events=events,linear_form_carriers=carrier_records,region_entries=region_entries)")
    namespace['build'] = lambda h:built
    exec(compile(compiler,'<literal-row-joint-compiler>','exec'),namespace)
    return namespace['compile_']


def move_frame(frame, order):
    rank,core,symbols = frame
    moved = [0]*len(order)
    for i,label in enumerate(symbols):
        moved[order[i]] = label
    return (rank,sum(1<<order[i] for i in range(len(order)) if core>>i&1),tuple(moved))


def audit_carriers(word, built):
    """Replay source payloads through actual XORs independently of synthesis."""
    c,blocks,uses,value_uses,owner,_,order,fits = built
    signals = {}
    labels = word['source_label_permutation']
    for value in sorted(c.active):
        signals[value] = signals[c.args[value][0]]^signals[c.args[value][1]] if c.args[value] else 1<<labels[value-1]
    entries = {entry['region']:entry for entry in word['region_entries']}
    pending = defaultdict(list)
    for entry in entries.values():
        pending[entry['op_offset']].append(('input',entry))
    terminal_uses = [u for u,item in enumerate(uses) if item[2] is not None]
    terminals = {u:word['outputs'][i][0] for i,u in enumerate(terminal_uses)}
    donor_rows = defaultdict(list)
    seen = set()
    nonunit = 0
    for record in word['linear_form_carriers']:
        g,u,row = record['donor_region'],record['use'],record['row']
        assert u not in seen
        seen.add(u)
        value,target,terminal = uses[u]
        assert record['value'] == value
        assert tuple(record['inputs']) == tuple(blocks[g]['inputs'])
        assert row and row >> len(record['inputs']) == 0
        actual = 0
        for i,input_value in enumerate(record['inputs']):
            if row>>i&1:
                actual ^= signals[input_value]
        assert actual == signals[value]
        assert entries[g]['step'] < (len(order) if terminal is not None else entries[target]['step'])
        assert contained(record['frame'], entries[target]['frame'])
        receiver_slot = terminals[u] if terminal is not None else dict(entries[target]['input_roles'])[value]
        assert receiver_slot == record['physical_slot']
        donor_rows[g].append(row)
        nonunit += row.bit_count()>1
        pending[record['op_offset']].append(('carrier',record))
    for g,rows in donor_rows.items():
        desired = list(blocks[g]['coeff'][value] for value in blocks[g]['outvalues'])
        assert linear_rank(desired+rows) == linear_rank(desired)+len(rows)
    slots = [0]*word['R']
    for source,slot in word['sources'].items():
        slots[slot] = 1<<labels[int(source)]
    for offset in range(len(word['ops'])+1):
        for kind,record in pending.get(offset,()):
            if kind == 'input':
                for value,slot in record['input_roles']:
                    assert slots[slot] == signals[value]
            else:
                assert slots[record['physical_slot']] == signals[record['value']]
        if offset < len(word['ops']):
            a,b,_ = word['ops'][offset]
            slots[a] ^= slots[b]
    return dict(status='exact source-form, independent capacities, chronology, destinations and actual XOR replay PASS',
                selected_carriers=len(seen),selected_nonunit_carriers=nonunit,
                every_region_input_checked=True,proof_scope='Finite F2 payload; rational address containment checked exactly. Full geometry/CRT/recurrence remain separate.')


def evaluate(document, configuration, work):
    started = time.monotonic()
    name = '-'.join([document['id'],configuration['frame'],str(configuration['degree']),configuration['protection'],configuration['carrier']])
    target = work/'raw'/name
    target.mkdir(parents=True,exist_ok=False)
    try:
        c,old_blocks,old_owner,parent_word,ordinary,signed,successors,closure,parent_digest = joint.prepare(document)
        if configuration['frame'] == 'original':
            labels,changed = ordinary,0
        else:
            labels,changed = joint.selected_frames(ordinary,signed,successors,configuration['frame'],0 if configuration['frame']=='maximal' else 18 if document['h']>10 else 4)
        built,discovery = build_candidates(c,labels,old_owner,'preserve-regions',configuration['carrier'],configuration['degree'],configuration['protection'])
        compile_ = install_compiler(built,configuration['protection'])
        compiled,word = compile_(document['h'],matching=True,reclaim=True,dirty=True)
        Q = document.get('Q',list(range(document['h'])))
        word = joint.canonicalize(word,Q)
        for record in word['linear_form_carriers']+word['region_entries']:
            record['frame'] = move_frame(record['frame'],Q)
        carrier_audit = audit_carriers(word,built)
        raw = (json.dumps(word,separators=(',',':'))+'\n').encode()
        path = target/'word.json.gz'
        with path.open('wb') as stream:
            with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0) as gz:
                gz.write(raw)
        independent = check(path,target/'signed-transitions.bin')
        result = dict(status='DISCOVERY exact nonunit joint word source/address/bothdirty PASS',
                      case_id=name,configuration=dict(parent=document,**configuration),
                      compiled=compiled,independent=independent,carrier_audit=carrier_audit,
                      discovery=discovery,scalar=c.verify(),enlarged_parent_regions=changed,
                      parent_word_sha256=parent_digest,word_path=str(path),word_sha256=sha256(raw).hexdigest(),
                      source_head='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',
                      limitations='Finite F2 witness. No exponent accepted until independent source-only recovery, actual rational CRT profiles, complete data geometry and full recurrence/assembly.')
    except Exception as error:
        import traceback
        traceback.print_exc()
        result = dict(status='failed',case_id=name,configuration=dict(parent=document,**configuration),error=repr(error))
    result.update(seconds=time.monotonic()-started,completed_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    (target/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(case_id=name,status=result['status'],R=result.get('compiled',{}).get('roles'),
                         discovery=result.get('discovery'),carrier_audit=result.get('carrier_audit'),seconds=result['seconds'],error=result.get('error'))),flush=True)
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
    parser.add_argument('--degree',type=int,choices=[1,2,3,4,5,6],default=2)
    parser.add_argument('--protection',choices=['first-use','all-paid-retirement'],default='first-use')
    parser.add_argument('--carrier',choices=['original','large-rise','small-rise','terminal-first'],default='original')
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    joint.initialize(args.source,args.work)
    if args.small:
        parents = [dict(id='small-h10-baseline',h=10,configuration=dict(h=10,policy='baseline',rank_delta=1,sweeps=1,limit=0))]
        configurations = [dict(frame='original',degree=1,protection='first-use',carrier='original'),
                          dict(frame='original',degree=2,protection='first-use',carrier='original'),
                          dict(frame='original',degree=3,protection='all-paid-retirement',carrier='original')]
    else:
        assert args.parents
        parents = [p for p in json.loads(args.parents.read_text()) if args.h is None or p['h']==args.h]
        configurations = [dict(frame=args.frame,degree=args.degree,protection=args.protection,carrier=args.carrier)]
    result = dict(status='running',command=sys.argv,rows=[])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    for document in parents:
        for configuration in configurations:
            result['rows'].append(evaluate(document,configuration,args.work))
            args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat())
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
