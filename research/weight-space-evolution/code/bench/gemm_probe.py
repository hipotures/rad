"""Tensor-core throughput probe: dense GEMM TFLOP/s for BF16/FP16 (FP32 accumulate) and FP16 with reduced-precision
(FP16) accumulation, plus TF32, on the visible GPU.

    CUDA_VISIBLE_DEVICES=<uuid> python -m bench.gemm_probe [--n 8192] [--iters 50]

Stock GeForce Ada (RTX 4090) runs FP16/BF16 MMA with FP32 accumulation at half the FP16-accumulate rate; an
"unlocked" card/driver would show the two rates equal. Prints one JSON line.
"""
import argparse
import json

import torch


def tflops(fn, flop, iters):
    for _ in range(5):
        fn()
    torch.cuda.synchronize()
    s, e = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    best = []
    for _ in range(3):
        s.record()
        for _ in range(iters):
            fn()
        e.record()
        torch.cuda.synchronize()
        best.append(flop * iters / (s.elapsed_time(e) / 1e3) / 1e12)
    return round(max(best), 1)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8192)
    ap.add_argument("--iters", type=int, default=50)
    a = ap.parse_args(argv)
    n, flop = a.n, 2 * a.n ** 3
    res = {"device": torch.cuda.get_device_name(), "uuid": str(torch.cuda.get_device_properties(0).uuid), "n": n}
    for name, dt in (("bf16_fp32acc", torch.bfloat16), ("fp16_fp32acc", torch.float16)):
        x, y = torch.randn(n, n, device="cuda", dtype=dt), torch.randn(n, n, device="cuda", dtype=dt)
        torch.backends.cuda.matmul.allow_fp16_reduced_precision_reduction = False
        torch.backends.cuda.matmul.allow_bf16_reduced_precision_reduction = False
        res[name] = tflops(lambda: x @ y, flop, a.iters)
    try:   # cuBLAS FP16 compute type (FP16 accumulate) when PyTorch exposes it
        torch.backends.cuda.matmul.allow_fp16_accumulation = True
        x, y = torch.randn(n, n, device="cuda", dtype=torch.float16), torch.randn(n, n, device="cuda", dtype=torch.float16)
        res["fp16_fp16acc"] = tflops(lambda: x @ y, flop, a.iters)
        torch.backends.cuda.matmul.allow_fp16_accumulation = False
    except Exception as ex:   # noqa: BLE001
        res["fp16_fp16acc"] = f"unavailable: {type(ex).__name__}: {ex}"
    torch.backends.cuda.matmul.allow_tf32 = True
    x, y = torch.randn(n, n, device="cuda"), torch.randn(n, n, device="cuda")
    res["tf32"] = tflops(lambda: x @ y, flop, a.iters)
    res["bandwidth_GBps"] = None
    b = torch.empty(1 << 28, device="cuda", dtype=torch.float32)
    c = torch.empty_like(b)
    for _ in range(3):
        c.copy_(b)
    torch.cuda.synchronize()
    s, e = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    s.record()
    for _ in range(20):
        c.copy_(b)
    e.record()
    torch.cuda.synchronize()
    res["bandwidth_GBps"] = round(2 * b.numel() * 4 * 20 / (s.elapsed_time(e) / 1e3) / 1e9, 1)
    print(json.dumps(res))


if __name__ == "__main__":
    main()
