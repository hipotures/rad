"""Add buffered diagnostics to the separate direct-row candidate source tree."""
import pathlib, subprocess, sys
root=pathlib.Path(__file__).resolve().parents[1];src=pathlib.Path(sys.argv[1])
for script in ['patch_diagnostics.py','patch_direct_parts.py']:
    subprocess.run([sys.executable,str(root/'scripts'/script),str(src)],check=True)
