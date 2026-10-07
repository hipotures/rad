import subprocess,time
from common import *
no_gpu()
with Heartbeat('offline C++ build',2):
 for stem,source in [('offline',C/'scripts/offline.cpp'),('scorer-fixture',C/'tests/scorer_fixture.cpp'),('history-fixture',C/'tests/history_fixture.cpp'),('policy-fixture',C/'tests/policy_fixture.cpp'),('information-fixture',C/'tests/information_fixture.cpp')]:
  cmd=['g++','-O3','-std=c++20','-pthread','-I'+str(C/'source/runtime/include'),'-I/usr/local/cuda/include',str(source),'-L/usr/local/cuda/lib64','-Wl,-rpath,/usr/local/cuda/lib64','-lcudart','-o',str(C/'builds'/stem)];ledger('Compile '+stem,command=cmd);subprocess.run(cmd,check=True,timeout=120)
