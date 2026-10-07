"""Standalone measured-data figures; observed ranges are not confidence intervals."""
import statistics,subprocess
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from common import *
no_gpu();pairs=load(C/'results/paired-blocks.json');tasks=['code-archive','math-inventory','text-websocket','mixed-chinook'];out=C/'analysis/plots';out.mkdir(exist_ok=True)
fig,axes=plt.subplots(1,2,figsize=(10.6,4.7),sharey=True)
for ax,metric,label in zip(axes,['TG','wall'],['Replay-equivalent tok/s change (%)','Request wall reduction (%)']):
 for index,task in enumerate(tasks):
  rows=[p for p in pairs if p['task']==task]
  for prefix,offset,color,marker,name in [('learned',-.13,'#176b9a','o','Frozen learned victim'),('full',.13,'#6b7075','^','Full oracle reference')]:
   values=[p[prefix+'_TG_change_pct'] if metric=='TG' else -p[prefix+'_wall_change_pct'] for p in rows];median=statistics.median(values);y=index+offset
   ax.hlines(y,min(values),max(values),color=color,lw=1.1,alpha=.65)
   ax.scatter(values,y+np.linspace(-.025,.025,len(values)),s=27,color=color,marker=marker,label=name if index==0 else None,zorder=3)
   ax.plot([median,median],[y-.065,y+.065],color=color,lw=2,zorder=4)
 ax.axvline(0,color='#202020',lw=.8,ls='--');ax.grid(axis='x',alpha=.18);ax.set_xlabel(label);ax.set_yticks(range(4),tasks);ax.set_ylim(3.5,-.5);ax.spines[['top','right']].set_visible(False)
axes[0].legend(loc='upper left',bbox_to_anchor=(0,1.22),frameon=False,ncol=2,fontsize=9)
fig.suptitle('Fixed-work replay: no consistent learned-victim latency gain',fontsize=13,y=.99)
fig.text(.01,.025,'Each dot is one paired block; ticks show medians and lines min–max, without confidence intervals.\nOracle incoming/current-window protection are privileged. Three blocks per recorded task; all configured32K.',fontsize=8.5)
fig.tight_layout(rect=(0,.08,1,.90));fig.savefig(out/'paired-latency.png',dpi=180);fig.savefig(out/'paired-latency.svg');plt.close(fig)
save(out/'plot-data.json',pairs)
(C/'requirements-plotting.txt').write_text(subprocess.check_output(['uv','pip','freeze','--python',str(C/'.venv/bin/python')],text=True))
print('MEASURED DATA FIGURES',out,flush=True)
