"""Explicit complete text publication only after owned measurements/writers stop."""
import gzip, collections
from common import *

if __name__ == '__main__':
    no_gpu()
    root = C.parents[2]
    reproduction = pathlib.Path(load(C / 'tests/reproduction-checks.json')['live']['directory'])
    sources = [('completed-text-v1', W / 'raw'), ('runner-logs-v1', W / 'logs'), ('reproduction-text-v1', reproduction), ('fixtures-text-v1', C / 'tests')]
    receipt = []
    for namespace, source in sources:
        destination = C / 'evidence' / namespace
        assert not destination.exists(), 'Preserve existing publication namespace'
        pack = ['python3', str(root / 'tools/archive_workspace.py'), 'pack-text', '--source', str(source), '--destination', str(destination)]
        verify = ['python3', str(root / 'tools/archive_workspace.py'), 'verify-text', '--destination', str(destination), '--check-originals']
        outcomes = []
        for stage, command in [('pack', pack), ('verify', verify)]:
            # These final logs must not mutate any of the roots currently being packed.
            log = C / 'results' / ('publication-' + namespace + '-' + stage + '.log')
            ledger('Text publication ' + stage + ' START', namespace=namespace, command=command)
            with Heartbeat('text publication ' + namespace + ' ' + stage, 5), log.open('x') as output:
                result = subprocess.run(command, cwd=root, stdout=output, stderr=subprocess.STDOUT, timeout=600)
            ledger('Text publication ' + stage + ' END', namespace=namespace, exit_code=result.returncode)
            assert result.returncode == 0, str(log)
            outcomes.append({'stage':stage,'command':command,'exit_code':result.returncode,'log':str(log.relative_to(C))})
        records = [json.loads(line) for line in gzip.open(destination / 'archive-manifest.jsonl.gz', 'rt').read().splitlines()]
        statuses = collections.Counter(r.get('status','header') for r in records)
        receipt.append({'namespace':str(destination.relative_to(C)),'source':str(source),'outcomes':outcomes,'manifest_statuses':dict(statuses),'manifest':'archive-manifest.jsonl.gz'})
        save(C / 'results/text-publication.json', receipt)
        print('TEXT NAMESPACE VERIFIED', namespace, dict(statuses), flush=True)
    print('TEXT PUBLICATION COMPLETE', len(receipt), flush=True)
