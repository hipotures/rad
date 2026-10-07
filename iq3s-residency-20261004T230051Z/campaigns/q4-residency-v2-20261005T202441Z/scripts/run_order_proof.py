"""Bounded minimal dependency proof, runs only on idle GPUs after diagnostics."""
from campaign import C,save,guard
from pathlib import Path
import subprocess,time,os

def main():
 guard();out=C/'analysis/async-order-proof';out.mkdir(exist_ok=False)
 cmds=[['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_89','-Xcompiler','-pthread',str(C/'scripts/tests_async_order.cu'),'-o',str(out/'proof')],[str(out/'proof')]]
 for i,cmd in enumerate(cmds):
  t=time.time()
  with (out/f'step{i}.log').open('x') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=180)
  save(out/f'step{i}.json',{'command':cmd,'exit_code':r.returncode,'wall_s':time.time()-t})
  assert not r.returncode,(cmd,(out/f'step{i}.log').read_text())
 print('ORDER_PROOF_PASS',flush=True)
if __name__=='__main__':main()
