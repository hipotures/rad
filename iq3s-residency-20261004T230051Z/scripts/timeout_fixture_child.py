"""Owned detached sleeper only: exercises run_logged cleanup without model/GPU work."""
import pathlib,subprocess,sys,time
import psutil
from lab import save
child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(40)'],start_new_session=True)
save(pathlib.Path(sys.argv[1]),{'pid':child.pid,'create_time':psutil.Process(child.pid).create_time()})
time.sleep(40)
