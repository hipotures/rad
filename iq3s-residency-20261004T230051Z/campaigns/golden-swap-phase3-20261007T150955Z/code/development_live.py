"""Compiled smoke plus frozen OFF regression and counterordered wait-instrumentation guard."""
from common import *
import live
TASK=next(t for t in load(P0/'benchmark-manifest.json')['tasks'] if t['task_id']=='math-rational')
order=[('PLANNER_OPT',1,False,'smoke-opt-profile1-attempt2'),('PLANNER_BASELINE',0,False,'guard-profile0-a'),('PLANNER_BASELINE',1,False,'guard-profile1-a'),('PLANNER_BASELINE',1,False,'guard-profile1-b'),('PLANNER_BASELINE',0,False,'guard-profile0-b'),('PLANNER_BASELINE',0,True,'frozen-phase2-history')]
save(C/'configs/development-order.json',{'task':'math-rational','order':order,'purpose':'First compiled integration smoke, two opposite-order instrumentation pairs, then bounded actual frozen binary regression','predeclared_instrumentation_guard':'If both profile pairs regress decode >3%, gate headline wait profiling and retain separate diagnostics instead.'})
results=[]
for idx,(arm,profile,frozen,label) in enumerate(order):
 progress(3,"Development request START",completed=len(results),remaining=len(order)-len(results),task=TASK["task_id"],arm=arm,next_action="Complete fixed smoke/guard sequence")
 r=live.point(TASK,arm,'dev-'+label,3,wait_profile=profile,frozen_phase2=frozen);r['kind']='development';r['wait_profile']=profile;r['frozen_phase2']=frozen;save(C/'raw'/r['label']/'episode.json',r);results.append(r);save(C/'results/development-execution.json',[{'label':x['label'],'arm':x['arm'],'valid':x['valid'],'wait_profile':x['wait_profile'],'frozen_phase2':x['frozen_phase2'],'operating_s':x['total_operating_s']} for x in results])
progress(3,'Development smoke, overhead and frozen baseline checks finished',completed=len(results),remaining=0,next_action='Inspect guard then launch frozen matrix')
