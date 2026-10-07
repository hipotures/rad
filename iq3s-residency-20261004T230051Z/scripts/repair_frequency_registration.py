"""Preserve a failed registration and exclude the read-only dependency symlink."""
import pathlib
from lab import ROOT, save
source = ROOT/'src/frequency-v1'
failed = ROOT/'variants/frequency-v1'
assert failed.is_dir() and not list(failed.iterdir()), 'Unexpected content; refuse repair'
record = {'state': 'FAILED', 'error': 'Untracked .venv symlink rejected by source identity check',
          'failed_registration_path': str(failed), 'source': str(source),
          'repair': 'Exclude read-only pinned venv in local .git/info/exclude. Register frequency-v1-ready separately; no rebuild or runtime change.'}
save(ROOT/'experiments/E006-frequency/v1/registration-failure.json', record)
(failed/'FAILED.json').write_text(__import__('json').dumps(record, indent=2)+'\n')
with (source/'.git/info/exclude').open('a') as stream:
    stream.write('\n# Read-only pinned research dependency environment\n.venv\n')
