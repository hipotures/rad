#!/usr/bin/env python3
"""Independent fused PR168 module, graph, matching and carrier reconstruction.

No producer or search Python is imported. Pair modules are finite DAG data;
their exact support contract is checked before instantiation. The coordinate
channels, nested-prefix module and compiler role word are rebuilt here. Exact
row reduction uses this reviewer's separately checked full-pivot algebra.
Inherited source mechanisms retain their original Apache-2.0 attribution.
"""
from collections import Counter,defaultdict
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import time

from binary_exact_algebra import reduce_rows, nullspace, need


def dot(a,b):return sum(x*y for x,y in zip(a,b))


def module_support(module):
    n=module['input_count'];args=module['args'];support=[]
    need(type(n)is int and n>0 and len(args)>=n,'module input domain')
    for node,operands in enumerate(args):
        if node<n:
            need(operands is None,'module source leaves');support.append(1<<node)
        else:
            need(isinstance(operands,list) and len(operands)==2 and
                 all(type(x)is int and 0<=x<node for x in operands),'module chronological operands')
            a,b=operands;need(not support[a]&support[b],'module disjoint integer support')
            support.append(support[a]|support[b])
    need(all(type(x)is int and 0<=x<len(args) for x in module['roots']),'module root indices')
    return support


def verify_pair_module(pair,p):
    supports=module_support(pair);labels=list(combinations(range(p-1),2))
    need(pair['kind']=='pair_disjoint' and pair['n']==p-1 and pair['input_count']==len(labels) and
         pair['input_labels']==[list(x) for x in labels],'pair-disjoint module input labelling')
    need(len(pair['roots'])==len(labels) and all(supports[root]==sum(1<<j for j,other in enumerate(labels)
         if not set(label)&set(other)) for label,root in zip(labels,pair['roots'])),
         'complete integer pair-disjoint module contract')
    return supports


def nested_prefix(n,kind):
    need(n>=3 and kind in ('nested_prefix','reversed_nested_prefix'),'all-but-one construction policy')
    args=[None]*n
    def add(a,b):args.append([a,b]);return len(args)-1
    prefix={1:0}
    for stop in range(1,n-1):prefix[stop+1]=add(prefix[stop],stop)
    suffix={n-1:n-1}
    for start in range(n-2,0,-1):suffix[start]=add(start,suffix[start+1])
    roots=[None]*n;roots[0]=suffix[1];roots[-1]=prefix[n-1];roots[1]=add(0,suffix[2])
    for omitted in range(1,n-2):roots[omitted+1]=add(prefix[omitted],add(omitted,suffix[omitted+2]))
    if kind=='reversed_nested_prefix':
        args=[None if a is None else [n-1-x if x<n else x for x in a] for a in args]
        roots=list(reversed(roots))
    result=dict(input_count=n,args=args,roots=roots);support=module_support(result)
    need(all(support[r]==((1<<n)-1)^(1<<i) for i,r in enumerate(roots)),'all-but-one exact roots')
    return result


