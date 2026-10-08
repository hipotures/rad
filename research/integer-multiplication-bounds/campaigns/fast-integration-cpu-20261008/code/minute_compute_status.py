#!/usr/bin/env python3
"""Real one-second CPU observations, printed every60seconds until deadline."""
import datetime as dt, importlib.util,json,os,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("resource",ROOT/"code/resource_sample.py");mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
def main():
 out=ROOT/"work/compute-minute";out.mkdir(parents=True,exist_ok=True)
 deadline=dt.datetime.fromisoformat("2026-10-08T14:40:55+00:00");hz=os.sysconf(os.sysconf_names["SC_CLK_TCK"])
 with (out/"observations.jsonl").open("a") as f:
  while dt.datetime.now(dt.timezone.utc)<deadline:
   a=mod.snapshot(ROOT);time.sleep(1);b=mod.snapshot(ROOT);elapsed=b["monotonic"]-a["monotonic"];old={p["pid"]:p for p in a["task_processes"]};delta=[x-y for x,y in zip(b["cpu_ticks"],a["cpu_ticks"])];busy=(sum(delta[:8])-delta[3]-delta[4])/hz/elapsed
   active=[]
   for p in b["task_processes"]:
    rate=(p["cpu_ticks"]-old.get(p["pid"],p)["cpu_ticks"])/hz/elapsed
    if rate>0.01 or p["state"].startswith("R"):
     p=dict(p,cpu_slots=round(rate,3));active.append(p)
   root_results=list((ROOT/"work/correction-20261008T1402Z/cyclic-family").glob("s*-t*.json"))
   row=dict(utc=b["utc"],cpu_percent_of_12=round(100*busy/12,2),busy_cpu_slots=round(busy,3),active_compute=active,completed_new_cyclic_cases=len(root_results),total_new_cyclic_cases=8,mem_available_kib=b["mem_available_kib"],disk_free_bytes=b["disk_free_bytes"],best_campaign_certified_kappa=None,best_unverified_kappa=None,eliminated=["generic continuation graph alternatives","uncosted near-primitive CRT composition"],queue="new cyclic inverse cases; expanded tensor/layout families; dirty-guard CRT states")
   print(json.dumps(row),flush=True);f.write(json.dumps(row)+"\n");f.flush()
   remaining=(deadline-dt.datetime.now(dt.timezone.utc)).total_seconds();time.sleep(max(0,min(59,remaining)))
if __name__=="__main__":main()
