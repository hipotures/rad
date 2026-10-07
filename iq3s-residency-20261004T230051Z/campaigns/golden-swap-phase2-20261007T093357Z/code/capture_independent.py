"""One predeclared continuous natural request, ordinary native adaptation, same derivative binary."""
import copy,signal,threading,time
from common import *
import live,lab
from q4_multigpu import Q4Session
from tape import Tape
no_gpu();i=live.identities();task=load(C/'inputs/independent-task-manifest.json');p=C/'raw/independent-natural';cfg=copy.deepcopy(load(P0/'configs.json')['32k']);cfg.update(exe=i['exe'],cwd=i['source'],source_sha=i['source_sha'],Strata_HEAD=i['source_sha'],binary_sha256=i['binary_sha256'],server_entrypoint=str(C/'code/serve_capture.py'),build_variant='phase2-natural-independent')
cfg['env'].update(STRATA_Q4_TAPE=task['trace_path'],STRATA_Q4_TAPE_MODE='record',STRATA_Q4_TAPE_REQUEST='2',STRATA_Q4_TAPE_OBSERVATIONS=str(p/'raw/observations.bin'),STRATA_Q4_ORACLE_SUBSTRATE='1',STRATA_Q4_ORACLE_MODE='off',STRATA_Q4_ORACLE_LOG=str(p/'raw/native'),STRATA_Q4_CAUSAL_VICTIM='off',STRATA_Q4_TRANSACTION_CONTROL='0')
save(C/'configs/independent-natural.json',cfg);ledger('Independent natural capture START',task=task['task_id'],protocol='configs/independent-source-protocol.json');start=time.monotonic();s=Q4Session(C,cfg,p,'32k',port=18166)
try:
 with Heartbeat('independent continuous natural capture',4):
  signal.setitimer(signal.ITIMER_REAL,180);s.__enter__();s.budgeted=True;warm=s.request('warmup','warmup','warmup');assert warm['state']=='VALID';signal.setitimer(signal.ITIMER_REAL,240);r=s.request(task['task_id'],'run','capture');signal.setitimer(signal.ITIMER_REAL,0);assert r['state']=='VALID' and r['actual_engine_input_verified'];save(p/'results.json',{'run':r,'warmup':warm});t=Tape(task['trace_path']);v=t.validate();assert v['state']=='PASS';save(p/'validation.json',v)
  out=int(t.h['output_count']);after=t.ws['emitted_before']+t.ws['accepted']+1;main_windows=int((after<=2048).sum());main_output=int(after[main_windows-1]) if main_windows else 0
  task.update(reference_observations=str(p/'raw/observations.bin'),tape_sha256=v['tape_sha256'],work_sha256=v['work_sha256'],actual_output_tokens=out,main_windows=main_windows,main_output_tokens=main_output,observed_tail_tokens=out-main_output,capture_stop=r['finish_reason'],context_occupancy_tokens=len(t.prompt)-1+int(v['committed_in_state_prefix']),guard_tail='observed' if out>main_output else 'none; natural EOS or output cap censoring');save(C/'inputs/independent-task-manifest.json',task);save(C/'results/independent-capture.json',{'task':task,'validation':v,'capture_wall_s':r['wall_s'],'capture_decode_s':r['decode_s'],'natural_output_quality':'Not evaluated; task has no injected answer and no executed tools'})
except BaseException as e:ledger('Independent capture failure',error=repr(e));raise
finally:
 signal.setitimer(signal.ITIMER_REAL,0);s.__exit__();no_gpu();ledger('Independent natural capture END',elapsed_s=time.monotonic()-start)
progress(4,'Independent tape captured and validated',task=task['task_id'],output=task.get('actual_output_tokens'),main=task.get('main_output_tokens'),tail=task.get('observed_tail_tokens'),next_action='Execute frozen comparable replay block; no retune')
