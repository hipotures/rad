"""Repair the device-plan PLE producer dependency, only in the new opt-in scope."""
import pathlib,subprocess,sys
r=pathlib.Path(__file__).resolve().parents[1];s=pathlib.Path(sys.argv[1])
subprocess.run([sys.executable,str(r/'scripts/patch_device_plan_ids.py'),str(s)],check=True)
p=s/'src/core/verify.cpp';t=p.read_text()
old='                if (all_resident_) wait_flag_ge(m_flag_, 1, cs);'
new='''                // Layer0 may skip expert waits, but host PLE readiness is an independent dependency.
                if (all_resident_ || device_plan_ids_) wait_flag_ge(m_flag_, 1, cs);'''
assert t.count(old)==1;p.write_text(t.replace(old,new))
print('Restored PLE readiness before layer1 for the opt-in device plan; actual model untouched',flush=True)
