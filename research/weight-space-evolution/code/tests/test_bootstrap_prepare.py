"""Fail-closed preparation checks; all fixture payloads remain under topic work/."""
import hashlib
import json
from pathlib import Path
import shutil
import uuid

import pytest

from wse.bootstrap_prepare import TOPIC, verify, verify_rows


@pytest.fixture
def scratch():
    p = TOPIC / 'work/tmp' / ('bootstrap-test-' + uuid.uuid4().hex)
    p.mkdir(parents=True)
    yield p
    shutil.rmtree(p)


def test_payload_corruption_and_duplicates_refused(scratch):
    row = {'id': 'instance'}
    for ext in ('json', 'npz'):
        payload = b'original fixture'
        (scratch / f'instance.{ext}').write_bytes(payload)
        row[f'{ext}_sha256'] = hashlib.sha256(payload).hexdigest()
    assert verify_rows([row], scratch) == 1
    with pytest.raises(ValueError, match='duplicate'):
        verify_rows([row, row], scratch)
    (scratch / 'instance.npz').write_bytes(b'corrupted')
    with pytest.raises(ValueError, match='hash mismatch'):
        verify_rows([row], scratch)


def test_missing_salt_never_replaced(scratch):
    cfg = scratch / 'configs/phaseD_bootstrap'
    cfg.mkdir(parents=True)
    (cfg / 'frozen-lock.json').write_text('{"files": {}}')
    frozen = scratch / 'configs/phaseD_v2'
    frozen.mkdir()
    (frozen / 'protocol_v2_frozen.json').write_text('{}')
    with pytest.raises(ValueError, match='salt missing'):
        verify(scratch)
    assert not (scratch / 'work').exists()


def test_frozen_source_drift_refused(scratch):
    cfg = scratch / 'configs/phaseD_bootstrap'
    cfg.mkdir(parents=True)
    (scratch / 'source.py').write_text('changed')
    (cfg / 'frozen-lock.json').write_text(json.dumps({'files': {'source.py': 'incorrect'}}))
    with pytest.raises(ValueError, match='frozen file changed'):
        verify(scratch)
