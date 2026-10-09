#!/usr/bin/env python3
"""Bounded terminal-root eligibility and actual frame obstruction survey.

RaD; GPT-6.1 Sol assistance; Apache-2.0. The body is already freshly
regenerated and immutable. Each case changes its literal sink substitutions,
then executes the complete native forward/reflected gate. An algebraically
valid substitution rejected by geometry receives no moment or paid profile.
"""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode=True
from screen_pr168_modules import need, load_code, write


def candidates(graph,word,pairs):
    phase=set(word['phase1'])
    order=sorted(phase)+[i for i in range(len(word['ops'])) if i not in phase]
    position={i:k for k,i in enumerate(order)}
    writes=defaultdict(list);control=set()
    for i,(a,b,node) in enumerate(word['ops']):
        writes[a].append(i);control.add(b)
    sources=set(word['sources'].values())
    gauges={item['role'] for item in word['selected']}
    donors={a for a,b,t in pairs};recipients={b for a,b,t in pairs}
    deadline={b:t for a,b,t in pairs};first_read={}
    for item in word['selected']:
        op=deadline.get(item['role'])
        when=position[op] if op is not None else len(phase)
        for target in item['targets']:
            first_read[target]=min(first_read.get(target,10**12),when)
    census=[];eligible=[]
    for root,role in zip(graph['roots'],word['rootroles']):
        if root['kind']!='side':continue
        failures=[]
        if role in sources:failures.append('source_injection')
        if role in gauges:failures.append('selected_gauge')
        if role in donors:failures.append('alias_donor')
        if role in recipients:failures.append('alias_recipient')
        if role in control:failures.append('used_as_control')
        if not writes[role]:failures.append('no_destination_write')
        if any(i in phase for i in writes[role]):failures.append('center_phase_write')
        pivots=[]
        if writes[role]:
            last=max(position[i] for i in writes[role])
            pivots=[t for t in root['targets'] if first_read.get(t,10**12)>last]
            if not pivots:failures.append('pivot_old_read_before_last_write')
        record=dict(role=role,channel=root['channel'],targets=root['targets'],writes=writes[role],
                    pivots=pivots,all_obstructions=failures)
        census.append(record)
        if not failures:eligible.append([role,pivots[0],root['channel']])
    return census,eligible


def run(task):
    source,body,outdir,name,selected=task
    source,body,outdir=map(Path,(source,body,outdir))
    out=outdir/name;out.mkdir();start=time.monotonic()
    sys.path.insert(0,str(source/'scripts'))
    from paired_cube_physical import physical
    graph,witness,word,row,frames,pairs=[json.loads((body/name).read_text()) for name in
        ('graph.json','frames.json','word.json','profile-before.json','physical-frames.json','physical-pairs.json')]
    base=physical(graph,witness,word,row,frames,pairs)
    gate=load_code('rad_sink_obstruction_gate',source/'research/terminal-sinks/sinks_gate.py')
    write(out/'sinks.json',selected)
    try:
        paid=gate.sinks_record(graph,witness,word,row,frames,pairs,selected,base)
    except AssertionError as error:
        result=dict(variant=name,status='REJECTED_ACTUAL_LITERAL_SINK_GEOMETRY',sinks=len(selected),
                    diagnostic=str(error),paid_profile_available=False,elapsed_seconds=time.monotonic()-start)
    else:
        write(out/'profile.json',paid)
        result=dict(variant=name,status='PASS_COMPLETE_LITERAL_SINK_GEOMETRY',sinks=len(selected),
                    paid_profile_available=True,complete_paid_profile=paid,elapsed_seconds=time.monotonic()-start)
        if name=='control':
            need(json.loads(json.dumps(paid))==json.loads((source/'certificates/paired-cube-sinks-input.json').read_text()),
                 'unchanged complete sink profile equals frozen source')
    write(out/'result.json',result)
    print(name+': '+result['status']+' '+result.get('diagnostic',''),flush=True)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('source','body-export','output'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--workers',type=int,default=4)
    a=p.parse_args();need(not sys.flags.optimize,'assertion-disabled execution rejected')
    protocol=json.loads((a.body_export/'protocol.json').read_text())
    for filename,pin in protocol['input_pins'].items():
        need(sha256((a.body_export/filename).read_bytes()).hexdigest()==pin['sha256'],'body input pin '+filename)
    for filename,digest in protocol['source_pins'].items():
        need(sha256((a.source/filename).read_bytes()).hexdigest()==digest,'source pin '+filename)
    graph,word,pairs=[json.loads((a.body_export/name).read_text()) for name in
                      ('graph.json','word.json','physical-pairs.json')]
    census,eligible=candidates(graph,word,pairs)
    face0=[[role,pivot] for role,pivot,channel in eligible if channel=='face0']
    control=json.loads((a.source/'research/terminal-sinks/sinks.json').read_text())['sinks']
    need(len(face0)==6,'pinned body face0 candidate census')
    need({role for role,pivot,channel in eligible if channel=='disjoint'}=={role for role,pivot in control},
         'all-eight candidate set equals unchanged source set')
    cases=[('control',control),('append_first_face0',control+face0[:1]),
           ('append_last_face0',control+face0[-1:]),('append_all_face0',control+face0)]
    a.output.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    write(a.output/'eligibility.json',dict(census=census,eligible=eligible,
                                          all_eight_roots=sum(len(item['targets'])==8 for item in census),
                                          all_eight_eligible=sum(channel=='disjoint' for role,pivot,channel in eligible)))
    write(a.output/'protocol.json',dict(started_utc=datetime.now(timezone.utc).isoformat(),
                                        source_head=protocol['source_head'],body_input_pins=protocol['input_pins'],
                                        source_pins=protocol['source_pins'],workers=a.workers,
                                        gate_sha256=sha256((a.source/'research/terminal-sinks/sinks_gate.py').read_bytes()).hexdigest(),
                                        driver_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                                        variants=[name for name,selection in cases],
                                        scope='Exact full role census and unchangedcontrol+3distinct candidate substitutions. '
                                              'Full actual forward/reflected geometry/paid/native controls run for each; '
                                              'failed candidates are retained without supplier scores.'))
    tasks=[(str(a.source.resolve()),str(a.body_export.resolve()),str(a.output.resolve()),name,selection)
           for name,selection in cases]
    rows=[]
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        for future in as_completed([pool.submit(run,task) for task in tasks]):rows.append(future.result())
    rows.sort(key=lambda item:[name for name,selection in cases].index(item['variant']))
    write(a.output/'batch-result.json',dict(status='COMPLETE_BOUNDED_TERMINAL_SINK_OBSTRUCTION_BATCH',
                                          results=rows,elapsed_seconds=time.monotonic()-start))


if __name__=='__main__':main()
