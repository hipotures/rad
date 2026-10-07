"""Bounded reconstruction check from pinned obtainable base plus cumulative patch."""
import subprocess,hashlib,datetime
from common import *
if __name__=='__main__':
 no_gpu();identity=load(C/'configs/runtime-identity.json');base='6f32ec070f23ced9f50e704d854d775da52591ab';patch=C/'patches/cumulative-from-original.diff';patch.write_bytes(subprocess.check_output(['git','diff','--binary',base,identity['source_sha']],cwd=SOURCE));dest=W/'repos/source-recovery-check';assert not dest.exists()
 subprocess.run(['git','worktree','add','--detach',str(dest),base],cwd=SOURCE,check=True,timeout=60)
 subprocess.run(['git','apply','--check',str(patch)],cwd=dest,check=True,timeout=30);subprocess.run(['git','apply',str(patch)],cwd=dest,check=True,timeout=30)
 paths=subprocess.check_output(['git','diff','--name-only',base,identity['source_sha']],cwd=SOURCE,text=True).splitlines();subprocess.run(['git','add','--',*paths],cwd=dest,check=True,timeout=30);tree=subprocess.check_output(['git','write-tree'],cwd=dest,text=True).strip();expected=subprocess.check_output(['git','rev-parse',identity['source_sha']+'^{tree}'],cwd=SOURCE,text=True).strip();assert tree==expected,'Full reconstructed tree differs'
 result={'state':'PASS','obtainable_base':base,'upstream':'https://github.com/Niko1221/Strata','derivative_source_sha':identity['source_sha'],'derivative_tree':expected,'reconstructed_tree':tree,'patch':'patches/cumulative-from-original.diff','patch_sha256':hashlib.sha256(patch.read_bytes()).hexdigest(),'patch_bytes':patch.stat().st_size,'changed_paths':paths,'namespace':str(dest),'tested':'Apply-check plus full application and entire staged Git tree equality; no rebuild/rebenchmark in this check'};save(C/'tests/source-recovery.json',result);print('SOURCE_RECOVERY_PASS',tree,flush=True)
