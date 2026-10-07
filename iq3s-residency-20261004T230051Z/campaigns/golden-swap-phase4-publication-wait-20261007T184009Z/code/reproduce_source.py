"""Reconstruct tracked runtime source from obtainable base plus cumulative patch."""
import argparse,json,subprocess
from pathlib import Path
C=Path(__file__).resolve().parents[1]
BASE='6f32ec070f23ced9f50e704d854d775da52591ab'
def main():
    q=argparse.ArgumentParser();q.add_argument('--clone-source',required=True);q.add_argument('--output',required=True,type=Path);a=q.parse_args();assert not a.output.exists()
    assert not a.output.resolve().is_relative_to(C.parents[2]),'Dependency checkout must be external'
    subprocess.run(['git','clone','--no-checkout',a.clone_source,str(a.output)],check=True,timeout=180)
    def git(*args):return subprocess.check_output(['git',*args],cwd=a.output,text=True,timeout=60).strip()
    git('checkout','--detach',BASE);git('apply','--index',str(C/'patches/cumulative-from-original.diff'))
    tree=git('write-tree');expected=json.loads((C/'configs/runtime-recovery.json').read_text())['tracked_tree_sha'];assert tree==expected,(tree,expected)
    print(json.dumps({'state':'PASS','base':BASE,'reconstructed_tree':tree,'matches_final_derivative_tree':True,'compiled':False}))
if __name__=='__main__':main()
