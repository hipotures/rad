"""Explicit retained binary layouts. No guesses from filenames or vector chronology."""
import numpy as np
from pathlib import Path

L = np.dtype([('event','<u8'),('begin','<u8'),('plan_end','<u8'),('cpu_end','<u8'),
              ('layer','<i4'),('n','<i4'),('ids','<i4',(40,)),('slots','<i4',(40,)),('path','<i4',(40,))])
E = np.dtype([(k,'<u8') for k in ['issue_ns','stage_begin','stage_end','copy_begin','copy_end','publish_ns']] +
             [(k,'<i4') for k in ['trigger','target','published_at','layer','incoming','victim','slot','oldslot','status']] +
             [('pad','<u4')] + [(k,'<u8') for k in ['bytes','uses','victim_uses']])
N = np.dtype([('issue_ns','<u8'),('publish_ns','<u8'),('bytes','<u8')] +
             [(k,'<i4') for k in ['window','layer','incoming','victim','slot']] + [('pad','<u4')])
LC = np.dtype([(k,'<i4') for k in ['generation','first_use','last_use','distinct_uses','evicted_at','released_at','expiry','reason']])
HEADER = np.dtype([('magic','<u8'),('version','<u4'),('window_bytes','<u4'),('windows','<u8'),
                   ('prompt_count','<u8'),('output_budget','<u8'),('output_count','<u8'),('work_hash','<u8')])
ROUTES = np.dtype([('ids','<i4',(48,40)),('weights','<f4',(48,40)),('mtp_ids','<i4',(3,10)),
                  ('mtp_weights','<f4',(3,10)),('drafts','<i4',(3,)),('probs','<f4',(3,))])
ROUTES2 = np.dtype(ROUTES.descr + [('qsa','<i4',(12,8204))])
def window_dtype(routes):
    return np.dtype([('position','<i8'),('T','<i4'),('accepted','<i4'),('draft_count','<i4'),
                     ('emitted_before','<i4'),('inputs','<i4',(4,)),('outputs','<i4',(4,)),('routes',routes)])

def read(path, dtype):
    path = Path(path)
    dtype = np.dtype(dtype)
    if not path.exists():
        return np.zeros(0, dtype)
    if path.stat().st_size % dtype.itemsize:
        raise ValueError(f"Truncated {path}: record size {dtype.itemsize}")
    return np.fromfile(path, dtype)

class Tape:
    """Memory map tapes; only the retained route batches and startup table are used."""
    def __init__(self, path):
        self.path = Path(path)
        with self.path.open('rb') as f:
            self.h = np.frombuffer(f.read(56), HEADER, 1)[0].copy()
        assert int(self.h['magic']) == 0x3150455441343451 and int(self.h['version']) in (1,2)
        wd = window_dtype(ROUTES2 if int(self.h['version']) == 2 else ROUTES)
        assert int(self.h['window_bytes']) == wd.itemsize
        off = 64 if int(self.h['version']) == 2 else 56
        off += 4 * int(self.h['prompt_count'])
        self.initial = np.memmap(self.path, dtype='<i4', offset=off, mode='r', shape=(48,512))
        off += self.initial.nbytes
        self.heat = np.memmap(self.path, dtype='<f4', offset=off, mode='r', shape=(48,512))
        off += self.heat.nbytes
        self.ws = np.memmap(self.path, dtype=wd, offset=off, mode='r', shape=(int(self.h['windows']),))
        assert off + self.ws.nbytes == self.path.stat().st_size

ENTRY = np.dtype([('expert','<i2'),('token','i1'),('path','i1'),('slot','<i4')])
TL = np.dtype([(x,'<u8') for x in ['window','t0','t1','t2','t3','t4','offset']] +
              [('layer','<u4'),('tokens','<u2'),('k','<u2')])
TW = np.dtype([(x,'<u8') for x in ['number','position','begin','verify_end','end','pending_begin','pending_end']] +
              [(x,'<u4') for x in ['T','accepted','produced','reserved']] + [('tokens','<i4',(8,))])
PROM = np.dtype([(x,'<u8') for x in ['window','issue','observed_ready','bytes']] +
                [(x,'<i4') for x in ['layer','incoming','outgoing','slot']])
PROM2 = np.dtype(PROM.descr + [('outgoing_layer','<i4'),('reserved','<i4')])

class NativeTrace:
    def __init__(self, prefix):
        import json
        self.prefix = str(prefix)
        schema_path = Path(self.prefix+'-schema.json')
        schema = json.loads(schema_path.read_text()) if schema_path.exists() else {'version':1}
        assert schema['version'] in (1,2)
        def r(name, dtype): return read(self.prefix+'-'+name+'.bin', dtype)
        self.layers = r('layers', TL)
        self.entries = r('entries', ENTRY)
        self.windows = r('windows', TW)
        self.promotions = r('promotions', PROM2 if schema['version']==2 else PROM)
        self.blobs = r('blob-bytes', '<u8')
        self.initial = r('initial','<i4').reshape(48,512)
        self.final = r('final','<i4').reshape(48,512)
        self.slot_bytes = [r('slot-bytes-gpu0','<u8'), r('slot-bytes-gpu1','<u8')]
        self.index = {int(w['number']): i for i,w in enumerate(self.windows)}

assert (L.itemsize, E.itemsize, N.itemsize, LC.itemsize) == (520,112,48,32)
