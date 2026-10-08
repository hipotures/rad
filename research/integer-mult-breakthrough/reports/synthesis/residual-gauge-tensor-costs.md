# Residual monomial synthesis: exact finite words and tensor costs

**Status: exact finite Gaussian operator words, an analytic direct-sum obstruction, and a linear-depth control. No native recursion, precision guarantee or multiplication improvement is claimed.**

The completed constant-scalar/common-frame searches omit independent per-address monomial actions and shears between differing logical frames. This experiment broadens the literal physical operator word. A one-bit construction has no C child on its two data banks, suggesting large recursive savings if extrapolated carelessly. Tensor replication exposes the omitted cost. A second exact word compresses the exponential direct sum to linearly many address-controlled stages; those stages still grow with the number of replicated columns.

## Direct physical Pauli word

Let `alpha=(1+i)/2`, `beta=(1-i)/2`, and X interchange the two one-bit addresses. Then

```text
C = [[alpha,beta],[beta,alpha]] = alpha*I + beta*X.
```

Thus `y+=C*x` can be performed using two Gaussian coefficient shears and a reversible source-address interchange, with x restored. For `N=h*f` active address bits, the tensor expansion is

```text
C_h tensor f = sum_S alpha^(N-|S|)*beta^|S| * X_S.
```

Every coefficient is nonzero and has squared norm `2^-N`. A Gray-code walk through all S changes just one source address bit between terms, restores the source at the end, and uses `2^N` coefficient shears and `2^N` XOR-address permutations. Its coefficients have denominator at most `2^ceil(N/2)`.

The finite experiment also transforms an independent arbitrary-dirty helper by one separately counted full-width `C_h tensor f` call. That helper call is not concealed or described as scratch restoration. The complete target map is

```text
x -> x,
y -> y + (C_h tensor f)*x,
d -> (C_h tensor f)*d.
```

Every initial source, sink and dirty-helper address column was checked. This is a physical operator construction outside the earlier constant/common-frame logical state model: the data shears do not supply the old common-frame endpoint chronology. Its favorable child count is not an invocation histogram certified by that model, and a small f example cannot establish an all-size primitive.

## Why one-layer monomial sums cannot compress the tensor

The Pauli operators `X^u Z^v` are orthogonal under the Hilbert-Schmidt pairing and form a basis of the `2^N by 2^N` matrix space. Projecting the tensor matrix onto every basis element gives exactly the `2^N` X-only coefficients above. Therefore its direct Pauli-sum representation has that many necessary nonzero terms; alternative phases cannot remove them.

There is a simpler stronger obstruction. Every monomial operator, including an arbitrary address permutation followed by arbitrary per-address diagonal multipliers, has at most one nonzero entry in each row. A sum of K such operators has at most K entries per row. The C tensor has all `2^N` entries nonzero in every row, so **any direct linear sum of monomial operators needs at least `2^N` terms**. This covers more than Pauli or quadratic-unit gauges, and does not depend on their coefficient ring.

The restriction is essential: a layered circuit may create exponentially many paths from a small number of stages. If a circuit begins with monomial bank rows and uses only monomial operations, diagonal scales and additive two-bank/address shears, each additive stage at most doubles the maximum number of nonzero initial columns in an output row. Producing a dense C row therefore needs at least N additive stages. This is only a support-growth bound in a circuit without mixing children; it neither excludes the ordinary N-layer construction nor bounds a circuit that shares useful smaller-width C calls.

## A compressed, reversible layered control

The direct sum's width can be compressed. The exact dyadic factorization is

```text
U = [[1,-i],[0,1]],
D = diag((1+i)/2,1+i),
L = [[1,0],[-i,1]],
C = L*D*U.
```

Both diagonal entries are Gaussian-dyadic units, with inverses `1-i` and `(1-i)/2`. For each selected address bit, U adds `-i` times the high-address value to the low-address value, D applies its two conditional scales, and L adds `-i` times the updated low value to the high value. This acts in place and requires no clean initialization. Repeating across all N bits gives the C tensor.

The complete source-preserving word factors every transform, including the required dirty-helper map:

```text
x <- (C_h tensor f)*x;
y += x;
x <- (C_h tensor f)^-1*x;
d <- (C_h tensor f)*d.
```

