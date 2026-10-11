#!/usr/bin/env python3
"""New-input finite adapter for the three explicit current binary local variants.

Use the frozen finite core's mathematical functions with a separately defined
producer reconstruction. Their complete code hashes are gated first. The
core recomputes all candidate frames, literal columns, physical reflection,
mutations and paid children. Afterwards this adapter certifies every original
compiler-frame Gram denominator too, rather than silently treating a changed
graph's frames as unchanged public inputs. No old receipt is a proof input.

The command line is the finite core's --source/--source170/--export/--plan/
--profile/--pin/--output interface. Pin manifests must additionally include
reviewer_dependencies for every required code file below.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
import time


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    need(not sys.flags.optimize, 'assertion-disabled execution rejected')
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'source170', 'export', 'plan', 'profile', 'pin', 'output'):
        ap.add_argument('--'+name, type=Path, required=True)
    args = ap.parse_args()
    need(not args.output.exists(), 'fresh finite-adapter output required')
    started = time.monotonic()
    pin = json.loads(args.pin.read_text())
    required = {
        'independent_binary_lifetime.py', 'independent_binary_lifetime_inputs.py',
        'binary_exact_algebra.py', 'independent_binary_inline_inputs.py',
        'independent_binary_local_inputs.py',
    }
    expected = pin['reviewer_dependencies']
    need(set(expected) == required, 'complete finite-adapter dependency closure')
    directory = Path(__file__).parent
    for name, value in expected.items():
        need(Path(name).name == name and digest(directory / name) == value,
             'unchanged reviewer dependency: ' + name)
    import independent_binary_lifetime as core
    import independent_binary_local_inputs as inputs
    need(pin['compiler_config']['diagonal_change'] in inputs.SETS,
         'one explicit supported local association change')
    # This replaces only the producer module selected by the frozen core's
    # explicit import. No core function or file is patched, and the original
    # inherited module object remains bound inside the new adapter.
    sys.modules['independent_binary_lifetime_inputs'] = inputs
    core.main()
    receipt_path = args.output / 'receipt.json'
    prime_path = args.output / 'prime-projectors.json'
    receipt = json.loads(receipt_path.read_text())
    primes = json.loads(prime_path.read_text())
    need(receipt['checker_sha256'] == expected['independent_binary_lifetime.py'] and
         receipt['producer_reconstruction_code_sha256'] == expected['independent_binary_local_inputs.py'],
         'fresh core and explicit changed-producer binding')
    values = sorted({w['gram_determinant'] for w in primes['original_frame_witnesses']})
    factors = []
    for value in values:
        # Each number was just recomputed by exact rank/Gram construction,
        # independently of upstream/discovery code and saved source flags.
        factors.append(dict(gram_determinant=value, unit=core.prime_unit_factors(value)))
    frame_denominator = {value: i for i, value in enumerate(values)}
    unit_witness = dict(prime_lower_bound=2**80, unique_Gram_denominator_certificates=factors,
                        compiler_frames=[dict(frame_id=w['frame_id'], dimension=w['dimension'],
                                              presentation=w['presentation'],
                                              denominator_certificate=frame_denominator[w['gram_determinant']],
                                              defining_rows_sha256=w['defining_rows_sha256'])
                                         for w in primes['original_frame_witnesses']],
                        scope='All freshly reconstructed original compiler-frame denominators are units '
                              'at every q>2^80. Changed operation-frame projectors and both cleared nesting '
                              'orders are certified by the new finite core receipt. All inherited finite '
                              'prime exclusions for other tables, pivots and factorizations remain retained.')
    unit_path = args.output / 'new-compiler-prime-units.json'
    with unit_path.open('x') as stream:
        json.dump(unit_witness, stream, indent=2)
        stream.write('\n')
    result = dict(status='PASS_INDEPENDENT_CHANGED_GRAPH_BINARY_FINITE',
                  source_revision=pin['source_revision'], plan_sha256=pin['plan_sha256'],
                  compiler_config=pin['compiler_config'],
                  source_pin_manifest_sha256=digest(args.pin),
                  core_finite_receipt_sha256=digest(receipt_path),
                  core_prime_projectors_sha256=digest(prime_path),
                  all_new_compiler_frame_units_sha256=digest(unit_path),
                  freshly_recounted_profile_sha256=digest(args.output / 'profile.json'),
                  literal_scalar_program_sha256=receipt['literal_scalar_program_sha256'],
                  original_compiler_frames=len(primes['original_frame_witnesses']),
                  all_changed_compiler_frame_unit_denominators_checked=True,
                  maximum_compiler_determinant_bits=max(abs(x).bit_length() for x in values),
                  reviewer_dependencies=expected, adapter_sha256=digest(Path(__file__)),
                  completed_utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.monotonic()-started,
                  scope='Fresh complete module/local/global graph, native carriers/arcs/frames, actual physical '
                        'compensated program, all formal F2 columns both ways, full G-complemented physical '
                        'reflection and complete paid children. Every compiler/new operation G-projector '
                        'denominator has an exact unit certificate. Moments, ordinary bridge, full scalar/router '
                        'stock, final exponent and inherited all-size contracts are separate gates.')
    with (args.output / 'adapter-receipt.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
