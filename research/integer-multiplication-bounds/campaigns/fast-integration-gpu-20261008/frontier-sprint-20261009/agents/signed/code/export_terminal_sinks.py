#!/usr/bin/env python3
"""Rebuild and export a pinned source's literal terminal-sink substitution.

RaD; GPT-6.1 Sol assistance, Apache-2.0. Native terminal-sink lemma/gate
attribution is retained. Runtime profiling observes the native gate's return
locals without changing any source or mathematical operation. Independent
exact integer and complemented geometry checks consume the exported events.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time

sys.dont_write_bytecode = True


def need(condition, message):
    if not condition:
        raise ValueError(message)


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, separators=(',', ':'))
        stream.write('\n')
    path.chmod(0o444)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('source','body-export','output'):
        p.add_argument('--'+name,type=Path,required=True)
    a = p.parse_args()
    need(not sys.flags.optimize,'assertion-disabled execution rejected')
    start = time.monotonic()
    source, body, out = a.source.resolve(), a.body_export.resolve(), a.output.resolve()
    protocol = json.loads((body/'protocol.json').read_text())
    for filename,pin in protocol['input_pins'].items():
        need(sha256((body/filename).read_bytes()).hexdigest() == pin['sha256'],'body input pin '+filename)
    for filename,digest in protocol['source_pins'].items():
        need(sha256((source/filename).read_bytes()).hexdigest() == digest,'body source pin '+filename)
    sys.path.insert(0,str(source/'scripts'))
    from paired_cube_physical import physical
    graph,witness,word,row,frames,pairs,saved = [json.loads((body/name).read_text()) for name in
        ('graph.json','frames.json','word.json','profile-before.json','physical-frames.json','physical-pairs.json','profile.json')]
    base = physical(graph,witness,word,row,frames,pairs)
    need(json.loads(json.dumps(base)) == saved,'full physical body recount')
    gate_path = source/'research/terminal-sinks/sinks_gate.py'
    sinks_path = source/'research/terminal-sinks/sinks.json'
    spec = importlib.util.spec_from_file_location('rad_native_terminal_sink_gate',gate_path)
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    sinks = json.loads(sinks_path.read_text())['sinks']
    captured = {}
    def observe(frame,event,arg):
        if event == 'return' and frame.f_code is gate.sinks_record.__code__:
            for key in ('W','removed','live','slot','sink','ops','coef','phase1','rest','fwd','ref','reflect','build'):
                captured[key] = frame.f_locals[key]
    previous = sys.getprofile()
    sys.setprofile(observe)
    try:
        paid = gate.sinks_record(graph,witness,word,row,frames,pairs,sinks,base)
    finally:
        sys.setprofile(previous)
    need(json.loads(json.dumps(paid)) == json.loads((source/'certificates/paired-cube-sinks-input.json').read_text()),
         'fresh terminal-sink record equals pinned source certificate')
    forward = captured['W']
    reflected = [captured['reflect'](event) for event in reversed(forward)]
    unsubstituted = captured['build']({})
    kind = lambda events: dict(Counter(event[0] for event in events))
    sink_map = [{**value,'role':role} for role,value in captured['sink'].items()]
    out.mkdir(parents=True,exist_ok=False)
    write(out/'sinks.json',sinks)
    write(out/'profile.json',paid)
    write(out/'forward-events.json',forward)
    write(out/'reflected-events.json',reflected)
    write(out/'unsubstituted-events.json',unsubstituted)
    write(out/'sink-map.json',sink_map)
    write(out/'register-map.json',dict(v=graph['v'],logical_R=row['R'],body_live=captured['live'],
                                      body_slot=captured['slot'],removed=sorted(captured['removed']),
                                      forward_inventory=kind(forward),reflected_inventory=kind(reflected),
                                      unsubstituted_inventory=kind(unsubstituted)))
    files = [path for path in out.iterdir() if path.is_file()]
    pins = {path.name:dict(sha256=sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size) for path in files}
    source_pins = {str(path.relative_to(source)):sha256(path.read_bytes()).hexdigest() for path in
                   (gate_path,sinks_path,source/'certificates/paired-cube-sinks-input.json')}
    write(out/'protocol.json',dict(started_utc=datetime.now(timezone.utc).isoformat(),source_head=protocol['source_head'],
                                  body_export=str(body),body_input_pins=protocol['input_pins'],input_pins=pins,
                                  source_pins=source_pins,driver_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                                  native_source_unchanged=True,export_method='Observe return locals; no source patch',
                                  scope='Fresh literal forward/reflected terminal-sink word and full paid profile. '
                                        'Native full frame scans and modular controls pass; independent exact '
                                        'integer identity and independent complemented geometry are separate.'))
    write(out/'reconstruction.json',dict(status='PASS_REGENERATED_LITERAL_TERMINAL_SINK_WORD',sinks=len(sinks),
                                        paid=paid,forward_inventory=kind(forward),reflected_inventory=kind(reflected),
                                        unsubstituted_inventory=kind(unsubstituted),input_pins=pins,source_pins=source_pins,
                                        elapsed_seconds=time.monotonic()-start,
                                        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
    print('PASS freshly reconstructed literal sinks %d physicalR%d W%d events%d %.3fs' %
          (len(sinks),paid['physical_R'],paid['W_per_vertex'],len(forward),time.monotonic()-start),flush=True)


if __name__ == '__main__':
    main()
