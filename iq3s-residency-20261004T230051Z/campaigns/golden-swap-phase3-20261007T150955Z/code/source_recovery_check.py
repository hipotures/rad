"""Test the documented public-base reconstruction without rebuilding or touching inputs."""
import hashlib, io, os, tarfile
from common import *

BASE = '6f32ec070f23ced9f50e704d854d775da52591ab'

def preserve_summary(result):
    summary = {k:v for k,v in result.items() if k != 'files'}
    summary['full_inventory'] = 'evidence/fixtures-text-v1/source-recovery.json.gz'
    summary['full_inventory_original_sha256'] = hashlib.sha256((C / 'tests/source-recovery.json').read_bytes()).hexdigest()
    summary['row_inventory_policy'] = 'Original full JSON remains local and unchanged; complete verified gzip is the published row-level record.'
    save(C / 'tests/source-recovery-summary.json', summary)

if __name__ == '__main__':
    no_gpu()
    assert not (C / 'tests/source-recovery.json').exists(), 'Preserve completed source inventory; use a fresh campaign/output namespace'
    identity = load(C / 'configs/runtime-identity.json')
    destination = W / 'tmp' / ('source-recovery-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    destination.mkdir(parents=True, exist_ok=False)
    commands = []
    with Heartbeat('public source reconstruction', 5):
        metadata = subprocess.check_output(['gh', 'api', 'repos/Niko1221/Strata/commits/' + BASE], timeout=60)
        assert json.loads(metadata)['sha'] == BASE
        commands.append(['git', 'archive', BASE])
        archive = subprocess.check_output(commands[-1], cwd=SOURCE, timeout=60)
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(destination, filter='data')
        patch = C / 'patches/cumulative-from-original.diff'
        command = ['git', 'apply', '--exclude=.venv', str(patch)]
        commands.append(command)
        subprocess.run(command, cwd=destination, check=True, timeout=60)
        entries = subprocess.check_output(['git', 'ls-tree', '-r', '-z', identity['source_sha']], cwd=SOURCE).split(b'\0')
        checked = []
        excluded = []
        for entry in entries:
            if not entry:
                continue
            header, filename = entry.split(b'\t', 1)
            mode, kind, blob = header.decode().split()
            relative = os.fsdecode(filename)
            if relative == '.venv':
                excluded.append({'path': relative, 'reason': 'Machine-local environment symlink; excluded in documented portable rebuild'})
                continue
            path = destination / relative
            actual = os.fsencode(os.readlink(path)) if mode == '120000' else path.read_bytes()
            expected = os.fsencode(os.readlink(SOURCE / relative)) if mode == '120000' else (SOURCE / relative).read_bytes()
            assert actual == expected, relative
            if mode != '120000':
                assert bool(path.stat().st_mode & 0o111) == (mode == '100755'), relative
                # Public attributes request CRLF in .bat checkouts; also prove canonical blob identity.
                canonical = subprocess.check_output(['git', 'hash-object', '--path=' + relative, str(path)], cwd=SOURCE, text=True).strip()
                assert canonical == blob, relative
            else:
                assert actual == subprocess.check_output(['git', 'cat-file', 'blob', blob], cwd=SOURCE)
            checked.append({'path': relative, 'mode': mode, 'git_blob': blob, 'bytes': len(actual), 'sha256': hashlib.sha256(actual).hexdigest()})
    save(C / 'tests/source-recovery.json', {'state': 'PASS', 'public_base': BASE, 'public_base_verified_with': 'gh api repos/Niko1221/Strata/commits/' + BASE, 'source': identity['source_sha'], 'destination': str(destination), 'commands': commands, 'patch_sha256': hashlib.sha256(patch.read_bytes()).hexdigest(), 'checked_files': len(checked), 'files': checked, 'excluded': excluded, 'scope': 'Exact checkout bytes, executable modes and canonical Git blobs. Public .gitattributes CRLF checkout conversions are honored; no second binary build or model acquisition claimed.'})
    preserve_summary(load(C / 'tests/source-recovery.json'))
    print('SOURCE RECOVERY PASS', len(checked), flush=True)
