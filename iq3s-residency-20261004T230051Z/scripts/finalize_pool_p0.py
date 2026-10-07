"""Close P0 only after all paired observations and diagnostic waits have been reviewed."""
import argparse, statistics
from lab import ROOT, load, save
ap=argparse.ArgumentParser();ap.add_argument('--decision',required=True,choices=['P0-A','P0-B','P0-C']);ap.add_argument('--rationale',required=True);a=ap.parse_args()
base=ROOT/'experiments/E026-pool-generalization';s=load(base/'summary.json');d=load(base/'diagnostic-v1/summary.json')
assert s['state']=='COMPLETE_MEASUREMENTS' and d['state']=='COMPLETE_DIAGNOSTIC'
assert len(s['paired'])==18 and all(p['same_binary'] and p['same_input_IDs'] and p['same_capacity'] for p in s['paired'])
s.update(state='COMPLETE_SCOPED_VALIDATION',decision=a.decision,rationale=a.rationale,diagnostic=str(base/'diagnostic-v1/summary.json'))
s['parity']={k:sum(not p[k] for p in s['paired']) for k in ['same_actual_output_IDs','same_MTP','same_normal_routing','same_capacity']}
s['diagnostic_selection']=d['selection'];s['diagnostic_waits']=d['waits'];s['diagnostic_parity']=d['parity']
save(base/'summary.json',s)
text=(base/'report.md').read_text().replace('State: COMPLETE_MEASUREMENTS. Decision pending wait diagnostics and paired review.',f'State: COMPLETE_SCOPED_VALIDATION. Decision: **{a.decision}**.\n\n{a.rationale}')
text+='\n## Controlled checks and scope\n\n'
text+=f'18 paired comparisons /36 clean requests; each fresh server, same saved4096-input64-output warmup, same actual service-rendered inputIDs and same executable. Parity mismatches: `{s["parity"]}`. Every fixed-length valid point has exactly3 requests; no additional repetitions or favorable retries.\n\n'
text+='Independent tasks: real HEG repository/SQLite audit; CPython/NumPy polynomial/rational reasoning; official HTTP RFC operational prose. Complete immutable documents, tasks, payloads and actual inputIDs are in workloads/. Nonces differ between replicas but are identical between policies. This is not a universal claim for multilingual, extreme miss-heavy or concurrently CPU-loaded production traffic.\n\n'
text+='Natural stopping/invalid records are retained and excluded from fixed-length medians. Source control shutdown BrokenPipe traces after completed responses are the documented owned process-group cleanup, not an inference failure. Logical expert reads remain unavailable; physical counters are not substituted.\n\n'
text+='## CPU completion wait diagnostics\n\n'
text+='The CPU-heaviest family/profile was selected from clean median CPU entries per generated token, not assumed from task names. Same existing E021 event binary for default/100us; full4K buffers and selected layers2/24/40 only. Diagnostic throughput is excluded.\n\n'
text+='| Profile | Family | Layer | Category | Default median us | 100us median us | Default p95 us | 100us p95 us |\n|---|---|---:|---|---:|---:|---:|---:|\n'
for profile in ['32k','128k']:
    for layer in [2,24,40]:
        for cat in ['all-local','CPU-positive']:
            q={r['role']:r for r in d['waits'] if r['profile']==profile and r['layer']==layer and r['category']==cat}
            b=q['default']['completion_wait_us'];c=q['sleep100us']['completion_wait_us']
            if b and c:text+=f'| {profile} | {q["default"]["family"]} | {layer} | {cat} | {b["median"]:.2f} | {c["median"]:.2f} | {b["p95"]:.2f} | {c["p95"]:.2f} |\n'
text+='\nThese waits include event/kernel floors and overlap other streams. They cannot be multiplied by48 or summed into a synthetic request latency. Actual end-to-end wall/TG is the decision criterion. Full output/router/path/MTP diagnostic parity: `'+str(d['parity'])+'`.\n\n'
text+='## Next phase\n\n'+('Freeze existing100us, run targeted wakeup stress and fresh paired standard-workload confirmation; reuse the P0 independent confirmations instead of exceeding3valid repetitions.' if a.decision=='P0-A' else 'Proceed to a small evidence-driven P1 parking policy; preserve these fixed-policy results and do not change completed points.')+'\n'
(base/'report.md').write_text(text)
print(a.decision,s['parity'],flush=True)