class Builder:
    def __init__(self,p):
        self.p=p;self.cubes=list(combinations(range(p),3));self.selectors=list(product(range(2),repeat=3))
        self.labels=[list(2*i+b for i,b in zip(cube,selector)) for cube in self.cubes for selector in self.selectors]
        self.args=[None]*len(self.labels);self.support=[1<<i for i in range(len(self.labels))];self.intern={}
        self.address={(cube,selector):8*j+k for j,cube in enumerate(self.cubes) for k,selector in enumerate(self.selectors)}
        self.faces={};self.edges={};self.roots=[];self.mix=[]
    def add(self,a,b):
        a,b=sorted((a,b));key=(a,b)
        if key not in self.intern:
            need(not self.support[a]&self.support[b],'rebuilt graph disjoint integer addition')
            self.intern[key]=len(self.args);self.args.append([a,b]);self.support.append(self.support[a]|self.support[b])
        return self.intern[key]
    def balanced_sum(self,values):
        values=list(values)
        while len(values)>1:values=[self.add(values[i],values[i+1]) if i+1<len(values) else values[i] for i in range(0,len(values),2)]
        need(values,'nonempty balanced center');return values[0]
    def instantiate(self,module,inputs):
        need(len(inputs)==module['input_count'],'module instantiation arity');image=list(inputs)
        for a,b in module['args'][module['input_count']:]:image.append(self.add(image[a],image[b]))
        return [image[r] for r in module['roots']]
    def build(self,pair,allbut):
        for cube in self.cubes:
            edge={}
            for i,j in combinations(range(3),2):
                free=3-i-j
                for a,b in product(range(2),repeat=2):
                    lo=[0]*3;lo[i]=a;lo[j]=b;hi=lo.copy();hi[free]=1
                    edge[i,j,a,b]=self.add(self.address[cube,tuple(lo)],self.address[cube,tuple(hi)])
                self.edges[cube,cube[i],cube[j],0]=self.add(edge[i,j,0,0],edge[i,j,1,1])
                self.edges[cube,cube[i],cube[j],1]=self.add(edge[i,j,0,1],edge[i,j,1,0])
            for i in range(3):
                j=next(x for x in range(3) if x!=i)
                for a in range(2):
                    ports=[edge[(i,j,a,b) if i<j else (j,i,b,a)] for b in range(2)]
                    self.faces[cube,cube[i],a]=self.add(*ports)
        P,Q={},{}
        for i in range(self.p):
            opposite=list(combinations([x for x in range(self.p) if x!=i],2))
            for bit in range(2):
                values=[self.faces[tuple(sorted((i,*K))),i,bit] for K in opposite]
                for K,node in zip(opposite,self.instantiate(pair,values)):P[tuple(sorted((i,*K))),i,bit]=node
        for i,j in combinations(range(self.p),2):
            others=[x for x in range(self.p) if x not in (i,j)]
            for mode in range(2):
                values=[self.edges[tuple(sorted((i,j,k))),i,j,mode] for k in others]
                for k,node in zip(others,self.instantiate(allbut,values)):Q[tuple(sorted((i,j,k))),i,j,mode]=node
        def emit(cube,selectors,node,channel):
            self.roots.append(dict(node=node,targets=[self.address[cube,s] for s in selectors],kind='side',channel=channel,coefficient=1))
        for cube in self.cubes:
            for a in range(2):emit(cube,[s for s in self.selectors if s[0]==a],P[cube,cube[0],a],'face0')
            for a in range(2):
                for parity in range(2):emit(cube,[s for s in self.selectors if s[0]==a and s[1]^s[2]==parity],Q[cube,cube[1],cube[2],1-parity],'edge12')
            for s in self.selectors:
                emit(cube,[s],P[cube,cube[1],s[1]],'face1')
                emit(cube,[s],Q[cube,cube[0],cube[1],1-(s[0]^s[1])],'edge01')
                emit(cube,[s],P[cube,cube[2],s[2]],'face2')
                emit(cube,[s],Q[cube,cube[0],cube[2],1-(s[0]^s[2])],'edge02')
                emit(cube,[s],self.address[cube,(s[0],1-s[1],1-s[2])],'partner')
            for parity in range(2):
                for first in range(2):
                    source=sorted(s for s in self.selectors if sum(s)%2==parity and s[0]==first)
                    target=sorted(s for s in self.selectors if sum(s)%2==parity and s[0]!=first)
                    self.mix.append(dict(carrier=self.address[cube,source[0]],passive=self.address[cube,source[1]],receivers=[self.address[cube,s] for s in target]))
        for coordinate in range(2*self.p):
            i,bit=divmod(coordinate,2)
            node=self.balanced_sum(self.faces[cube,i,bit] for cube in self.cubes if i in cube)
            self.roots.append(dict(node=node,targets=[t for t,label in enumerate(self.labels) if coordinate in label],kind='center',coordinate=coordinate,coefficient=1))
        return dict(p=self.p,h=2*self.p,v=len(self.labels),labels=self.labels,args=self.args,roots=self.roots,partner_mix=self.mix)


