#!/usr/bin/env python3
"""Read-only offline audit of one generated publication script.

This never imports/extracts/executes packaged code or invokes Git/GitHub. It
writes only its explicitly requested independent JSON receipt.
"""
import argparse
import base64
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import tarfile


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(name):
    need(isinstance(name, str) and name and '\\' not in name and
         not PurePosixPath(name).is_absolute() and
         not any(part in {'', '.', '..', '.git'} for part in name.split('/')) and
         not any(ord(character) < 32 for character in name), 'unsafe path ' + repr(name))


def audit(script, expected_spec=None):
    source = script.read_bytes()
    shell = source.decode('utf-8')
    encoded = re.search(r'encoded = """(.*?)"""', shell, re.S)
    need(encoded is not None, 'embedded payload missing')
    payload = base64.b64decode(''.join(encoded.group(1).split()), validate=True)
    payload_hash = re.search(r'if sha\(compressed\) != "([a-f0-9]{64})"', shell).group(1)
    manifest_hash = re.search(r'if sha\(entries.get\("manifest.json", b""\)\) != "([a-f0-9]{64})"', shell).group(1)
    runtime_hash = re.search(r'if sha\(entries.get\("publication_runtime.py", b""\)\) != "([a-f0-9]{64})"', shell).group(1)
    need(digest(payload) == payload_hash, 'compressed archive hash mismatch')
    entries = {}
    total = 0
    with tarfile.open(fileobj=io.BytesIO(payload), mode='r:gz') as archive:
        for entry in archive:
            safe_path(entry.name)
            need(entry.isfile() and entry.size <= 1048576, 'unsafe entry type/size')
            need(entry.name not in entries, 'duplicate member')
            total += entry.size
            need(total <= 33554432, 'archive expansion exceeds bound')
            entries[entry.name] = archive.extractfile(entry).read()
    need(digest(entries['manifest.json']) == manifest_hash, 'manifest hash mismatch')
    need(digest(entries['publication_runtime.py']) == runtime_hash, 'runtime hash mismatch')
    manifest = json.loads(entries['manifest.json'])
    need(set(entries) == set(manifest['members']) | {'manifest.json'}, 'member allowlist mismatch')
    for name, item in manifest['members'].items():
        safe_path(name)
        need(item['mode'] in (420, 493), 'unsafe member mode')
        need(item['bytes'] == len(entries[name]) and item['sha256'] == digest(entries[name]),
             'member hash or size mismatch: ' + name)
    release = manifest['release']
    if expected_spec:
        spec = json.loads(expected_spec.read_text())
        # Prepared body and normalized rules are builder outputs. Compare the
        # immutable scientific/policy/allowlist fields directly, never invent
        # candidate approval from this equality.
        for key in ('candidate_id', 'candidate_digest', 'exact_kappa', 'base_sha',
                    'upstream', 'default_branch', 'minimum_relative_improvement',
                    'status', 'freeze_approved', 'gates', 'changes',
                    'source_fingerprints', 'protected_base_paths', 'local_checks'):
            need(release[key] == spec[key], 'frozen spec field differs: ' + key)
    need(release['minimum_relative_improvement'] == '1/100', 'policy is not immutable 1%')
    expected = {'publication_runtime.py'}
    acquired = []
    content_warnings = []
    for change in release['changes']:
        safe_path(change['path'])
        if change.get('acquire'):
            acquired.append({'path': change['path'], 'source': change['acquire']})
            continue
        name = 'files/' + change['path']
        expected.add(name)
        need(name in entries and digest(entries[name]) == change['sha256'], 'change payload mismatch')
        data = entries[name]
        if change['path'].endswith('.gz'):
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as compressed:
                data = compressed.read(33554433)
            need(len(data) <= 33554432, 'gzip fixture scan expansion bound exceeded')
        if any(marker in data for marker in (b'/srv/ai/', b'/home/user/', b'frontier-sprint-20261009')):
            content_warnings.append({'path': change['path'], 'kind': 'internal path or campaign marker'})
        if re.search(rb'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|sk-(?:proj-)?[A-Za-z0-9_-]{24,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)', data):
            content_warnings.append({'path': change['path'], 'kind': 'credential pattern'})
    need(set(manifest['members']) == expected, 'unrelated embedded payload member')
    text = entries['manifest.json']
    if any(marker in text for marker in (b'/srv/ai/', b'/home/user/', b'frontier-sprint-20261009')):
        content_warnings.append({'path': 'manifest.json', 'kind': 'internal path or campaign marker'})
    return {'schema_version': 1, 'script_sha256': digest(source), 'bytes': len(source),
            'compressed_payload_sha256': payload_hash, 'manifest_sha256': manifest_hash,
            'runtime_sha256': runtime_hash, 'candidate_id': release['candidate_id'],
            'candidate_digest': release['candidate_digest'], 'exact_kappa': release['exact_kappa'],
            'embedded_member_count': len(manifest['members']), 'embedded_uncompressed_bytes': total,
            'change_count': len(release['changes']), 'acquired': acquired,
            'content_warnings': content_warnings, 'offline_integrity_pass': True,
            'executed_packaged_code': False, 'candidate_science_approved_by_audit': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--script', type=Path, required=True)
    parser.add_argument('--spec', type=Path)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    need(not args.receipt.exists(), 'fresh receipt required')
    result = audit(args.script, args.spec)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ('candidate_id', 'script_sha256',
                       'embedded_member_count', 'change_count', 'content_warnings')}))


if __name__ == '__main__':
    main()
