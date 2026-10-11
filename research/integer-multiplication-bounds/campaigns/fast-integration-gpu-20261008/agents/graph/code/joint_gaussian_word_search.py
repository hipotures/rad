#!/usr/bin/env python3
"""Distinct physical joint words from desired/carry/completion basis orders.

Pinned joint compiler: eumemic PR57/PR62, Apache-2.0, OpenAI Codex assisted.
Pinned scalar interval producer: Avi Eisenberg PR62, Anthropic assisted.
Changes only formal Gaussian desired-output ordering, preserved-input row
ordering, carry/output phase ordering and unit completion choices. Every
formal carrier remains separate, and every resulting word receives a full
independent source/terminal/address/dirty replay before matrix profiling.
Pivot-only changes are excluded because they leave the typed trajectory
unchanged. Region builder is the exact retained original-E budget map.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor,wait,FIRST_COMPLETED
from datetime import datetime,timezone
import gzip
from hashlib import sha256
import inspect,json
from pathlib import Path
import sys,time
import joint_region_search_v3 as region
from joint_word_check_v4 import check
WORK=None


def initialize(source,work):
    global WORK
    WORK=Path(work);region.initialize(source,work)


def row_order(outvalues,block,uses,blocks,policy):
    values=list(outvalues)
    if policy=='reverse':return list(reversed(values))
    if policy=='formal-sparsity':return sorted(values,key=lambda x:(block['coeff'][x].bit_count(),x))
    count={x:0 for x in values};future={x:0 for x in values}
    for u in block['uses']:
        x,g,target=uses[u]
        if x in count:count[x]+=1;future[x]=max(future[x],blocks[g]['rank']if target is None else max(b['rank']for b in blocks))
    if policy=='fanout':return sorted(values,key=lambda x:(-count[x],x))
    if policy=='future-high':return sorted(values,key=lambda x:(-future[x],block['coeff'][x].bit_count(),x))
    return values


def carry_order(selected,edges,uses,blocks,policy):
    if policy=='reverse':return sorted(selected,reverse=True)
    if policy=='future-high':return sorted(selected,key=lambda e:(-blocks[uses[edges[e][1]][1]]['rank'],edges[e][2],e))
    return sorted(selected)


def evaluate(config):
    start=time.monotonic();case='-'.join(str(config[k])for k in('h','budget','outputs','carries','phase','units','reclaim'));target=WORK/'raw'/case;target.mkdir(parents=True,exist_ok=False)
    original=region.COMPILER.build
    try:
        builder=dict(h=config['h'],policy='rank-first'if config['budget']else'baseline',rank_delta=1,sweeps=1,limit=config['budget']);region.COMPILER.build=lambda h:region.build_regions(h,builder)
        function=inspect.getsource(region.COMPILER.compile_)
        first=function.index('   rows=[];labels=[];echelon=[]\n');last=function.index('   for i in range(len(ins)):',first)
        replacement='''   rows=[];labels=[];echelon=[]
   entries=[]
   output_entries=[('value',x,b['coeff'][x])for x in row_order(outvalues,b,uses,blocks,output_policy)]
   carry_entries=[('carry',edges[e][1],1<<edges[e][2])for e in carry_order(b['selected'],edges,uses,blocks,carry_policy)]
   entries=(carry_entries+output_entries)if carry_first else(output_entries+carry_entries)
   for kind,key,r in entries:
    if kind=='carry':assert independent(echelon,r)
    if independent(echelon,r):rows.append(r);labels.append((kind,key));echelon=basis(rows)
   output_rank=sum(kind=='value'for kind,key in labels)
   assert output_rank==len(b['outbasis'])
'''
        function=function[:first]+replacement+function[last:]
        assert function.count('   for i in range(len(ins)):')==1
        function=function.replace('   for i in range(len(ins)):','   for i in (reversed(range(len(ins)))if reverse_units else range(len(ins))):')
        assert function.count('for s in sorted(retired):')==1
        key={'original':'s','same-frame':"(frames[s]!=g,-blocks[frames[s]]['rank'],s)",'highest-rank':"(-blocks[frames[s]]['rank'],s)"}[config['reclaim']]
        function=function.replace('for s in sorted(retired):','for s in sorted(retired,key=lambda s:'+key+'):')
        function=function.replace('baseline_pr48_roles={23:36432,25:48329}[h]','baseline_pr48_roles={23:36432,25:48329}.get(h)')
        namespace=dict(region.COMPILER.__dict__);namespace.update(row_order=row_order,carry_order=carry_order,output_policy=config['outputs'],carry_policy=config['carries'],carry_first=config['phase']=='carry-first',reverse_units=config['units']=='reverse')
        exec(compile(function,'<task-owned-Gaussian-basis-order>','exec'),namespace)
        compiled,word=namespace['compile_'](config['h'],matching=True,reclaim=True,dirty=True);region.COMPILER.build=original
        raw=(json.dumps(word,separators=(',',':'))+'\n').encode();path=target/'word.json.gz'
        with path.open('wb')as stream:
            with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0)as out:out.write(raw)
        independent=check(path,target/'transitions.bin')
        result=dict(status='actual Gaussian/carry/completion word full source/dirty/address PASS',case_id=case,configuration=config,compiled=compiled,independent=independent,word_path=str(path),word_sha256=sha256(raw).hexdigest(),source_revision='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',seconds=time.monotonic()-start)
    except Exception as error:
        region.COMPILER.build=original;result=dict(status='failed',case_id=case,configuration=config,error=repr(error),seconds=time.monotonic()-start)
    result['source_sha256']=sha256(Path(__file__).read_bytes()).hexdigest();result['completed_utc']=datetime.now(timezone.utc).isoformat();(target/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(case_id=case,status=result['status'],R=result.get('compiled',{}).get('roles'),error=result.get('error'),seconds=result['seconds'])),flush=True)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--workers',type=int,default=6);p.add_argument('--dimensions',nargs='+',type=int,default=[23,25]);p.add_argument('--budgets',nargs='+',type=int,default=[4096]);p.add_argument('--small',action='store_true');p.add_argument('--previous-output',type=Path);p.add_argument('--previous-total',type=int,default=240)
    a=p.parse_args();assert not a.work.exists()and not a.output.exists();a.work.mkdir(parents=True)
    if a.small:
        configs=[dict(h=10,budget=0,outputs=o,carries=c,phase=p,units=u,reclaim=r)for o,c,p,u,r in [('reverse','reverse','carry-first','reverse','same-frame'),('formal-sparsity','future-high','output-first','forward','highest-rank'),('fanout','ordered','carry-first','reverse','original')]]
    else:
        configs=[dict(h=h,budget=budget,outputs=o,carries=c,phase=phase,units=unit,reclaim=reclaim)for budget in a.budgets for h in a.dimensions for o in('reverse','formal-sparsity','fanout','future-high')for c in('ordered','reverse','future-high')for phase in('output-first','carry-first')for unit in('forward','reverse')for reclaim in('original','same-frame','highest-rank')]
    pending=list(configs);active={};result=dict(status='running',command=sys.argv,configurations=configs,rows=[])
    with ProcessPoolExecutor(max_workers=a.workers,initializer=initialize,initargs=(a.source,a.work))as pool:
        while pending or active:
            remaining=max(0,a.previous_total-len(json.loads(a.previous_output.read_text())['rows']))if a.previous_output else 0;cap=a.workers-min(a.workers,remaining)
            while pending and len(active)<cap:
                config=pending.pop(0);active[pool.submit(evaluate,config)]=config
            done,_=wait(active,timeout=.5,return_when=FIRST_COMPLETED)if active else(set(),set())
            if not active:time.sleep(.2)
            for future in done:
                active.pop(future);row=future.result();result['rows'].append({k:v for k,v in row.items()if k!='independent'});tmp=a.output.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');tmp.replace(a.output)
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat());a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
