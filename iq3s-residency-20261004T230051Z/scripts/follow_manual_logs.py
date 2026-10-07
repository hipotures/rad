"""Display a running manual server's logs without restarting or signalling it."""
import argparse
import os
import pathlib
from lab import ROOT, load

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--variant', default='p1-baseline')
args = parser.parse_args()
record = load(ROOT/'variants'/args.variant/'owned-process.json')
logs = pathlib.Path(record['attempt'])/'logs'
paths = [logs/'server.log', logs/'engine.log']
if not all(path.is_file() for path in paths):
    parser.error('Both saved log files must exist: '+str(logs))
print('Following logs from '+str(logs)+'; Ctrl-C stops only this viewer.', flush=True)
os.execvp('tail', ['tail', '-n', '20', '-f', '--sleep-interval=0.2', *map(str, paths)])
