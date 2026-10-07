"""Create the wider-horizon analysis with explicit target keys and confidence audits."""
from lab import ROOT
source = (ROOT/'scripts/analyze_gpu_router.py').read_text()
def replace(old, new):
    global source
    assert source.count(old) == 1, (old[:100], source.count(old))
    source = source.replace(old, new)
replace("spanmap={(int(s['window']),int(s['current_layer'])):float(s['gpu_ms'])*1000 for s in spans}",
        "spanmap={(int(s['window']),int(s['current_layer']),int(s['reserved'])):float(s['gpu_ms'])*1000 for s in spans}\nassert len(spanmap)==len(spans)\nconfidence=np.fromfile(prefix+'-gpu-router-confidence.bin','<f4')\nassert len(confidence)==len(values) and np.isfinite(confidence).all() and np.all((confidence>=0)&(confidence<=1))")
replace("ids=values[at:at+n*k].reshape(n,k);assert np.all((ids>=0)&(ids<512))",
        "ids=values[at:at+n*k].reshape(n,k);assert np.all((ids>=0)&(ids<512))\n weights=confidence[at:at+n*k].reshape(n,k)\n assert np.allclose(weights.sum(axis=1),1,rtol=1e-4,atol=1e-5) and all(len(set(row))==k for row in ids)")
replace("if (w,current,row) in fresh:", "if (w,current,row) in fresh and pathlib.Path(refbase+f'-gate-layer{target}.bin').exists():")
replace("spanmap[w,current]", "spanmap[w,current,target]")
replace("'predicted_IDs':chosen.tolist()", "'predicted_IDs':chosen.tolist(),'horizon':target-current,'top10_normalized_weights':weights[row].tolist()")
replace("'native_GPU_score_publish_us':dist([r['GPU_score_top10_publish_us'] for r in rs])",
        "'native_GPU_score_publish_us':dist(list({(r['window'],r['current_layer'],r['target_layer']):r['GPU_score_top10_publish_us'] for r in rs}.values()))")
replace("'by_layer':{str(l):aggregate([r for r in records if r['current_layer']==l]) for l in sorted({r['current_layer'] for r in records})}",
        "'by_horizon':{str(h):aggregate([r for r in records if r['horizon']==h]) for h in [4,8]},'by_pair':{f'{l}->{target}':aggregate([r for r in records if r['current_layer']==l and r['target_layer']==target]) for l,target in sorted({(r['current_layer'],r['target_layer']) for r in records})},'confidence_semantics':'Native normalized top10 routing weights; not calibrated probability of future use.'")
replace("'Five same-device pairs only; no cross-GPUboundary prediction.'", "'Five same-device origins, two horizons4/8; no cross-GPUboundary prediction. CPUfullgate agreement unavailable where no matching frozen gate snapshot exists.'")
path = ROOT/'scripts/analyze_wide_gate.py'
if path.exists():
    raise RuntimeError('Existing analysis module; do not overwrite')
path.write_text(source)
print(path)
