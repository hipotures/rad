"""vLLM worker extension for the persistent Phase D evaluator (loaded with LLM(worker_extension_cls=...)).

Runs inside the vLLM worker process (TP = 1 only; fails closed otherwise). Methods are called through
`LLM.collective_rpc("<method>", kwargs=...)`; data travels through files under work/, never through the RPC channel.

Direct patching writes new BF16 values at given flat indices into the *same* parameter storage that vLLM's public
`reload_weights(..., is_checkpoint_format=False)` path copies into (`param.copy_`), so CUDA graphs and compiled
graphs (which reference parameter storage, not values) see the new weights. It is only allowed for parameters whose
runtime tensor is byte-identical to the checkpoint tensor (same name mapping, shape, dtype, layout); this is verified
by hashing the runtime parameter against the expected base hash before every write and the expected edited hash after.
Fused/stacked/repacked parameters (qkv_proj, gate_up_proj, in_proj_*) are refused, and the caller falls back to a full
checkpoint reload.
"""
import hashlib
import time

import numpy as np
import torch

CKPT_PREFIX = "model.language_model."
RUNTIME_PREFIX = "model."


def runtime_name(ckpt_name):
    """Checkpoint (HF text export) name -> vLLM Qwen3_5ForCausalLM parameter name."""
    if ckpt_name.startswith(CKPT_PREFIX):
        return RUNTIME_PREFIX + ckpt_name[len(CKPT_PREFIX):]
    return ckpt_name


def _sha(t):
    """sha256 of a tensor's raw bytes in row-major order (equals wse.tensors.sha256_array of the BF16 bit array)."""
    a = t.detach().contiguous()
    if a.dtype == torch.bfloat16:
        a = a.view(torch.int16)
    return hashlib.sha256(a.cpu().numpy().tobytes()).hexdigest()


class WSEWorkerExtension:
    def _wse_params(self):
        if not hasattr(self, "_wse_param_cache"):
            from vllm.distributed import get_tensor_model_parallel_world_size
            assert get_tensor_model_parallel_world_size() == 1, "direct patching is defined for TP = 1 only"
            self._wse_param_cache = dict(self.model_runner.get_model().named_parameters())
        return self._wse_param_cache

    def wse_param_info(self):
        return [(n, list(p.shape), str(p.dtype), p.is_contiguous()) for n, p in self._wse_params().items()]

    def wse_fingerprint(self, names=None):
        """{runtime name: sha256} for the given runtime parameter names (all if None) and the elapsed seconds."""
        t = time.perf_counter()
        ps = self._wse_params()
        out = {n: _sha(ps[n]) for n in (names if names is not None else sorted(ps))}
        torch.cuda.synchronize()
        return {"hashes": out, "seconds": time.perf_counter() - t}

    def wse_memory(self):
        torch.cuda.synchronize()
        return {"allocated": torch.cuda.memory_allocated(), "reserved": torch.cuda.memory_reserved(),
                "max_allocated": torch.cuda.max_memory_allocated()}

    def wse_apply(self, spec_path, verify=True):
        """Apply a sparse BF16 write described by a JSON spec (see wse.swap_engine.write_spec).

        For each tensor: check runtime hash == expected 'before' hash, write values at flat indices, check runtime
        hash == expected 'after' hash. On any mismatch every tensor written so far is rolled back from the saved
        old values and an error is raised (no partial state survives)."""
        import json
        t0 = time.perf_counter()
        spec = json.loads(open(spec_path).read())
        ps = self._wse_params()
        z = np.load(spec["npz"], allow_pickle=False)
        done, timings = [], {}
        try:
            for t in spec["tensors"]:
                name = t["runtime_name"]
                if name not in ps:
                    raise RuntimeError(f"no runtime parameter {name}")
                p = ps[name]
                if list(p.shape) != t["shape"] or p.dtype != torch.bfloat16 or not p.is_contiguous():
                    raise RuntimeError(f"{name}: runtime layout {list(p.shape)} {p.dtype} not patchable")
                if verify and _sha(p) != t["before_sha256"]:
                    raise RuntimeError(f"{name}: runtime tensor does not match the expected base")
                flat = p.data.view(-1).view(torch.int16)
                idx = torch.from_numpy(z[t["key"] + "_idx"]).to(p.device)
                new = torch.from_numpy(z[t["key"] + "_val"].view(np.int16)).to(p.device)
                old = flat[idx].clone()
                flat[idx] = new
                done.append((flat, idx, old))
                if verify and _sha(p) != t["after_sha256"]:
                    raise RuntimeError(f"{name}: runtime tensor hash after write differs from the expected edit")
        except Exception:
            for flat, idx, old in reversed(done):
                flat[idx] = old
            torch.cuda.synchronize()
            raise
        torch.cuda.synchronize()
        timings["apply_s"] = time.perf_counter() - t0
        # same follow-up invalidation as GPUModelRunner.reload_weights
        mr = self.model_runner
        for fn in ("reset_lora_state", "reset_encoder_cache", "reset_mm_cache"):
            if hasattr(mr, fn):
                getattr(mr, fn)()
        return {"tensors": len(done), "entries": int(sum(int(i.numel()) for _, i, _ in done)), **timings}
