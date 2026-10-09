#!/usr/bin/env python3
"""Pin and freshly regenerate PR168's changed complex DAG and literal word.

RaD; prepared with OpenAI GPT-6.1 Sol assistance. Apache-2.0.
Inherited paired-cube module/compiler/checker attribution is retained in the
pinned source snapshot. Saved physical choices are rechecked against this
regenerated word. Historical optimization searches are not regenerated.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
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
        json.dump(value, stream, separators=(',', ':')); stream.write('\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    a = p.parse_args()
    need(not sys.flags.optimize, 'Run without -O: finite assertions are required')
    start = time.monotonic(); utc = datetime.now(timezone.utc).isoformat()
    source = a.source.resolve(); out = a.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(source/'scripts'))
    import paired_cube_producer as producer
    import paired_cube_physical as physical
    from paired_cube.closure import compile_closure
    need(producer.ROOT == source and physical.ROOT == source, 'native source-root binding')
    native_files = ['scripts/paired_cube_producer.py', 'scripts/paired_cube_physical.py'] + [
        'scripts/paired_cube/'+name+'.py' for name in ('graph','modules','closure','frames','gauges','verify')]
    reference_files = [str(path.relative_to(source)) for root in (
        source/'references/paired-cube/sources', source/'references/paired-cube/selected-module',
        source/'references/paired-cube/physical', source/'references/three-stage-cover/pr117')
        for path in sorted(root.iterdir()) if path.is_file()]
    expected = json.loads((source/'certificates/paired-cube-complex-input.json').read_text())
    receipt = producer.regenerate(expected, out/'native-export')
    graph, witness, word = [json.loads((out/'native-export'/name).read_text())
                            for name in ('graph.json','frames.json','selection.json')]
    baseline, rebuilt = compile_closure(graph, witness['matching_arcs'])
    need(json.loads(json.dumps(rebuilt)) == witness, 'fresh dependency closure agrees')
    moved = json.loads((source/'references/paired-cube/physical/frames.json').read_text())['frames']
    pairs = json.loads((source/'references/paired-cube/physical/pairs.json').read_text())['pairs']
    paid = physical.physical(graph, witness, word, expected, moved, pairs)
    published = json.loads((source/'certificates/paired-cube-physical-input.json').read_text())
    need(json.loads(json.dumps(paid)) == published, 'fresh full physical profile differs from pinned certificate')
    inputs = {'graph.json':graph, 'baseline.json':baseline, 'frames.json':witness,
              'word.json':word, 'profile-before.json':expected, 'physical-frames.json':moved,
              'physical-pairs.json':pairs, 'profile.json':paid}
    for name, data in inputs.items():
        write(out/name, data); (out/name).chmod(0o444)
    pins = {name:dict(sha256=sha256((out/name).read_bytes()).hexdigest(),bytes=(out/name).stat().st_size)
            for name in inputs}
    source_pins = {name:sha256((source/name).read_bytes()).hexdigest()
                   for name in native_files+reference_files+['certificates/paired-cube-complex-input.json',
                                                           'certificates/paired-cube-physical-input.json']}
    protocol = dict(started_utc=utc,source_root=str(source),source_head_prefix='98c115b',
                    input_pins=pins,source_pins=source_pins,
                    scope='Fresh PR168 graph from restricted triples, annealed pair module and both-sided nested-prefix '
                          'all-but-one module; frozen carrier arcs freshly recompiled; chronological gauges and signed word '
                          'freshly regenerated. Saved operation frames/pairs rechecked on that exact graph and word, with '
                          'complete paid profile rebuilt. No historical optimization search regeneration is claimed.')
    write(out/'protocol.json', protocol)
    result = dict(status='PASS_REGENERATED_PR168_COMPLEX_CONTROL',producer=receipt,complete_paid_profile=paid,
                  source_pins=source_pins,input_pins=pins,driver_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  elapsed_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope=protocol['scope'])
    write(out/'regeneration.json',result)
    print('PASS fresh PR168 complex control; ops %d, physical roles %d, W %d, %.3fs' %
          (expected['total_M_operations'],paid['physical_R'],paid['W_per_vertex'],result['elapsed_seconds']),flush=True)


if __name__ == '__main__':
    main()
