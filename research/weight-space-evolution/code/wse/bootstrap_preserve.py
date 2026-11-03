"""Export completed parent provenance and every accepted lineage without private CLI homes or credentials."""
import json
from pathlib import Path
import sqlite3

from . import patch
from .bootstrap_patch_archive import export
from .bootstrap_prepare import TOPIC


def main():
    root=TOPIC/'work/phaseD-bootstrap/execution'
    state=json.loads((root/'supervisor.json').read_text())
    if state['status']!='terminal':raise RuntimeError('parent supervisor is not terminal')
    destination=TOPIC/'work/raw/20261103T-phaseD-bootstrap-parent-provenance'
    destination.mkdir(parents=True,exist_ok=True)
    database=root/'ledger.sqlite'
    with sqlite3.connect(database.as_uri()+'?mode=ro',uri=True) as db:
        sessions=[{'session_id':sid,'started':stamp,'limits':json.loads(limits),'counts':json.loads(counts),'sealed':sealed}
                  for sid,stamp,limits,counts,sealed in db.execute('SELECT * FROM sessions ORDER BY id')]
        candidates=[{'session_id':sid,'patch_id':pid,'editor_id':eid} for sid,pid,eid in db.execute('SELECT * FROM candidates ORDER BY session,patch')]
        for session in sessions:
            sid=session['session_id']
            events=[{'sequence':i,'session_id':sid,'timestamp':stamp,'kind':kind,'body':json.loads(body)}
                    for i,_,stamp,kind,body in db.execute('SELECT * FROM events WHERE session=? ORDER BY id',(sid,))]
            (destination/(sid+'-tools.jsonl')).write_text(''.join(json.dumps(e)+'\n' for e in events))
    (destination/'sessions.json').write_text(json.dumps(sessions,indent=2)+'\n')
    (destination/'candidates.json').write_text(json.dumps(candidates,indent=2)+'\n')
    (destination/'supervisor.json').write_text(json.dumps(state,indent=2)+'\n')
    members=set()
    for c in candidates:
        members.update(patch.lineage(c['patch_id']))
    for pid in sorted(members):export(pid,destination/'patch-exports')
    for sid in [s['session_id'] for s in sessions]:
        source=root/'logs'/(sid+'-parent.jsonl')
        rows=[json.loads(line) for line in source.read_text().splitlines()]
        if rows[-1].get('type')!='turn.completed':raise RuntimeError('parent conversation is not terminal')
        # Public research event stream only. Never copy private home, login or internal account/session databases.
        (destination/source.name).write_bytes(source.read_bytes())
    manifest={'source':'completed operator broker and Codex public JSON event streams','sessions':len(sessions),
              'accepted_candidates':len(candidates),'distinct_lineage_members_exported':len(members),
              'retained':'every lab request/response/failure, terminal conversation stream, lossless accepted patch deltas',
              'excluded':'private CLI homes/authentication/account databases; redundant numpy views and scratch payloads',
              'recovery':'obtain registered Gold, decompress patch-exports, recover each lineage parent-first with wse.bootstrap_patch_archive',
              'salt':'not read or exported; private backup recovery gap remains'}
    (destination/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':main()
