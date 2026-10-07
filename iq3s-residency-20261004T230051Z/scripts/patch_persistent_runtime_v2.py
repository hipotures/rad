"""One predeclared persistent utility repair; native math and copy boundary unchanged."""
import pathlib,subprocess,sys
root=pathlib.Path(__file__).resolve().parents[1];src=pathlib.Path(sys.argv[1]);subprocess.run([sys.executable,str(root/'scripts/patch_persistent_runtime_fixed.py'),str(src)],check=True)
p=src/'src/program/generate.cpp';s=p.read_text();anchor='        persistent_cfg.prediction_weight = 1.0f; // frozen development selection before full trace ranking';assert s.count(anchor)==1;s=s.replace(anchor,anchor+'\n        persistent_cfg.forecast_windows = 64; // predeclared E028v2 lifetime repair\n        persistent_cfg.bytes_per_device = 64ull*1024*1024;')
# Fail rather than publish if an event reports copy failure. OFF preserves upstream behavior.
old='            if (wait) cudaEventSynchronize(adapt_ev);\n            else if (cudaEventQuery(adapt_ev) != cudaSuccess) return;';new='''            if (wait) {
                const auto status = cudaEventSynchronize(adapt_ev);
                if (strata::research::persistent.enabled && status != cudaSuccess)
                    throw std::runtime_error("persistent: primary copy completion failed before publication");
            } else if (cudaEventQuery(adapt_ev) != cudaSuccess) return;''';assert s.count(old)==2;s=s.replace(old,new,2)
old='                    if (wait) cudaEventSynchronize(st->adapt_ev);\n                    else if (cudaEventQuery(st->adapt_ev) != cudaSuccess) return;';new='''                    if (wait) {
                        const auto status = cudaEventSynchronize(st->adapt_ev);
                        if (strata::research::persistent.enabled && status != cudaSuccess)
                            throw std::runtime_error("persistent: stage copy completion failed before publication");
                    } else if (cudaEventQuery(st->adapt_ev) != cudaSuccess) return;''';assert s.count(old)==1;s=s.replace(old,new)
p.write_text(s)
