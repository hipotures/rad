"""Record completed falsification evidence and bounded ongoing diagnostics."""
from datetime import datetime,timezone
from lab import ROOT,load,save
p=ROOT/'STATUS.json';s=load(p)
s['updated_utc']=datetime.now(timezone.utc).isoformat()
s['running']=['E016 correctness arithmetic diagnosis','E017 GPU next-gate availability/cost diagnostic']
s['pending']=['Diagnose E016 first-layer arithmetic divergence before conditional speed confirmation','Analyze E017 same-device prediction cost/causal tail readiness and decide one bounded follow-up','Consolidate research tree, launch index, report and owned cleanup before09:00:51UTC']
s['next_exact_action']='Finish E017 isolated GPU-router collection; then build/run same-binary DP ON/OFF per-layer warmup snapshots. No headline DP run while arithmetic correctness unresolved.'
s['last_stage']={'id':'E015','state':'COMPLETE_NEGATIVE_CPU_VARIANTS_ONLY','updated_utc':s['updated_utc'],'note':'Fresh activation diagnostics correct earlier stale signals; actual route/output/heat parity verified. GPU follow-up E017 required before general router-family conclusion.'}
s['current_winners']['reference']='Keep rebuilt CURRENT reference pending completed research. E010128 apparent gain not established as a portable policy benefit: exact-choice E013 gave identical outputs/counts and substantially different TG; E014same-binaryOFF guard also changed TG with same control outputs.'
s['current_winners']['128k_candidate']['state']='PROVISIONAL_NOT_SELECTED: falsification completed E013/E014; see analysis/confirmation-falsification-v1. No universal or isolated policy18.47%claim.'
for item in s['excluded']:
 if 'E008-router-boundary/v2/analysis-r2' in item['path']:item['path']=str(ROOT/'experiments/E008-router-boundary/analysis-r2')
s['excluded'].append({'path':str(ROOT/'experiments/E017-gpu-router/v1'),'reason':'Retained build failure: duplicated input-width argument in native GEMV invocation. Repaired separatev2; no inference results in failedv1.'})
s['excluded'].append({'path':str(ROOT/'experiments/E016-device-plan-ids/diagnostic-v1'),'reason':'Diagnostic-only. First-head bit-identical, but warmup trajectory diverges25tokens; firstsame-input router divergencewindow3/layer1. Arithmetic correctness unresolved, so no speedheadline forv1 yet.'})
save(p,s)
(ROOT/'STATUS.md').write_text('# Research status\n\nUpdated '+s['updated_utc']+'\n\nAbsolute deadline:09:00:51UTC; consolidation08:15:51UTC.\n\nCompleted E001–E015. E013/E014 falsify a simple interpretation of E010128 gain; output-identical binaries/batches show large TG variation. Do not declare the compatible policy a production winner.\n\nE016: native/Python/realIQ tests and narrow10case ground truth pass. Stable IDs fix shared-buffer overwrite, but same-input arithmetic divergence needs diagnosis before speed. Full layer/head snapshots predeclared, warmup-only.\n\nE017: v1 compile failure retained; v2 builds and targeted/realIQ tests pass. Five same-device extra gate projections measured separately; no expert movement. GPU experiments serial.\n\nNext: '+s['next_exact_action']+'\n')
print(s['updated_utc'])
