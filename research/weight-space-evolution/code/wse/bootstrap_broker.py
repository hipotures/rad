"""Session-bound parent tools. Operator process only; parent receives no filesystem/queue access.

SQLite admission transactions count failures before execution. Arbitrary numerical code runs only in the existing
bubblewrap sandbox, whose isolation is rechecked before each execution. Frozen evaluator source stays unchanged.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import sqlite3
import time
import uuid

import numpy as np

from . import patch, registry
from .bootstrap_prepare import TOPIC
from .sandbox import Sandbox
from .tensors import bf16_bits_to_f32, f32_to_bf16_bits

GOLD = 'qwen3.5-0.8B@2fc0636'
TIERS = ['T0', 'T1', 'T2', 'T2P']


class Refused(ValueError):
    pass


class Ledger:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path = self.root / 'ledger.sqlite'
        with self.connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY, started REAL, limits TEXT, counts TEXT, sealed TEXT);
            CREATE TABLE IF NOT EXISTS candidates(session TEXT, patch TEXT, editor TEXT UNIQUE, PRIMARY KEY(session,patch));
            CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, session TEXT, stamp REAL, kind TEXT, body TEXT);
            ''')
        self.path.chmod(0o600)

    def connect(self):
        return sqlite3.connect(self.path, timeout=60)

    def init(self, sid, limits):
        with self.connect() as db:
            db.execute('INSERT OR IGNORE INTO sessions VALUES(?,?,?,?,NULL)',
                       (sid, time.time(), json.dumps(limits, sort_keys=True), '{}'))
            old = db.execute('SELECT limits FROM sessions WHERE id=?', (sid,)).fetchone()[0]
            if json.loads(old) != limits:
                raise Refused('session limits cannot be changed after initialization')

    def event(self, sid, kind, body):
        with self.connect() as db:
            db.execute('INSERT INTO events(session,stamp,kind,body) VALUES(?,?,?,?)',
                       (sid, time.time(), kind, json.dumps(body, allow_nan=False)))

    def charge(self, sid, resource):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT started,limits,counts,sealed FROM sessions WHERE id=?', (sid,)).fetchone()
            if row is None:
                raise Refused('unknown session')
            started, limits, counts, sealed = row
            limits, counts = json.loads(limits), json.loads(counts)
            if sealed is not None:
                raise Refused('session is sealed')
            if time.time() - started > limits['wall_seconds']:
                raise Refused('session wall budget exhausted')
            if resource not in ('dev_evaluation_passes', 'sandbox_runs'):
                raise Refused('unknown resource')
            if counts.get(resource, 0) >= limits[resource]:
                raise Refused('session resource budget exhausted')
            counts[resource] = counts.get(resource, 0) + 1
            db.execute('UPDATE sessions SET counts=? WHERE id=?', (json.dumps(counts), sid))
            return counts[resource]

    def own(self, sid, pid):
        with self.connect() as db:
            row = db.execute('SELECT editor FROM candidates WHERE session=? AND patch=?', (sid, pid)).fetchone()
        if row is None:
            raise Refused('patch is not owned by this session')
        return row[0]

    def add(self, sid, pid):
        eid = sid + '-' + pid
        with self.connect() as db:
            if db.execute('SELECT sealed FROM sessions WHERE id=?', (sid,)).fetchone()[0] is not None:
                raise Refused('session is sealed')
            db.execute('INSERT OR IGNORE INTO candidates VALUES(?,?,?)', (sid, pid, eid))
        return eid

    def seal(self, sid, pid):
        if pid:
            self.own(sid, pid)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT sealed FROM sessions WHERE id=?', (sid,)).fetchone()
            if row is None or row[0] is not None:
                raise Refused('unknown or already sealed session')
            db.execute('UPDATE sessions SET sealed=? WHERE id=?', (pid or 'FAILURE', sid))
        return {'sealed_patch_id': pid, 'failure': not bool(pid)}

    def status(self, sid):
        with self.connect() as db:
            started, limits, counts, sealed = db.execute(
                'SELECT started,limits,counts,sealed FROM sessions WHERE id=?', (sid,)).fetchone()
            owned = db.execute('SELECT patch FROM candidates WHERE session=?', (sid,)).fetchall()
        return {'session_id': sid, 'limits': json.loads(limits), 'counts': json.loads(counts),
                'elapsed_seconds': time.time() - started, 'sealed': sealed, 'owned_patches': [r[0] for r in owned]}


class Broker:
    def __init__(self, sid, campaign_root=None, limits=None, gold_id=GOLD):
        # Session identity comes from operator startup arguments, never tool arguments.
        specs = json.loads((TOPIC / 'configs/phaseD_bootstrap/sessions.json').read_text())['sessions']
        if sid not in {s['session_id'] for s in specs}:
            raise Refused('unknown session')
        self.sid, self.gold_id = sid, gold_id
        self.spec = next(s for s in specs if s['session_id'] == sid)
        self.root = Path(campaign_root or TOPIC / 'work/phaseD-bootstrap/execution')
        self.ledger = Ledger(self.root)
        b = json.loads((TOPIC / 'configs/phaseD_bootstrap/budget.json').read_text())
        self.ledger.init(sid, limits or b['proposed_limits']['per_session'])
        self.session = self.root / sid
        self.session.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.man = registry.manifest(gold_id)
        self.allowed = sorted(n for n in self.man['tensors'] if n.startswith('model.language_model.layers.'))
        self.view = self.session / 'gold-view'
        self.view.mkdir(exist_ok=True)
        desc = {'shapes': {n: self.man['tensors'][n]['shape'] for n in self.allowed}, 'editable': self.allowed}
        (self.view / 'description.json').write_text(json.dumps(desc))
        self.sandbox = Sandbox(TOPIC / 'work/envs/sandbox', self.view, self.session / 'scratch',
                               self.session / 'tmp', timeout=120, mem=8 << 30)

    def checked_names(self, names):
        if not isinstance(names, list) or len(names) > 8 or not all(isinstance(n, str) and n in self.allowed for n in names):
            raise Refused('select at most eight allowed layer tensors')
        return names

    def export(self, names):
        for n in self.checked_names(names):
            p = self.view / (n + '.npy')
            if not p.exists():
                dt, a = registry.load(self.gold_id, [n])[n]
                a = bf16_bits_to_f32(a) if dt == 'BF16' else a.astype(np.float32)
                np.save(p, a)
                p.chmod(0o400)

    def run(self, code, names):
        if not isinstance(code, str) or len(code.encode()) > 100000:
            raise Refused('code payload too large')
        self.ledger.charge(self.sid, 'sandbox_runs')
        self.export(names)
        checks = self.sandbox.selftest([TOPIC, self.root, Path.home() / '.ssh', TOPIC / 'work/benchmarks/phaseD-v2'])
        if not checks or not all(v is True for v in checks.values()):
            raise Refused('sandbox isolation failed')
        return self.sandbox.run(code)

    def submit(self, parent_id, rationale):
        if parent_id:
            self.ledger.own(self.sid, parent_id)
        edit = self.session / 'scratch/edit'
        if edit.is_symlink() or not edit.is_dir():
            raise Refused('no regular edit directory')
        files = sorted(edit.iterdir())
        if len(files) > 8:
            raise Refused('at most eight proposal tensors')
        names = self.checked_names([p.name[:-4] for p in files if p.name.endswith('.npy')])
        if len(names) != len(files):
            raise Refused('unexpected proposal file')
        proposed = {}
        for p, n in zip(files, names):
            if p.is_symlink() or not p.is_file() or p.stat().st_size > 128 << 20:
                raise Refused('proposal must be a bounded regular file')
            a = np.load(p, allow_pickle=False)
            if a.dtype != np.float32 or list(a.shape) != self.man['tensors'][n]['shape'] or not np.isfinite(a).all():
                raise Refused('proposal dtype, shape or values invalid')
            dt = self.man['tensors'][n]['dtype']
            proposed[n] = f32_to_bf16_bits(a) if dt == 'BF16' else a
        policy = {'allowed_tensors': self.allowed, 'max_abs_value': 1e4,
                  'max_changed_entries': 10 ** 7, 'forbid_uniform_scale': True}
        rec = patch.create(self.gold_id, proposed, policy, {'author_session': self.sid, 'rationale': rationale,
                            'method': 'sandboxed direct numerical proposal'}, parent_id=parent_id)
        self.ledger.add(self.sid, rec['patch_id'])
        return {k: rec[k] for k in ('patch_id', 'parent_id', 'changed_entries_total', 'delta_l2_total')}

    def evaluate(self, pid):
        eid = self.ledger.own(self.sid, pid)
        number = self.ledger.charge(self.sid, 'dev_evaluation_passes')
        jid = f'{self.sid}-pass-{number:03d}__dev'
        job = {'job_id': jid, 'editor_id': eid, 'split': 'dev', 'tiers': TIERS, 'ids': None,
               'submitted_at': time.time()}
        d = self.root / 'queue/pending'
        d.mkdir(parents=True, exist_ok=True)
        tmp = d / ('.' + uuid.uuid4().hex)
        tmp.write_text(json.dumps(job))
        os.replace(tmp, d / (jid + '.json'))
        return {'job_id': jid, 'status': 'submitted', 'dev_passes_used': number}

    def result(self, jid):
        if not isinstance(jid, str) or Path(jid).name != jid or not jid.startswith(self.sid + '-pass-') or not jid.endswith('__dev'):
            raise Refused('not a dev job of this session')
        # Only the session's admitted job IDs can be queried, not arbitrary operator files.
        with self.ledger.connect() as db:
            rows = db.execute("SELECT body FROM events WHERE session=? AND kind='response'", (self.sid,)).fetchall()
        if not any(json.loads(r[0]).get('job_id') == jid for r in rows):
            raise Refused('job was not admitted')
        p = self.root / 'results' / (jid + '.summary.json')
        if not p.exists():
            return {'job_id': jid, 'status': 'pending'}
        rec = json.loads(p.read_text())
        if 'error' in rec:
            return {'job_id': jid, 'status': 'failed'}
        return {'job_id': jid, 'status': 'done', 'summary': rec['summary'],
                'resources': {k: rec.get(k) for k in ('gen', 'score_s')}}

    def call(self, req):
        if not isinstance(req, dict):
            raise Refused('request must be an object')
        if self.ledger.status(self.sid)['sealed'] is not None and req.get('action') != 'status':
            raise Refused('session is sealed')
        fields = {'status': set(), 'inventory': set(), 'examples': {'indices'}, 'run': {'code', 'names'},
                  'submit': {'parent_id', 'rationale'}, 'evaluate': {'patch_id'}, 'result': {'job_id'},
                  'seal': {'patch_id'}}
        action = req.get('action')
        if action not in fields or set(req) - {'action'} - fields[action]:
            raise Refused('unknown action or forbidden request field')
        self.ledger.event(self.sid, 'request', req)
        try:
            if action == 'status':
                out = self.ledger.status(self.sid)
            elif action == 'inventory':
                out = {'tensors': {n: self.man['tensors'][n] for n in self.allowed}}
            elif action == 'examples':
                indices = req.get('indices', [0])
                if not isinstance(indices, list) or len(indices) > 4 or any(type(i) is not int or not 0 <= i < 104 for i in indices):
                    raise Refused('at most four dev example indices in [0,103]')
                prompts = json.loads((TOPIC / self.spec['scratch'] / 'view/dev_prompts.json').read_text())
                out = {'examples': [prompts[i] for i in indices]}
            elif action == 'run':
                out = self.run(req.get('code'), req.get('names', []))
            elif action == 'submit':
                out = self.submit(req.get('parent_id'), req.get('rationale', ''))
            elif action == 'evaluate':
                out = self.evaluate(req.get('patch_id'))
            elif action == 'result':
                out = self.result(req.get('job_id'))
            elif action == 'seal':
                out = self.ledger.seal(self.sid, req.get('patch_id'))
            json.dumps(out, allow_nan=False)
        except Exception as ex:
            self.ledger.event(self.sid, 'failure', {'type': type(ex).__name__, 'message': str(ex)[:500]})
            raise
        self.ledger.event(self.sid, 'response', out)
        return out
