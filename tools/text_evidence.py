"""Deterministic gzip copies of text evidence; originals are never modified."""
import codecs
import collections
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import time
import zlib

EXTENSIONS = {'.json', '.jsonl', '.log', '.txt'}
MAX_COMPRESSED_BYTES = 10 * 1024 * 1024
CHUNK_BYTES = 64 * 1024
PRUNE = {'.git', '.venv', '.cache', '__pycache__', 'node_modules',
         'site-packages', 'dist-packages', 'repos', 'vendor', 'third_party',
         'build', 'builds', 'envs', 'src', 'source', 'sources', 'downloads',
         'dependency', 'dependencies', 'models', 'checkpoints', '.uv-cache',
         'python-packages', 'hf-xet-env', 'hf-xet-lib'}


class TextRejected(ValueError):
    pass


def private_part(part):
    return part.startswith('.env') or part in {'.ssh', 'credentials', 'secrets'} or part.split('.')[0] in {'credentials', 'secrets'}


def path_reason(parts):
    if any(private_part(p) for p in parts):
        return 'private-configuration'
    if any(p in PRUNE or p.endswith('venv') for p in parts):
        return 'source-or-environment-directory'
    return None


class TextScan:
    """Bounded-memory UTF-8 and credential checks, including chunk boundaries."""
    def __init__(self, patterns):
        self.patterns = patterns
        self.decoder = codecs.getincrementaldecoder('utf-8')()
        self.tail = b''
        self.bytes = 0
        self.digest = hashlib.sha256()

    def feed(self, chunk):
        if b'\0' in chunk:
            raise TextRejected('binary-content')
        try:
            self.decoder.decode(chunk, final=False)
        except UnicodeDecodeError:
            raise TextRejected('non-utf8-content') from None
        combined = self.tail + chunk
        for label, pattern in self.patterns:
            if pattern.search(combined):
                raise TextRejected(label)
        self.tail = combined[-512:]
        self.bytes += len(chunk)
        self.digest.update(chunk)

    def finish(self):
        try:
            self.decoder.decode(b'', final=True)
        except UnicodeDecodeError:
            raise TextRejected('non-utf8-content') from None
        return {'original_bytes': self.bytes, 'original_sha256': self.digest.hexdigest()}


def inspect_gzip(data, patterns, heartbeat=None):
    """Inspect decompressed indexed bytes and verify gzip framing/CRC to EOF."""
    if len(data) >= MAX_COMPRESSED_BYTES:
        return 'large-artifact'
    scanner = TextScan(patterns)
    try:
        if not data.startswith(b'\x1f\x8b'):
            return 'invalid-gzip'
        with gzip.GzipFile(fileobj=io.BytesIO(data), mode='rb') as stream:
            while chunk := stream.read(CHUNK_BYTES):
                scanner.feed(chunk)
                if heartbeat:
                    heartbeat()
        scanner.finish()
    except TextRejected as exc:
        return str(exc)
    except (OSError, EOFError, zlib.error):
        return 'invalid-gzip'
    return None


class LimitedWriter:
    def __init__(self, stream):
        self.stream = stream
        self.bytes = 0
        self.over_limit = False

    def write(self, chunk):
        if self.over_limit or self.bytes + len(chunk) >= MAX_COMPRESSED_BYTES:
            # Keep the gzip writer's close path valid, but discard over-limit
            # output. The caller rejects and removes this temporary file.
            self.over_limit = True
            return len(chunk)
        written = self.stream.write(chunk)
        self.bytes += written
        return written

    def flush(self):
        self.stream.flush()


def signature(st):
    return st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns


