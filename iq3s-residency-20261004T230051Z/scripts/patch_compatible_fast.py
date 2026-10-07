"""Retain exact compatible-v1 matching and runtime backend; optimize cold-candidate representation."""
import pathlib,shutil,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];src=pathlib.Path(sys.argv[1])
subprocess.run([sys.executable,str(ROOT/'scripts/patch_compatible.py'),str(src)],check=True)
shutil.copy2(ROOT/'scripts/templates/compatible_policy_fast.hpp',src/'include/strata/research/compatible_policy.hpp')
print('Compatible matching unchanged in intent; exact causal equivalence must pass before runtime',flush=True)
