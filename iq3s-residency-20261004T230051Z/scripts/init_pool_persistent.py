"""Initialize the separately authorized ten-hour follow-up without overwriting prior evidence."""
import datetime, hashlib, json, pathlib, shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
START=1791193680
STAMP='20261005T094800Z'
C=ROOT/'campaigns'/('pool-persistent-'+STAMP)
assert not C.exists()
C.mkdir(parents=True)
archive=C/'previous-root';archive.mkdir()
names=['report.md','summary.json','summary.csv','STATUS.md','STATUS.json','launch-index.md','launch-index.json','candidate-ledger.json','deadline.json','GOAL.md']
inventory=[]
for name in names:
    p=ROOT/name
    if p.exists():
        shutil.copy2(p,archive/name)
        inventory.append({'path':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
def utc(t):return datetime.datetime.fromtimestamp(t,datetime.timezone.utc).isoformat()
d={'campaign':'pool-persistent-'+STAMP,'start_epoch':START,'start_utc':utc(START),'deadline_epoch':START+36000,'deadline_utc':utc(START+36000),'consolidation_start_epoch':START+33300,'consolidation_start_utc':utc(START+33300),'previous_deadline_unchanged':str(ROOT/'deadline.json'),'source':'New explicit user authorization; includes initial read/setup. Previous completed goal is not resumed.'}
(C/'deadline.json').write_text(json.dumps(d,indent=2)+'\n')
(C/'previous-root-manifest.json').write_text(json.dumps(inventory,indent=2)+'\n')
(ROOT/'active-campaign.json').write_text(json.dumps({'path':str(C),'deadline_path':str(C/'deadline.json'),'state':'ACTIVE'},indent=2)+'\n')
(C/'GOAL.md').write_text('''# Authorized pool/residency follow-up

Hard maximum ten hours from 2026-10-05 09:48:00 UTC. New substantial experiments stop at 19:03:00 UTC; absolute stop 19:48:00 UTC. Finish earlier if all three phase conclusions are defensible.

P0: same frozen CURRENT binary, default versus STRATA_POOL_SPIN_US=100 on at least three independent real workload families at max contexts32768/131072. Exact frozen token IDs, common64-token warmup, greedy/MTP4/minp0.5/INT8/K25/PCIe0.28/workers15/suffix0/reuse0, output4096 cap. At most3 valid measured repetitions per unchanged point. Preserve natural EOS and use common-prefix/application latency rather than favorable prompt retries. Include miss-heavy diagnostic evidence. Write P0 report before P1.

P1: select one defensible fixed100us/default or smallest adaptive parking policy only if P0 warrants it. Stress wakeups/job bursts/idle periods/alternating work. Confirm standard and independent workloads at both profiles, at most3 valid per point. Freeze source/binary/config and start32/128/stop/reproduce launchers. Write P1 report before P2.

P2: on P1 only, replay then implement persistent, byte-aware, same-device router/horizon8 + heat/demand residency. Keep exact physical capacity, asynchronous immutable RAM→VRAM transfer, publication only after completion, safe readers/victims/reservations, no immediate restore, no mathematical routing changes. Charge contended queues, useful/wasted/late bytes and victim damage. Diagnostic32K funnel then at most3 valid final paired confirmations32K/128K. Preserve failures and completed negatives; no tuning until it wins. Optional narrow crossGPU analysis only if phases complete/capacity-blocked and90minutes remain before cutoff.

No64K/256K/helper/v0138/dense sweeps/retraining/temporary swap-restore repeats. No push/PR/sudo/model changes/global changes/deletion of prior data. Existing normal user launchers unchanged. Continue this laboratory with E026 onward and separate source/build/raw/variant provenance. Phase/root reports and status/ledger/launchindex/summary updated; final best real-prompt commands, performance, correctness, negatives and actual unfinished work. Stop owned compute and verify bothGPUsfree. Final recommendation exactly one of USE_P1_BASELINE, USE_PERSISTENT_RESIDENCY, WORKLOAD_DEPENDENT, PROMISING_NEEDS_MORE_WORK, KEEP_PREVIOUS_CURRENT.
''')
s={'state':'ACTIVE','campaign':d['campaign'],'start_utc':d['start_utc'],'deadline_utc':d['deadline_utc'],'running':'E026-pool-generalization','completed':[],'pending':['P0 independent workloads and paired comparison','P1 select/freeze/confirm pool baseline','P2 replay/implement/live persistent residency','Final reproducibility/report/cleanup'],'previous_complete_campaign':str(archive),'next_exact_action':'Freeze independent workloads and paired fresh-server protocol; run P0 before P1/P2.'}
(ROOT/'STATUS.json').write_text(json.dumps(s,indent=2)+'\n')
(ROOT/'STATUS.md').write_text('# Follow-up status\n\nACTIVE: E026 pool generalization.\n\nStart09:48 UTC; experiment cutoff19:03 UTC; absolute deadline19:48 UTC. Previous completed evidence archived unchanged under '+str(archive)+'.\n\nNext: freeze P0 independent workloads and same-binary paired protocol. P1/P2 not started.\n')
(ROOT/'experiments.jsonl').open('a').write(json.dumps({'id':'E026','state':'PREPARING','campaign':d['campaign'],'note':'New explicit authorization; old completed evidence unchanged.'})+'\n')
print(json.dumps(d,indent=2))
