"""Freeze a runnable variant and generate executable start/benchmark/reproduce/stop entry points."""
import argparse, copy, hashlib, json, pathlib, subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('name');ap.add_argument('--source',required=True);ap.add_argument('--binary',required=True);ap.add_argument('--diagnostic',action='store_true');ap.add_argument('--extra-args',nargs='*',default=[]);ap.add_argument('--overrides');a=ap.parse_args()
overrides=json.loads(pathlib.Path(a.overrides).read_text()) if a.overrides else {}
src=pathlib.Path(a.source);exe=pathlib.Path(a.binary);dest=ROOT/'variants'/a.name
if dest.exists():raise RuntimeError('Variant exists; refuse overwrite')
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=src,text=True).strip();status=subprocess.check_output(['git','status','--porcelain'],cwd=src,text=True)
if status:raise RuntimeError('Commit local patch before registering source identity: '+status)
if not exe.is_file():raise RuntimeError('Frozen binary does not exist')
dest.mkdir()
base=json.loads((ROOT/'references/threeway/configs/CURRENT.json').read_text())
for profile,limit in [('32k',32768),('128k',131072)]:
 cfg=copy.deepcopy(base);args=cfg['args'];args[args.index('--max-context')+1]=str(limit)
 cfg.update(exe=str(exe),cwd=str(src),python=str(ROOT/'src/control/.venv/bin/python'),max_total_context=limit,source_sha=head,binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),build_variant=a.name,Strata_HEAD=head,upstream_base='6f32ec070f23ced9f50e704d854d775da52591ab',source_status=status,port=18132,host='127.0.0.1',headline_instrumentation='DIAGNOSTIC_ONLY' if a.diagnostic else 'OFF',model_revision='ed59f92082b1e93c0e96d60a8b11aab089b52f09',args=args+a.extra_args+overrides.get('extra_args',[]))
 cfg['env']={'CUDA_VISIBLE_DEVICES':'0,1','STRATA_SPLIT_TIMING':'1','STRATA_DECODE_TIMING':'1'}
 cfg['env'].update(overrides.get('env',{}));cfg['variant_overrides']=overrides
 for key in ['source_provenance','initial_layout_policy','PR_head','encoder_variant','environment_overrides','effective_experiment_environment','extra_env','benchmark_environment']:cfg.pop(key,None)
 if a.diagnostic:cfg['diagnostic_env']={'STRATA_LAB_TRACE':'{attempt}/traces/runtime'}
 (dest/f'{profile}.json').write_text(json.dumps(cfg,indent=2)+'\n')
 py=str(ROOT/'src/control/.venv/bin/python');lab=str(ROOT/'scripts/lab.py')
 for mode in ['start','benchmark']:
  script=dest/f'{mode}-{profile}.sh';script.write_text(f'#!/usr/bin/env bash\nset -euo pipefail\nexec "{py}" "{lab}" {mode} --variant "{a.name}" --profile "{profile}" "$@"\n');script.chmod(0o755)
stop=dest/'stop.sh';stop.write_text(f'#!/usr/bin/env bash\nset -euo pipefail\nexec "{py}" "{lab}" stop --variant "{a.name}" "$@"\n');stop.chmod(0o755)
rep=dest/'reproduce.sh';rep.write_text('#!/usr/bin/env bash\nset -euo pipefail\n'+f'"{dest}/benchmark-32k.sh" "$@"\n"{dest}/benchmark-128k.sh" "$@"\n');rep.chmod(0o755)
(dest/'README.md').write_text(f'# {a.name}\n\nFrozen source: `{head}`; binary: `{exe}`. Configs are printed and hashes verified at every startup. No rebuild/update during launch. Uses saved IQ3_S files and fixed K=25 / PCIe 0.28.\n\n```bash\n{dest}/start-32k.sh --port 18132\n{dest}/start-128k.sh --port 18132\n{dest}/stop.sh\n{dest}/benchmark-32k.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction\n{dest}/benchmark-128k.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction\n{dest}/reproduce.sh --experiment YOUR_NEW_EXPERIMENT --attempt v1 --reproduction\n```\n\nUse one server at a time. The original normal user launchers are unchanged. A benchmark refuses to overwrite an existing attempt. Fresh research launches obey the absolute deadline. The explicit --reproduction flag is only permitted after that deadline for a later user replay; it does not extend the active campaign. Diagnostic variants are not headline speed builds.\n')
print(a.name,head,flush=True)
