"""Non-invasive root consolidation; new statistics cite original raw records."""
import csv, datetime, pathlib
from lab import ROOT, load, save
c=pathlib.Path(load(ROOT/'active-campaign.json')['path']);old=load(c/'previous-root/summary.json')
new=[];reports=[]
for experiment,phase in [('E026-pool-generalization','P0'),('E027-pool-baseline','P1'),('E028-persistent-replay','P2 replay'),('E029-persistent-runtime','P2 live')]:
    folder=ROOT/'experiments'/experiment
    if (folder/'summary.json').exists():
        summary=load(folder/'summary.json');reports.append({'phase':phase,'experiment':experiment,'summary':str(folder/'summary.json'),'report':str(folder/'report.md'),'state':summary.get('state'),'decision':summary.get('decision')})
        for cell in summary.get('cells',[]):new.append(cell)
result={'state':load(ROOT/'STATUS.json')['state'],'campaign':str(c),'prior_completed_summary':str(c/'previous-root/summary.json'),'prior_measured_cells':old.get('measured_cells',[]),'followup_measured_cells':new,'phase_reports':reports,'deadline':load(c/'deadline.json')}
save(ROOT/'summary.json',result);save(c/'summary.json',result)
rows=[]
for cell in new:
    row={k:cell.get(k) for k in ['experiment','phase','family','profile','role','attempts','valid_fixed_length']}
    for k,v in cell.get('metrics',{}).items():
        if isinstance(v,dict):
            for stat in ['min','median','max']:row[k+'_'+stat]=v.get(stat)
    rows.append(row)
if rows:
    fields=list(dict.fromkeys(k for row in rows for k in row))
    for path in [ROOT/'summary.csv',c/'summary.csv']:
        with path.open('w') as f:w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
text='# IQ3_S CPU-pool validation and persistent residency\n\n'
text+='This separately authorized follow-up began2026-10-05 09:48 UTC, with absolute deadline19:48 UTC and experiment cutoff19:03 UTC. The previous completed campaign is preserved in [previous report]('+str(c/'previous-root/report.md')+'). No prior raw data are overwritten.\n\n'
text+='Current status: [STATUS.md](STATUS.md).\n\n'
for report in reports:
    p=pathlib.Path(report['report'])
    if p.exists():text+='## '+report['phase']+'\n\n'+p.read_text()+'\n\n'
text+='## Remaining work\n\n'+ '; '.join(load(ROOT/'STATUS.json')['pending'])+'\n\nNo production launcher is changed. Final recommendation and exact real-prompt launch commands will be frozen after phase conclusions.\n'
(ROOT/'report.md').write_text(text);(c/'report.md').write_text(text)
print('ROOT_CONSOLIDATED',len(new),'new cells',flush=True)
