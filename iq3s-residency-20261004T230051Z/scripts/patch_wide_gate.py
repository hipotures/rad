"""Two meaningfully wider same-device horizons; no real routing or policy changes."""
import pathlib,subprocess,sys
r=pathlib.Path(__file__).resolve().parents[1];s=pathlib.Path(sys.argv[1])
subprocess.run([sys.executable,str(r/'scripts/patch_gpu_router_v2.py'),str(s)],check=True)
p=s/'include/strata/research/lab_gpu_router.hpp';t=p.read_text()
def change(old,new):
 global t
 assert t.count(old)==1,(old[:100],t.count(old));t=t.replace(old,new)
change('static constexpr std::array<int, 5> layers{5, 20, 25, 40, 46};','static constexpr std::array<int, 10> layers{5,5,12,12,25,25,32,32,38,38};\n    static constexpr std::array<int, 10> targets{9,13,16,20,29,33,36,40,42,46};')
change('std::array<Pair, 5> pairs{};','std::array<Pair, 10> pairs{};')
change('std::array<float*, 2> weights{};','std::array<float*, 2> weights{}, host_weights{}, mapped_weights{};\n    std::vector<float> confidence;')
change('int layer = layers[i], target = layer + 1;','int layer = layers[i], target = targets[i];')
change('        *host_sequence[device] = 0;','''        if (!allocate(cudaHostAlloc(&host_weights[device], layers.size()*max_tokens*k*sizeof(float), cudaHostAllocMapped)) ||
            !allocate(cudaHostGetDevicePointer(&mapped_weights[device],host_weights[device],0))) {
            error="wide gate: confidence allocation";return false;
        }
        *host_sequence[device] = 0;''')
change('predictions.clear(); values.clear(); spans.clear();','predictions.clear(); values.clear(); confidence.clear(); spans.clear();')
change('predictions.reserve(320); values.reserve(64 * 5 * max_tokens * k); spans.reserve(320);','predictions.reserve(640); values.reserve(64*10*max_tokens*k); confidence.reserve(64*10*max_tokens*k); spans.reserve(640);')
start=t.index('    void score(');end=t.index('    void completed(',start)
t=t[:start]+'''    void score(int layer,int tokens,const float* activation,float* temporary_logits,cudaStream_t stream){
        if(!enabled)return;
        if(tokens<1||tokens>max_tokens)throw std::runtime_error("wide gate: token geometry");
        for(int i=0;i<(int)layers.size();++i){
            if(layers[i]!=layer||!pairs[i].configured)continue;
            auto& pair=pairs[i];int device=pair.device;
            if(cudaEventRecordWithFlags(pair.begin,stream,cudaEventRecordExternal)!=cudaSuccess)throw std::runtime_error("wide gate: begin event");
            strata::kernels::bf16_gemv_fp32_mmvf_multi(activation,width,pair.gate,temporary_logits,experts,width,experts,tokens,stream);
            strata::kernels::native_router_top10_multi(temporary_logits,ids[device],weights[device],tokens,stream);
            strata::kernels::doorbell_publish(nullptr,ids[device],weights[device],0,tokens*k,nullptr,
                mapped_ids[device]+i*max_tokens*k,mapped_weights[device]+i*max_tokens*k,mapped_sequence[device],stream);
            if(cudaEventRecordWithFlags(pair.end,stream,cudaEventRecordExternal)!=cudaSuccess)throw std::runtime_error("wide gate: end event");
        }
    }
    void host(int layer,int tokens){
        if(!enabled||!trace.active||trace.windows.size()>64)return;
        for(int i=0;i<(int)layers.size();++i){
            if(layers[i]!=layer||!pairs[i].configured)continue;
            uint64_t available=ns(),offset=values.size();int device=pairs[i].device;
            const auto* input=host_ids[device]+i*max_tokens*k;
            const auto* probs=host_weights[device]+i*max_tokens*k;
            values.insert(values.end(),input,input+tokens*k);
            confidence.insert(confidence.end(),probs,probs+tokens*k);
            predictions.push_back({trace.window,available,offset,layer,targets[i],tokens,k});
        }
    }
''' +t[end:]
change('spans.push_back({trace.window, ns(), layers[i], device, elapsed, 0});','spans.push_back({trace.window, ns(), layers[i], device, elapsed, targets[i]});')
change('trace.file(prefix + "-gpu-router-values.bin", values);','trace.file(prefix + "-gpu-router-values.bin", values);\n        trace.file(prefix + "-gpu-router-confidence.bin", confidence);')
# Explicit metadata records the enlarged mapped allocation and changed span field.
change('\\"mapped_CPU_bytes\\":864','\\"mapped_CPU_bytes\\":3264')
change('\\"span_record_bytes\\":32}','\\"span_record_bytes\\":32,\\"span_target_field\\":true,\\"horizons\\":[4,8]}')
p.write_text(t)
print('Opt-in native GPU horizons4/8 with confidence; actual IDs/weights and expert math untouched',flush=True)
