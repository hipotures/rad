# A smaller arithmetic constant and its complete dirty scalar transcription

Status: **EXACT FINITE SCALAR COMPONENT** and **ALL-SIZE TRANSCRIPTION LEMMA**.
An actual native phase/routing ledger remains open. No larger kappa is asserted.

## Primary mechanism and independent reconstruction

Alman and Rao's [Algorithm 5, arXiv:2211.06459v2](https://arxiv.org/pdf/2211.06459v2)
shares a rank-two correction with sparse Walsh terms, and defers powers of two
to the recursion's leaves. Its leading arithmetic constant is23/24.
The [independent implementation](../../code/obstructions/wht_arithmetic_dirty_echo.py)
constructs every scalar signal explicitly; it does not import their software.
The [source pins](../../configs/obstructions/wht-primary-source-pins.json)
retain the downloaded PDF identity and revision.

Write N=2^n, ell=floor(n/3), r=n mod3. Each three-bit level contributes
22N/8 additions and N/8 divisions by two. The final base transforms contribute
rN additions. Multiplication by one is an alias in our literal word, so the
number of nontrivial leaf scales is N-2^r. Thus our exact counts are

```text
additions = 22N*ell/8 + rN,
divisions = N*ell/8,
leaf scales = N-2^r.
```

These counts use the complete recurrence rather than fractional leading-term
bookkeeping at n not divisible by three. They satisfy the paper's upper bound.
At N=8 the local body has23 operations, while the complete first instance has
another seven leaf scales, for30. Paying30 at one instance does not invalidate
the asymptotic leading constant, and charging only23 for that instance would
omit its inputs' scalings.

The complete clean SSA coefficient rows have an exact additional bound:
every prefix is integral on the input grid, and its maximum row-L1 norm is
7N/4 when N>=8 (N for the smaller base cases). At a recursive node the seven
doubled children are disjoint input blocks; their undivided total has norm
14 times its block length and incoming scale. Dividing by two preserves the
known doubled grid. Every remaining partial output changes a block's sign or
retains it, and has norm at most the scaled node width. Deeper nodes satisfy
2^k*N_node<=N. The source checks multiplication temporaries as well as sums.
This is an analytical coefficient bound, not free normalization or repacking.

## Arbitrary dirty helpers instead of initialized SSA storage

For any linear SSA program with S signals, introduce S arbitrary dirty
scalar helpers. A signal with terms c_j*source_j or c_j*earlier_signal_j
becomes successive shears into its own helper. Call this reversible triangular
word T_x. Its readout is linear in the source vector x and helper vector z:

```text
read(T_x(z)) = H_N*x + L*z.
```

T_0 omits every original-source term and retains every earlier-helper term.
It has the same dirty coefficient matrix L. The literal chronology is

```text
T_x;  y += read;  inverse(T_x);
T_0;  y -= read;  inverse(T_0).
```

Both inverse passes reverse all shear terms and negate their coefficients.
The sources remain unchanged, the helpers return to exactly their original
arbitrary values, and the sinks become y+H_N*x. No helper is overwritten or
initialized. Deleting the zero-source echo leaves L*z in the sinks; the
bounded verifier rejects that shortcut.

This lemma applies over any field supporting the program's scalars, including
Q(i). The finite tests use exact real dyadics. Extension to real and imaginary
components follows from linearity; it is not a separate Gaussian phase check.
Scalar shears require the same actual address operator in a native application.
The transcription supplies no free synchronization between unequal frames.

Dirty values can invalidate the clean divisibility. A safe grid allowance for
this word is P+ell for inputs and helpers on grid2^-P: a leaf scale introduces
no denominator, and each three-bit level introduces at most one division.
Inverse multiplication temporaries obey the same bound because they retrace
the triangular word. The final helpers and integer Walsh sinks return to
grid2^-P. The actual physical representation may retain P+ell throughout;
an exact endpoint does not authorize unpaid output conversion.

## Complete finite results

The four-worker run checks every Walsh coefficient row, all source basis
columns, five seeded fields per size, arbitrary initial sinks, and arbitrary
dirty helpers. The oracle is the direct sign formula, independently evaluated.

| N | Clean SSA operations/helpers | Complete dirty scalar shears | Clean prefix row-L1 | Checked sink values |
| ---: | ---: | ---: | ---: | ---: |
|8|30|206|14|104|
|16|76|540|28|336|
|64|431|3130|112|4416|
|128|990|7284|224|17024|

The largest case took4.31 seconds. The observed dirty peaks and denominators
are measurements of the retained seeded fields, not worst-case guards.
The clean symbolic bounds apply to all inputs of each checked size.

## What this changes and what remains

This is a concrete cancellation-allowing arithmetic circuit and an explicit
arbitrary-dirty reversible implementation. It exposes why an arithmetic
operation improvement alone is insufficient: the literal dirty conversion
uses O(N log N) helper banks and several shears per SSA signal. A favorable
Gaussian native child distribution, address movement and precision treatment
must be derived from an alternative sharing/chronology before claiming a
complex-component saving. A constant factor on an unchanged N log N transfer
does not imply any fixed positive kappa.

The next discriminator is to reuse shared signals without giving every SSA
node its own full-width helper, while paying literal sources, sinks and
helper restoration. This implementation is a reference for that experiment,
not a reason to reopen fixed arithmetic-constant parameter sweeps.

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/wht_arithmetic_dirty_echo.py --bounded
python3 -B research/integer-mult-breakthrough/code/obstructions/wht_arithmetic_dirty_echo.py \
  --workers 4 --output /tmp/fresh-wht-dirty-echo.json
```

The analytical transcription and implementation were developed with OpenAI
Codex assistance. An [import-free independent review](../complex/wht-dirty-echo-independent-review.md)
checks its own 30-helper,206-shear N=8 word on all46 source/sink/helper basis
columns and eight dirty fields per seed, with four independent seeds. All
19,872 forward/inverse scalar values pass; omitted-zero-echo and omitted-first-
inverse corruptions fail. The review also accepts the analytical transcription
and stated scalar grid/norm scope. This is internal research review, not
external human review or formal verification.
