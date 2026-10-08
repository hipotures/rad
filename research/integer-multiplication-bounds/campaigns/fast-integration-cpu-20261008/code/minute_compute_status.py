#!/usr/bin/env python3
"""Real one-second CPU observations, printed every 60 seconds until user-requested closure."""
import datetime as dt, importlib.util,json,os,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("resource",ROOT/"code/resource_sample.py");mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
def main():
 out=ROOT/"work/compute-minute";out.mkdir(parents=True,exist_ok=True)
 deadline=None;hz=os.sysconf(os.sysconf_names["SC_CLK_TCK"])
 with (out/"observations.jsonl").open("a") as f:
  while True:
   a=mod.snapshot(ROOT);time.sleep(1);b=mod.snapshot(ROOT);elapsed=b["monotonic"]-a["monotonic"];old={p["pid"]:p for p in a["task_processes"]};delta=[x-y for x,y in zip(b["cpu_ticks"],a["cpu_ticks"])];busy=(sum(delta[:8])-delta[3]-delta[4])/hz/elapsed
   active=[]
   for p in b["task_processes"]:
    rate=(p["cpu_ticks"]-old.get(p["pid"],p)["cpu_ticks"])/hz/elapsed
    if rate>0.1:
     p=dict(p,cpu_slots=round(rate,3));active.append(p)
   root_results=[];planned=0;passed=failed=basis=0
   directories=list((ROOT/"work").glob("correction-*/cyclic-*"))+list((ROOT/"work").glob("cyclic-*-20261008T*"))
   for directory in directories:
    protocol=directory/"protocol.json"
    if protocol.exists():planned+=len(json.loads(protocol.read_text()).get("cases",[]))
    for result in directory.glob("s*-t*.json"):
     data=json.loads(result.read_text());root_results.append(result);passed+=data.get("status")=="passed";failed+=data.get("status")=="failed";basis+=data.get("basis_probes",0)
   context_path=ROOT/"results/live-compute-context.json"
   context=json.loads(context_path.read_text()) if context_path.exists() else {}
   row=dict(utc=b["utc"],cpu_percent_of_12=round(100*busy/12,2),busy_cpu_slots=round(busy,3),active_compute=active,completed_new_cyclic_cases=len(root_results),total_new_cyclic_cases=planned,passed_cyclic_attempts=passed,failed_cyclic_attempts=failed,complete_numeric_basis_probes=basis,mem_available_kib=b["mem_available_kib"],disk_free_bytes=b["disk_free_bytes"],best_campaign_certified_kappa=None,best_unverified_kappa=context.get("best_unverified_kappa"),eliminated=context.get("eliminated",[]),queue=context.get("queue",[]),completed_parameter_combinations=context.get("completed_parameter_combinations",0),passing_parameter_combinations=context.get("passing_parameter_combinations",0),candidate_status=context.get("candidate_status"))
   print(json.dumps(row),flush=True);f.write(json.dumps(row)+"\n");f.flush()
   remaining=float("inf");time.sleep(max(0,min(59,remaining)))
if __name__=="__main__":main()
