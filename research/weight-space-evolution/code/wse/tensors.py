"""Tensor containers: safetensors (numpy, BF16 kept as uint16 bits) and .npz, plus hashing helpers.

Independent re-implementation (not a copy) of the format handling needed to verify the upstream exp8 edits.
"""
import hashlib
import json
import struct
from pathlib import Path

import numpy as np

ST_DT = {"BF16": np.uint16, "F16": np.float16, "F32": np.float32, "F64": np.float64, "I64": np.int64,
         "I32": np.int32, "I16": np.int16, "I8": np.int8, "U8": np.uint8, "BOOL": np.bool_}


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_array(a: np.ndarray) -> str:
    return sha256_bytes(np.ascontiguousarray(a).tobytes())


def sha256_file(path, chunk=1 << 24) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while blk := f.read(chunk):
            h.update(blk)
    return h.hexdigest()


def st_header(path):
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        return json.loads(f.read(n)), 8 + n


def st_load(path, names=None):
    """{name: (dtype, array)}; arrays are read-only views of the file bytes copied into memory."""
    head, off = st_header(path)
    out = {}
    with open(path, "rb") as f:
        for name, info in head.items():
            if name == "__metadata__" or (names is not None and name not in names):
                continue
            a, b = info["data_offsets"]
            f.seek(off + a)
            arr = np.frombuffer(f.read(b - a), dtype=ST_DT[info["dtype"]]).reshape(info["shape"])
            out[name] = (info["dtype"], arr)
    if names is not None:
        missing = set(names) - set(out)
        assert not missing, f"tensors not in {path}: {sorted(missing)}"
    return out


def st_save(path, tensors, metadata=None):
    head, off, blobs = {}, 0, []
    for name in sorted(tensors):
        dt, arr = tensors[name]
        b = np.ascontiguousarray(arr).tobytes()
        head[name] = {"dtype": dt, "shape": list(arr.shape), "data_offsets": [off, off + len(b)]}
        off += len(b)
        blobs.append(b)
    if metadata:
        head["__metadata__"] = metadata
    h = json.dumps(head, separators=(",", ":")).encode()
    h += b" " * (-len(h) % 8)
    with open(path, "wb") as f:
        f.write(struct.pack("<Q", len(h)))
        f.write(h)
        for b in blobs:
            f.write(b)


def f32_to_bf16_bits(x):
    """Round-to-nearest-even float32 -> bfloat16 bits (finite inputs)."""
    u = np.ascontiguousarray(x, dtype=np.float32).view(np.uint32).astype(np.uint64)
    return ((u + 0x7FFF + ((u >> 16) & 1)) >> 16).astype(np.uint16)


def bf16_bits_to_f32(bits):
    return (np.asarray(bits, dtype=np.uint16).astype(np.uint32) << 16).view(np.float32)


def npz_load(path):
    """{name: ('F32'|..., array)} from an .npz without pickle."""
    with np.load(Path(path), allow_pickle=False) as z:
        return {k: (np.dtype(z[k].dtype).name, z[k].copy()) for k in z.files}


def load_any(path, names=None):
    p = str(path)
    if p.endswith(".safetensors"):
        return st_load(p, names)
    if p.endswith(".npz"):
        t = npz_load(p)
        return t if names is None else {k: t[k] for k in names}
    raise ValueError(f"unsupported tensor container: {p}")
