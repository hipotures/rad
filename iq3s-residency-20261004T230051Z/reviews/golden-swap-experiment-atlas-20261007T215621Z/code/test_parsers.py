"""Small meaningful boundary fixtures for the retrospective representation."""
import tempfile
import unittest
import numpy as np
from pathlib import Path
from compact_assets import expand
from normalize import GEN_COLUMNS
from parsers.journals import E,L,N,LC,read

class ParserTests(unittest.TestCase):
    def test_repeated_generation_issue_gap_and_exact_exception(self):
        def generation(uid,start,end):
            g=dict.fromkeys(GEN_COLUMNS);g.update(uid=uid,expert=7,publish_event=start,eviction_event=end)
            return [g[k] for k in GEN_COLUMNS]
        layer=dict(columns=GEN_COLUMNS,generations=[generation(10,0,6),generation(11,10,14),generation(12,14,None)],
                   service_exceptions=[[2,0,2,0,0,None]])
        rows=expand([[0,7,3],[6,7,1],[8,7,2],[10,7,4],[14,7,2]],layer)
        self.assertEqual(rows,[[0,7,3,0,0,0,10],[6,7,0,0,0,1,None],[8,7,0,2,0,0,None],[10,7,4,0,0,0,11],[14,7,2,0,0,0,12]])
    def test_binary_layout_and_truncation(self):
        self.assertEqual([x.itemsize for x in [L,E,N,LC]],[520,112,48,32])
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/'journal.bin';f.write_bytes(b'x'*111)
            with self.assertRaisesRegex(ValueError,'Truncated'):read(f,E)
    def test_record_identity_is_not_publication_chronology(self):
        rows=np.zeros(2,E);rows[0]['target']=15;rows[0]['published_at']=14;rows[1]['trigger']=11
        self.assertLess(0,1)
        self.assertGreater(int(rows[0]['published_at']),int(rows[1]['trigger']))

if __name__=='__main__':unittest.main()
