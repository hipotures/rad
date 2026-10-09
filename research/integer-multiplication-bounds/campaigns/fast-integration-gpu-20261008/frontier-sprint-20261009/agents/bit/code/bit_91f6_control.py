#!/usr/bin/env python3
"""Regenerate and fully replay the immutable PR168 91f6a05 binary control.

The public late-copy physical word is a separately pinned literal input. Its
frames, copied values, read deadlines and aliases are checked against a freshly
regenerated graph, not against operation numbers from an earlier candidate.
Native saving arithmetic is distinct from final multiplication kappa.
Prepared for RaD with OpenAI assistance. Upstream Apache-2.0 credits persist.
"""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time

sys.dont_write_bytecode = True
HEAD = '91f6a059f44fb0513639d5185bde2a38973e99ca'
METHOD_HEAD = '29892e2fe8a90714ef61bd8cbfb1a74bec6f8fd4'


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def source_pins(src, method):
    paths = [
        'research/paired-cube-bit/paired_cube_bit_word.py',
        'research/paired-cube-bit/check_paired_cube_bit.py',
        'research/paired-cube-bit/data/pair_module_p12.json',
        'research/paired-cube-bit/data/arcs_p12.json',
        'research/paired-cube-bit/LEMMA.md',
        'research/paired-cube-bit/README.md',
        'scripts/paired_cube_bit_physical.py',
        'references/paired-cube/bit-physical/word_p12.json.gz',
        'references/paired-cube/bit-physical/frames_p12.json.gz',
        'references/paired-cube/bit-physical/kchron_p12.json',
        'certificates/paired-cube-bit-physical-input.json',
    ] + ['research/paired-cube-bit/out/' + n + '_p12.json'
         for n in ('graph', 'word', 'frames', 'kchron', 'profile')]
    method_paths = [
        'research/paired-cube-lifetime/bit.py',
        'research/paired-cube-lifetime/parameters.py',
        'research/paired-cube-bit/check_paired_cube_bit.py',
        'scripts/audit_community_candidate.py', 'scripts/certify.py',
        'scripts/paired_cube_network.py', 'scripts/structured_bulk_assembly.py',
    ]
    return {name: {p: dict(bytes=(root / p).stat().st_size, sha256=sha(root / p))
                   for p in files}
            for name, root, files in [('source91f6', src, paths), ('source170', method, method_paths)]}


def modules(src, method):
    need(sha(src / 'research/paired-cube-bit/check_paired_cube_bit.py') ==
         sha(method / 'research/paired-cube-bit/check_paired_cube_bit.py'),
         'exact source checker compatibility')
    sys.path.insert(0, str(src / 'research/paired-cube-bit'))
    gen = load('actual91f6_generator', src / 'research/paired-cube-bit/paired_cube_bit_word.py')
    physical = load('actual91f6_physical', src / 'scripts/paired_cube_bit_physical.py')
    lifetime = load('retained170_lifetime_for91f6', method / 'research/paired-cube-lifetime/bit.py')
    params = load('retained170_parameters_for91f6', method / 'research/paired-cube-lifetime/parameters.py')
    return gen, physical, lifetime, params


