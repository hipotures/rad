"""Plots from already-frozen evaluation data; never fit or select a policy."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
C=Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text())
def main():
 h=load(C/'phase-b/holdout-decision.json');cal=load(C/'phase-b/calibration.json');out=C/'analysis/plots';out.mkdir(exist_ok=True)
 plt.rcParams.update({'figure.dpi':160,'axes.spines.top':False,'axes.spines.right':False,'font.size':9})
 fig,axes=plt.subplots(1,3,figsize=(12,3.6))
 for name,data in [('H4 + history',h['classification']),('History/state only',h['history_only_ablation'])]:
  curve=data['precision_recall_curve'];axes[0].plot(curve['recall'],curve['precision'],label=f"{name}; AP={data['PR_AUC_average_precision']:.3f}")
 axes[0].set(xlabel='Publication recall',ylabel='Precision',title='Sealed task holdout');axes[0].legend(fontsize=7)
 for name,data in [('Calibration',cal['calibrated']),('Holdout',h['classification'])]:
  bs=[b for b in data['calibration_bins'] if b['n']];axes[1].plot([b['predicted'] for b in bs],[b['observed'] for b in bs],marker='o',label=name)
 axes[1].plot([0,1],[0,1],color='grey',linestyle=':');axes[1].set(xlabel='Mean predicted probability',ylabel='Observed target-ready fraction',title='Probability calibration');axes[1].legend(fontsize=7)
 for p in h['frozen_precision_traffic_curve']:
  axes[2].scatter(100*p['unpublished_reduction'],100*p['benefit_recall'],marker='*' if p['policy']==h['frozen_policy'] else 'o',s=100 if p['policy']==h['frozen_policy'] else 25)
  axes[2].annotate(p['policy'],(100*p['unpublished_reduction'],100*p['benefit_recall']),fontsize=6,xytext=(3,4),textcoords='offset points')
 axes[2].axvline(50,color='grey',linestyle=':');axes[2].axhline(80,color='grey',linestyle=':');axes[2].set(xlabel='Unpublished bytes avoided (%)',ylabel='Next-four demand potential retained (%)',title='Frozen operating points; no holdout selection')
 fig.tight_layout();fig.savefig(out/'admission-holdout.png');fig.savefig(out/'admission-holdout.svg');plt.close(fig)
 path=C/'analysis/live-cells.json'
 if path.exists():
  cells=load(path);fig,axes=plt.subplots(1,3,figsize=(11,3.5))
  for variant in ('control','conditional'):
   cs=sorted([x for x in cells if x['variant']==variant],key=lambda x:int(x['context'][:-1]))
   for ax,field,label in zip(axes,['TG','wall_s','copied_GB'],['Decode tokens/s','Request wall seconds','Promotion GB/request']):
    xs=[int(x['context'][:-1]) for x in cs if x.get(field)];ds=[x[field] for x in cs if x.get(field)]
    ax.errorbar(xs,[d['median'] for d in ds],yerr=[[d['median']-d['min'] for d in ds],[d['max']-d['median'] for d in ds]],label=variant,marker='o');ax.set(xlabel='Total context limit (K)',ylabel=label)
  for ax in axes:ax.legend(fontsize=7)
  fig.suptitle('Application measurements: outputs/MTP diverge; 32K gain has an OFF-build timing confound',fontsize=9)
  fig.tight_layout(rect=(0,0,1,.93));fig.savefig(out/'runtime.png');fig.savefig(out/'runtime.svg');plt.close(fig)
 print('PLOTS_FROM_FROZEN_DATA',out,flush=True)
if __name__=='__main__':main()
