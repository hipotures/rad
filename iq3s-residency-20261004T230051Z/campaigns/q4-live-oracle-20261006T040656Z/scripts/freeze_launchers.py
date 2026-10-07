"""Create new control-only launchers; never modify prior user launchers."""
from pathlib import Path
C=Path(__file__).resolve().parents[1]
for profile in ['32k','128k','256k']:
 p=C/'launchers/control'/f'start-{profile}.sh';p.write_text('#!/usr/bin/env bash\nset -euo pipefail\nexec '+str(C.parents[1]/'src/control/.venv/bin/python')+' '+str(C/'scripts/normal_control.py')+' start --profile '+profile+' "$@"\n');p.chmod(0o755)
p=C/'launchers/control/stop.sh';p.write_text('#!/usr/bin/env bash\nset -euo pipefail\nexec '+str(C.parents[1]/'src/control/.venv/bin/python')+' '+str(C/'scripts/normal_control.py')+' stop "$@"\n');p.chmod(0o755)
(C/'launchers/control/README.md').write_text('# Unchanged Q4 serving control\n\nFrozen original Strata0.1.39 binary, K24/.28, pool100us,15workers, spec4/.5, INT8, kv-resident32768, prefillauto, suffix/reuseOFF. These scripts never enable tape/oracle, rebuild or change models. They print resolved config and live logs. Default bind0.0.0.0 port8080; --host/--port override. --check validates hashes/provenance without starting a server. Foreground lifetime defaults to12hours and may be set with --timeout-s. stop.sh checks ownedPID/create-time and terminates only this campaign manual process group.\n')
