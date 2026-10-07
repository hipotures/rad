"""Repair the retained GPU diagnostic's native GEMV call signature only."""
import pathlib
import subprocess
import sys

root = pathlib.Path(__file__).resolve().parents[1]
source = pathlib.Path(sys.argv[1])
subprocess.run([sys.executable, str(root / 'scripts/patch_gpu_router.py'), str(source)], check=True)
path = source / 'include/strata/research/lab_gpu_router.hpp'
text = path.read_text()
old = 'experts, width, width, experts, tokens, stream);'
assert text.count(old) == 1
path.write_text(text.replace(old, 'experts, width, experts, tokens, stream);'))
print('Removed the duplicated input-width argument; no algorithm change', flush=True)
