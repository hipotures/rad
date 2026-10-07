"""Freeze the missing same-binary OFF ablation of the completed E010 candidate."""
from lab import ROOT,save
out=ROOT/'experiments/E014-policy-off-guard/v1'
if (out/'protocol.json').exists():raise RuntimeError('Protocol already frozen')
save(out/'protocol.json',{
    'question':'Does E010 compatible-v1 appear faster128k because the policy changes, or because the binary/build/scheduling/time differs from clean rebuilt control?',
    'comparison':'Same exact E010compatible-v1 source/binary, policyOFF vs already completed policyON. Reuse all3validONrequests/profile. Exact base/model/flags/worker/K/PCIe/settings/payloads/capacities/warmup policy. This is a new binary/config point, not a renamed repetition of E002control.',
    'changed_variable':'STRATA_LAB_COMPATIBLE unset. Existing same-layer EMA branch remains original. No rebuild, no diagnostic instrumentation.',
    'reason':'E010128k+18.47% but real/free trajectories diverge; E011same-trajectory diagnostics differed +21.5%32k/-9.45%128k. A same-binary OFF guard can falsify attribution to the new admission algorithm.',
    'budget':'Original fullRAM/nativeIQ3_S/fixedphysicalslotclasses; no new GPU allocation, unused compatible metadata vectors empty whenOFF.',
    'prerequisites':'OriginalE010completeupstream/kernel/battery evidence; additionally run saved10caseOFFbattery vs existing cleancontrol for this configuration before speed. Basic numeric/JSON checks and noNaN required.',
    'batch':'Freshserver/profile, saved4096input64outputwarmup, exactly3attempts saved4096outputrequests,32kthen128k. No more unchangedON/E002runs. Stop unsafe crash, preserve invalid/failed.',
    'interpretation':'Source/binary identical ON/OFF isolates the flag better, but separated serial batches still have time/cache and numerical trajectory effects. Three runs do not establish small universal gains.',
    'completion':'Both-profile3attempt batch and comparison to ON/control; output hashes/MTP/accounting/capacity checked; no production launcher change.'})
save(out/'overrides.json',{'policy':'original same-layerEMA; exact compatible-v1 binary with opt-in OFF','extra_gpu_bytes':0,'ablation':'Same-binary guard for E010 policy attribution.'})
print(out)
