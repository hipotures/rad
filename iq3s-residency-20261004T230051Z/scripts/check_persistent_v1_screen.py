from lab import ROOT,load,save
from pathlib import Path
import re
base=ROOT/'experiments/E029-persistent-runtime/v1-fixed';r=load(base/'screen-summary.json');a,b=r['rows'];previous=load(ROOT/'experiments/E027-pool-baseline/v1/standard/32k/sleep100us/rep1/raw/run.json')
x=load(base/'screen/32k/off/rep1/raw/output-ids-request2.json');old=load(ROOT/'experiments/E027-pool-baseline/v1/standard/32k/sleep100us/rep1/raw/output-ids-request2.json')
out={'state':'COMPLETE_NEGATIVE_SCREEN','TG_off':a['TG'],'TG_on':b['TG'],'deltaTG':r['deltaTG'],'deltaWall':r['deltaWall'],'CPU_entries_off':a['cpu_fallback_entries'],'CPU_entries_on':b['cpu_fallback_entries'],'PCIe_entries_off':a['offloaded_entries'],'PCIe_entries_on':b['offloaded_entries'],'MTP_accept_off':a['mtp_acceptance_pct'],'MTP_accept_on':b['mtp_acceptance_pct'],'MTP_windows_off':a['verify_windows'],'MTP_windows_on':b['verify_windows'],'OFFmatchesP1output':x==old,'OFFmatchesP1normalrouting':all(a.get(k)==previous.get(k) for k in ['local_vram_entries','cpu_fallback_entries','offloaded_entries','mtp_proposed','mtp_accepted','verify_windows']),'newbinaryOFFTG_vs_P1rep1':100*(a['TG']/previous['TG']-1),'not_a_median':True,'decision':'Rejectv1production; onlyonepredeclaredv2lifetimeutilityrepair and finalconfirmation. Do notrepeatconservativeunderadmission.'}
save(base/'screen-analysis.json',out);print(out)
