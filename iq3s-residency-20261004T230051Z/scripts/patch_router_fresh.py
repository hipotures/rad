"""Diagnostic-only fresh current-layer activations, including fully resident groups."""
import pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];src=pathlib.Path(sys.argv[1])
subprocess.run([sys.executable,str(ROOT/'scripts/patch_signals.py'),str(src)],check=True)
p=src/'src/core/verify.cpp';s=p.read_text()
old='                const int32_t* layer_res = hits_.d_res != nullptr ? (hits_.d_res + l * g.n_expert) : nullptr;\n                doorbell_publish_res'
new='''                const int32_t* layer_res = hits_.d_res != nullptr ? (hits_.d_res + l * g.n_expert) : nullptr;
                // Diagnostic only: the normal all-VRAM doorbell deliberately omits x.
                // A fresh activation is required to evaluate a future router signal.
                if (strata::research::signals.enabled && strata::research::signals.selected((int32_t)l)) layer_res = nullptr;
                doorbell_publish_res'''
assert s.count(old)==1;s=s.replace(old,new);p.write_text(s)
print('Selected-layer fresh activation diagnostic; true router/math/cache unchanged',flush=True)
