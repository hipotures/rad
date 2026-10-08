#!/usr/bin/env python3
"""Restrict independent controls to actual enlarged two-core endpoints.

This exports an immutable subset of an already certified native transition
audit. The full signed word remains the matrix input; the subset is a control
selection, never a replacement full-network certificate.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import struct


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--selection', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    configs = json.loads(args.input.read_text())
    selections = {row['parent']['h']: row for row in
                  json.loads(args.selection.read_text())}
    controls = []
    for config in configs:
        binary = Path(config['binary']).read_bytes()
        h, _, _, nf, nt, _, _, _ = struct.unpack_from('<6I2Q', binary)
        assert len(binary) == 40 + nf * (12 + h) + 16 * nt
        selection = selections[h]
        assert sha256(binary).hexdigest() == selection['expected_transition_sha256']
        masks = {sum(1 << i for i in pair) for pair in selection['pairs']}
        endpoints = set()
        for frame in range(nf):
            forced, rank = struct.unpack_from('<QI', binary, 40 + frame * (12 + h))
            if forced in masks and rank > 0:
                endpoints.add(frame)
        assert endpoints
        audit_path = Path(config['audit'])
        audit = json.loads(audit_path.read_text())
        assert audit['h'] == h and audit['basis'] == selection['basis']
        rows = [row for row in audit['transitions']
                if row['a'] in endpoints or row['b'] in endpoints]
        assert rows
        subset = dict(h=h, basis=audit['basis'], transitions=rows,
                      selection_scope='Actual selected two-core endpoints only; '
                                      'full network certificate remains separate.',
                      actual_endpoint_ids=sorted(endpoints),
                      selected_pairs=selection['pairs'],
                      original_audit_path=str(audit_path),
                      original_audit_sha256=sha256(audit_path.read_bytes()).hexdigest(),
                      binary_sha256=sha256(binary).hexdigest())
        output = args.work / f'h{h}-targeted-native-audit-subset.json'
        output.write_text(json.dumps(subset, indent=2) + '\n')
        controls.append(dict(config, case_id=f'h{h}-enlarged-pair-core-targeted',
                             audit=str(output)))
        print(json.dumps(dict(h=h, actual_endpoint_ids=sorted(endpoints),
                              selected_transition_matrices=len(rows))), flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(controls, indent=2) + '\n')


if __name__ == '__main__':
    main()
