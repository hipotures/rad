"""Trace stable actual routed IDs plus one unchanged-input head for E016."""
import pathlib
import subprocess
import sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
source = pathlib.Path(sys.argv[1])
subprocess.run([sys.executable, str(ROOT / 'scripts/patch_diagnostics.py'), str(source)], check=True)
subprocess.run([sys.executable, str(ROOT / 'scripts/patch_device_plan_ids.py'), str(source)], check=True)
path = source / 'src/program/generate.cpp'
text = path.read_text()
old = '                int a = 0;\n                while (a < T - 1 && window[(size_t) a + 1] == outv[(size_t) a]) ++a;'
new = '''                if (first_window && strata::research::trace.enabled) {
                    std::vector<float> lab_logits((size_t)ver.vocab());
                    if (!ver.copy_logits(0, lab_logits.data())) { std::printf("ERR lab first logits copy failed\\n"); return 1; }
                    strata::research::trace.file(strata::research::trace.prefix + "-request" + std::to_string(strata::research::trace.request) + "-first-logits.bin", lab_logits);
                }
''' + old
assert text.count(old) == 1
path.write_text(text.replace(old, new))
print('Applied buffered demand/head diagnostics; no stale shared activation capture', flush=True)
