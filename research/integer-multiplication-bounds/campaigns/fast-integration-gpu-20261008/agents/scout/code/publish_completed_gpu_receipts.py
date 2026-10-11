#!/usr/bin/env python3
"""Copy compact completed GPU receipts and archive complete unsplit text.

No Git operations. Large binary pivot tables remain external and are bound by
the completed summaries and deterministic reproduction source.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work-root', type=Path, required=True)
    parser.add_argument('--tag', required=True)
    args = parser.parse_args()
    own = Path(__file__).resolve().parent.parent
    repository = next(parent for parent in own.parents
                      if (parent / 'tools/archive_workspace.py').is_file())
    assert (repository / 'tools/archive_workspace.py').is_file()
    compact = own / 'gpu-parameter-results' / ('completed-' + args.tag)
    evidence = own / 'evidence' / ('gpu-complete-' + args.tag)
    assert not compact.exists() and not evidence.exists()
    compact.mkdir(parents=True)
    prefixes = (
        'gpu-basis-weight-classes-20261008T1558-',
        'gpu-basis-reserve-20261008T1612-',
        'gpu-basis-full-family-20261008T1615-',
        'gpu-basis-full-family-followup-20261008T1619-',
        'gpu-basis-full-crt-20261008T1629-',
        'gpu-basis-full-crt-wide-20261008T1629-',
        'gpu-basis-other-families-20261008T1634-',
        'gpu-basis-other-crt-20261008T1638-')
    runs = [path for path in sorted((args.work_root / 'derived/scout').iterdir())
            if path.is_dir() and path.name.startswith(prefixes)]
    assert len(runs) == 15
    manifest = {'created_utc': datetime.now(timezone.utc).isoformat(),
                'publisher_source_sha256': digest(Path(__file__)),
                'scope': 'Completed post15:53 scout GPU runs, two failed31bit controls and one intentionally stopped reserve run.',
                'recovery': 'Readable protocols/summaries and complete unsplit text archives are retained. Binary pivots are deterministic external execution artifacts with original summary hashes.',
                'runs': [], 'archives': []}
    for root in runs:
        assert any((root / name).exists() for name in ('summary.json', 'failure.json', 'termination.json'))
        item = {'run_id': root.name, 'original': str(root), 'compact_files': [],
                'binary_payload_policy': 'No binary arrays copied into Git; original summary records bytes, hashes and deterministic recovery.'}
        destination = compact / root.name
        destination.mkdir()
        for source in sorted(root.glob('*.json')):
            assert source.stat().st_size <= 1024 * 1024
            target = destination / source.name
            shutil.copyfile(source, target)
            assert digest(source) == digest(target)
            item['compact_files'].append({'original': str(source),
                                          'copy': str(target.relative_to(own)),
                                          'bytes': source.stat().st_size,
                                          'sha256': digest(source)})
        manifest['runs'].append(item)
    log_groups = sorted({root.name.rsplit('-device', 1)[0] for root in runs})
    sources = [(root, evidence / root.name) for root in runs]
    sources += [(args.work_root / 'logs/scout' / name, evidence / ('stdout-' + name))
                for name in log_groups]
    for source, destination in sources:
        assert source.is_dir()
        commands = [
            ['python3', 'tools/archive_workspace.py', 'pack-text', '--source', str(source),
             '--destination', str(destination.relative_to(repository))],
            ['python3', 'tools/archive_workspace.py', 'verify-text',
             '--destination', str(destination.relative_to(repository)), '--check-originals']]
        for command in commands:
            result = subprocess.run(command, cwd=repository, text=True, capture_output=True)
            assert result.returncode == 0, {'command': command, 'output': result.stdout,
                                           'error': result.stderr}
        files = list(destination.glob('**/*.gz'))
        assert files and all(path.stat().st_size < 10485760 for path in files)
        manifest['archives'].append({'source': str(source),
                                     'destination': str(destination.relative_to(own)),
                                     'verify_text_check_originals': 'PASS',
                                     'gzip_files': len(files),
                                     'gzip_bytes': sum(path.stat().st_size for path in files),
                                     'largest_gzip_bytes': max(path.stat().st_size for path in files)})
    manifest['total_gzip_bytes'] = sum(item['gzip_bytes'] for item in manifest['archives'])
    manifest['originals_changed'] = False
    path = compact / 'manifest.json'
    path.write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'status': 'PASS COMPLETED TEXT ARCHIVES VERIFIED',
                      'manifest': str(path), 'runs': len(runs),
                      'total_gzip_bytes': manifest['total_gzip_bytes']}))


if __name__ == '__main__':
    main()
