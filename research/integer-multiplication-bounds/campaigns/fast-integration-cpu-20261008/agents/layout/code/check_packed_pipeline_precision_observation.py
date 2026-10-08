#!/usr/bin/env python3
"""Retain finite precision failures of the genuine packed/actual-CRT driver."""
import argparse
import hashlib
import json
import runpy
import sys
from pathlib import Path
from time import perf_counter

parser=argparse.ArgumentParser();parser.add_argument('--driver',required=True)
args,rest=parser.parse_known_args()
out=Path(rest[rest.index('--output')+1]);started=perf_counter()
sys.argv=[args.driver,*rest]
try:
    runpy.run_path(args.driver,run_name='__main__')
except AssertionError as error:
    frames=[];trace=error.__traceback__
    while trace:
        frames.append(trace.tb_frame);trace=trace.tb_next
    observed=next((f.f_locals for f in reversed(frames)
                   if all(k in f.f_locals for k in ['actual','oracle','maximum_real_error'])),None)
    if observed is None:
        result={'status':'component assertion failure retained without coefficient-threshold interpretation',
                'assertion':str(error)[:2000]}
    else:
        actual,oracle=observed['actual'],observed['oracle']
        wrong=sum(a!=b for a,b in zip(actual,oracle))
        result={'status':'finite coefficient recovery failure retained' if wrong else
                         'integer recovery passed but required numerical margin failed',
                'incorrect_integer_coefficients':wrong,'source_volume':len(actual),
                'maximum_integer_difference':max(abs(a-b) for a,b in zip(actual,oracle)),
                'coefficient_real_error':str(observed['maximum_real_error']),
                'coefficient_imaginary_error':str(observed['maximum_imaginary_error'])}
    out.mkdir(parents=True,exist_ok=True)
else:
    certificate=json.loads((out/'certificate.json').read_text())
    result={'status':'complete packed actual-CRT precision case passed',
            'coefficient_real_error':certificate['arithmetic']['coefficient_real_error'],
            'coefficient_imaginary_error':certificate['arithmetic']['coefficient_imaginary_error']}
result.update(seconds=perf_counter()-started,
              config=json.loads(Path(rest[rest.index('--config')+1]).read_text()),
              driver_sha256=hashlib.sha256(Path(args.driver).read_bytes()).hexdigest(),
              observation_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              limitation='Matched finite work-grid observations; component errors remain distinct from coefficient failures. A failed producer returns before final actual CRT inversion.')
(out/'precision-observation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result),flush=True)
