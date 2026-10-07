"""Invoke unmodified upstream calibrator; retain every native request's IDs/output/stats."""
import sys,json,time,os,hashlib
from pathlib import Path
REPO=Path('/srv/ai/strata-v0.1.32');sys.path[:0]=[str(REPO),str(REPO/'tools')]
from calibrate import run
from serve.server import StrataEngine,child_env
import psutil
R=Path(__file__).resolve().parent;cfg=json.loads(Path(sys.argv[1]).read_text());counter=0

def start(args):
 global counter
 engine=StrataEngine(cfg['exe'],args,cwd=cfg['cwd'],log=cfg['log'],env=child_env(cfg));original=engine.generate
 command=psutil.Process(engine.proc.pid).cmdline()
 def generate(ids,maximum,sampling,event):
  global counter
  counter+=1;number=counter;start=time.monotonic();output=[]
  try:
   for token in original(ids,maximum,sampling,event):
    if token is not None:output.append(token)
    yield token
  finally:
   record={'Strata_HEAD':'c499bd102e7a4135c0de389dcfe38c399759ccc8','Strata_version':'0.1.32','build_variant':'default','model_revision':'38bb39ee97821de2c9009abb7e93950eec396e66','topology':'layer_split','full_config':cfg,'full_engine_command':command,'actual_prompt_tokens':len(ids),'input_ids':list(ids),'output_ids':output,'generated_tokens':len(output),'max_tokens':maximum,'sampling':sampling,'wall_s':time.monotonic()-start,'engine_last':dict(engine.last or {}),'purpose':'UPSTREAM_CALIBRATOR_NATIVE_REQUEST; not a64K screening measurement'}
   (R/'raw'/f'calibrator-native-request-{number:03d}.json').write_text(json.dumps(record,indent=2))
 engine.generate=generate;return engine

res=run(cfg,start_engine=start)
res.update(Strata_HEAD='c499bd102e7a4135c0de389dcfe38c399759ccc8',Strata_version='0.1.32',build_variant='default',model_revision='38bb39ee97821de2c9009abb7e93950eec396e66',full_config=cfg,topology='layer_split',native_requests=counter)
(R/'raw/calibration.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2),flush=True)
