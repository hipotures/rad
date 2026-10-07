"""Isolated protocol repair: prove equivalent initial KV/GDN/PLE/MTP state, not just expert slots."""
from pathlib import Path
import subprocess
C=Path(__file__).resolve().parents[1];s=C/'src/oracle-v3'
if not s.exists():subprocess.run(['git','clone','--no-hardlinks',str(C/'src/oracle-v2'),str(s)],check=True,timeout=60)
if not(s/'.venv').exists():(s/'.venv').symlink_to(C.parents[1]/'src/control/.venv',target_is_directory=True)
(s/'include/strata/research/q4_state.hpp').write_text((C/'scripts/state_header.txt').read_text());p=s/'src/program/generate.cpp';t=p.read_text();t='#include "strata/research/q4_state.hpp"\n'+t;a='strata::research::q4_tape.begin(ids,max_new,host_res.data(),drive.d.usage.data(),rounds);';assert t.count(a)==1;t=t.replace(a,a+'strata::research::q4_state.begin(ss,stages[0]->ss,mtp.kv_state(),g,n);');p.write_text(t);print('PATCH_STATE_V3',s,flush=True)
