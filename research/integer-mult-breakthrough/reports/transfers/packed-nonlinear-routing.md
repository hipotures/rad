# Paid packed nonlinear routing with complete guards

Status: **PROPOSED CONDITIONAL FIXED-TAPE ROUTING LEMMA**, with **EXACT FINITE ADDRESS AND FULL-PAYLOAD CONTROLS**. This is an address permutation supplier, not a Gaussian primitive or a multiplication exponent. It extends the original packed variable-control addition proof to a particular nonlinear control while explicitly changing its required address shape.

## Complete interface and construction

Fix `h>=4` address slots inside one role stream. Four distinct slots, named x, z, y and w, each have the complete range `[2^L]`, where `L=(f+1)K`, `K>=6`, `f>=1` and `0<=rho<K`. Every intervening prefix, suffix, row and other address slot is complete and retained. Payloads contain arbitrary complete R-bit records; they are never initialized as scratch. On the first f selected positions `j_i=rho+iK`, the target permutation is

```text
x -> x, z -> z, y[j_i] -> y[j_i] XOR (x[j_i] AND z[j_i]), w -> w.
```

Every other bit of y, including its extra complete K-axis chunk, is restored. This is a columnwise Toffoli, with w an arbitrary existing address companion. It does not assert universality for arbitrary permutations.

For each column put `c_i=x[j_i] AND z[j_i]`. Apply the same eight chronological packed rotations as in the original variable-control addition lemma, using c_i rather than a source bit. In local integer coordinates, c is fixed throughout all eight operations. When c=0 the local word is identity; when c=1 the word returns the arbitrary companion and flips the target parity while retaining both quotients. The proof uses only the Boolean value and its independence from the target/companion being updated. It therefore applies to this nonlinear predicate without a new algebraic oracle.

The difference from the original CNOT supplier is essential: ALL f selected positions participate in the rotations. The segment beginning at `j_(f-1)` ends at `rho+fK-1`, which lies inside the complete `(f+1)K` range. The extra chunk supplies its full guard, including the crossing segment when rho is nonzero. No final elementary top Toffoli is invoked for free. The previously supplied elementary operation concerns two address bits and does not automatically supply a three-bit top gate.

Let B contain addresses for which any of the 2f used target/companion guard values fails `10<=g<=2^(K-1)-11`. The segments are disjoint and each guard is a complete `(K-1)`-bit range, so

```text
|B|/M <= delta = min(1,80 f 2^-K).
```

Outside B, bounded local displacements prevent cross-segment carries, proving that the rotation word S equals the desired Toffoli T. Every rotation is a bijection: its offset reads x, z and the other current slot, never its target. The ideal T is bijective and preserves B because it toggles only the selected target parities. Thus `S(B)=B` follows from bijectivity and agreement outside B. This is an exact set argument, not a conclusion from sampled preservation.

After S, apply `T*S^-1` to B. Its destination address is computed from the current complete address, eight inverse rotations, and the ideal Toffoli. Extract every exceptional COMPLETE R-bit record with its complete destination key, sort the keys, and reinsert those complete records into the holes in original order. Correction does not drop guard data, source fields, coefficients, row indices or companion values. Every output address and payload has a unique preimage.

## Conditional tape bill and shape limits

The retained assumptions are the original paid complete equal-width chunk exchange, ordered cyclic rotation with an offset depending on preceding fields, and complete-record radix correction. A target can be moved last among the four slots and returned for each rotation, using at most sixteen whole-L exchanges across the word. Offset predicates have a fixed polynomial-time bit implementation; there is no discrete-log or table oracle. Write `V=MR` and `A=ceil(log2(2V))`. The conditional bill is

```text
O(V(L^tau+1) + M A^3 + delta M A(R+A)), 0<tau<1.
```

The fixed number of controls changes constants. For a fixed finite sequence of such Toffolis, each complete gate restores its companion and every other slot before the next gate. Add all gates' displayed bills. A length growing with e cannot be hidden in a fixed constant.

In the original long-record family `A=O(p)`, R exceeds every fixed polynomial in p, `f<=p`, and `K/log(p)->infinity`. The setup and repair terms divided by V vanish uniformly, giving `O_h(V((eK)^tau+1))` for fixed h and e comparable to hf. The proof remains conditional on the original paid interfaces and the complete shape at EVERY use. Python address arithmetic and list sorting are finite oracles, not compiled tape implementations or native timings.

