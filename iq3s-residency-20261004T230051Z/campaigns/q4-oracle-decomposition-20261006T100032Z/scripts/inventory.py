"""Hash retained new data without modifying or recursively following prior evidence."""
import hashlib
import json
import time
from pathlib import Path

from owned import C


def main():
    output = C / 'analysis/artifact-inventory.json'
    rows = []
    mark = time.monotonic()
    for path in sorted(C.rglob('*')):
        if path == output or any(x in path.relative_to(C).parts
                                 for x in ['src', 'builds', '__pycache__', '.git']):
            continue
        if path.is_symlink():
            rows.append({'path': str(path.relative_to(C)), 'symlink': str(path.resolve()),
                         'scope': 'Referenced prior evidence; not recursively inventoried'})
            continue
        if not path.is_file():
            continue
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            while block := stream.read(8 * 1024**2):
                digest.update(block)
        stat = path.stat()
        rows.append({'path': str(path.relative_to(C)), 'bytes': stat.st_size,
                     'mtime_ns': stat.st_mtime_ns, 'sha256': digest.hexdigest()})
        if time.monotonic() - mark > 10:
            print('INVENTORY_PROGRESS', len(rows), path.relative_to(C), flush=True)
            mark = time.monotonic()
    value = {'state': 'PASS', 'files': rows,
             'scope': 'New retained artifacts, including ignored raw/test data. '
                      'Source/build directories use separate git/build identities; '
                      'prior evidence is referenced without traversal. Mutable status/audit '
                      'files may subsequently change during final commit/audit.',
             'new_regular_payload_bytes': sum(r.get('bytes', 0) for r in rows)}
    output.write_text(json.dumps(value, indent=2) + '\n')
    print('ARTIFACT_INVENTORY_COMPLETE', len(rows), value['new_regular_payload_bytes'], flush=True)


if __name__ == '__main__':
    main()
