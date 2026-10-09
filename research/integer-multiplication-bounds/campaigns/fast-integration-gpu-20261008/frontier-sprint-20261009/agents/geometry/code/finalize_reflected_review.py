#!/usr/bin/env python3
"""Preserve a completed independent reflected run and bounded CLI controls.

Stdlib only. This utility does not confer mathematical acceptance: the full
reviewer receipt and complete event ledger must already exist and match.
"""
import argparse
import datetime
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time


def need(condition, message):
    if not condition:
        raise ValueError(message)


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--checker', type=Path, required=True)
    parser.add_argument('--pins', type=Path, required=True)
    parser.add_argument('--scalar-receipt', type=Path, required=True)
    parser.add_argument('--scope', required=True)
    args = parser.parse_args()
    need(not sys.flags.optimize, 'assertion-disabled finalization rejected')
    review = json.loads((args.run/'reflected-review.json').read_text())
    pins = json.loads(args.pins.read_text())
    paths = {k:Path(v) for k,v in pins['paths'].items()}
    need(sha256(args.checker.read_bytes()).hexdigest() == review['checker_sha256'], 'executed checker drift')
    need(sha256(args.pins.read_bytes()).hexdigest() == review['pins_sha256'], 'run pins drift')
    need({k:sha256(v.read_bytes()).hexdigest() for k,v in paths.items()} == review['input_sha256'] == pins['sha256'], 'completed input drift')
    need(args.scalar_receipt.is_file(), 'missing separate scalar receipt')
    export = paths['graph'].parent
    tree = paths['physical_compiler'].parent.parent
    command = [sys.executable, '-I', str(args.checker), '--export', str(export), '--tree', str(tree),
               '--frames', str(paths['candidate_frames']), '--profile', str(paths['candidate_profile']),
               '--construction-code', str(paths['fusion_construction_helper']), '--pins', str(args.pins),
               '--output', str(args.run/'rejected-control-output.json')]
    controls = {}

    def reject_command(name, actual):
        started = time.monotonic()
        result = subprocess.run(actual, text=True, capture_output=True)
        need(result.returncode != 0, 'CLI negative control accepted: '+name)
        controls[name] = dict(command=actual, exit_code=result.returncode, stdout=result.stdout,
                              stderr=result.stderr, elapsed_seconds=time.monotonic()-started)

    reject_command('assertion_disabled', [sys.executable, '-O'] + command[1:])
    corrupt = args.run/'source-corruption'
    corrupt.mkdir()
    for name in ('graph.json','frames.json','word.json','physical-pairs.json','profile-before.json','protocol.json'):
        shutil.copyfile(export/name, corrupt/name)
    with (corrupt/'graph.json').open('ab') as stream:
        stream.write(b' ')
    corrupted_command = list(command)
    corrupted_command[corrupted_command.index('--export')+1] = str(corrupt)
    reject_command('source_corruption_cli', corrupted_command)

    spec = importlib.util.spec_from_file_location('independent_reflected_review', args.checker)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    graph = json.loads(paths['graph'].read_text())
    witness = json.loads(paths['witness'].read_text())
    word = json.loads(paths['word'].read_text())
    R = json.loads(paths['record'].read_text())['R']
    witness['matching_arcs'][0][1] = (1 << 31) | len(graph['roots'])
    started = time.monotonic()
    try:
        module.regenerate_closure_and_word(graph, witness, word, R)
    except ValueError as error:
        controls['absent_fused_root_use'] = dict(mutation='Replace the first actual carrier use with the first absent fused-root index.',
                                                 rejection=str(error), elapsed_seconds=time.monotonic()-started)
    else:
        raise ValueError('absent fused root use accepted')
    save(args.run/'execution-controls.json', controls)
    complete_command = command[:-1] + [str(args.run/'reflected-review.json'), '--events', str(args.run/'forward-literal.jsonl.gz')]
    protocol = dict(recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), command=complete_command,
                    working_directory=str(Path.cwd()), python=sys.version, checker_sha256=review['checker_sha256'],
                    pins_sha256=review['pins_sha256'], scalar_receipt=str(args.scalar_receipt),
                    scalar_receipt_sha256=sha256(args.scalar_receipt.read_bytes()).hexdigest(),
                    input_export_protocol=str(paths['fused_construction_protocol']), source_commit=review['source_commit'],
                    scope=args.scope, finalizer_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    save(args.run/'protocol.json', protocol)
    args.evidence.mkdir()
    for name in ('reflected-review.json','execution-controls.json','protocol.json'):
        shutil.copyfile(args.run/name, args.evidence/name)
    digest = sha256()
    size = 0
    with gzip.open(args.run/'forward-literal.jsonl.gz','rb') as source, (args.evidence/'forward-literal.jsonl').open('xb') as target:
        while True:
            chunk = source.read(1048576)
            if not chunk:
                break
            target.write(chunk)
            digest.update(chunk)
            size += len(chunk)
    need(digest.hexdigest() == review['forward_literal_sha256'], 'complete literal ledger digest mismatch')
    print(json.dumps(dict(status='COMPLETED_REVIEW_AND_CONTROLS_PRESERVED', evidence=str(args.evidence),
                          literal_bytes=size, literal_sha256=digest.hexdigest(), controls=list(controls)), sort_keys=True))


if __name__ == '__main__':
    main()
