# Perturbed exact rank-seven calibration on both GPUs

The same seed109, noise0.05, Douglas--Rachford relaxation0.5 and known rational h8 seven-color initialization were run independently on both RTX4090 devices. Both reached maximum affine/rank residual `6.415645792401392e-12` at iteration550. Their final compressed numerical coefficient artifacts have the same SHA256. The outer wall times were 1.316 and1.266 seconds; maximum process RSS was647356 and685640 KiB, with no swaps.

This calibrates recovery near a known exact rank-seven fixture. It does not claim that the numerical coefficients are an exact rational witness or that every initialization should find a reduced-rank fitting map. The previous h8 rank7 trial began near the rank-eight vertex fixture and failed its bounded cap. That failure and its old source version remain intact.

See the [independent exact fixture and graph-orientation review](../../reports/review-haemers-pair-features.md) and [vertex-feature scope](../../reports/vertex-feature-uniqueness.md). Complete commands, settings, code hashes and original log/resource paths are retained in protocol.json.