An added K-bit range in each of four slots multiplies the address cube by `2^(4K)`. It cannot be called free padding. The K1 payload control concretely grows from 1024 to 16384 records. Existing guard ranges must be exhibited and charged in the current stream shape. The [separate guard-allocation lemma](guarded-slot-layout-transfer.md) obtains them by preprocessing existing selected axes and retaining the same address cube. It does not insert additional records or use zero-valued address bits. A companion ADDRESS slot within a role is different from a Gaussian scalar helper bank.

The exact completed address permutation is independent of payloads and preserves the dyadic grid and coefficient magnitude. Intermediate arithmetic in a surrounding Gaussian network still needs the [endpoint-aware guard contract](endpoint-aware-guards.md), complete row allocation, and a legal child stopping rule.

## Inputs, finite evidence and recovery

The primary proof input is `openai/math` revision `adc7f1241b42e322a6451854ab7e4b4c146bf78a`, [05-layers.tex](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Integer-multiplication-below-n-log-n-September-23-2026/build/sections/05-layers.tex), SHA256 `20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594`. The new proof specializes its Boolean-control calculation and replaces its omitted-top shape. I inspected the pinned source in the read-only PR127 upstream checkout; that downloaded tree is not a runtime dependency or a durable authored artifact.

The checker [packed_toffoli.py](../../code/transfers/packed_toffoli.py), SHA256 `5fc6fb8ce5507fae0568e85d701918cd8ddfe65ed124810eb3edfbfff9fa7f80`, imports only the previously independent [native_gl_review.py](../../code/transfers/native_gl_review.py), SHA256 `1ae606d030f1f71ebe2d2497399601f1cdc6e59aa4e3209527533ecf57432d19`. The [config](../../configs/transfers/packed-toffoli.json), SHA256 `3ad7bcdb5e3c0ced19391d1f0dec5b688e17755ffd5c377962c72c1d5d368910`, pins that effective helper. No producer module or external checkout is imported.

The [actual-UTC four-worker repaired run](../../runs/20261009T033513Z-transfer-packed-toffoli-parse-repair/report.md) exhausts 262144 native quotient representatives at K6/f2/rho0 over all sixteen pairs of low control masks. Its unrepaired failure fraction is exactly 1/512, so omitting correction fails. There are also 4096 seeded complete-address samples, forced carry-free examples, explicit inverses, exceptional-set controls and arbitrary companion restoration. Quotient translations by the representative period commute with each rotation; unused control bits do not enter offsets. The exact native fraction is specific to this declared quotient test, not a general estimate replacing delta.

The separate K1/f2 control replays all 16384 four-field records through the eight literal permutations and full correction sort. Prefix, suffix, both controls, the arbitrary companion and the extra target guard bit are preserved. K1 lies outside the native guard band; all toy records are exceptional. This control verifies complete payload semantics without pretending it establishes a favorable correction fraction.

The [first attempt](../../runs/20261009T033427Z-transfer-packed-toffoli/report.md) failed during parsing before scientific main because of an invalid hyphenated keyword. Its original launcher/failure receipt and rejected source SHA256 `7ce6b18dccbff5d295235fc8ff0caaf586e972fa1c2c934e385c733b36b43088` are preserved. The [parse recovery patch](../../fixtures/transfers/packed-toffoli-parse-recovery.patch) reconstructs it from the accepted source. A [real source-recovery run](../../runs/20261009T034420Z-transfer-guard-routing-source-recovery/report.md) verified that exact hash in an isolated ignored tree. No accepted output is assigned to the parse-only version.

Protocols and compact summaries are unchanged original copies in the durable runs. Ignored `work/transfers/<same-run-id>/` contains the originals and disposable recovery copies. They are deterministically regenerable with Python's standard library. The full experiment uses approximately four CPU workers; the bounded CI invocation is

```bash
python3 research/integer-mult-breakthrough/code/transfers/packed_toffoli.py --workers 1
```

The [final bounded one-worker replay](../../runs/20261009T035722Z-transfer-packed-toffoli-bounded/report.md) passed in 1.290869410 seconds with the final source/config/helper.

For a new immutable attempt, append `--output research/integer-mult-breakthrough/work/transfers/<fresh-actual-UTC>-toffoli/results`. Each output path must be absent. The previous source can be recovered with `git apply` in an isolated tree; never replace the live accepted source to reproduce a rejected attempt.

The mathematical leverage is a paid nonlinear address wrapper that preserves complete dirty records and may implement fixed finite nonlinear circuits. It closes neither an improved child histogram nor a same-volume integer-multiplication kernel. A whole canonical primitive and a contracting paid moment remain necessary before an exponent claim.
