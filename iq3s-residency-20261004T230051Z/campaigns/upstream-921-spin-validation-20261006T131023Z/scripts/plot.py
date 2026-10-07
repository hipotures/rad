"""Standalone publication figures; run only after headline timing completes.

Example: uv run --no-project --with matplotlib python scripts/plot.py
Never installs plotting packages into the inference environment.
"""
import csv,json,pathlib,statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
C=pathlib.Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((C/'pairs.csv').open()));s=json.loads((C/'summary.json').read_text());F=C/'figures';F.mkdir(exist_ok=True)
cells=['IQ3_S-32k','IQ3_S-128k','Q4-32k','Q4-128k'];colors={'code':'#3366AA','math':'#228866','prose':'#BB5566'}
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','pdf.fonttype':42})
fig,axs=plt.subplots(1,2,figsize=(11.5,4.8),layout='constrained')
for ax,metric,title in zip(axs,['TG','CPU'],['Paired decode throughput change','Paired guest CPU change']):
 for ci,cell in enumerate(cells):
  rs=[r for r in rows if r['cell']==cell]
  for n,r in enumerate(rs):
   y=100*(float(r[metric+'_ratio_B_over_A'])-1);x=ci+(n-(len(rs)-1)/2)*.022
   ax.scatter(x,y,s=28,color=colors[r['family']],alpha=.85,zorder=3)
  d=s['cells'][cell]['paired'][metric];median=100*(d['median']-1)
  ax.plot([ci-.22,ci+.22],[median,median],color='black',lw=2,zorder=4)
  if metric=='TG':
   lo,hi=d['inference']['bootstrap_median_ratio_percentile95'];ax.errorbar(ci+.29,median,yerr=[[median-100*(lo-1)],[100*(hi-1)-median]],fmt='s',color='black',capsize=3,ms=4,zorder=4)
  ax.annotate(f'{median:+.1f}%',(ci,median),xytext=(0,10 if metric=='TG' else -16),textcoords='offset points',ha='center',fontsize=9)
 ax.axhline(0,color='#777777',lw=.8,ls='--');ax.set_xticks(range(4),['IQ3_S\n32K','IQ3_S\n128K','Q4\n32K','Q4\n128K']);ax.set_ylabel('100 × (B/A − 1)');ax.yaxis.set_major_formatter(PercentFormatter());ax.set_title(title);ax.grid(axis='y',alpha=.18)
for family,color in colors.items():axs[0].scatter([],[],color=color,label=family,s=28)
handles,labels=axs[0].get_legend_handles_labels();fig.legend(handles,labels,frameon=False,loc='lower center',bbox_to_anchor=(.5,.075),ncols=3)
axs[1].set_ylim(-95,5)
fig.suptitle('Strata v0.1.40.1: actual default spin versus 100 µs',fontsize=13)
fig.get_layout_engine().set(rect=(0,.17,1,.72))
fig.text(.5,.018,'Each dot is one A/B pair; black line is paired median; TG bars are seeded 95% paired-median bootstrap intervals.\nOne dual RTX 4090 / 16-vCPU 7950X3D KVM machine; fixed workloads; intervals do not establish cross-machine safety.',ha='center',fontsize=8)
for ext in ['png','svg','pdf']:fig.savefig(F/f'paired-results.{ext}',dpi=300)
plt.close(fig)

fig,ax=plt.subplots(figsize=(8.2,5.1),layout='constrained')
regime_colors={'IQ3_S':'#3366AA','Q4':'#DD7733'};markers={'32768':'o','131072':'^'}
for regime in ['IQ3_S','Q4']:
 for context in ['32768','131072']:
  rs=[r for r in rows if r['regime']==regime and r['context']==context]
  x=[(float(r['cpu_experts_per_layer_window_A'])+float(r['cpu_experts_per_layer_window_B']))/2 for r in rs]
  y=[float(r['TG_paired_delta_pct']) for r in rs]
  ax.scatter(x,y,c=regime_colors[regime],marker=markers[context],s=42,alpha=.8,label=f"{regime} {'32K' if context=='32768' else '128K'}")
ax.axhline(0,color='#777777',lw=.8,ls='--');ax.set_xlabel('Mean CPU experts per layer-window (A and B)');ax.set_ylabel('Paired TG change: 100 × (B/A − 1)');ax.yaxis.set_major_formatter(PercentFormatter());ax.set_title('Real CPU expert demand versus paired throughput change');ax.legend(frameon=False,ncols=2);ax.grid(alpha=.18)
fig.get_layout_engine().set(rect=(0,.09,1,.82));fig.text(.5,.012,'One point per pair. Descriptive only: model, context and workload covary; no regression fit or causal slope.',ha='center',fontsize=8)
for ext in ['png','svg','pdf']:fig.savefig(F/f'cpu-demand.{ext}',dpi=300)
plt.close(fig)
print('FIGURES COMPLETE',F)