def verify_compiler(g,w,nf,root_frames,threshold):
    start=time.monotonic();h,v,args=g['h'],g['v'],g['args'];nodes=len(args)
    def join(rows):return reduce_rows(tuple(row for group in rows for row in group),h)
    def sub(a,b):return len(a)<=len(b) and all(dot(x,y)==0 for x in a for y in nullspace(b,h))
    labels=g['labels'];chi=[tuple(int(i in lab) for i in range(h)) for lab in labels]
    support=[1<<i for i in range(v)]+[0]*(nodes-v);spans=[(row,) for row in chi]+[()]*(nodes-v)
    for x in range(v,nodes):
        a,b=args[x];support[x]=support[a]|support[b];spans[x]=join((spans[a],spans[b]))
    root_ann=[]
    for root in g['roots']:
        root_ann.append(nullspace(spans[root['node']],h) if root['kind']=='center' else
                        join(((tuple(3*int(i in labels[t])-1 for i in range(h)),) for t in root['targets'])))
    need(all(tuple(a)==frame.A for a,frame in zip(root_ann,root_frames)),'rebuilt exact root frames')
    successor=defaultdict(list);direct=defaultdict(list)
    for x in range(v,nodes):
        for operand in args[x]:successor[operand].append(x)
    for j,root in enumerate(g['roots']):direct[root['node']].append(root_ann[j])
    preann=[()]*nodes;initial=[()]*nodes
    for x in reversed(range(nodes)):
        preann[x]=join(direct[x]+[preann[y] for y in successor[x]])
        cover=0
        bits=support[x]
        while bits:
            bit=bits&-bits;bits^=bit
            for coordinate in labels[bit.bit_length()-1]:cover|=1<<coordinate
        padded=[tuple(int(j==i) for j in range(h)) for i in range(h) if not cover>>i&1]
        initial[x]=join([preann[x],padded])
    order=sorted(range(nodes),key=lambda x:(h-len(initial[x]),x));position={x:j for j,x in enumerate(order)}
    need(order==w['order'],'coordinate-padded initial compiler order')
    uses=defaultdict(list);codes=[];values=[];targets=[];useann=[]
    for x in order:
        if args[x] is not None:
            for port,operand in enumerate(args[x]):
                uses[operand].append(len(codes));codes.append(('op',x,port));values.append(operand);targets.append(x);useann.append(initial[x])
    for j,root in enumerate(g['roots']):
        uses[root['node']].append(len(codes));codes.append(('root',j));values.append(root['node']);targets.append(nodes+j);useann.append(root_ann[j])
    code_index={code:i for i,code in enumerate(codes)};arcs={}
    for donor,code in w['arcs']:
        need(type(donor)is int and v<=donor<nodes and donor not in arcs and tuple(code) in code_index,'matching arc domain')
        u=code_index[tuple(code)];target=targets[u]
        need(values[u] in args[donor] and (target>=nodes or position[target]>position[donor]),'matching carrier chronology')
        need(sub(useann[u],initial[donor]),'matching coordinate frame compatibility')
        arcs[donor]=u
    need(len(set(arcs.values()))==len(arcs),'one matching recipient per donor')
    successor2={x:list(successor[x]) for x in range(nodes)};direct2={x:list(direct[x]) for x in range(nodes)}
    for donor,u in arcs.items():
        target=targets[u]
        if target<nodes:successor2[donor].append(target)
        else:direct2[donor].append(root_ann[target-nodes])
    ann=[()]*nodes
    for x in reversed(order):ann[x]=join(direct2[x]+[ann[y] for y in successor2[x]])
    plain=set(range(v))
    for x in range(v,nodes):
        if len(spans[x])<=threshold and all(y in plain for y in args[x]):plain.add(x)
    incoming=defaultdict(list)
    for donor,u in arcs.items():
        if targets[u]<nodes:incoming[targets[u]].append(donor)
    changed=True
    while changed:
        changed=False
        for target in sorted(plain):
            if any(donor not in plain or not sub(spans[donor],spans[target]) for donor in incoming[target]):
                plain.remove(target);changed=True;stack=[target]
                while stack:
                    x=stack.pop()
                    for y in successor[x]:
                        if y in plain:plain.remove(y);stack.append(y)
    need(sorted(plain)==w['plain'],'plain-frame operand and donor closure')
    for x in plain:ann[x]=nullspace(spans[x],h)
    need(all(ann[x]==nf[x].A for x in range(nodes)),'every exact node frame from spliced matching and plain rule')
    # Rebuild the entire scalar carrier word from use assignments. Source
    # rows are created only once; all extra uses become explicit copies.
    incoming_uses=set(arcs.values());assignment={};sources={};ops=[];R=0
    for x in order:
        if args[x] is not None:
            a,b=args[x];dest=assignment[code_index['op',x,0]];control=assignment[code_index['op',x,1]]
            if x in arcs:
                u=arcs[x]
                if values[u]==a:dest,control=control,dest
                need(u not in assignment,'recipient use assignment once');assignment[u]=control
            ops.append([dest,control,x])
        else:dest=R;R+=1;sources[str(x)]=dest
        free=[u for u in uses[x] if u not in incoming_uses];need(free,'unassigned output carrier use')
        for j,u in enumerate(free):
            if j==0:assignment[u]=dest
            else:assignment[u]=R;ops.append([R,dest,x]);R+=1
    rootroles=[assignment[code_index['root',j]] for j in range(len(g['roots']))]
    need(ops==w['ops'] and sources==w['sources'] and rootroles==w['rootroles'],'entire scalar word/source/root role reconstruction')
    need(R==(nodes-v)+len(g['roots'])-len(arcs),'compiler persistent role stock')
    first={}
    for a,b,node in ops:
        first.setdefault(a,node);first.setdefault(b,node)
    need(all(item['first']==first[item['role']] for item in w['gauges']),'actual gauge first-node metadata')
    H=Counter()
    for x in order:
        r=nf[x].dim;H[r]+=len(uses[x])-1
        if args[x] is None:H[1]+=1;H[r-1]+=1
        else:
            H[h-r]+=1
            for operand in args[x]:H[r-nf[operand].dim]+=1
    for root,frame in zip(g['roots'],root_frames):
        r=nf[root['node']].dim;rt=frame.dim
        if root['kind']=='center':H[r]+=1;H[h-r]+=1
        else:H[rt-r]+=1;H[h-rt]+=1
    for donor,u in arcs.items():
        rv,rd=nf[values[u]].dim,nf[donor].dim;target=targets[u]
        rt=nf[target].dim if target<nodes else root_frames[target-nodes].dim
        H[h-rd]-=1;H[rv]-=1;H[rt-rv]-=1;H[rt-rd]+=1
    # Gauge rank d replaces one r entrance by r-d and retains its exterior
    # width-3d child. This compact ledger includes rank-zero terms as well.
    for item in w['gauges']:
        r=nf[item['first']].dim;d=item['dim'];H[r]-=1;H[r-d]+=1
    need(min(H.values())>=0,'complete compact carrier ledger nonnegative')
    return dict(nodes=nodes,addition_nodes=nodes-v,roots=len(g['roots']),roles=R,scalar_mutations=len(ops),
        frozen_matching_arcs=len(arcs),plain_threshold=threshold,plain_frames=len(plain),
        exact_node_frame_reconstructions=nodes,coordinate_padding_rebuilt=True,whole_scalar_word_rebuilt=True,
        compact_remaining_internal_histogram={r:n for r,n in sorted(H.items()) if n},
        elapsed_seconds=time.monotonic()-start)


