"""Parse normal upstream startup logs; configured size is never resolved size."""
import json,re,sys
from pathlib import Path

def parse(path,argument):
 text=Path(path).read_text(errors='replace');events=[];chunk=None if argument.startswith('auto') else int(argument)
 patterns=[r'prompt chunk auto: (\d+) tokens',r'prompt chunk \d+ -> (\d+) tokens',r'free: (\d+)-token chunks',r'trying a (\d+)-token chunk']
 for line in text.splitlines():
  for pattern in patterns:
   m=re.search(pattern,line)
   if m:chunk=int(m[1]);events.append(line)
 loans={}
 for m in re.finditer(r'prompt path borrows (\d+) CUDA0 cache slots \(([\d.]+) GiB\)',text):loans['GPU0']={'slots':int(m[1]),'GiB_rounded':float(m[2])}
 for m in re.finditer(r'CUDA(\d+) prompt path borrows (\d+) of its (\d+) slots \(([\d.]+) GiB\)',text):loans['GPU'+m[1]]={'slots':int(m[2]),'total_slots':int(m[3]),'GiB_rounded':float(m[4])}
 own=[line for line in text.splitlines() if 'own prompt buffers' in line or 'allocates its own buffers' in line]
 return {'configured_prefill':argument,'resolved_chunk_tokens':chunk,'resolution_events':events,'initial_cache_loans':loans,'own_buffer_log_lines':own,'log':str(path),'note':'Loans are startup allocations before possible chunk retry; no invented per-request loan counters. Explicit unchanged chunk derives from argument and absence of upstream step-down log.'}

if __name__=='__main__':
 root=Path(__file__).resolve().parent;rows=[]
 for path in sorted((root/'raw').glob('PREFILL-*-done.json')):
  d=json.loads(path.read_text());cfg=json.loads((root/'configs'/f"{d['candidate']}.json").read_text());arg=cfg['args'][cfg['args'].index('--prefill')+1]
  rows.append(dict(status=d['status'],candidate=d['candidate'],**parse(cfg['log'],arg)))
 (root/'raw/prefill-allocation-evidence.json').write_text(json.dumps(rows,indent=2))
 print(json.dumps(rows,indent=2))
