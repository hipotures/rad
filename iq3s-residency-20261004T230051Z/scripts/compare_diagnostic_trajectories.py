"""Compare retained actual diagnostic token trajectories, not pretend free-generation parity."""
import numpy as np
from lab import ROOT,load,save
from trace_reader import Trace
rows=[]
for profile,attempt in [('32k','v5'),('128k','v5-portfix')]:
    cpath=ROOT/'experiments/E003-diagnostics'/attempt/profile
    fpath=ROOT/'experiments/E006-frequency/diagnostic-v1'/profile
    c=Trace(cpath/'traces/runtime-request2');f=Trace(fpath/'traces/runtime-request2')
    assert c.validate()['state']=='PASS' and f.validate()['state']=='PASS'
    n=min(len(c.output_ids),len(f.output_ids));bad=np.flatnonzero(c.output_ids[:n]!=f.output_ids[:n]);prefix=int(bad[0]) if len(bad) else n
    cr=load(cpath/'raw/trace-run1.json');fr=load(fpath/'raw/trace-run1.json')
    assert cr['payload']['input_ids_sha256']==fr['payload']['input_ids_sha256']
    rows.append({'profile':profile,'same_effective_input_ids':True,'same_diagnostic_binary':cr['binary_sha256']==fr['binary_sha256'],'common_output_prefix_tokens':prefix,'first_diverging_tokens':[int(c.output_ids[prefix]),int(f.output_ids[prefix])] if prefix<n else None,'output_tokens':[len(c.output_ids),len(f.output_ids)],'control_TG_diagnostic':cr['TG'],'frequency_TG_diagnostic':fr['TG'],'MTP_accept_pct':[cr['mtp_acceptance_pct'],fr['mtp_acceptance_pct']],'CPU_entries':[cr['cpu_fallback_entries'],fr['cpu_fallback_entries']],'mapped_entries':[cr['offloaded_entries'],fr['offloaded_entries']],'promotion_bytes':[int(c.promotions['bytes'].sum()),int(f.promotions['bytes'].sum())],'source_paths':[str(cpath),str(fpath)],'limits':'Whole free-generation accounting includes trajectories after divergence; do not convert the byte or miss difference into a causal TG gain. Same diagnostic trace hooks, separate fresh servers with equal warmup.'})
out=ROOT/'experiments/E006-frequency/diagnostic-v1/comparison.json'
save(out,{'state':'COMPLETE','rows':rows,'fixed_input_logits':'Not available in v5; first-window logits in E008 v7 can strengthen this limited comparison.'})
print(rows)
