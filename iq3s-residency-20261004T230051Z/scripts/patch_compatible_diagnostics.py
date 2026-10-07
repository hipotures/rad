"""Combine retained compatible policy and scoped diagnostics with explicit cross-layer victim IDs."""
import pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];src=pathlib.Path(sys.argv[1])
for script in ['patch_compatible.py','patch_miss_waits.py']:
    subprocess.run([sys.executable,str(ROOT/'scripts'/script),str(src)],check=True)
def edit(path,old,new,count=1):
    p=src/path;s=p.read_text()
    if s.count(old)!=count:raise RuntimeError(f'{path}: expected{count}, got{s.count(old)}: {old[:100]}')
    p.write_text(s.replace(old,new,count))
header='include/strata/research/lab_trace.hpp'
edit(header,'struct Promotion { uint64_t window, issue, observed_ready, bytes; int32_t layer, incoming, outgoing, slot; };\nstatic_assert(sizeof(Promotion)==48);',
     'struct Promotion { uint64_t window, issue, observed_ready, bytes; int32_t layer, incoming, outgoing, slot, outgoing_layer, reserved; };\nstatic_assert(sizeof(Promotion)==56);')
edit(header,'    void promotion(int32_t l,int32_t in,int32_t out,int32_t slot,uint64_t bytes) {\n        if(active) promotions.push_back({window,ns(),0,bytes,l,in,out,slot});\n    }',
     '    void promotion(int32_t l,int32_t in,int32_t out,int32_t slot,uint64_t bytes,int32_t out_layer=-1) {\n        if(active) promotions.push_back({window,ns(),0,bytes,l,in,out,slot,out_layer<0 ? l : out_layer,0});\n    }')
edit(header,'        file(p+"-promotions.bin",promotions);file(p+"-reach.bin",reach);',
     '        file(p+"-promotions.bin",promotions);file(p+"-reach.bin",reach);\n        FILE* meta=std::fopen((p+"-schema.json").c_str(),"w");\n        if(meta) {std::fprintf(meta,"{\\"version\\":2,\\"promotion_record_bytes\\":56,\\"cross_layer_victim\\":true}\\n");std::fclose(meta);}')
p=src/'src/program/generate.cpp';s=p.read_text();start=s.index('        auto adapt = [&]() -> bool {');end=s.index('        // #477: write the learned profile',start);section=s[start:end]
old='strata::research::trace.promotion((int32_t)s.layer, (int32_t)s.in, (int32_t)s.out, slot, strata::kernels::cpu::expert_layout().blob_bytes(s.layer));'
assert section.count(old)==1
section=section.replace(old,old[:-2]+', out_layer);')
p.write_text(s[:start]+section+s[end:])
print('Compatible policy unchanged; schema2 diagnostic adds real outgoing layer identity',flush=True)
