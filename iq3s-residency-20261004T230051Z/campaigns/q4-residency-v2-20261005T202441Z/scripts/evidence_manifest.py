"""Hash retained experiment data without touching shared model files or old campaigns."""
from campaign import C, save
import datetime
import hashlib


def main():
    roots = ['raw', 'diagnostics', 'independent', 'traces', 'datasets', 'checkpoints',
             'manual', 'logs', 'inputs', 'phase-b/replay', 'phase-b/early-projection',
             'analysis/launcher-smokes']
    records = []
    for directory in roots:
        root = C / directory
        if not root.exists():
            continue
        for path in sorted(root.rglob('*')):
            if not path.is_file() or path.is_symlink():
                continue
            before = path.stat()
            digest = hashlib.sha256()
            with path.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024 ** 2), b''):
                    digest.update(chunk)
            after = path.stat()
            assert before.st_size == after.st_size and before.st_mtime_ns == after.st_mtime_ns, path
            records.append({'path': str(path.relative_to(C)), 'bytes': after.st_size,
                            'mtime_ns': after.st_mtime_ns, 'sha256': digest.hexdigest()})
    save(C / 'git/retained-evidence-manifest.json', {
        'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': roots, 'files': records,
        'total_bytes': sum(row['bytes'] for row in records),
        'exclusions': 'Shared model weights, source/build output and mutable root bookkeeping. Their identities are recorded separately; no previous campaign is a write target.',
    })
    print('RETAINED_EVIDENCE_MANIFEST', len(records), sum(row['bytes'] for row in records))


if __name__ == '__main__':
    main()