No opaque C calls remain. The word contains `6N` conditional-address shears, `3N` conditional-address diagonal stages and one ordinary bank copy: **`9N+1` whole-bank stages**. They correspond to `3N*2^N` elementary two-address additions and the same number of individual diagonal multiplications, plus the bank copy. These stages are paid operations on many address pairs, not zero-cost gauge changes or constant-time substitutes for a replicated child.

Completed tensor factors are unitary. For U, DU, the two inverse prefixes, and the ordinary two-bank copy, the exact Gram trace is 3 and determinant is 1. Hence their squared singular values are `(3+sqrt(5))/2` and `(3-sqrt(5))/2`, lying strictly between 1/3 and3. At any full-word prefix there is at most one incomplete bit factor and one bank-copy block after unitary completed factors. Both its norm and inverse norm are therefore less than3, independently of N.

This conditioning statement is not a fixed-point precision theorem. A native implementation must still pay conditional-address routing, stored buffers, repeated rounding and coefficient precision. There are linearly many stages, and a vector error guarantee must be translated to the required coordinate/word error norm. The finite exact rational replay does not settle that translation. The usual layered transform already has this growing stage count; eliminating opaque calls is not an exponent improvement.

## Four-case exact outcomes and preserved failure

Both independent words were checked at `(h,f)=(1,1),(1,2),(2,2),(2,3)`:

| N | Direct coefficient shears | Direct address XORs | Compressed whole-bank stages | Complete initial columns |
|---:|---:|---:|---:|---:|
| 1 | 2 | 2 | 10 | 6 |
| 2 | 4 | 4 | 19 | 12 |
| 4 | 16 | 16 | 37 | 48 |
| 6 | 64 | 64 | 55 | 192 |

All positive complete-column replays pass. Omitting a direct term, extrapolating only the two one-bit endpoint terms to a larger tensor, changing a compressed shear's sign, and omitting a conditional scale each give explicit single-payload counterexamples. Full projection checks all `4^N` Pauli basis elements, including those with zero coefficient.

The first compressed implementation exchanged the low/high entries of the inverse conditional scale. Complete-column replay rejected it before any accepted result was produced. Its original protocol and observed failure are preserved in [the failed run](../../runs/20261008T231309Z-synthesis-compressed-tensor-failed/). The [minimal reconstruction patch](../../fixtures/synthesis/compressed-inverse-order-failure.patch) regenerates the failed source exactly from the corrected source; its SHA256 matches the original protocol. The repaired attempt uses a fresh run and output path. A bounded verifier deliberately restores that incorrect ordering and requires rejection.

## Reproduction and limits

From the repository root:

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/pauli_tensor_discriminator.py \
  --workers 4 --output research/integer-mult-breakthrough/work/synthesis/NEW-PAULI/results
python3 -B research/integer-mult-breakthrough/code/synthesis/compressed_tensor_chronology.py \
  --workers 4 --output research/integer-mult-breakthrough/work/synthesis/NEW-COMPRESSED/results
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_tensor_chronologies.py
```

Only Python's standard library is used. The [direct receipts](../../runs/20261008T230433Z-synthesis-pauli-tensor/results/certificate.json) and [repaired compressed receipts](../../runs/20261008T231328Z-synthesis-compressed-tensor/results/certificate.json) retain exact counts, basis-projection hashes, every compressed event, scalar/address maps, negative witnesses, source hashes and worker allocation. Original evidence is unchanged in ignored `work/synthesis/20261008T230320Z-pauli-tensor/results/`, `work/synthesis/20261008T231130Z-compressed-tensor/results/`, and `work/synthesis/20261008T231235Z-compressed-tensor-repair/results/`. The short failed attempt has no retained full stdout/stderr log; its observed exception and exact reconstruction are explicitly recorded instead.

The reusable bounded verifier checks f=1 and f=2 for both words, all matched corruption controls and the inverse-order regression; its [recorded receipt](../../runs/20261008T231657Z-synthesis-tensor-ci/results/check.json) passes. Its scope is finite operators and small-factor conditioning, not native costs. The direct one-layer route is rejected as a constant/poly(f)-overhead mechanism. The compressed route is retained as an exact control for future shared chronologies. A useful next mechanism must share layers or use different operators/embeddings rather than charging the same growing number of address operations as a constant. These elementary identities and their independent executable checks were developed with OpenAI Codex; no external novelty or formal verification is claimed.