def merge_output_pairs(builder,original,specs):
    need(all(isinstance(spec,list) and len(spec)==2 for spec in specs),'paired output channel policy')
    group={channel:i for i,spec in enumerate(specs) for channel in spec}
    need(len(group)==2*len(specs),'disjoint paired channel names')
    found={};keep=[];centers=[]
    for root in original['roots']:
        if root['kind']=='center':centers.append(root)
        elif root['channel'] in group:
            need(len(root['targets'])==1,'only singleton channel fusion')
            key=group[root['channel']],root['targets'][0],root['channel']
            need(key not in found,'unique selected channel per receiver');found[key]=root['node']
        else:keep.append(root)
    merged=[]
    for i,target in sorted({(i,t) for i,t,channel in found}):
        a,b=(found[i,target,channel] for channel in specs[i])
        need(not builder.support[a]&builder.support[b],'fusion exact disjoint source supports')
        node=builder.add(a,b)
        need(builder.support[node]==builder.support[a]^builder.support[b],'fusion exact scalar contribution')
        merged.append(dict(node=node,targets=[target],kind='side',channel='paired'+str(i),coefficient=1))
    need(len(merged)==len(specs)*original['v'],'all selected output pairs retained')
    return dict(original,args=builder.args,roots=keep+merged+centers)


