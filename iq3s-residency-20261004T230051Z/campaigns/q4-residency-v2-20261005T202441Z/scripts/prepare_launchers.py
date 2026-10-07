"""Preserve separate runnable variants without changing normal user launchers."""
from campaign import C,R,load,save
import os

def main():
    for variant in ['control','history-v2','early-v1']:
        path=C/'launchers'/variant;path.mkdir(parents=True,exist_ok=True)
        for profile in ['32k','128k','256k']:
            cfg=load(C/'configs'/f'{variant}-{profile}.json');save(path/f'{profile}.json',cfg)
            script=path/f'start-{profile}.sh'
            script.write_text('#!/usr/bin/env bash\nset -euo pipefail\nexec "'+str(R/'src/control/.venv/bin/python')+'" "'+str(C/'scripts/launch.py')+'" start --variant '+variant+' --profile '+profile+' "$@"\n');script.chmod(0o755)
        for name,action in [('stop.sh','stop'),('reproduce.sh','reproduce')]:
            script=path/name;script.write_text('#!/usr/bin/env bash\nset -euo pipefail\nexec "'+str(R/'src/control/.venv/bin/python')+'" "'+str(C/'scripts/launch.py')+'" '+action+' --variant '+variant+' "$@"\n');script.chmod(0o755)
        description={'control':'Unchanged frozen Q4/100us baseline; no experimental residency algorithm.',
            'history-v2':'Experimental joint history/copy-cost selector; existing safe end-of-window cache-copy machinery. Not selected for user use unless final report supports it.',
            'early-v1':'Experimental H4 native-router + CPU-only frozen linear ranking, dedicated persistent staging worker and guarded target publication. Charges one existing3.072MB physical spare/device; possible output/MTP divergence. Not a universal improvement.'}[variant]
        (path/'README.md').write_text('# '+variant+'\n\n'+description+'\n\nDefault bind127.0.0.1, port8080. Settings frozen: Q4, K24, PCIe0.28, workers15, pool100us, spec4/minp0.5, INT8, kv-resident32768 where runtime permits, prefillauto, lookup/reuse0.\n\n```bash\n./start-32k.sh\n./start-128k.sh --host 0.0.0.0 --port 8080\n./start-256k.sh\n./stop.sh\n./reproduce.sh --profile 128k --port 18140\n```\n\nStart runs in foreground and streams engine/frontend logs; Ctrl-C stops owned processes. `--check` verifies frozen identities/config without inference; `--smoke` actually starts and generates the fixed64-output saved warmup, then stops. Reproduction is refused during the active research campaign. After completion it uses three fresh servers, each with the identical fixed warmup and one measured request, matching the primary protocol. No auto build/update/download. Colliding GPU/port/Strata processes cause a visible failure. Monitor snapshots are preserved under manual/<variant>/<profile>-<timestamp>/telemetry/ui-monitor/.\n\nSource/binary identities and exact command are in each profile JSON. Large weights retain previous verified hashes with current size/mtime checks; small pack/profile/tokenizer files are rehashed. Existing main model weights/normal user launchers are untouched. See ../../report.md for correctness and negative performance limitations.\n')
    print('PREPARED3_SEPARATE_LAUNCHER_VARIANTS')

if __name__=='__main__':main()
