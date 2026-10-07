"""Post-measurement housekeeping: make isolated replays self-describing."""
from pathlib import Path
import shutil
for name in ['run.py','analyze.py','audit.py']:
 shutil.copyfile(Path('scripts')/name,Path('provenance')/('post-measurement-original-'+name))
p=Path('scripts/run.py');s=p.read_text()
s=s.replace(";a=ap.parse_args()", ";ap.add_argument('--run-dir',type=pathlib.Path,help='Ownership-ledger directory for stop only');a=ap.parse_args()")
s=s.replace("if a.action=='stop':\n  j=load(C/'owned-process.json')", "if a.action=='stop':\n  stop_dir=a.run_dir.resolve() if a.run_dir else C\n  j=load(stop_dir/'owned-process.json')")
s=s.replace("  timing={'measurement_cutoff_monotonic':time.monotonic()+26100,'deadline_monotonic':time.monotonic()+28800}\n  save(C/'timing.json',timing)", "  start=time.monotonic();start_utc=datetime.datetime.now(datetime.timezone.utc)\n  timing={'start_monotonic':start,'start_utc':start_utc.isoformat(),'measurement_cutoff_monotonic':start+26100,'deadline_monotonic':start+28800,'measurement_cutoff_utc':(start_utc+datetime.timedelta(seconds=26100)).isoformat(),'deadline_utc':(start_utc+datetime.timedelta(seconds=28800)).isoformat()}\n  save(C/'timing.json',timing)\n  save(C/'orders/all.json',{cell:orders[cell] for cell in cells})\n  save(C/'protocol.json',{**protocol,'cells':cells,'replay_of':str(global_original),'replay_created_utc':utc()})\n  save(C/'workloads/manifest.json',manifest)\n  save(C/'configs-base.json',bases)\n  save(C/'invalid-pair-ledger.json',[])\n  print('REPLAY DIRECTORY',C,flush=True)")
p.write_text(s)
p=Path('scripts/analyze.py');s=p.read_text().replace('def main():\n ap=', 'def main():\n global C\n ap=')
s=s.replace(";a=ap.parse_args()\n orders=", ";ap.add_argument('--root',type=pathlib.Path,help='Analyze an isolated replay instead of the original');a=ap.parse_args()\n if a.root:C=a.root.resolve()\n orders=")
p.write_text(s)
p=Path('scripts/audit.py');s=p.read_text()
s=s.replace("timing=run.load(C/'timing.json');elapsed=time.monotonic()-timing['start_monotonic'];assert elapsed<28800,'EIGHT_HOUR_LIMIT'", "timing=run.load(C/'timing.json');lifecycle=run.load(C/'STATUS.json')\n audit_end=lifecycle['finished_monotonic'] if lifecycle.get('state')=='COMPLETE' else time.monotonic()\n elapsed=audit_end-timing['start_monotonic'];assert 0<elapsed<28800,'EIGHT_HOUR_LIMIT'")
p.write_text(s)
with Path('reproduce.md').open('a') as f:
 f.write('''\nIsolated replay analysis and owned cleanup (use the directory printed by the runner):\n\n```bash\n"$PYTHON" scripts/analyze.py --root /absolute/path/to/replays/TIMESTAMP --require-complete\n"$PYTHON" scripts/run.py stop --run-dir /absolute/path/to/replays/TIMESTAMP\n```\n\nReplays retain their own frozen orders, payload references, protocol, timing,\ninvalid ledger and configuration identities. Model/binary paths still reference\nthe original frozen artifacts. The original report renderer describes the\noriginal campaign; replay statistics are written into the replay directory.\nA later original audit checks the recorded completion time against the original\neight-hour limit, rather than treating a later audit as additional measurement time.\n''')
with Path('DECISIONS.md').open('a') as f:
 f.write('\nAfter all headline measurements finished, replay housekeeping was completed: isolated runs now retain order/protocol/workload/config manifests and full UTC/monotonic deadlines, print their directory, support separate statistical aggregation and identity-checked owned cleanup. The original final audit uses recorded COMPLETE lifecycle time for subsequent audits. No measured request or numerical result was changed. Before-edit scripts are preserved in provenance.\n')
