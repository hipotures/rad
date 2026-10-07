"""Max-predecessor DAG; waits constrain readiness and never duplicate producer work."""
def span(nodes, reduced=None):
 reduced=reduced or {};end={}
 for name,duration,parents in nodes:
  if any(p not in end for p in parents):raise ValueError('Missing/topologically invalid edge')
  if duration<0:raise ValueError('Negative required duration')
  end[name]=max([end[p] for p in parents] or [0])+max(0,duration-reduced.get(name,0))
 return max(end.values(),default=0),end

def union_length(intervals):
 merged=[]
 for a,b in sorted(intervals):
  if b<a:raise ValueError('Reversed interval')
  if merged and a<=merged[-1][1]:merged[-1]=(merged[-1][0],max(merged[-1][1],b))
  else:merged.append((a,b))
 return sum(b-a for a,b in merged)

def conservative_counterfactual_bound(removed, decode_s, missing_edges=True):
 # Any fixed-trace longest-path shortening is bounded by the sum of removed node durations.
 # This remains valid when unsupported competing dependencies force the lower bound to zero.
 return [0.0, min(1.0,sum(max(0,x) for x in removed)/(decode_s*1e9))]
