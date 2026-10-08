#!/usr/bin/env python3
"""Seeded actual fixed-profile surrogate ordering of original HK matching.

A deterministic authored header profiles eligible transitions in one field
for ranking only. The selected matching is then evaluated by the unchanged
five-prime full profiler. Output suffixes retain seed and noise amplitude.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
from fixed_profiler_prepare import PIN, SOURCE, crt_enclosure


ADJACENCY = '''auto adjacency=[&](U donor,auto&& action){for(U value:args[donor])for(U j=begin[value];j<begin[value+1];j++)if(before(donor*2,uses[j])&&incl(donor*2,uses[j]))if(action(j))return true;return false;};'''
WEIGHTED = '''
FixedMatchingSurrogate scout_surrogate(h,core,cover,ranks,active);
std::vector<std::vector<U>> scout_adjacency(n);
std::vector<uint8_t> scout_prepared(n);
std::vector<double> scout_best(n,-std::numeric_limits<double>::infinity());
auto scout_tie=[&](U donor,U edge)->V{return scout_seed?scout_splitmix(scout_seed^(V(donor)<<32)^edge):V(edge);};
auto adjacency=[&](U donor,auto&& action){
 if(!scout_prepared[donor]){
  scout_prepared[donor]=1;std::vector<std::pair<double,U>> weighted;
  for(U value:args[donor])for(U j=begin[value];j<begin[value+1];j++)
   if(before(donor*2,uses[j])&&incl(donor*2,uses[j])){
    const U target=nd(uses[j]);
    double score=scout_surrogate.gain(donor,value,target);
    if(scout_noise_milli){V z=scout_splitmix(scout_seed^(V(donor)<<32)^j);
      score+=(double(z>>11)/9007199254740992.0-0.5)*double(scout_noise_milli)/1000;}
    weighted.push_back({score,j});scout_best[donor]=std::max(scout_best[donor],score);
   }
  std::sort(weighted.begin(),weighted.end(),[&](auto a,auto b){
    if(a.first!=b.first)return a.first>b.first;
    const V x=scout_tie(donor,a.second),y=scout_tie(donor,b.second);
    return x!=y?x<y:a.second<b.second;});
  for(auto item:weighted)scout_adjacency[donor].push_back(item.second);
 }
 for(U j:scout_adjacency[donor])if(action(j))return true;
 return false;
};
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-root', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--max-dimension', type=int, default=28)
    ap.add_argument('--compiler', default=os.environ.get('CXX','c++'))
    ap.add_argument('--no-compile', action='store_true')
    args = ap.parse_args()
    assert __debug__
    if not 6 <= args.max_dimension <= 28:
        ap.error('Supported dimensions6..28 except9')
    root = args.source_root.resolve()
    original = (root/SOURCE).read_text()
    header = Path(__file__).with_name('fixed_matching_surrogate.hpp').resolve()
    assert original.count(ADJACENCY) == 1
    assert original.count('assert(h==23)') == 2
    assert original.count('assert(argc==2||argc==3)') == 1
    assert original.count('if(argc==3)') == 1
    target = original.replace('assert(h==23)','assert(h>=6&&h<=%d&&h!=9)' % args.max_dimension)
    target = target.replace('#include "binary_io.hpp"', '#include "binary_io.hpp"\n#include '+json.dumps(str(header)))
    target = target.replace('assert(argc==2||argc==3);',
                            'assert(argc>=2&&argc<=6);V scout_seed=argc>=4?std::stoull(argv[3]):0;V scout_noise_milli=argc>=5?std::stoull(argv[4]):0;')
    target = target.replace('if(argc==3)','if(argc>=3)')
    target = target.replace(ADJACENCY,WEIGHTED)
    reconstruction='// Reconstruct the actual transition multiset before changing the common basis.'
    assert target.count(reconstruction)==1
    exact_uses='''if(argc>=3){std::ofstream useout(std::string(argv[2])+".uses.bin",std::ios::binary);
 U header[2]={n,U(matches)};write_array(useout,header);
 for(U donor:donors)if(leftmatch[donor]){U pair[2]={donor,uses[leftmatch[donor]-1]};write_array(useout,pair);}assert(useout);}
'''
    target=target.replace(reconstruction,exact_uses+'if(argc==6){assert(std::string(argv[5])=="--matching-only");return 0;}\n'+reconstruction)
    needle='std::vector<U>leftmatch(n)'
    assert target.count(needle)==1
    sorting='''std::sort(donors.begin(),donors.end(),[&](U a,U b){
 if(scout_best[a]!=scout_best[b])return scout_best[a]>scout_best[b];
 V x=scout_tie(a,a),y=scout_tie(b,b);return x!=y?x<y:a<b;});
std::cerr<<"SURROGATE frames "<<scout_surrogate.frame_count()<<" pairs "<<scout_surrogate.profiled_pairs()<<" seed "<<scout_seed<<" noise_milli "<<scout_noise_milli<<"\\n";
'''
    target=target.replace(needle,sorting+needle)
    output='std::string target=std::string(argv[1])+".h23_five_prime_profiles.json";'
    assert target.count(output)==1
    target=target.replace(output,'std::string target=std::string(argv[1])+".fixed_ij_weighted_seed"+std::to_string(scout_seed)+"_noise"+std::to_string(scout_noise_milli)+".json";')
    args.output.mkdir(parents=True,exist_ok=False)
    cpp,binary=args.output/'fixed_ij_weighted_profiles.cpp',args.output/'fixed_ij_weighted_profiles'
    cpp.write_text(target)
    command=[*shlex.split(args.compiler),'-O3','-std=c++17','-I',str(root/'scripts/partial_swap'),str(cpp),'-o',str(binary)]
    receipt=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),source_pin=PIN,source_file=SOURCE,
                 source_sha256=hashlib.sha256(original.encode()).hexdigest(),generated_sha256=hashlib.sha256(target.encode()).hexdigest(),
                 header_sha256=hashlib.sha256(header.read_bytes()).hexdigest(),wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 compile_command=command,compiled=False,crt_enclosures=[crt_enclosure(h) for h in range(6,args.max_dimension+1) if h!=9],
                 ranking='one-field sum(t*log(t)) marginal matching proxy, deterministic seed/noise_milli',
                 matching_identity='Canonical sorted donor/exact-use pairs in links.uses.bin; node-pair link order alone is not a complete identity',
                 verification='unchanged full five-prime rational profiles on selected ORIGINAL matching',
                 invocation='binary input.bin fresh.links [seed [noise_milli [--matching-only]]]',
                 scope='HK preserves maximum cardinality; no weighted matching or controller optimum is asserted')
    if not args.no_compile:
        subprocess.run(command,check=True)
        receipt['compiled']=True
        receipt['binary_sha256']=hashlib.sha256(binary.read_bytes()).hexdigest()
    (args.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(binary=str(binary),compiled=receipt['compiled'],invocation=receipt['invocation']),indent=2))


if __name__=='__main__':
    main()
