#!/usr/bin/env python3
"""Retain one completed exact fixed-axis witness and its complete selected map."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import argparse
import json
from original_envelope_labels import encode


def retain(row, output, input_file):
    assert not output.exists()
    producer = dict(row['producer'])
    dag = Path(row['dag_path'])
    witness = Path(row.get('witness_path', row.get('selected_links_path', '')))
    labels = Path(str(dag)+'.positive')
    if not labels.exists():
        encode(dag, labels)
    producer.update(dag_path=str(dag), dag_sha256=sha256(dag.read_bytes()).hexdigest(),
                    positive_sha256=sha256(labels.read_bytes()).hexdigest(),
                    witness_path=str(witness), witness_sha256=sha256(witness.read_bytes()).hexdigest())
    result = dict(producer=producer, fixed_profile=row['fixed_profile'],
                  selected_links=json.loads(witness.read_text()), configuration=row['configuration'],
                  retained_utc=datetime.now(timezone.utc).isoformat(),
                  provenance=dict(completed_summary=str(input_file), input_sha256=sha256(input_file.read_bytes()).hexdigest()),
                  status='Exact local profiles; independent compiler and full assembly are separate obligations')
    for key in ('discovery', 'local_phi'):
        if key in row:
            result[key] = row[key]
    output.write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--case-id', required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    data = json.loads(args.input.read_text())
    rows = data['rows'] if isinstance(data, dict) else data
    choices = [r for r in rows if r.get('case_id', r['configuration'].get('case_id')) == args.case_id]
    assert len(choices) == 1
    retain(choices[0], args.output, args.input)
