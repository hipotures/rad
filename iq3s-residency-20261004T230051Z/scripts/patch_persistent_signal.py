"""Full-window horizon8 signals on the existing E020 diagnostic, never real routing."""
import pathlib,subprocess,sys
r=pathlib.Path(__file__).resolve().parents[1];s=pathlib.Path(sys.argv[1])
subprocess.run([sys.executable,str(r/'scripts/patch_wide_gate.py'),str(s)],check=True)
p=s/'include/strata/research/lab_gpu_router.hpp';t=p.read_text()
changes={
 'static constexpr std::array<int, 10> layers{5,5,12,12,25,25,32,32,38,38};':'static constexpr std::array<int, 5> layers{5,12,25,32,38};',
 'static constexpr std::array<int, 10> targets{9,13,16,20,29,33,36,40,42,46};':'static constexpr std::array<int, 5> targets{13,20,33,40,46};',
 'std::array<Pair, 10> pairs{};':'std::array<Pair, 5> pairs{};',
 'predictions.reserve(640); values.reserve(64*10*max_tokens*k); confidence.reserve(64*10*max_tokens*k); spans.reserve(640);':'predictions.reserve(10000); values.reserve(2000*5*max_tokens*k); confidence.reserve(2000*5*max_tokens*k); spans.reserve(10000);',
 '\\"mapped_CPU_bytes\\":3264':'\\"mapped_CPU_bytes\\":1664',
 '\\"horizons\\":[4,8]':'\\"horizons\\":[8],\\"full_windows\\":true'}
for old,new in changes.items():assert t.count(old)==1,(old,t.count(old));t=t.replace(old,new)
assert t.count('||trace.windows.size()>64')==1;t=t.replace('||trace.windows.size()>64','')
assert t.count(' || trace.windows.size() > 64')==1;t=t.replace(' || trace.windows.size() > 64','')
p.write_text(t);print('Full persistent-lifetime horizon8 diagnostic only; true routing unchanged',flush=True)
