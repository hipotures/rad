"""Campaign adapter for the unchanged Phase D v2 evaluator; live registry from broker ledger."""
import argparse
import json
from pathlib import Path

from . import pd2_eval as E
from .bootstrap_broker import GOLD, Ledger, Refused


class LiveEditors:
    def __init__(self, root):
        self.ledger = Ledger(root)

    def __getitem__(self, eid):
        if eid == 'E0':
            return {'editor_id': 'E0', 'patch_id': None, 'gold_id': GOLD}
        with self.ledger.connect() as db:
            row = db.execute('SELECT session,patch FROM candidates WHERE editor=?', (eid,)).fetchone()
        if row is None:
            raise Refused('editor not admitted by broker')
        return {'editor_id': eid, 'patch_id': row[1], 'gold_id': GOLD, 'author_session': row[0]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--campaign', required=True)
    ap.add_argument('--follow', action='store_true')
    a = ap.parse_args()
    E.editors = lambda: LiveEditors(Path(a.root))
    E.worker(argparse.Namespace(queue=str(Path(a.root) / 'queue'), campaign=a.campaign,
             swap_mode='direct', engine_profile='profile3', engine_json='{}', follow=a.follow,
             allow_heldout=False))


if __name__ == '__main__':
    main()
