#!/usr/bin/env python3
"""Minute console measurements for this campaign, without environment output."""
import argparse,json,os,subprocess,time
from pathlib import Path
from datetime import datetime,timezone

def cpu():
    return list(map(int,Path('/proc/stat').read_text().splitlines()[0].split()[1:]))

def processes(needle):
    out={}
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:
            raw=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
            if needle not in raw or any(x in raw for x in ('console_status.py','resource_monitor.py','scout_watch.py','scout_poll.py')):continue
            s=(p/'stat').read_text().split();out[int(p.name)]={'ticks':int(s[13])+int(s[14]),'threads':int(s[19]),'state':s[2],'program':Path(raw.split()[0]).name,'command':raw[:1200]}
        except (OSError,ValueError,IndexError):pass
    return out

def main():
    a=argparse.ArgumentParser();a.add_argument('--work',type=Path,required=True);a.add_argument('--campaign',type=Path,required=True);a.add_argument('--deadline');x=a.parse_args()
    deadline=datetime.fromisoformat(x.deadline.replace('Z','+00:00')) if x.deadline else None;low_since=None
    while deadline is None or datetime.now(timezone.utc)<deadline:
        t=time.monotonic();s0=cpu();p0=processes(str(x.work));time.sleep(1);s1=cpu();p1=processes(str(x.work));elapsed=time.monotonic()-t
        delta=[b-a for a,b in zip(s0,s1)];system=100*(sum(delta)-delta[3]-delta[4])/max(1,sum(delta));hz=os.sysconf('SC_CLK_TCK');active=[]
        for pid,v in p1.items():
            pct=100*(v['ticks']-p0.get(pid,v)['ticks'])/hz/elapsed
            if pct>1 or v['state']=='R':active.append(dict(pid=pid,cpu_percent=round(pct,1),threads=v['threads'],program=v['program'],command=v['command']))
        tested={};agent_status={}
        for name,rel in [('graph','graph/live-status.json'),('geometry','geometry/live-status.json'),('scout','derived/scout/live-status.json')]:
            try:
                obj=json.loads((x.work/rel).read_text())
                agent_status[name]={k:obj[k] for k in ('utc','updated_utc','completed_cohorts','completed_experiments','running_experiments','current_batch','progress','next_batch','running','completed_prior_positive_exact_profiles') if k in obj}
                if name=='scout':
                    agent_status[name]['experiments']=[{k:e[k] for k in ('run_id','state','attempts_may_repeat','tested_canonical_beta_pairs','tested_source_weight_classes','source_weight_catalogue_classes') if k in e} for e in obj.get('experiments',[])]
            except (OSError,ValueError):pass
        for path in sorted(x.work.glob('root-*/results.json')):
            try:
                obj=json.loads(path.read_text());tested[path.parent.name]={'status':obj.get('status'),'complete':len(obj.get('rows',[])),'planned':len(obj.get('configurations',[]))}
            except (OSError,ValueError):pass
        for path in sorted(x.work.glob('root-*/status.json')):
            try:
                obj=json.loads(path.read_text());tested[path.parent.name]={k:obj[k] for k in ('completed','failed','total','workers','utc') if k in obj}
            except (OSError,ValueError):pass
        ledger=json.loads((x.campaign/'reports/construction-ledger.json').read_text());rows=ledger['rows'];best=max((r['kappa_decimal'] for r in rows if r['status']=='accepted conditional construction'),default=None);candidate=max((r['kappa_decimal'] for r in rows if r['status']!='accepted conditional construction'),default=None)
        gpu=subprocess.run(['nvidia-smi','--query-gpu=index,utilization.gpu,memory.used,power.draw','--format=csv,noheader,nounits'],capture_output=True,text=True).stdout.strip()
        if system<70:low_since=low_since or time.monotonic()
        else:low_since=None
        print(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),'actual_system_cpu_percent':round(system,1),'campaign_cpu_percent_of_16':round(sum(r['cpu_percent'] for r in active)/16,1),'active_compute_processes':active,'gpu_utilization_memory_power':gpu,'tested_configurations':tested,'best_certified_kappa':best,'best_unverified_kappa':candidate,'live_agent_batches':agent_status,'below70_seconds':round(time.monotonic()-low_since,1) if low_since else 0}),flush=True)
        time.sleep(max(0,60-(time.monotonic()-t)))

if __name__=='__main__':main()
