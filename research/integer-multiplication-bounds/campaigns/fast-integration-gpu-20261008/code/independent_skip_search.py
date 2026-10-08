#!/usr/bin/env python3
"""Independent skip-prefix strip integration on the pinned PR36 generator.

Skip-prefix identity: Avi Eisenberg / ikeboy, with Anthropic Claude assistance,
public PR53 body at https://github.com/CrocSwap/integer-mult-bounds/pull/53,
head3ffd4021995c959ac02d12920e0279ae97dd03c7. No PR53/54 implementation or
held derivative source is used. Existing generator: icekylinx PR36, Apache2,
and the retained earlier exclusion-circuit credits. This implementation and
joint producer/positive-frame experiments are RaD GPU campaign work.
"""
import argparse,json,multiprocessing,sys,time
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path

def evaluate(config):
    from partial_swap.paired import PairedExclusionCircuit
    from exclusion_circuit import ExclusionCircuit
    from point_order_search import evaluate as producer
    original=PairedExclusionCircuit.vector
    def vector(self,values,two=True):
        if two:return ExclusionCircuit.vector(self,values,two)
        n=len(values);policy=config['vector_policy'];order=list(range(n))
        if policy=='reverse-all' or n==config['h']//2:order.reverse()
        elif policy=='top-reverse-support-left':
            order.sort(key=lambda i:(self.support[values[i]].bit_count(),self.support[values[i]]))
        elif policy=='top-reverse-support-right':
            order.sort(key=lambda i:(self.support[values[i]].bit_count(),-self.support[values[i]]))
        vals=[values[i]for i in order];prefix=[0]
        for x in vals:prefix.append(self.add(prefix[-1],x))
        suffix=[0]*(n+1)
        for i in range(n-1,-1,-1):suffix[i]=self.add(vals[i],suffix[i+1])
        outputs=[]
        for j in range(n):
            outputs.append(suffix[1] if j==0 else self.add(prefix[j-1],self.add(vals[j-1],suffix[j+1])))
        restored=[0]*n
        for j,i in enumerate(order):restored[i]=outputs[j]
        for i,node in enumerate(restored):
            expected=0
            for j,x in enumerate(values):
                if i!=j:expected|=self.support[x]
            assert self.support[node]==expected
        return prefix[-1],restored,{}
    PairedExclusionCircuit.vector=vector
    try:return producer(config)
    finally:PairedExclusionCircuit.vector=original

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True);p.add_argument('--code',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True);p.add_argument('--workers',type=int,required=True)
    p.add_argument('--cached-builds',type=Path,required=True)
    p.add_argument('--dimensions',type=int,nargs='+',default=[10,23,25])
    p.add_argument('--thresholds',type=int,nargs='+',default=[2])
    p.add_argument('--seed',type=int,default=1300000033)
    p.add_argument('--config-file',type=Path,
                   help='Replay an explicit frozen configuration list instead of the discovery grid.')
    a=p.parse_args();assert not a.work.exists();a.work.mkdir(parents=True)
    sys.path.insert(0,str(a.code));from producer_search import initialize
    import shutil
    builds=a.work/'builds';builds.mkdir()
    for name in ['moment_match_positive','match_exported_dag']:
        shutil.copy2(a.cached_builds/name,builds/name)
    configs=[]
    for h in a.dimensions:
      for threshold in a.thresholds:
        for tree in ['left','support-left','support-right','seeded-left']:
            for vp in ['reverse-all','top-reverse-support-left','top-reverse-support-right']:
                for pp in ['common-rotate','alternating-reverse','paired-rotate']:
                    for mode in [2,4]:
                        if h==10 and (tree!='left' or pp!='common-rotate' or mode!=2):continue
                        configs.append(dict(h=h,threshold=threshold,grouping='pairs',tree=tree,mode=mode,
                            seed=a.seed+104729*len(configs),point_policy=pp,vector_policy=vp))
    if a.config_file:
        frozen=json.loads(a.config_file.read_text())
        configs=frozen['configurations'] if isinstance(frozen,dict) else frozen
        assert configs and all(set(c)=={'h','threshold','grouping','tree','mode','seed','point_policy','vector_policy'} for c in configs)
        assert all(c['grouping']=='pairs' and c['vector_policy'] in ['reverse-all','top-reverse-support-left','top-reverse-support-right'] for c in configs)
    result=dict(status='running',started_utc=datetime.now(timezone.utc).isoformat(),command=sys.argv,
        source_revision='11817ccacb564bb7f98789c20dc11d3fece207e3',
        borrowed_public_identity='PR53 skip-prefix strips only; no held implementation/source',
        authored_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        configurations=configs,workers=a.workers,rows=[])
    if a.config_file:
        result['frozen_configuration_input']=dict(path=str(a.config_file),sha256=sha256(a.config_file.read_bytes()).hexdigest())
    (a.work/'protocol.json').write_text(json.dumps({k:v for k,v in result.items()if k!='rows'},indent=2)+'\n')
    with ProcessPoolExecutor(max_workers=a.workers,mp_context=multiprocessing.get_context('fork'),
         initializer=initialize,initargs=(a.source,a.work,builds/'moment_match_positive'))as pool:
        futures=[pool.submit(evaluate,c)for c in configs]
        for future in as_completed(futures):
            row=future.result();result['rows'].append(row)
            (a.work/'results.json').write_text(json.dumps(result,indent=2)+'\n')
            print(json.dumps({k:row.get(k)for k in ['case_id','h','R','matched','status','seconds','pid','error']}),flush=True)
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat())
    (a.work/'results.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
