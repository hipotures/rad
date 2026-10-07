"""Keep v1 buffered diagnostics and restore the independent host PLE fence."""
import pathlib,subprocess,sys
r=pathlib.Path(__file__).resolve().parents[1];s=pathlib.Path(sys.argv[1])
subprocess.run([sys.executable,str(r/'scripts/patch_device_plan_diagnostics.py'),str(s)],check=True)
p=s/'src/core/verify.cpp';t=p.read_text();old='                if (all_resident_) wait_flag_ge(m_flag_, 1, cs);'
assert t.count(old)==1
p.write_text(t.replace(old,'                // Host PLE readiness is independent of whether layer0 routed experts are local.\n                if (all_resident_ || device_plan_ids_) wait_flag_ge(m_flag_, 1, cs);'))
