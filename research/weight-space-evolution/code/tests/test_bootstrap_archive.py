"""Lossless BF16 lineage reconstruction and corruption rejection on a tiny immutable Gold fixture."""
import json
import shutil
import uuid

import numpy as np
import pytest

from wse import patch, registry
from wse.bootstrap_patch_archive import export, recover
from wse.bootstrap_prepare import TOPIC
from wse.tensors import f32_to_bf16_bits, st_save


def test_lossless_bf16_parent_child_recovery_and_corruption(monkeypatch):
    root=TOPIC/'work/tmp'/('archive-test-'+uuid.uuid4().hex);root.mkdir(parents=True)
    monkeypatch.setenv('WSE_WORK_ROOT',str(root))
    try:
        name='model.language_model.layers.0.mlp.down_proj.weight'
        a=f32_to_bf16_bits(np.arange(1,9,dtype=np.float32).reshape(2,4))
        source=root/'input.safetensors';st_save(source,{name:('BF16',a)})
        registry.register('tiny-bf16@1',source,{'generator':'test fixture'})
        policy={'allowed_tensors':[name],'max_abs_value':100,'max_changed_entries':8,'forbid_uniform_scale':True}
        b=a.copy();b[0,0]+=1
        parent=patch.create('tiny-bf16@1',{name:b},policy,{'method':'fixture'})
        c=b.copy();c[1,1]+=1
        child=patch.create('tiny-bf16@1',{name:c},policy,{'method':'fixture child'},parent['patch_id'])
        for rec in (parent,child):
            evidence=export(rec['patch_id'],root/'evidence')
            shutil.rmtree(patch.patches_dir()/rec['patch_id'])
            assert recover(evidence)==rec['patch_id']
        assert np.array_equal(patch.materialize('tiny-bf16@1',child['patch_id'],[name])[name][1],c)
        body=json.loads(evidence.read_text());body['arrays']['t0_val']['values'][0]+=2
        evidence.write_text(json.dumps(body))
        with pytest.raises(ValueError,match='identity mismatch'):recover(evidence)
        assert registry.verify('tiny-bf16@1')
    finally:
        for p in root.rglob('*'):
            if p.is_dir():p.chmod(0o700)
            else:p.chmod(0o600)
        shutil.rmtree(root)
