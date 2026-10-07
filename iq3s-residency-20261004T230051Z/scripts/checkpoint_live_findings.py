"""Persist completed evidence and genuine remaining work without changing the hard deadline."""
from lab import ROOT,load,save
ledger=load(ROOT/'candidate-ledger.json')
for f in ledger['families']:
    if f['id']=='F07':
        f.update(state='COMPLETE_MIXED',next='E009fixedtrace and E010actualcompatibleplacement complete.32k TG150.2vs155.9,128k157.8vs133.2; exactbudgets. E012shows freeoutputdivergence/MTP/group-work effects. E013exactchoiceheaprepair and E014samebinaryOFFguard in progress; do not call18.47%policy-onlygain.')
save(ROOT/'candidate-ledger.json',ledger)
status=load(ROOT/'STATUS.json')
status['pending']=['E013 exact selector-cost repair prerequisites/conditional live confirmation','E014 same-binary OFF guard battery/both-profile confirmation','bounded supported prediction/execution followup if evidence warrants','final report, launch audit and owned cleanup']
status['current_winners']['128k_candidate']={'variant':'compatible-v1','TG_median':157.8,'PP_median':5994.7,'path':str(ROOT/'experiments/E010-compatible-runtime/v1/128k'),'state':'PROVISIONAL: same-binaryOFFguard/trajectory mechanism not yet resolved; no universal winner'}
status['current_winners']['reference']='Frozen CURRENT rebuilt control at exact same-base toolchain. E010candidate outcome mixed; recommendation pending falsification/confirmation.'
status['excluded'].append({'path':str(ROOT/'experiments/E011-miss-waits/v1'),'reason':'Diagnostic GPU-event build, all timing rates excluded from headline ranking. Same-output comparison differs +21.5%32k/-9.45%128k; no<=1%overhead certificate.'})
status['excluded'].append({'path':str(ROOT/'experiments/E012-compatible-diagnostic/v1'),'reason':'Diagnostic-only policy mechanism/numerical traces; not clean headline speed.'})
# Do not accumulate duplicate entries if metadata is audited again later.
status['excluded']=list({x['path']:x for x in status['excluded']}.values())
save(ROOT/'STATUS.json',status)
with (ROOT/'DECISIONS.md').open('a') as f:
    f.write('\n## E010–E014 checkpoint\n\nE010completed six valid4Krequests.32kcompatible median150.2vs155.9(control),128k157.8vs133.2. E011uses three selected-layer GPUevent brackets, preserves all4KIDs/router/MTP and firsthead, but its timing changes materially; never promote diagnosticTG to headline. E012unchanged compatible algorithm firstheadbit-identical then diverges after47/84outputtokens.128kMTP and resident-group work changes help explain end-to-end gain; CPUwait distributions are mixed. Falsify policy attribution with E014samebinaryOFF, not extra unchanged repetitions. E013min-heaps preserve all672causal decisions and fullfinitecopy outcomes while reducing offline native median selector cost from~0.786ms to~0.282ms. Meets preregistered25%cost reduction; complete correctness and bothprofile confirmation before choosing it. No production switch.\n')
print('Checkpoint evidence/ledger persisted')
