"""Retain v1 snapshots and add a controlled host-PLE delay to expose its race."""
import pathlib,subprocess,sys
r=pathlib.Path(__file__).resolve().parents[1];s=pathlib.Path(sys.argv[1])
subprocess.run([sys.executable,str(r/'scripts/patch_plan_compare.py'),str(s)],check=True)
p=s/'src/core/verify.cpp';t=p.read_text()
old='        if (k == 0 && do_ple) {\n            const Clock::time_point tp = Clock::now();'
new='''        if (k == 0 && do_ple) {
            // Diagnostic only: identical finite producer delay for all three fence modes.
            if(strata::research::plan_compare.enabled) std::this_thread::sleep_for(std::chrono::milliseconds(5));
            const Clock::time_point tp = Clock::now();'''
assert t.count(old)==1
t=t.replace(old,new);t=t.replace('#include "strata/research/lab_plan_compare.hpp"','#include "strata/research/lab_plan_compare.hpp"\n#include <thread>')
p.write_text(t)
