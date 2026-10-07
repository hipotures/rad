"""Standalone measured-data figures; simulations never plotted as measured TG."""
from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
C=Path(__file__).resolve().parents[1]
if __name__=='__main__':
 s=json.loads((C/'summary.json').read_text());assert s['state']=='COMPLETE';out=C/'analysis/plots';out.mkdir(exist_ok=True)
 fig,axes=plt.subplots(1,3,figsize=(13,4))
 for policy,name,color in [('REPLAY_CURRENT','Current replay','#3366aa'),('REPLAY_ORACLE_FULL','Full-future oracle','#dd7722')]:
  cells=[x for x in s['cells'] if x['policy']==policy]
  for ax,key,label in zip(axes,['replay_equivalent_tok_s','decode_s','wall_s'],['Replay-equivalent output tok/s','Measured decode (s)','Request-comparable wall (s)']):
   v=[x['metrics'][key]['median'] for x in cells];err=np.array([[v[i]-x['metrics'][key]['min'] for i,x in enumerate(cells)],[x['metrics'][key]['max']-v[i] for i,x in enumerate(cells)]])
   ax.errorbar(range(3),v,yerr=err,marker='o',capsize=4,color=color,label=name);ax.set_xticks(range(3),['32K','128K','256K']);ax.set_xlabel('Total context limit');ax.set_ylabel(label);ax.grid(alpha=.2)
 axes[0].legend();fig.suptitle('Q4 fixed work: three attempts per policy, median and min/max');fig.tight_layout();fig.savefig(out/'measured-performance.png',dpi=180);fig.savefig(out/'measured-performance.svg');plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(10,4));width=.32
 for i,policy in enumerate(['REPLAY_CURRENT','REPLAY_ORACLE_FULL']):
  cells=[x for x in s['cells'] if x['policy']==policy];x=np.arange(3)+(i-.5)*width
  axes[0].bar(x,[c['metrics']['CPU_entries']['median']+c['metrics']['mapped_entries']['median'] for c in cells],width,label=policy)
  axes[1].bar(x,[c['metrics']['copy_GB']['median'] for c in cells],width,label=policy)
 for ax,label in zip(axes,['Main CPU + mapped routed entries','Completed expert copy GB incl. restoration']):ax.set_xticks(range(3),['32K','128K','256K']);ax.set_ylabel(label);ax.grid(axis='y',alpha=.2)
 axes[0].legend(fontsize=8);fig.suptitle('Locality gain costs more real H2D expert traffic');fig.tight_layout();fig.savefig(out/'locality-versus-traffic.png',dpi=180);fig.savefig(out/'locality-versus-traffic.svg');plt.close(fig)
 print('FIGURES_WRITTEN',out,flush=True)