def verify_inputs(source,context,config):
    start=time.monotonic();g,w=context['g'],context['w'];p=g['p'];directory=Path(source)/'research/paired-cube-bit/data'
    pair=json.loads((directory/'pair_module_p12.json').read_text());verify_pair_module(pair,p)
    policy=config.get('all_but_one','nested_prefix');allbut=nested_prefix(p-2,policy)
    builder=Builder(p);rebuilt=builder.build(pair,allbut)
    specs=config.get('merged_output_pairs',[])
    if specs:rebuilt=merge_output_pairs(builder,rebuilt,specs)
    need(all(g[name]==value for name,value in rebuilt.items()),'whole changed module/coordinate producer graph')
    source_arcs=json.loads((directory/'arcs_p12.json').read_text())
    if config.get('require_source_arcs',True):need(w['arcs']==source_arcs,'frozen source matching arcs')
    compiler=verify_compiler(g,w,context['nf'],context['root_frames'],config.get('plain_threshold',8))
    if 'remaining_internal_histogram' in context['supplied_profile']:
        need(compiler['compact_remaining_internal_histogram']=={int(r):n for r,n in context['supplied_profile']['remaining_internal_histogram'].items() if n},
             'complete compact carrier profile including rank-zero terms')
    target_hist=Counter();current=[()] * g['v']
    def read(target,cap):
        need(all(dot(a,b)==0 for a in cap.A for b in current[target]),'compact target chronology')
        target_hist[cap.dim-len(current[target])]+=1;current[target]=cap.B
    for item in reversed(w['gauges']):
        for target in item['targets']:read(target,context['frames'][item['frame']])
    for root,cap in zip(g['roots'],context['root_frames']):
        if root['kind']!='center':
            for target in root['targets']:read(target,cap)
    for target in range(g['v']):target_hist[g['h']-1-len(current[target])]+=1
    need(dict(target_hist)=={int(r):n for r,n in context['supplied_profile']['target_data_histogram'].items() if n},
         'complete compact target profile including rank-zero terms')
    compiler['compact_target_histogram']={r:n for r,n in sorted(target_hist.items()) if n}
    return dict(pair_module_additions=len(pair['args'])-pair['input_count'],pair_module_all_roots_exact=True,
        pair_module_sha256=sha256((directory/'pair_module_p12.json').read_bytes()).hexdigest(),all_but_one_policy=policy,
        all_but_one_additions=len(allbut['args'])-allbut['input_count'],all_but_one_exact_integer_roots=True,
        rebuilt_graph_semantic_sha256=sha256(json.dumps(rebuilt,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        compiler=compiler,elapsed_seconds=time.monotonic()-start,
        scope='Independent integer module contracts, every producer node/root/partner label, coordinate padding, '
              'matching chronology/compatibility, spliced and plain frames, every scalar carrier/source/root assignment. '
              'Gauge physical legality and full formal/reflected execution are checked separately by this lane.')
