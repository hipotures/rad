"""One predeclared persistent utility repair; native math and copy boundary unchanged."""
import pathlib,subprocess,sys
root=pathlib.Path(__file__).resolve().parents[1];src=pathlib.Path(sys.argv[1]);subprocess.run([sys.executable,str(root/'scripts/patch_persistent_runtime_fixed.py'),str(src)],check=True)
p=src/'src/program/generate.cpp';s=p.read_text();anchor='        persistent_cfg.prediction_weight = 1.0f; // frozen development selection before full trace ranking';assert s.count(anchor)==1;s=s.replace(anchor,anchor+'\n        persistent_cfg.forecast_windows = 64; // predeclared E028v2 lifetime repair\n        persistent_cfg.bytes_per_device = 64ull*1024*1024;')
# Fail rather than publish if an event reports copy failure. OFF preserves upstream behavior.
old='            if (wait) cudaEventSynchronize(adapt_ev);\n            else if (cudaEventQuery(adapt_ev) != cudaSuccess) return;';new='''            if (wait) {
                const auto status = cudaEventSynchronize(adapt_ev);
                if (strata::research::persistent.enabled && status != cudaSuccess)
                    throw std::runtime_error("persistent: primary copy completion failed before publication");
            } else if (cudaEventQuery(adapt_ev) != cudaSuccess) return;''';assert s.count(old)==1;s=s.replace(old,new,1)
old='                    if (wait) cudaEventSynchronize(st->adapt_ev);\n                    else if (cudaEventQuery(st->adapt_ev) != cudaSuccess) return;';new='''                    if (wait) {
                        const auto status = cudaEventSynchronize(st->adapt_ev);
                        if (strata::research::persistent.enabled && status != cudaSuccess)
                            throw std::runtime_error("persistent: stage copy completion failed before publication");
                    } else if (cudaEventQuery(st->adapt_ev) != cudaSuccess) return;''';assert s.count(old)==1;s=s.replace(old,new)
p.write_text(s)

# Diagnostic-only actual GPU weight readback after headline decode timing; no extra hot path.
old='            persistent.finish();'
new='''
            const char* persistent_check = std::getenv("STRATA_LAB_PERSISTENT_CHECK");
            if (lab_persistent && persistent_check && persistent_check[0] == '1') {
                apply_pending(true);
                if (!persistent.validate(host_res, lab_blob, lab_slots0, lab_slots1)) {
                    std::printf("ERR persistent final byte/slot identity invariant\\n"); return 1;
                }
                uint64_t checked = 0, checked_bytes = 0;
                std::vector<uint8_t> bytes;
                for (const auto& admission : persistent.admissions) {
                    const size_t at = (size_t)admission.layer * g.n_expert + admission.in;
                    if (host_res[at] != admission.slot) continue;
                    const int stage = stage_of(admission.layer);
                    GpuStage* gs = stage > 0 ? stages[(size_t)stage - 1].get() : nullptr;
                    const strata::core::OnDevice on(gs ? gs->dev : -1);
                    bytes.resize((size_t)lab_blob[(size_t)admission.layer]);
                    const uint8_t* canonical = srcp->blob(admission.layer, admission.in);
                    if (!canonical || cudaMemcpy(bytes.data(), gs ? gs->cache.device_slot(admission.slot) : xcache.device_slot(admission.slot),
                                                  bytes.size(), cudaMemcpyDeviceToHost) != cudaSuccess ||
                                      std::memcmp(bytes.data(), canonical, bytes.size()) != 0) {
                        std::printf("ERR persistent cached weights differ from immutable expert %d/%d\\n", admission.layer, admission.in); return 1;
                    }
                    ++checked; checked_bytes += bytes.size();
                }
                std::fprintf(stderr, "strata persistent audit: exact RAM/GPU expert bytes PASS, checked=%llu bytes=%llu; outside decode timer\\n",
                             (unsigned long long)checked, (unsigned long long)checked_bytes);
            }
            persistent.finish();
'''
assert s.count(old)==1;s=s.replace(old,new);p.write_text(s)
