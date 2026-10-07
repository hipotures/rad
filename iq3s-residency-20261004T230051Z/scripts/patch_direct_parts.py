"""Opt-in direct native expert rows with a CPU copy that preserves GPU ownership."""
import pathlib,sys
s=pathlib.Path(sys.argv[1])
def edit(name,old,new,count=1):
 p=s/name;t=p.read_text();assert t.count(old)==count,(name,old[:90],t.count(old));p.write_text(t.replace(old,new,count))
edit('include/strata/core/verify.hpp','    bool device_plan_ = false;','    bool lab_direct_parts_ = false;\n    bool device_plan_ = false;')
anchor='    // E-6: a layer whose routed experts are all resident is planned on the device'
edit('src/core/verify.cpp',anchor,'''    const char* lab_parts=std::getenv("STRATA_LAB_DIRECT_PARTS");
    lab_direct_parts_=lab_parts&&lab_parts[0]=='1';
    if(lab_direct_parts_ && (all_resident_ || remote_opt_ || g.n_layers!=48 || g.n_embd!=2560 ||
        g.n_expert!=512 || ss.k!=10 || !strata::kernels::cpu::expert_layout().native ||
        !((lb_==0&&le_==25&&device_==0)||(lb_==25&&le_==48&&device_==1)))) {
        err="lab direct parts: only frozen native IQ3_S serial K25 dual split is validated";return false;
    }
''' +anchor)
anchor='    static const bool dec_batch = [] { const char* v = std::getenv("STRATA_DEC_BATCH");'
edit('src/core/verify.cpp',anchor,'''    if(lab_direct_parts_ && (G<1 || G>2 || batch_rec_)) {
        err="lab direct parts: concurrent slots unsupported";return false;
    }
''' +anchor)
edit('src/core/verify.cpp','            grouped(p_ptr, p_start, p_counts, 0, hit_out);',
 '            grouped(p_ptr, p_start, p_counts, 0, lab_direct_parts_ ? parts_out : hit_out);')
edit('src/core/verify.cpp','            grouped(p_ptr2, p_start2, p_counts + 2, kPcieGroupRows, hit_out);',
 '            grouped(p_ptr2, p_start2, p_counts + 2, kPcieGroupRows, lab_direct_parts_ ? parts_out : hit_out);')
edit('src/core/verify.cpp', '''                copy_or_zero_from_mapped(parts_out, m_ymiss_ + (size_t) tb * K * N, (long long) n * K * N,
                                         skip_ + grp, ring, cs);''', '''                if(lab_direct_parts_)
                    copy_cpu_rows_preserving_gpu(parts_out,m_ymiss_+(size_t)tb*K*N,(int64_t)n*K,N,p_dst,p_counts+1,cs);
                else
                    copy_or_zero_from_mapped(parts_out, m_ymiss_ + (size_t) tb * K * N, (long long) n * K * N,
                                             skip_ + grp, ring, cs);''')
edit('src/core/verify.cpp','                if (remote_opt_)   // #578: the helper\'s rows come back reduced; skip them as well',
 '''                if(lab_direct_parts_)
                    copy_cpu_rows_preserving_gpu(parts_out,m_ymiss_+(size_t)tb*K*N,(int64_t)n*K,N,p_dst,p_counts+1,cs);
                else if (remote_opt_)   // #578: the helper's rows come back reduced; skip them as well''')
edit('src/core/verify.cpp','            moe_hit_add(parts_out, hit_out, p_dst, p_counts + 1, cap, N, cs);',
 '            if(!lab_direct_parts_) moe_hit_add(parts_out, hit_out, p_dst, p_counts + 1, cap, N, cs);')
edit('include/strata/kernels/elementwise.hpp','void copy_from_mapped(float* dst, const float* src, int64_t n, void* stream);',
 '''/// Local experiment: preserve rows owned by the native GPU plan; copy only its CPU complement.
void copy_cpu_rows_preserving_gpu(float* dst,const float* src,int64_t rows,int64_t width,
                                  const int32_t* hit_rows,const int32_t* count,void* stream);
void copy_from_mapped(float* dst, const float* src, int64_t n, void* stream);''')
p=s/'src/kernels/cuda/elementwise.cu';t=p.read_text()
start=t.index('__global__ void copy_rows_from_mapped_kernel(');end=t.index('\nnamespace {',start)
kernel=t[start:end]
kernel=kernel.replace('copy_rows_from_mapped_kernel','copy_cpu_rows_preserving_gpu_kernel')
old='''    if (hit) {
        for (int64_t i = threadIdx.x; i < row4; i += blockDim.x) d[i] = make_float4(0.0f, 0.0f, 0.0f, 0.0f);
    } else {'''
assert kernel.count(old)==1
kernel=kernel.replace(old,'''    if (hit) return;   // Existing GPU result must remain untouched.
    {''')
anchor='void copy_from_mapped(float* dst, const float* src, int64_t n, void* stream) {'
assert t.count(anchor)==1
wrapper='''void copy_cpu_rows_preserving_gpu(float* dst,const float* src,int64_t rows,int64_t width,
                                  const int32_t* hit_rows,const int32_t* count,void* stream) {
    if(rows<=0)return;
    if((width&3)!=0 || ((uintptr_t)dst&15)!=0 || ((uintptr_t)src&15)!=0) {
        std::fprintf(stderr,"copy_cpu_rows_preserving_gpu: alignment/width error\\n");std::exit(1);
    }
    copy_cpu_rows_preserving_gpu_kernel<<<(unsigned)rows,128,0,(cudaStream_t)stream>>>(
        (float4*)dst,(const volatile float4*)src,width/4,hit_rows,count);
}
'''
t=t[:end]+'\n'+kernel+t[end:]
t=t.replace(anchor,wrapper+anchor)
p.write_text(t)
import shutil
root=pathlib.Path(__file__).resolve().parents[1]
shutil.copy2(root/'scripts/direct_parts_test.cpp',s/'tests/cuda/direct_parts_test.cpp')
with (s/'CMakeLists.txt').open('a') as f:
 f.write('''
# Local opt-in row-ownership regression; no changes to upstream test targets.
if(STRATA_BUILD_TESTS AND STRATA_ENABLE_CUDA)
  add_executable(lab_direct_parts_test tests/cuda/direct_parts_test.cpp)
  target_link_libraries(lab_direct_parts_test PRIVATE strata_kernels CUDA::cudart)
  add_test(NAME lab_direct_parts_test COMMAND lab_direct_parts_test)
endif()
''')
print('Default-off direct parts + preserving CPU complement; native expert arithmetic unchanged',flush=True)
