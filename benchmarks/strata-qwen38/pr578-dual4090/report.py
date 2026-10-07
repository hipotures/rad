import analyze,json,statistics,re,math
from pathlib import Path
R=analyze.R

def val(v,nd=1):return '—' if v is None else f'{v:.{nd}f}' if isinstance(v,(int,float)) else str(v)
def write():
 cells=analyze.summarize();by={x['config']:x for x in cells};raw=json.loads((R/'summary.json').read_text());lines=['# IQ3_S · PR578 · 2× RTX4090','','## Status','','Controlled local comparison on frozen same upstream base. Every headline is decode tok/s after warmup with MTPspec4/min-p0.5; suffixOFF unless explicitly labeled LOOKUP-ON. Model unchanged; normal sm89 Release CUDA.','']
 lines+=['## Source/build/tests','','Main/base99f3dbd0b21d1401b3769e0c0d963913607f380b; openPRheadb28121ff6ef117bec2558b3ece7e188dd33a2b7e. Clean merge, no conflicts. FreshCONTROL andPR checkout; no pushes. Each raw contains binarySHA256, sourceHEAD, fullcommand/config, modelrevision and tokenIDs hash.','', 'BothCTest suites:56pass,2skip,4environment failures (Q2_0PLEfixture absent, legacy experts.bin fixtures absent,256MiBmlock test exceeding8MiBhard limit). BothPythonserve suites197tests,9skip,OK. No real correctness failure observed. Tests are not described as allpassing. Details:test-status.json and logs/.','']
 corr=R/'correctness/summary.json'
 if corr.exists():
  cc=json.loads(corr.read_text());lines+=['## Correctness','',f'10 paired greedy cases, identicalinputIDs, actualoutputIDs saved. Malformed flags: {sum(x["malformed_output"] for x in cc)}. First divergences recorded; autoregressive positional agreement is not teacher-forced top1. NaN debug path enabled only in correctness, none observed. No easy serve/native optimized-helper KLdump available. Outputs manually inspected for evident corruption; no qualityranking.','']
 lines+=['## Primary32K · suffixOFF','','|Config|PPmedian|TGmedian|TGmin/max|TTFTs|accepted/window|suffixaccepted|CPUfallback entries¹|helperentries|overlap²|CPU%³|GPU0%|GPU1%|','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
 for label in ['LS-A','LS-B','PR-LS','H-OLD','H-OPT','H-OPT-FIXED']:
  x=by.get(label)
  if x:lines.append('|'+ '|'.join([label,val(x['pp_tps']),val(x['tg_tps']),val(x['tg_tps_min'])+'/'+val(x['tg_tps_max']),val(x['ttft_s'],3),val(x['mean_accepted_length'],3),val(x['suffix_accepted'],0),val(x['cpu_fallback_entries_estimate'],0),val(x['helper_entries'],0),val(x['cache_overlap'],0),val(x['decode_cpu_system_pct']),val(x['gpu0_decode_util_pct']),val(x['gpu1_decode_util_pct'])])+'|')
 lines+=['','¹ CPU entries derived approximately from normal log rounded per-layer-window means ×48layers×verifywindows. DistinctCPU expert count and routedentry count are separate. ² FinalspeeddiagnosticsOFF; overlap measured separately in DIAG runs. Missing metrics stayunknown. ³ System100%=all16vCPU; process100%=onevCPU.1Hzdecode samples sparse for256output. PCIe hardware counters in telemetry/*pcie-dmon.log; timing-aligned aggregates are supplemental.','']
 lines+=['## Fairness / initialcache','','AutoPR:8586actualprimaryslots+11796helperslots=20382initial residents. NumericprimaryCLI6567 reproduces actual8586 because upstream converts max-blob budget into variable-sized slots. Original/optimized correctness startup captured identicalprimaryIDs/helperIDs andzerooverlap. Mainhelper configurations must match actualcounts beforewarmup; see layouts and fairness-audit.json. Auto/fixed comparisons use physicalcapacity, notmatchingCLI numerals.','', 'Old4096payload is warmup only. Its natural EOS may generate fewer than256; perwarmup outputcount is retained and notused in headline medians. All measured fixedlength requests with<256, reuse!=0, incorrectactualcount remainINVALID. No discarded request is silently replaced.','']
 lines+=['## Cache diagnostics / transfers','','|Config|TGmediandiagnostic|startup overlap|afterwarmup|afterrun3|helperreturnedMiB|helperwaitms|','|---|---:|---:|---:|---:|---:|---:|']
 for label in ['H-OLD-DIAG','H-OPT-DIAG']:
  x=by.get(label)
  layout=R/'raw'/f'{label}-layout.json';wp=R/'raw'/f'{label}-32K-warmup.json';rp=R/'raw'/f'{label}-32K-run3.json'
  def ov(p,start=False):
   if not p.exists():return None
   d=json.loads(p.read_text());snap=d.get('snapshot') if start else (d.get('cache_snapshots') or [None])[-1];return snap.get('overlap') if snap else None
  if x:lines.append('|'+ '|'.join([label,val(x['tg_tps']),val(ov(layout,True),0),val(ov(wp),0),val(ov(rp),0),val(x.get('helper_returned_bytes')/1048576 if x.get('helper_returned_bytes') is not None else None),val(x.get('helper_wait_ms'))])+'|')
 lines+=['','Instrumentation consists solely of default-off boundary cache snapshots; no new hot-pathper-token counters. All headlines instrumentationOFF regardless of observednoise. Differences in residentIDs are netchanges, notall adaptation swaps. Quantizationskips notcounted. Nativehelperreturnedbytes counter approximates logprecision0.1MiB; it is notwholePCIetraffic.','']
 lines+=['## Finalcontextmatrix · suffixOFF','','|Config|Actualinput|validruns|PP|TG|TTFT|CPUfallback¹|helperentries|CPU%|GPU0%|GPU1%|','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
 for x in cells:
  if x['config'].endswith('-FINAL'):lines.append('|'+ '|'.join([x['config'],val(x['actual_prompt'],0),val(x['valid_runs'],0),val(x['pp_tps']),val(x['tg_tps']),val(x['ttft_s'],3),val(x.get('cpu_fallback_entries_estimate'),0),val(x.get('helper_entries'),0),val(x.get('decode_cpu_system_pct')),val(x.get('gpu0_decode_util_pct')),val(x.get('gpu1_decode_util_pct'))])+'|')
 lines+=['','Same literaloldpayloads acrossconfig at31400/63400/127000/259500. Eachcontext warmup then3requests; contextsmatrix hasadaptivecachehistory preserved within freshserver perconfig. Onlyvalid256output/reuse0 requests count. No 3-runmedian claimed whenvalidcount<3.','', '## Secondary lookupON / steadydecode','','|Config|Actualinput|Outputkind|Validruns|PP|TG|TGmin/max|TTFT|suffixaccepted|','|---|---:|---|---:|---:|---:|---:|---:|---:|']
 for x in cells:
  if 'LOOKUP-ON' in x['config'] or 'STEADY' in x['config']:lines.append('|'+ '|'.join([x['config'],val(x['actual_prompt'],0),'2048' if 'STEADY' in x['config'] else '256',val(x['valid_runs'],0),val(x['pp_tps']),val(x['tg_tps']),val(x['tg_tps_min'])+'/'+val(x['tg_tps_max']),val(x['ttft_s'],3),val(x['suffix_accepted'],0)])+'|')
 lines+=['','Steadydecode is a distinct workload, shared deterministicsavedprompt andsuffixOFF. --prompt-cache0 prevents repeatedprompt reuse; nothistoricalAB. Allactual2048output required; earlyEOSnegative retained. Main32K benchmarks a code-agent workload;10short math/prose correctness requests arenot a formal mixed/math speedbenchmark. Therefore no workload-general codevsMathwinner claim.','']
 lines+=['## Historical / author references','','Historicaloldv0.1.31:PP4652.5/TG131.2. v0.1.38exactoldreplay:PP4580.4/TG131.7;TG111.7/147.5/131.7,secondlookup173/173. HISTORICAL/NOT_CONTROLLED_A_B; differsautoPCIefraction andwarm/cachehistory. Never used ascleancontrol forPR attribution.','', 'AuthorPRbody dual4090v0.1.37:originalhelper88.07/85.15 mixed/code;layersplit126.86/146.95;optimized143.35/197.58. Differentworkload/config; requests/scriptsnotaddedbyPR. No expectations ofmatchingabsolutethroughput.','']
 lines+=['## Limitations','','No tensorweights changes/newmodeldownloads. No exactteacherforcedKL/top1 output. Per-tokenquantizationskip counter unavailable; no inventedcount. Netcachechanges do notcounttransientswaps. Guest virtiofsfile/counter telemetry cannotprovephysicalhostSSDreads. CPU/GPU1Hzphaseaverages andPCIetimealignmentapproximate, particularly2sdecode. NoPSSpolling1Hz. Negativeattempts andwarmups arepreserved.','']
 selection=R/'selection.json';recommendation='NEED_MORE_DATA'
 if selection.exists():
  d=json.loads(selection.read_text());l=d['best_layer_split'];o=d['best_optimized_helper'];delta=(o['tg_tps']/l['tg_tps']-1)*100
  lines+=['## Analysis','',f'Primary32K optimizedhelper {o["config"]}: {o["tg_tps"]:.1f}TG vs layer split {l["config"]}: {l["tg_tps"]:.1f}TG; delta{delta:+.2f}%. CompareH-OLDvsH-OPT/FIXED atmatchedinitialcapacity to attributeoptimizationeffect. PR-LSguard separates inactivePRfromtopology.','']
  final=[x for x in cells if x['config'].endswith('-FINAL')];steady=[x for x in cells if 'STEADY' in x['config']]
  if len(final)==8 and all(x['valid_runs']==3 for x in final) and len(steady)>=2 and all(x['valid_runs']==3 for x in steady):recommendation='USE_PR578_HELPER' if delta>5 else 'KEEP_LAYER_SPLIT'
 lines+=['## RECOMMENDATION','',recommendation,'', 'Recommendation remains provisional until context/steadydecode andsame-capacityaudits are complete; allvalues reproducible from rawrecords andscriptanalyze.py.']
 (R/'report.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':write()
