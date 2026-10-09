# Restricted line preparation loses exponentially many input positions

Status: **EXACT RESTRICTED FINITE OPERATOR CERTIFICATE**, with an elementary
**SCOPED INPUT-VOLUME OBSTRUCTION**. A sparse line transform can be prepared
by copies and phases in a declared orbit-major layout. Its input contract
does not fit the existing dense coefficient-record supplier at growing f.
No arbitrary-dirty supplier, native layout algorithm or new exponent follows.

## Exact positive identity

Write `A_U=alpha*I+beta*X_U`, where `alpha=(1+i)/2`, `beta=(1-i)/2` and
`X_U` translates by a nonzero binary vector U. For f independent selected
columns, choose one pivot bit in U and restrict each input to the transversal
where those f pivot bits are zero. Let J inject its arbitrary Gaussian
records into the full address cube, placing zero records elsewhere.

Every output address is uniquely `a=t+sum_j p_j U_j`, with t in the
transversal and `p_j` binary. The complete exact prepared field is

```text
(A_U^tensor(f) Jx)_a = alpha^f * (-i)^weight(p) * x_t.
```

The coefficient has common reduced dyadic denominator exponent `ceil(f/2)`.
There is one source value per orbit, copied to all `2^f` orbit addresses.
The physical partial operator also satisfies
`F*(A_U^tensor(f))^-1*(A_U^tensor(f) Jx)=F*Jx`. Thus this preparation can
remove a source-line boundary on its restricted domain algebraically.
It does not repair an arbitrary independent sink or dirty bank.

In orbit-major record order, preparation repeats the representative stream
with a per-copy unit phase and a common dyadic scale. This observation needs
its real buffers, records and precision. Converting the existing interleaved
guarded address layout into that order is a separate paid problem; array
index access in this checker does not establish a native tape cost.

## Complete input contract and volume

The full address cube has exactly `2^f` times as many records as the
transversal. A domain with one independent record per orbit therefore has
input density at most `2^-f`, regardless of its address ordering.

The pinned `original-assembly` source uses `q=ceil(n/b)` radix-digit records
and a power-of-two box satisfying `4n/b<=T<8n/b`. Hence `q/T>1/8`.
Allowed inputs can make all q digit records nonzero. The stated CRT address
map is bijective and its coefficient twists are nonzero, so neither
operation reduces that count. With unchanged independent coefficient-record
semantics, no address permutation can guarantee the f-direction transversal
contract for `f>=3`: its capacity `T/2^f` is smaller than q.

Embedding all q records in a new such cube requires

```text
T_new >= 2^f*q,
T_new/T > 2^(f-3).
```

This counts complete physical records, with unchanged per-record field
semantics. It does not exclude packing several coefficients into a new
payload algebra or a different structured arithmetic supplier; those changes
must account for their own widths, arithmetic and recovery.

In the original fixed-parameter size family, `d=Theta(p^epsilon)` for fixed
`epsilon>0`. A fixed-dimensional macro uses `f=Theta(d)` at its growing root.
For every fixed C,

```text
log(2^(f-3)/p^C) = (f-3)*log(2)-C*log(p) -> infinity.
```

Thus forcing this sparse contract throughout such a supplier consumes more
than any fixed polynomial in p of volume overhead. The reference source's
`Tp=Theta(n)` near-linear input volume cannot retain that overhead for free.
Bounded f, a separate stopping region, other restrictions and fusion remain
open. This is an exclusion of a specific preparation strategy, not a lower
bound on multiplication or sparse transforms.

## Retained discriminator and limits

The [standalone checker](../../code/obstructions/sparse_line_input_encoding.py)
uses exact integer Gaussian numerators and explicit common dyadic grids.
Four workers verified 164 complete restricted basis columns and 51,232
coefficients, plus three complete arbitrary Gaussian fields per case.
Cases are `(h,f,U)=(3,1,7),(4,2,7),(3,3,7),(6,1,21)`.
All prepared, inverse and partial/full endpoints agree exactly. Omitting
the address phase fails; using an input outside the transversal also fails.

Exact finite samples check the original box and density inequalities. Their
radix widths 3,5,9 are free sample parameters; they do not instantiate the
original assembly's additional rule `b=ceil(log2(n))`. The retained JSON key
`original_assembly_samples` names those inequality samples, not complete
assembly parameter instances. This source-review clarification leaves the
original protocol and result bytes unchanged. Additional
growth illustrations deliberately use `epsilon=1/8`, not the inherited
assembly's tiny exponent. They illustrate exact powers only; the all-epsilon
limit above is the mathematical argument. Python runtime is not native tape
timing. [The complete run receipt](../../runs/20261009T034709Z-sparse-line-input/report.md)
preserves all results, source identity and launch/completion times.

From the repository root, standard library only:

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/sparse_line_input_encoding.py --workers 1 --bounded
```

Omit `--bounded` and use `--workers 4 --output <fresh-directory>` to reproduce
the full retained cases. Neither invocation overwrites existing evidence.

Primary provenance: `openai/math` revision
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`,
`preprints/Integer-multiplication-below-n-log-n-September-23-2026/build/sections/08-assembly.tex`,
SHA-256 `763d7945b1e1ec4ebae9b799bcefcc45fa9bae6e2ffad799868a9c3d513dbd4a`.
The relevant sections are *The radix-digit polynomials*, *An explicit
cyclic-convolution layout* and the size relation labeled `eq:sizes`.
This is the existing immutable input `original-assembly`; the checker needs
no downloaded source at runtime.
