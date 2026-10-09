# Independent logical buffer review of the partial product word

Status: **INDEPENDENT ANALYTICAL SOURCE REVIEW**. This review does not
independently replay the producer's arithmetic packet or establish a
native tape, arbitrary-dirty or multiplication-exponent theorem.

The inspected source is
`code/complex/partial_product_prefix_audit.py`, SHA256
`12fdf73ca5d4b0963b42db1dd5b4ec55e4429e31823ff82508594ea2eedc4219`.
Its endpoint reference is
`code/complex/partial_kernel_product_algebra.py`, SHA256
`3e56ceb544baa77441c6371c248ddabe770769940e8c3dc32b6ac683a9393553`.
The assertions and code were read directly on 2026-10-09 UTC.

Let E(D) be the additional simultaneously live Gaussian coefficient
buffers beyond the caller's two existing length-D input arrays.
Four half-input copies consume 2D. The P branch then peaks at
`2D+E(D/2)`. Keeping P adds D/2, so Q peaks at
`5D/2+E(D/2)`. Keeping P and Q consumes D; the two half-length
source sums consume another D. R therefore peaks at
`4D+E(D/2)`.

After R, the two sum arrays are released. The remaining slices,
P/Q/R arrays, the decoded output halves and their final concatenation
consume `2D+3D/2+D+D=11D/2` extra coefficients. The source's logical
release operations leave the two original inputs and one final output,
exactly 3D coefficients at the endpoint. Thus

```text
E(1)=1,
E(D)=max(4D+E(D/2),11D/2),
E(2)=11,
E(D)=8D-5 for D>=2.
```

For D>=4, the first term equals `8D-5` and exceeds `11D/2`; the base
D=2 separately uses the second term. Adding the two existing inputs
gives the stated total logical coefficient-array peak `10D-5`.

The conclusion concerns the explicit mathematical buffer word.
Python slice objects, reference counts, list-construction temporaries,
allocator overhead and integer object storage are not measured by it.
The source acknowledges this scope. Fixed scalar arithmetic registers
and native multiplication word buffers require an additional O(p+s)
bit allowance, separate from a Gaussian-coefficient array count.
The producer's own finite arithmetic/prefix receipts remain producer
evidence; this review verifies the storage recurrence and its closed
form only.
