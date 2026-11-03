"""Broker admission, ownership, immutable sealing and concurrency checks."""
import concurrent.futures
import json
from pathlib import Path
import shutil
import uuid

import numpy as np
import pytest

from wse.bootstrap_broker import Broker, Ledger, Refused
from wse.bootstrap_prepare import TOPIC


@pytest.fixture
def root():
    p=TOPIC/'work/tmp'/('broker-test-'+uuid.uuid4().hex)
    p.mkdir(parents=True)
    yield p
    shutil.rmtree(p)


def limits(n=2):
    return {'wall_seconds':1000,'sandbox_runs':n,'dev_evaluation_passes':n}


def test_atomic_budget_and_restart_cannot_reset(root):
    l=Ledger(root); l.init('a',limits(3))
    def charge(_):
        try: l.charge('a','dev_evaluation_passes'); return True
        except Refused: return False
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        assert sum(ex.map(charge,range(16)))==3
    Ledger(root).init('a',limits(3))
    assert l.status('a')['counts']['dev_evaluation_passes']==3
    with pytest.raises(Refused): l.init('a',limits(4))


def test_cross_session_and_seal(root):
    l=Ledger(root)
    for sid in ('a','b'): l.init(sid,limits())
    l.add('a','patch-a')
    with pytest.raises(Refused): l.own('b','patch-a')
    with pytest.raises(Refused): l.seal('b','patch-a')
    assert l.seal('a','patch-a')['sealed_patch_id']=='patch-a'
    for action in (lambda:l.add('a','patch-b'),lambda:l.charge('a','sandbox_runs'),lambda:l.seal('a','patch-a')):
        with pytest.raises(Refused): action()


def test_forbidden_fields_and_unowned_eval(root):
    b=Broker('phaseD-parent-01',root,limits())
    for req in ({'action':'evaluate','split':'test','patch_id':'foreign'},
                {'action':'run','session_id':'phaseD-parent-02','code':'print(1)'},
                {'action':'evaluate','patch_id':'foreign'},
                {'action':'result','job_id':'../secret_salt.txt'},
                {'action':'examples','indices':[-1]}):
        with pytest.raises(Refused): b.call(req)
    assert not (root/'queue').exists()
    assert b.call({'action':'status'})['counts']=={}


def test_failed_code_consumes_budget_and_isolated(root):
    b=Broker('phaseD-parent-01',root,limits(1))
    r=b.call({'action':'run','code':'raise RuntimeError("diagnostic failure")','names':[]})
    assert r['returncode']!=0
    assert b.call({'action':'status'})['counts']['sandbox_runs']==1
    with pytest.raises(Refused): b.call({'action':'run','code':'print(1)','names':[]})
    assert b.sandbox.selftest([TOPIC,root])['forbidden_paths_invisible']


def test_response_filters_private_fields(root):
    b=Broker('phaseD-parent-01',root,limits())
    b.ledger.add(b.sid,'test-patch')
    # No evaluator is run; exercise admitted job IDs and whitelist filtering.
    r=b.call({'action':'evaluate','patch_id':'test-patch'})
    assert b.call({'action':'result','job_id':r['job_id']})['status']=='pending'
    d=root/'results';d.mkdir()
    (d/(r['job_id']+'.summary.json')).write_text(json.dumps({
        'summary':{'F1/T0':{'mean_recovery':0}},'gen':{},'score_s':0,
        'oracle':'MUST_NOT_LEAK','test':'MUST_NOT_LEAK','editor':{'private':'MUST_NOT_LEAK'}}))
    out=b.call({'action':'result','job_id':r['job_id']})
    assert 'MUST_NOT_LEAK' not in json.dumps(out)