def compress_file(source, destination, patterns, heartbeat):
    """Read one stable regular source, validate it, and produce one complete gzip."""
    before = source.stat(follow_symlinks=False)
    if not stat.S_ISREG(before.st_mode):
        raise TextRejected('non-regular-source')
    fd = os.open(source, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
    with os.fdopen(fd, 'rb') as original:
        opened = os.fstat(original.fileno())
        if not stat.S_ISREG(opened.st_mode) or signature(opened) != signature(before):
            raise RuntimeError('Source changed before read: ' + str(source))
        scanner = TextScan(patterns)
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            with destination.open('xb') as out:
                writer = LimitedWriter(out)
                with gzip.GzipFile(filename='', fileobj=writer, mode='wb',
                                   compresslevel=9, mtime=0) as compressed:
                    while chunk := original.read(CHUNK_BYTES):
                        scanner.feed(chunk)
                        compressed.write(chunk)
                        if writer.over_limit:
                            raise TextRejected('compressed-size-limit')
                        heartbeat()
                    facts = scanner.finish()
                if writer.over_limit:
                    raise TextRejected('compressed-size-limit')
        finally:
            if signature(os.fstat(original.fileno())) != signature(before) or signature(source.stat(follow_symlinks=False)) != signature(before):
                raise RuntimeError('Source changed during read: ' + str(source))
    data = destination.read_bytes()
    facts.update(compressed_bytes=len(data), gzip_sha256=hashlib.sha256(data).hexdigest())
    return facts


def source_entries(source, paths=None):
    if paths is not None:
        for value in sorted(set(paths)):
            relative = Path(value)
            if relative.is_absolute() or '..' in relative.parts or not relative.parts:
                raise ValueError('Unsafe selected source path')
            p = source / relative
            if any((source.joinpath(*relative.parts[:n])).is_symlink() for n in range(1, len(relative.parts) + 1)):
                yield p, relative, 'local-symlink', False
            else:
                yield p, relative, path_reason(relative.parts), False
        return
    for parent, dirs, names in os.walk(source, followlinks=False):
        dirs.sort()
        for name in list(dirs):
            p = Path(parent) / name
            relative = p.relative_to(source)
            why = 'local-symlink' if p.is_symlink() else path_reason(relative.parts)
            if why:
                dirs.remove(name)
                yield p, relative, why, True
        for name in sorted(names):
            p = Path(parent) / name
            relative = p.relative_to(source)
            why = 'local-symlink' if p.is_symlink() else path_reason(relative.parts)
            yield p, relative, why, False


def pack(source, destination, patterns, paths=None):
    """Write a fresh evidence namespace atomically; skip rejected files with reasons."""
    source = Path(source).resolve(strict=True)
    destination = Path(destination).absolute()
    if not source.is_dir():
        raise ValueError('Source must be a directory')
    if destination != destination.resolve():
        raise ValueError('Refuse destination symlink or noncanonical path')
    if destination.exists():
        raise FileExistsError('Refuse existing destination: ' + str(destination))
    if source.is_relative_to(destination) or (paths is None and destination.is_relative_to(source)):
        raise ValueError('Source and destination must not contain each other')
    destination.parent.mkdir(parents=True, exist_ok=True)
    last = time.monotonic()

    def heartbeat():
        nonlocal last
        if time.monotonic() - last >= 25:
            print('HEARTBEAT text evidence packaging', len(records), 'records processed', flush=True)
            last = time.monotonic()

    records = []
    with tempfile.TemporaryDirectory(prefix='.text-evidence-', dir=destination.parent) as temp:
        target = Path(temp)
        for p, relative, why, is_directory in source_entries(source, paths):
            if is_directory:
                records.append({'path': str(relative) + '/', 'status': 'skipped', 'reason': why})
                continue
            record = {'path': str(relative), 'source_bytes': p.lstat().st_size}
            if why is None and p.suffix.lower() not in EXTENSIONS:
                why = 'non-text-format'
            archive = target / (str(relative) + '.gz')
            if why is None:
                try:
                    facts = compress_file(p, archive, patterns, heartbeat)
                except TextRejected as exc:
                    why = str(exc)
                    archive.unlink(missing_ok=True)
                else:
                    record.update(status='archived', **facts)
            if why:
                record.update(status='skipped', reason=why)
            records.append(record)
            heartbeat()
        header = {'record': 'header', 'schema': 'rad-text-evidence-v1',
                  'source_root': str(source), 'extensions': sorted(EXTENSIONS),
                  'gzip_level': 9, 'gzip_mtime': 0, 'gzip_filename': '',
                  'compressed_limit_bytes_exclusive': MAX_COMPRESSED_BYTES,
                  'originals_modified': False,
                  'selection': 'Explicit preselected source paths' if paths is not None else 'Completed source directory',
                  'scope': 'Complete bytes of selected text evidence; binary data and rejected files remain external. No payload splitting.'}
        # The index can be large too; retain it as a checked text archive.
        manifest = target / 'archive-manifest.jsonl.gz'
        if manifest.exists():
            raise ValueError('Source path conflicts with archive manifest')
        raw_manifest = target / '.manifest.tmp'
        with raw_manifest.open('x', encoding='utf-8') as stream:
            for record in [header, *records]:
                stream.write(json.dumps(record, sort_keys=True, separators=(',', ':')) + '\n')
        compress_file(raw_manifest, manifest, patterns, heartbeat)
        raw_manifest.unlink()
        selected = [r for r in records if r['status'] == 'archived']
        summary = {'destination': str(destination), 'files_archived': len(selected),
                   'original_bytes_archived': sum(r['original_bytes'] for r in selected),
                   'compressed_bytes_archived': sum(r['compressed_bytes'] for r in selected),
                   'manifest_bytes': manifest.stat().st_size,
                   'skipped': dict(collections.Counter(r['reason'] for r in records if r['status'] == 'skipped'))}
        if destination.exists():
            raise FileExistsError('Destination appeared during packaging: ' + str(destination))
        os.rename(target, destination)
    print(json.dumps(summary, indent=2), flush=True)
    return summary


def verify(namespace, patterns, check_originals=False):
    """Verify a complete namespace without extracting or overwriting any file."""
    namespace = Path(namespace).resolve(strict=True)
    manifest = namespace / 'archive-manifest.jsonl.gz'
    why = inspect_gzip(manifest.read_bytes(), patterns)
    if why:
        raise ValueError('Invalid archive manifest: ' + why)
    with gzip.open(manifest, 'rt', encoding='utf-8') as stream:
        header = json.loads(next(stream))
        if header.get('schema') != 'rad-text-evidence-v1':
            raise ValueError('Unsupported archive schema')
        records = [json.loads(line) for line in stream]
    source = Path(header['source_root'])
    expected = {'archive-manifest.jsonl.gz'}
    count = original_bytes = compressed_bytes = 0
    last = time.monotonic()
    for record in records:
        if record['status'] != 'archived':
            continue
        relative = Path(record['path'])
        if relative.is_absolute() or '..' in relative.parts or not relative.parts:
            raise ValueError('Unsafe manifest source path')
        archive = namespace / (str(relative) + '.gz')
        if archive.resolve() != archive.absolute() or not archive.is_file():
            raise ValueError('Missing or linked archive: ' + str(relative))
        if str(relative) + '.gz' in expected:
            raise ValueError('Duplicate manifest source path')
        expected.add(str(relative) + '.gz')
        data = archive.read_bytes()
        if len(data) != record['compressed_bytes'] or len(data) >= MAX_COMPRESSED_BYTES or hashlib.sha256(data).hexdigest() != record['gzip_sha256']:
            raise ValueError('Compressed identity mismatch: ' + str(relative))
        scanner = TextScan(patterns)
        with gzip.open(archive, 'rb') as stream:
            while chunk := stream.read(CHUNK_BYTES):
                scanner.feed(chunk)
        facts = scanner.finish()
        if any(facts[key] != record[key] for key in facts):
            raise ValueError('Original identity mismatch: ' + str(relative))
        if check_originals:
            original = source / relative
            if original.resolve() != original.absolute() or not original.is_file():
                raise ValueError('Missing or linked original: ' + str(relative))
            digest = hashlib.sha256()
            size = 0
            with original.open('rb') as stream:
                while chunk := stream.read(CHUNK_BYTES):
                    digest.update(chunk)
                    size += len(chunk)
            if size != facts['original_bytes'] or digest.hexdigest() != facts['original_sha256']:
                raise ValueError('Current original differs: ' + str(relative))
        count += 1
        original_bytes += facts['original_bytes']
        compressed_bytes += len(data)
        if time.monotonic() - last >= 25:
            print('HEARTBEAT text evidence verification', count, 'files', flush=True)
            last = time.monotonic()
    actual = {str(p.relative_to(namespace)) for p in namespace.rglob('*') if p.is_file() or p.is_symlink()}
    if actual != expected:
        raise ValueError('Archive namespace contains missing or unlisted files')
    return {'namespace': str(namespace), 'state': 'PASS', 'files': count,
            'original_bytes': original_bytes, 'compressed_bytes': compressed_bytes,
            'manifest_bytes': manifest.stat().st_size,
            'current_originals_checked': check_originals,
            'scope': 'Every gzip framing/CRC, UTF-8, recognizable credentials, compressed and original SHA256/size, complete namespace membership.'}
