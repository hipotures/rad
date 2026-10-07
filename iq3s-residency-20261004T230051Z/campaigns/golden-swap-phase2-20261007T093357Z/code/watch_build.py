import psutil,time
from common import *
while any('build.py' in ' '.join(p.info['cmdline'] or []) and p.pid!=os.getpid() for p in psutil.process_iter(['cmdline'])):
 progress(2,'HEARTBEAT isolated runtime build',version='target-use-v1',completed='Phase1 diagnosis',remaining='smoke, safety, offline, live, audit',next_action='Run first compiled smoke')
 time.sleep(25)
