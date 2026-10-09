#!/usr/bin/env python3
"""Collect completed structural attempts and rigorously enclose finite roots.

RaD, prepared with OpenAI GPT-6.1 Sol assistance. Apache-2.0.
This records finite circuit evidence only; it does not assert all-size or
analytic composition, conditional acceptance, or publication eligibility.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from math import floor
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'signed/code'))
from interval_moments import moment


def need(condition, message):
    if not condition:
        raise ValueError(message)


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'candidates', 'first-attempt', 'repair', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--repaired-full-batch', action='store_true',
                        help='Collect a new four-case run with seed revalidation already enabled.')
    a = parser.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((a.candidates/'manifest.json').read_text())
    for name, digest in manifest['source_input_hashes'].items():
        need(sha256((a.source/'references/paired-cube/sources'/name).read_bytes()).hexdigest() == digest,
             'original module remains unchanged '+name)
    source_pins = json.loads((a.first_attempt/'protocol.json').read_text())
    control_protocol = json.loads((Path(source_pins['immutable_control'])/'protocol.json').read_text())
    for name, digest in control_protocol['source_pins'].items():
        need(sha256((a.source/name).read_bytes()).hexdigest() == digest,
             'original public source remains unchanged '+name)
    log = a.first_attempt.with_suffix('.log').read_text()
    failed_seed = "AssertionError: ('frozen arc rejected', 1331, 2642)" in log
    need(failed_seed or a.repaired_full_batch,
         'first-attempt mapped-carrier failure retained')
    rows = []
    for name in ('control', 'all_edge', 'all_long', 'triple_balanced'):
        run = a.repair if name == 'all_long' else a.first_attempt
        path = run/name/'result.json'
        result = json.loads(path.read_text())
        need(result['status'] == 'EXACT_FINITE_STRUCTURAL_MODULE_SCREEN', 'finite completion status '+name)
        for check in result['exact_signed_core']:
            need(check['exact_signed_source_map'] and check['all_dirty_responses_zero'] and
                 check['exact_inverse_roundtrip'], 'both orientations exact integer dirty checks '+name)
        need(set(result['negative_scalar_controls']) == {'omitted_read', 'bad_sign', 'illegal_index', 'omit_cleanup'},
             'all body negative controls '+name)
        need(result['sink_checks']['status'] == 'EXACT_SYMBOLIC_TERMINAL_SUBSTITUTIONS_WITH_FULL_NATIVE_GEOMETRY',
             'terminal sink full checks '+name)
        paid = json.loads((run/name/'sink-profile.json').read_text())
        hist = {int(k): count for k, count in paid['child_histogram'].items()}
        low = Fraction(floor(result['numerical_complex_root_discovery_only']*10**12), 10**12)
        high = low+Fraction(1, 10**12)
        lo_lower, lo_upper = moment(paid['m'], paid['W_per_vertex'], hist, low)
        hi_lower, hi_upper = moment(paid['m'], paid['W_per_vertex'], hist, high)
        need(lo_upper < 1 and hi_lower > 1, 'strict rational finite root enclosure '+name)
        targets = {}
        for label, saving in (('original_required_complex', Fraction(655831073, 10**12)),
                              ('live_required_complex', Fraction(655861417, 10**12))):
            lower, upper = moment(paid['m'], paid['W_per_vertex'], hist, saving)
            need(lower > 1, 'all finite profiles reject required complex saving '+name)
            targets[label] = dict(saving=str(saving), moment_lower=str(lower), moment_upper=str(upper),
                                  classification='REJECTED')
        module = manifest['variants'][name]
        row = dict(variant=name, source_revision=result['source_head'],
                   local_additions_per_cube=module['local_checks']['additions'],
                   local_signed_additions_per_cube=module['local_checks']['signed_additions'],
                   triple_additions=module['triple_checks']['additions'],
                   triple_root_depth_histogram=module['triple_checks']['root_depth_histogram'],
                   rotations=len(module.get('transformation', {}).get('rotations', [])),
                   graph_binding_sha256=result['graph_binding_sha256'],
                   mapped_seed_arcs=result['initial_arcs'], carrier_arcs=result['matched'],
                   rejected_seed_arcs=result['adaptations'].get('seed_revalidation', {}).get('rejected', []),
                   mapping=result['mapping'], c=result['c'], q=result['q'], R=result['R'],
                   literal_M=result['literal_M'], aliases=result['pairs'],
                   terminal_sinks=len(result['sink_checks']['sinks']),
                   physical_R=result['physical_R'], W=result['W'], m=result['m'],
                   rank_mass=result['rank_mass'], deficit=result['deficit'],
                   complete_child_histogram=result['complete_children'],
                   finite_complex_root=dict(lower=str(low), upper=str(high),
                                            accepted_lower_moment_upper=str(lo_upper),
                                            rejected_upper_moment_lower=str(hi_lower)),
                   required_complex=targets, finite_checks=result['finite_checks'],
                   exact_integer_checks=result['exact_signed_core'],
                   negative_scalar_controls=result['negative_scalar_controls'],
                   sink_star_count=len(result['sink_checks']['independent_exact_star_identities']),
                   full_literal_and_reflected_sink_frame_scan=True,
                   result_source=str(path.resolve()),
                   result_sha256=sha256(path.read_bytes()).hexdigest(),
                   wall_seconds=result['wall_seconds'])
        rows.append(row)
    control_low = Fraction(rows[0]['finite_complex_root']['lower'])
    need(all(Fraction(row['finite_complex_root']['upper']) < control_low for row in rows[1:]),
         'every structural alternative rigorously below common fresh control')
    summary = dict(status='SCOPED_NEGATIVE_FULL_FINITE_STRUCTURAL_MODULE_BATCH',
                   collected_utc=datetime.now(timezone.utc).isoformat(),
                   source_revision=manifest['source_revision'], original_source_pins_unchanged=True,
                   random_generator_seed=None, evaluator_seed=20261009, workers_per_job_at_most=4,
                   nested_library_threads=1, local_frame_rounds=4, component_sweeps_at_most=6,
                   global_lower_budget=8192,
                   first_attempt=dict(status='PARTIAL_THREE_COMPLETE_ONE_INVALID_MAPPED_SEED' if failed_seed
                                             else 'FULL_BATCH_WITH_SEED_REVALIDATION',
                                      error="AssertionError: ('frozen arc rejected', 1331, 2642)" if failed_seed else None,
                                      log_sha256=sha256(a.first_attempt.with_suffix('.log').read_bytes()).hexdigest(),
                                      repair='Sequential current-span, accumulated-intersection, acyclicity and '
                                             'shear checks before admitting each mapped seed; rejected seeds do not '
                                             'mutate the matching state. '+('Only all_long was rerun in a fresh attempt.'
                                             if failed_seed else 'Enabled from the start in this new four-case run.')),
                   rows=rows,
                   conclusion='All changed circuits are exact over characteristic zero and pass the complete finite '
                              'paid-profile, dirty-state and literal reflected sink checks. All three alternatives '
                              'have a finite complex root strictly below the unchanged common fresh control. '
                              'All reject both required complex savings. Positive gate count and depth reduction '
                              'alone do not predict the paid profile in this semantically seeded construction.',
                   limitations='Not a search-complete obstruction. The carrier constructor is seeded by exact semantic '
                               'mapping of current native arcs then fresh legal extension, rather than independent '
                               'maximum matching. All operation frames and aliases are rebuilt. The control is freshly '
                               'optimized by this bounded common method and does not reuse optimized native physical '
                               'choices. All-size/analytic composition and conditional/publication gates were not attempted '
                               'for these negative candidates.')
    write(a.output/'summary.json', summary)
    for row in rows:
        print(row['variant'], 'root', row['finite_complex_root']['lower'], row['finite_complex_root']['upper'],
              'W', row['W'], 'sinks', row['terminal_sinks'], 'rejected_seeds', len(row['rejected_seed_arcs']))


if __name__ == '__main__':
    main()
