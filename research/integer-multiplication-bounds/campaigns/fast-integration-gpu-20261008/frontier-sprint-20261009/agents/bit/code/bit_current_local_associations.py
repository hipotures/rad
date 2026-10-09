#!/usr/bin/env python3
"""Regenerate three explicitly supported single-channel L1 associations.

Each local G channel still sums the same four source leaves. Only its binary
association changes. The inherited pair module, nested-prefix module, inline
u01/w02 outputs, plain8 compiler, gauge-selection policy and stopped supplier
framework remain fixed. Carrier arcs, role copies, phases, exact frames, gauge
instances and compensated terminal aliases are regenerated for the new graph.
The immutable public late-copy control is a reference; its operation numbers
and literal120-copy schedule are not assumed valid on these changed graphs.

Prepared for RaD with OpenAI assistance. Inherited eumemic/Anthropic Claude and
huxint/OpenAI Codex source assistance and Apache-2.0 attribution are retained.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import resource
import sys
import time

sys.dont_write_bytecode = True
from bit_current_control import HEAD, METHOD_HEAD, need, sha, read, modules, source_pins

REFERENCE = {(0, 1, 0), (0, 1, 1), (1, 2, 1)}
MAPS = {
    'without01-mode0': REFERENCE - {(0, 1, 0)},
    'without01-mode1': REFERENCE - {(0, 1, 1)},
    'with02-mode0': REFERENCE | {(0, 2, 0)},
}


def main():
    need(not sys.flags.optimize, 'assertions enabled')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--source170', type=Path, required=True)
    ap.add_argument('--control', type=Path, required=True)
    ap.add_argument('--variant', choices=sorted(MAPS), required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--seed', type=int, default=20261009)
    args = ap.parse_args()
    src, method, control = args.source.resolve(), args.source170.resolve(), args.control.resolve()
    output = args.output.resolve()
    need(not output.exists(), 'fresh attempt directory required')
    output.mkdir(parents=True)
    started = time.monotonic()
    frozen_control = read(control / 'receipt.json')
    need(frozen_control['protocol']['source_head'] == HEAD, 'same current control revision')
    for name, pin in frozen_control['logical_export_pins'].items():
        need(sha(control / 'logical-exports' / name) == pin['sha256'] ==
             sha(src / 'research/paired-cube-bit/out' / name), 'unchanged frozen control ' + name)
    supported = MAPS[args.variant]
    need(len(supported ^ REFERENCE) == 1, 'exactly one local channel changes association')
    protocol = dict(source_head=HEAD, method_head=METHOD_HEAD, variant=args.variant,
                    reference_L1_diagonal_map=sorted(REFERENCE), selected_L1_diagonal_map=sorted(supported),
                    source_parameter='BitGraph.local_l1 reads module-global L1_DIAGONAL; wrapper sets exact supported map.',
                    authored_source_sha256=sha(Path(__file__)), imported_wrapper_sha256=sha(Path(__file__).with_name('bit_current_control.py')),
                    source_files=source_pins(src, method), control_receipt_sha256=sha(control / 'receipt.json'),
                    control_reused_hash_equal=True, reference_physical_word_sha256=sha(control / 'physical-exports/word_p12.json'),
                    seed=args.seed, endpoint_rounds_before_alias=4, endpoint_rounds_after_alias=4,
                    compiler_plain_threshold=8, carrier_policy='Fresh maximum Hopcroft-Karp matching on actual new DAG.',
                    gauge_selection_trial=.00065, alias_kind='Gauged terminal side recipient', alias_rank=21,
                    workers=1, numerical_library_threads=1, started_utc=datetime.now(timezone.utc).isoformat(),
                    sufficient_native_coarse='656236129/1000000000000',
                    fixed_modules=['pair_module_p12.json', 'nested_prefix(10)', 'inline u01 and w02 output fusion'],
                    policy_limit='Fresh native compiler chronology, not a transplanted public physical late-copy schedule.',
                    scope='Actual binary supplier construction. Native coarse is not final multiplication kappa.')
    (output / 'protocol.json').write_text(json.dumps(protocol, indent=2, sort_keys=True) + '\n')
    stage = 'source loading'
    try:
        gen, _, lifetime, params = modules(src, method)
        need(set(gen.L1_DIAGONAL) == REFERENCE, 'exact pinned source L1 reference policy')
        gen.L1_DIAGONAL = set(supported)
        stage = 'actual local association graph'
        graph = gen.BitGraph(12).finish(read(gen.HERE / 'data' / gen.MODULES[12]),
                                       gen.nested_prefix(10), merge=True, l1=True)
        need(gen.check_decoder(graph) == 0, 'full actual graph mod-two decoder')
        print(json.dumps(dict(stage=stage, nodes=len(graph['args']), roots=len(graph['roots']),
                             diagonal_map=sorted(supported))), flush=True)
        stage = 'fresh carrier/frame/gauge chronology'
        profile, witness = gen.compile_word(graph, frozen=None, plain_k=8)
        gauges, internal, target, word = gen.select_gauges(graph, profile, witness)
        row = gen.profile(profile, gauges, internal, target)
        exports = gen.export(12, graph, profile, witness, word, row)
        exports['profile'] = row
        export = output / 'exports'
        export.mkdir()
        for name, data in exports.items():
            (export / (name + '_p12.json')).write_text(gen.dumps(data))
        (output / 'arcs.json').write_text(gen.dumps(exports['word']['arcs']))
        stage = 'exact native frames and complete source checker'
        e = lifetime.Experiment(export, 12, alpha=.000655401120, quiet=True)
        initial = e.profile()
        stage = 'bounded endpoint/component continuation'
        e.optimize(rounds=4, seed=args.seed)
        before_alias = e.profile()
        stage = 'fresh paid terminal matching'
        e.match_pairs(gauge_rank=21)
        e.optimize(rounds=4, seed=args.seed+1)
        stage = 'all F2 inputs and exact full paid profile'
        accepted = e.save(output / 'selected', replay=True)
        stage = 'rigorous full fallback and stopped supplier moments'
        native = params.select_supplier(params.counts(accepted), bit=True)
        atom = params.choose_atom(native['saving'])
        result = dict(status='PASS_SOURCE_BOUND_FINITE_DISCOVERY', protocol=protocol,
                      native_initial_profile=initial, before_alias_profile=before_alias,
                      profile=accepted, native_moment=native, paid_atom=atom,
                      plan_sha256=sha(output / 'selected/frames.json'),
                      profile_sha256=sha(output / 'selected/profile.json'),
                      graph_sha256=sha(export / 'graph_p12.json'),
                      word_sha256=sha(export / 'word_p12.json'),
                      exported_files={p.name: dict(bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(export.iterdir())},
                      wall_seconds=time.monotonic()-started, peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                      exclusions=['independent full reflected physical events', 'exact selected projector prime units',
                                  'same-source final complex/transfer/row-stock assembly'])
        (output / 'result.json').write_text(json.dumps(params.js(result), indent=2, sort_keys=True) + '\n')
        (output / 'moment.json').write_text(json.dumps(params.js(native), indent=2, sort_keys=True) + '\n')
        print(json.dumps(dict(status=result['status'], variant=args.variant, seconds=result['wall_seconds'],
                             R=accepted['physical_R'], W=accepted['W_per_vertex'], pairs=accepted['pairs'],
                             coarse=str(native['saving']), ordinary=str(atom['effective_saving']),
                             changed_frames=accepted['changed_operation_frames'])), flush=True)
    except Exception as error:
        (output / 'failure.json').write_text(json.dumps(dict(status='FAILED_ACTUAL_CONSTRUCTION_GATE', stage=stage,
            error_type=type(error).__name__, message=str(error), protocol=protocol,
            wall_seconds=time.monotonic()-started), indent=2, sort_keys=True) + '\n')
        raise


if __name__ == '__main__':
    main()
