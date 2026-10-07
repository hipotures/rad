"""Freeze phase handoffs from audited final evidence, retaining superseded pilot prose."""
from pathlib import Path
import json,datetime
C=Path(__file__).resolve().parents[1]
def load(p):return json.loads(Path(p).read_text())
def main():
 old=C/'phase-b/report.md';snapshot=C/'phase-b/report-pilot-v1-v2.md'
 if not snapshot.exists():snapshot.write_bytes(old.read_bytes())
 s=load(C/'summary.json');short=load(C/'phase-c/short64-v3-summary.json')
 lines=['# Phase B — feasible full-scope logical oracle scheduling',
 'This final phase handoff supersedes the preserved pilot report. The final common source is 117bc89b3bacbf263379c336557e6c8aa07aff5e; binary SHA256 is 30a31432b5aff51bcd4340900c13cad0c8487a832bfdb22d05f9157b88d5bdb3. Final matrix results and paired timing live in ../report.md.',
 '## Physical contract',
 'All 48 main routed layers and all three physical classes (3.072, 3.584 and 3.9936 MB) are eligible. GPU0 owns layers 0–23 and GPU1 owns 24–47. Five existing slots become class-compatible spares after timed decode begins. Allocated expert/dense/KV/MTP VRAM is unchanged; active residents decrease by five, and restoration of 17,305,600 bytes is charged. MTP stays on its original all-resident expert path.',
 'Immutable host-RAM weights pass through pinned staging and real nonblocking H2D streams. One transaction per device/class has exclusive ownership. Completed copy is published only at a safe routed-layer boundary; the old victim slot becomes the next spare. Current full-window batches protect readers. Victims are chosen at publication using the same future knowledge as admissions. No temporary swap/restore, remote experts, P2P or SSD source is used.',
 'REPLAY_CURRENT retains native adaptation. REPLAY_ORACLE_FULL is the sole exchange authority for main decode while causal heat updates continue. Native and oracle traffic, initial spare loss, online planning/publication wait, mandatory drain and restoration are reported separately. Copies are issued from logical milestones, never recorded wall-clock offsets.',
 '## Information and heuristic',
 'Full future supplies victim next-use and incoming future demand/lifetime. The rolling incoming issue frontier is 64 main routed-layer invocations; one invocation is the entire T-by-10 batch, not a generated token or verifier window. Measured event progress and staging/copy duration update lead estimates. Late work uses safe CPU/mapped fallback. This is a feasible next-use/slack heuristic with same-layer victims, not an optimal variable-size scheduler or upper bound.',
 '## Offline models',
 'The warmup counter correction (25 native adaptation rounds carried into request 2) exactly reproduces 32K native local/CPU/mapped counts and native traffic. Capacity-only full future reaches zero nonlocal entries using 215.698 GB of exchanges under relaxed transfer timing; no measured TG follows. Modeled full-deadline transfer replay yields 2,579 nonlocal entries and 217.438 GB. The alternative reuse-amortized strategy yields 121,381 nonlocal entries and 41.277 GB. Explicit modeled costs remain assumptions, separate from live timing.',
 'Offline horizons 1, 4, 16 and 64 constrain both admissions and victim queries. An early version leaked full current-window protection beyond short horizons; strict_offline.py repairs it and preserves the old results as safety-privileged diagnostics. Beyond the bound is unknown and uses causal heat, not guaranteed absence. The live H64 does not have this leak because all remaining current-window layers are inside 64.',
 '## Live result',
 '| Profile | Current decode s | Full-future decode s | Median paired TG gain |',
 '|---|---:|---:|---:|']
 for p in ['32k','128k','256k']:
  a=next(x for x in s['cells'] if x['profile']==p and x['policy']=='REPLAY_CURRENT');b=next(x for x in s['cells'] if x['profile']==p and x['policy']=='REPLAY_ORACLE_FULL');q=next(x for x in s['paired'] if x['profile']==p)
  lines.append(f"| {p} | {a['metrics']['decode_s']['median']:.3f} | {b['metrics']['decode_s']['median']:.3f} | {(q['median_of_paired_ratios']['throughput_oracle_over_current']-1)*100:.2f}% |")
 lines+=['',
 f"The single H64 confirmation took {short['run']['decode_s']:.4f} s ({short['run']['equivalent_tok_s']:.2f} replay-equivalent tok/s), with 317.525 GB copies and 85,392 victim-absent entries. Full-future attempt 1 used 207.126 GB with 10,036 victim-absent entries. This repaired bounded heuristic demonstrates harmful churn, not a universal impossibility result.",
 'The primary full-future schedule improved readiness/locality and measured replay decode at every profile, so a second live full-future heuristic was not needed. Independent substantive source content confirms a separate paired benefit. All primary counts, ownership, copies and work hashes passed. See phase-c/ and ../analysis/ for admission funnels, residual misses and distinct persistent reuse.',
 '## Safety and interpretation',
 'The real-CUDA scheduler fixture checks all physical classes, exact bytes, duplicate/inflight refusal, protected victims, became-resident suppression, delayed fallback, repeated spares, cancellation/drain/restoration, next request and pending shutdown. QSA record/replay overrides and initial-state sidecar tests pass. Actual Q4 expert math passes against dequant reference. CPU/GPU quantization and summation can differ; forced token equality is not model-quality proof.',
 'The full oracle exploits finite tape-end knowledge, has no guard tail and cannot establish a deployment bound. Remaining nonlocal work is dominated by victim absence; copied traffic is substantially greater than native adaptation. A practical predictor must learn incoming readiness/lifetime jointly with valuable victim protection and queue cost.',
 'The unchanged Q4/100us serving baseline remains the real-use configuration.']
 old.write_text('\n\n'.join(lines)+'\n')
 a=C/'phase-a/report.md';text=a.read_text();text=text.replace('Same-final-binary ordinary/replay overhead confirmation remains the declared next guard after the main matrix. Recording overhead is diagnostic and never a natural speed arm. See development-overhead-v1.json for provisional earlier3.0%decode/1.1%wall difference.','Final same-binary ordinary/replay overhead confirmation was completed after the main matrix, as transparently recorded in the protocol-order limitation below. Recording overhead is diagnostic and never a natural speed arm. Earlier v1 provisional overhead remains separate.')
 a.write_text(text)
 n=load(C/'tests/native-suite-summary.json');n['original_evidence_annotation']='tests/native-suite.xml/tests/native-suite.log';n['evidence']='tests/native-suite.log';n['erratum']='The original summary referenced an XML file not copied into this campaign. The retained native CTest text log is the actual evidence; no missing XML is claimed.';(C/'tests/native-suite-summary.json').write_text(json.dumps(n,indent=2)+'\n')
 events=[
  {'event':'FINAL_PRIMARY_MATRIX','state':'COMPLETE','valid':18,'attempts':18,'new_repetitions_added':False},
  {'event':'FINAL_OVERHEAD_AND_INDEPENDENT','state':'COMPLETE','evidence':'phase-a/overhead-v3-summary.json; phase-c/independent-v3-summary.json'},
  {'event':'SHORT_H64','state':'COMPLETE_NEGATIVE','evidence':'phase-c/short64-v3-summary.json','interpretation':'One scoped later attempt; high churn/victim damage, not an information bound'},
  {'event':'POST_ANALYSIS_REPAIRS','state':'COMPLETE','details':'Correct independent label in residual-miss analysis; refresh cached audit schema; isolate matplotlib dependency; no inference rerun or runtime change'},
  {'event':'SHUTDOWN_DIAGNOSTIC','state':'POST_REQUEST_EPIPE_RETAINED','details':'H64 successful complete request followed by upstream frontend close-of-already-ended-pipe race on owned group SIGTERM; outside request timing'},
  {'event':'LAUNCHER_CHECKS','state':'PASS','evidence':'tests/launcher-checks/summary.json','scope':'Shell syntax and identity/config/tape checks; same execution backends exercised in actual campaign. New-directory reproduction parent not live-inference tested.'}]
 with (C/'ledger.jsonl').open('a') as f:
  for e in events:e['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();f.write(json.dumps(e)+'\n')
 with (C/'DECISIONS.md').open('a') as f:f.write('\n## Final bounded decision\n\nAll 18 v3 primary attempts are valid. Full future improves paired replay decode at all three profiles; the independent source-content task confirms a separate gain. H64 is a retained negative churn result. Stop adding inference runs. Complete artifact/reproducer audits and cleanup, then finish early. The unchanged original Q4/100us baseline remains real-use; no predictor or production switch is authorized by this replay result.\n')
 print('PHASE_REPORTS_FINALIZED',flush=True)
if __name__=='__main__':main()
