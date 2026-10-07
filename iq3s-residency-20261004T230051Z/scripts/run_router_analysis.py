"""Serial offline timing repair; preserve the initially concurrent analysis."""
import subprocess
from lab import ROOT,save
py=str(ROOT/'src/control/.venv/bin/python');out=ROOT/'experiments/E008-router-boundary/analysis-r2'
if out.exists():raise RuntimeError('Existing serial analysis attempt')
save(out/'protocol.json',{'question':'Measure numeric CPU gate cost serially, without a second competing gate-analysis process.','excluded_timing':['v2/32k/analysis.json CPU scoring costs','v2/128k/analysis.json CPU scoring costs'],'reason':'The two first analyses were dispatched concurrently. Router quality and device-event durations remain valid, but CPU numeric-cost estimates have avoidable contention.','same_preserved_trace':True,'new_inference_requests':0,'order':['32k','128k']})
for profile in ['32k','128k']:
    prefix=ROOT/'experiments/E008-router-boundary/v2'/profile/'traces/runtime-request2'
    cmd=[py,str(ROOT/'scripts/analyze_router_boundary.py'),str(prefix),'--output',str(out/profile/'analysis.json')]
    wrapped=[py,str(ROOT/'scripts/run_logged.py'),'--path',str(out/profile/'logs/analysis'),'--timeout','120','--',*cmd]
    rc=subprocess.run(wrapped,cwd=ROOT,timeout=140).returncode
    if rc:raise SystemExit(rc)
