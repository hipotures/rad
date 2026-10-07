"""Freeze a bounded mechanism/numerical diagnosis of completed E010."""
from lab import ROOT,load,save
out=ROOT/'experiments/E012-compatible-diagnostic/v1'
if (out/'protocol.json').exists():raise RuntimeError('Protocol already exists')
save(out/'protocol.json',{
    'question':'Does the E010128k headline gain survive same-input mechanism checks, and does compatible placement shorten observed GPU waits or mainly change free-generation trajectory?',
    'evidence':'E0103valid/profile,32k medianTG150.2vs155.9(-3.66%);128k157.8vs133.2(+18.47%). CPUfallback reduced but MTP/actual greedy trajectories may differ. E011 direct selected-layer GPU spans measured; isolated boundary copies around20us, not entire wait.',
    'variant':'Identical retained compatible-v1 algorithm/native kernels/scheduler plus exactly E011 buffered diagnostics. No new policy or tuning.',
    'trace_schema':'Version2 adds explicit outgoing_layer and reserved int32 to promotion record(56B). Version1 originals remain untouched; reader switches only on explicit schema metadata.',
    'budget':'Same physical capacities/classes/K25. E010 CPU metadata and selector scratch; E01148timingevents/no new explicitGPUbuffers. Internal event resources not claimed zero.',
    'prerequisites':'Relevant native/event tests, realIQparity, trace schema synthetic regression; originalE01010case correctness remains preserved.',
    'batch':'Diagnostic only: one fresh server/profile, identical64outputwarmup, one frozen4096-outputrun1 each;32kthen128k. No additional unchanged E010 speed repetitions.',
    'validation':'Exact inputIDs, capacities, output counts/reuse0, noNaN/OOM. Validate cross-layer withdrawal/publication byte/owner accounting; compare first-head logits on same input and actual first output divergence versus E011.',
    'analysis':'CPU/local/mapped demands, unique native expert groups, promotions/usefulness/victim demand; selected-layer phase spans conditioned on actualT/group/work. Separate common prefix from complete divergent trajectories. Headtop1/KL only one position, not full parity.',
    'completion':'Bothprofiles diagnosis retained, all divergence disclosed, no speed claim from diagnostic TG. Use results to select justified next repair; do not repeat already complete clean points.'})
save(out/'overrides.json',{'env':{'STRATA_LAB_MISS_WAITS':'1','STRATA_LAB_COMPATIBLE':'1'},'diagnostic_only':True,'question':'Unchanged E010 policy plus E011scopedGPUspans/schema2crosslayervictims; mechanism and numerical diagnosis.'})
print(out)