def public_control(src, method, output):
    started = time.monotonic()
    need(not output.exists(), 'fresh run ID required')
    output.mkdir(parents=True)
    protocol = dict(source_head=HEAD, method_head=METHOD_HEAD,
                    started_utc=datetime.now(timezone.utc).isoformat(), workers=1,
                    numerical_library_threads=1, program_sha256=sha(Path(__file__)),
                    source_files=source_pins(src, method),
                    module_policy='Literal new-source pair module, nested-prefix n10, cube u01/w02 fusion.',
                    compiler_policy='Source frozen carrier arcs; plain span threshold8; source gauge policy.',
                    physical_policy='Public literal late-copy word, operation frames, all read deadlines and1760 aliases.',
                    sufficient_coarse_target='652992140/1000000000000',
                    scope='Fresh complete binary control, not final multiplication kappa.')
    (output / 'protocol.json').write_text(json.dumps(protocol, indent=2, sort_keys=True) + '\n')
    gen, physical, lifetime, params = modules(src, method)
    logical = output / 'logical-exports'
    logical.mkdir()
    frozen = read(src / 'research/paired-cube-bit/data/arcs_p12.json')
    _, row, arcs, exports = gen.build(12, frozen, log=lambda *v: print(*v, flush=True))
    exports['profile'] = row
    need(arcs == frozen, 'source frozen carrier arcs regenerated')
    pins = {}
    for name, data in exports.items():
        filename = name + '_p12.json'
        blob = gen.dumps(data).encode()
        (logical / filename).write_bytes(blob)
        need(blob == (src / 'research/paired-cube-bit/out' / filename).read_bytes(),
             'byte-identical regenerated ' + filename)
        pins[filename] = dict(bytes=len(blob), sha256=sha(logical / filename))
    print(json.dumps(dict(stage='fresh logical source byte-identical', seconds=time.monotonic()-started,
                         R=row['R'], W=row['W_per_vertex'])), flush=True)
    chk = physical.loaded(src / 'references/paired-cube/bit-physical', logical)
    result = physical.physical(chk)
    need(json.loads(json.dumps(result)) == read(src / 'certificates/paired-cube-bit-physical-input.json'),
         'complete public physical ledger and controls reproduce')
    phase = set(chk.w['phase1'])
    order = sorted(phase) + [i for i in range(len(chk.w['ops'])) if i not in phase]
    position = {i: t for t, i in enumerate(order)}
    role_ops = {}
    for i in order:
        for role in chk.w['ops'][i][:2]:
            role_ops.setdefault(role, []).append(i)
    recipients = {b for _, b in chk.w['pairs']}
    cut = len(phase)
    reads = {int(s): t for s, t in chk.w['reads'].items()}
    need(all(reads.get(z['role'], cut) == cut for z in chk.w['gauges'] if z['role'] not in recipients),
         'all remaining gauge reads retain the centre cut')
    pairs = []
    for a, b in chk.w['pairs']:
        t = reads[b]
        need(order[t] == role_ops[b][0], 'public compensated read at first actual use')
        pairs.append((a, b, order[t]))
    formal = lifetime.complete_replay(chk, pairs)
    binding = lifetime.fresh_opcode_binding(chk)
    native = params.select_supplier(params.counts(result), bit=True)
    atom = params.choose_atom(native['saving'])
    phys = output / 'physical-exports'
    phys.mkdir()
    for name, data in [('graph', chk.g), ('word', chk.w), ('frames', chk.fr), ('kchron', chk.k), ('profile', result)]:
        (phys / (name + '_p12.json')).write_text(gen.dumps(data))
    receipt = dict(status='PASS_SOURCE_BOUND_FINITE_CONTROL', protocol=protocol,
                   logical_export_pins=pins, physical_profile=result, full_F2=formal,
                   literal_opcode_binding=binding, native_moment=native, paid_atom=atom,
                   physical_pairs_with_op_deadlines=pairs,
                   wall_seconds=time.monotonic()-started,
                   peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   exclusions=['independent full reflected local-ring events',
                               'independent exact prime presentation audit', 'final multiplication assembly'])
    (output / 'receipt.json').write_text(json.dumps(params.js(receipt), indent=2, sort_keys=True) + '\n')
    print(json.dumps(dict(status=receipt['status'], seconds=receipt['wall_seconds'],
                         coarse=str(native['saving']), ordinary=str(atom['effective_saving']),
                         changed_frames=result['changed_operation_frames'], physical_R=result['physical_R'],
                         pairs=result['pairs'], children=sum(result['child_histogram'].values()))), flush=True)
    return receipt


def main():
    need(not sys.flags.optimize, 'assertions enabled')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--source170', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    public_control(args.source.resolve(), args.source170.resolve(), args.output.resolve())


if __name__ == '__main__':
    main()
