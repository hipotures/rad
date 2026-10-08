#!/usr/bin/env python3
"""Complete original/enlarged matching profiles on distinct changed computation DAGs."""
import argparse,concurrent.futures,hashlib,importlib.util,json,os,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def job(row,directory,matcher,source):
 began=time.time();identifier=row["id"];dag=directory/row["dag_file"]
 sys.path.insert(0,str(source/"scripts"));from partial_swap.positive import run as labels
 result=dict(id=identifier,h=row["h"],grouping=row["grouping"],association=row["association"],threshold=row["threshold"],worker_pid=os.getpid(),dag_sha256=hashlib.sha256(dag.read_bytes()).hexdigest())
 try:
  def run(name,suffix):
   # Retain matching diagnostics without flooding the coordinator console.
   with (directory/(identifier+"-"+name+".log")).open("w") as log:
    return json.loads(subprocess.check_output([str(matcher/name),str(dag),str(dag)+suffix],text=True,stderr=log))
  result["original_matching"]=run("match_exported_dag",".links")
  result["positive_labels"]=labels(str(dag))
  result["positive_matching"]=run("match_positive_dag",".positive")
  data=result["positive_matching"];assert data["rank_sum"]==row["h"]*data["R"]+2*data["loss"]
  result["status"]="passed"
 except Exception as e:result.update(status="failed",error=type(e).__name__+": "+str(e),traceback=traceback.format_exc())
 result["elapsed_seconds"]=time.time()-began;return result
if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("--source",type=Path,required=True);a.add_argument("--dags",type=Path,required=True);a.add_argument("--matchers",type=Path,required=True);a.add_argument("--workers",type=int,default=3);a.add_argument("--output",type=Path,required=True);z=a.parse_args();z.output.mkdir(parents=True,exist_ok=False)
 rows=[r for r in json.loads((z.dags/"results.json").read_text()) if "dag_file" in r and not r["duplicate_exact_dag"]]
 protocol=dict(cases=len(rows),workers=z.workers,scope="Changed graph matching histograms and denominators; I+J fixed-basis moments and native acceptance remain separate",source_head="43f59ff533598762cbc43a5e14af2bbbc76fabbd",wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_hashes={n:hashlib.sha256((z.source/"scripts/partial_swap"/n).read_bytes()).hexdigest() for n in ["positive.py","match_exported_dag.cpp","match_positive_dag.cpp"]})
 (z.output/"protocol.json").write_text(json.dumps(protocol,indent=2)+"\n")
 completed=0
 with concurrent.futures.ProcessPoolExecutor(max_workers=z.workers) as pool:
  pending={pool.submit(job,r,z.dags.resolve(),z.matchers.resolve(),z.source.resolve()):r["id"] for r in rows}
  for f in concurrent.futures.as_completed(pending):
   result=f.result();(z.output/(result["id"]+".json")).write_text(json.dumps(result,indent=2)+"\n");completed+=1
   if completed%25==0 or result["status"]!="passed":print(json.dumps(dict(event="progress",completed=completed,total=len(rows),latest=result["id"],status=result["status"])),flush=True)
 print(json.dumps(dict(event="complete",completed=completed)),flush=True)
