#!/usr/bin/env python3
"""Import-free finite-field/core replay and scoped packing/transfer audit.

Exact finite identities and integer products are verified. Python array
gathers, coefficient transpose and native integer multiplication cost are
not certified here. The exponent ledger is conditional, not a new kappa.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
import json
from math import lcm
from pathlib import Path
import random
import time


ZERO = (F(0), F(0))
ONE = (F(1), F(0))
I = (F(0), F(1))
ALPHA = (F(1, 2), F(1, 2))
TOPIC = Path(__file__).resolve().parents[2]
FIXTURE = TOPIC / 'fixtures/transfers/field-cyclic-producer-contract.json'


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def neg(a):
    return -a[0], -a[1]


def mul(a, b):
    return a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0]


def scale(a, q):
    return a[0]*q, a[1]*q


def power(a, n):
    answer = ONE
    for _ in range(n):
        answer = mul(answer, a)
    return answer


def reciprocal(a):
    norm = a[0]*a[0] + a[1]*a[1]
    return a[0]/norm, -a[1]/norm


def text_gaussian(a):
    return [str(a[0]), str(a[1])]


def polynomial_product_mod(a, b, polynomial, n):
    # Independently form the unreduced polynomial, then perform long division.
    product = 0
    for j in range(n):
        if (b >> j) & 1:
            product ^= a << j
    while product.bit_length() > n:
        product ^= polynomial << (product.bit_length() - n - 1)
    return product


def field_power(a, exponent, polynomial, n):
    answer = 1
    while exponent:
        if exponent & 1:
            answer = polynomial_product_mod(answer, a, polynomial, n)
        a = polynomial_product_mod(a, a, polynomial, n)
        exponent >>= 1
    return answer


def field_trace(a, polynomial, n):
    answer = 0
    for j in range(n):
        answer ^= field_power(a, 1 << j, polynomial, n)
    if answer not in (0, 1):
        raise ValueError('Supplied field has a non-prime-field trace')
    return answer


def binary_image(columns, value):
    answer = 0
    for j, column in enumerate(columns):
        if (value >> j) & 1:
            answer ^= column
    return answer


def independent_geometry(contract):
    n, polynomial = contract['n'], contract['polynomial']
    D, M = 1 << n, (1 << n) - 1
    powers = [field_power(2, j, polynomial, n) for j in range(M)]
    if sorted(powers) != list(range(1, D)) or field_power(2, M, polynomial, n) != 1:
        raise ValueError('Supplied element/polynomial does not enumerate the field')
    gram = [sum(field_trace(polynomial_product_mod(1 << i, 1 << j,
                polynomial, n), polynomial, n) << i for i in range(n)) for j in range(n)]
    images = {binary_image(gram, x): x for x in range(D)}
    if len(images) != D:
        raise ValueError('Trace Gram matrix is singular')
    dual = [images[1 << j] for j in range(n)]
    for x in range(D):
        for y in range(D):
            xy = polynomial_product_mod(binary_image(dual, x), y, polynomial, n)
            if field_trace(xy, polynomial, n) != ((x & y).bit_count() & 1):
                raise ValueError('Independent trace-dual/dot equality failed')
    kernel = [1 - 2*field_trace(x, polynomial, n) for x in powers]
    inputs = [0] + [powers[(-j) % M] for j in range(M)]
    outputs = [0] + [binary_image(gram, x) for x in powers]
    actual = dict(n=n, d=D, L=M, polynomial=polynomial,
                  trace_Gram_columns=gram, dual_columns=dual, kernel=kernel,
                  input_order=inputs, output_order=outputs)
    if actual != contract:
        raise ValueError('Independent geometry disagrees with immutable producer contract')
    return actual


def signed_product_digits(values, kernel, digit_bits):
    M = len(values)
    B = 1 << digit_bits
    # This differs from the producer's Horner encoding. All positions remain
    # reserved even when the numeric integer has shorter bit length or is zero.
    left = sum(z * (B ** j) for j, z in enumerate(values))
    right = sum(z * (B ** j) for j, z in enumerate(kernel))
    product = left * right
    remainder = product
    digits = []
    for _ in range(2*M - 1):
        digit = remainder % B
        if digit >= B//2:
            digit -= B
        digits.append(digit)
        remainder = (remainder - digit)//B
    return digits, remainder, dict(reserved_input_bits_each=M*digit_bits,
        variable_numeric_bits=abs(left).bit_length(), kernel_numeric_bits=abs(right).bit_length(),
        product_numeric_bits=abs(product).bit_length(), digit_bits=digit_bits)


def core(values, geometry, backwards=False):
    D, M, k = geometry['d'], geometry['L'], geometry['kernel']
    kernel = [k[(-j) % M] - 1 for j in range(M)] if backwards else k
    denominator = lcm(*(q.denominator for z in values for q in z))
    if denominator & (denominator - 1):
        raise ValueError('Input lies outside the stated Gaussian-dyadic interface')
    arrays = [[int(z[part]*denominator) for z in values] for part in (0, 1)]
    maximum = max((abs(z) for array in arrays for z in array), default=0)
    bound = M*maximum*max(abs(z) for z in kernel)
    digit_bits = max(1, (2*bound).bit_length())
    outputs, receipts = [], []
    for array in arrays:
        digits, leftover, receipt = signed_product_digits(array, kernel, digit_bits)
        ordinary = [sum(array[j]*kernel[index-j] for j in range(M)
                        if 0 <= index-j < M) for index in range(2*M-1)]
        if leftover or digits != ordinary:
            raise ValueError('Signed packing disagrees with exact ordinary convolution')
        folded = [digits[j] + (digits[j+M] if j+M < len(digits) else 0)
                  for j in range(M)]
        outputs.append(folded)
        receipts.append(receipt)
    divisor = denominator*(D if backwards else 1)
    return [(F(outputs[0][j], divisor), F(outputs[1][j], divisor)) for j in range(M)], receipts


def scatter(order, values):
    output = [ZERO]*len(order)
    for address, value in zip(order, values):
        output[address] = value
    return output


def transform(initial, geometry, backwards=False, corruption=None):
    n, D, M = geometry['n'], geometry['d'], geometry['L']
    # Early global normalization is explicit. Its inverse is last in the
    # inverse word. List gathers are finite algebra only, not paid routing.
    if not backwards:
        values = [mul(power((F(0), F(-1)), j.bit_count()), z)
                  for j, z in enumerate(initial)]
        values = [mul(power(ALPHA, n), z) for z in values]
        ordered = [values[j] for j in geometry['input_order']]
        nonzero = [add(z, neg(ordered[0])) for z in ordered[1:]]
        transformed, receipts = core(nonzero, geometry)
        zero = ordered[0] if corruption == 'omit D border scale' else scale(ordered[0], D)
        if corruption != 'omit border sum':
            for z in transformed:
                zero = add(zero, neg(z))
        values = scatter(geometry['output_order'], [zero] + transformed)
        values = [mul(power((F(0), F(-1)), j.bit_count()), z)
                  for j, z in enumerate(values)]
    else:
        values = [mul(power(I, j.bit_count()), z) for j, z in enumerate(initial)]
        ordered = [values[j] for j in geometry['output_order']]
        zero = ordered[0]
        for z in ordered[1:]:
            zero = add(zero, z)
        zero = scale(zero, F(1, D))
        transformed, receipts = core(ordered[1:], geometry, True)
        if corruption == 'wrong inverse kernel':
            transformed[0] = add(transformed[0], ONE)
        values = scatter(geometry['input_order'], [zero] + [add(z, zero) for z in transformed])
        values = [mul(power(I, j.bit_count()), z) for j, z in enumerate(values)]
        values = [mul(reciprocal(power(ALPHA, n)), z) for z in values]
    return values, receipts


def tensor_entry(n, row, column):
    return mul(power(ALPHA, n), power((F(0), F(-1)), (row ^ column).bit_count()))


def tensor_apply(values, n):
    result = []
    for row in range(1 << n):
        answer = ZERO
        for column, value in enumerate(values):
            answer = add(answer, mul(tensor_entry(n, row, column), value))
        result.append(answer)
    return result


def packing_slice_ledger(geometry):
    n, M = geometry['n'], geometry['L']
    cases = []
    for payload_bits, chunk_bits in ((17, 4), (65, 8), (129, 8)):
        rng = random.Random(20261008 + 1000*n + payload_bits)
        values = [rng.randrange(-(1 << (payload_bits-1)), 1 << (payload_bits-1))
                  for _ in range(M)]
        kernel = geometry['kernel']
        expected = [sum(values[j]*kernel[(i-j) % M] for j in range(M)) for i in range(M)]
        # Uniform-width signed radix expansion, using enough signed chunks.
        slice_count = (payload_bits + chunk_bits - 1)//chunk_bits + 1
        remaining = list(values)
        total = [0]*M
        receipts = []
        for t in range(slice_count):
            chunk = []
            for j in range(M):
                z = remaining[j] % (1 << chunk_bits)
                if z >= (1 << (chunk_bits-1)):
                    z -= 1 << chunk_bits
                chunk.append(z)
                remaining[j] = (remaining[j]-z) >> chunk_bits
            # Kernel max=1, |chunk|<=2^(b-1); 2*bound < 2^(b+n+1).
            spacing = chunk_bits+n+1
            digits, leftover, receipt = signed_product_digits(chunk, kernel, spacing)
            ordinary = [sum(chunk[j]*kernel[index-j] for j in range(M)
                            if 0 <= index-j < M) for index in range(2*M-1)]
            if leftover or digits != ordinary:
                raise ValueError('Uniform slice guard failed')
            for j in range(M):
                total[j] += (digits[j] + (digits[j+M] if j+M < len(digits) else 0)) << (t*chunk_bits)
            receipts.append(receipt)
        if any(remaining) or total != expected:
            raise ValueError('Long coefficient slicing/reconstruction failed')
        cases.append(dict(payload_bits=payload_bits, chunk_bits=chunk_bits,
            signed_slice_count=slice_count, digit_spacing=chunk_bits+n+1,
            real_integer_products=slice_count, physical_input_bits=M*payload_bits,
            reserved_product_operand_bits_each=M*(chunk_bits+n+1),
            packed_volume_inflation=str(F(slice_count*(chunk_bits+n+1), payload_bits)),
            per_product=receipts,
            transpose_status='Array slicing is a finite algebra oracle here. A native full-payload transpose is still required.'))
    return cases


def scoped_exponent_ledger():
    rows = []
    for epsilon in (F(1, 4), F(1, 2), F(3, 4)):
        for call_saving in (F(1, 10000), F(1, 1000)):
            resulting = epsilon*call_saving
            if resulting >= call_saving:
                raise ValueError('Scoped bootstrap discriminator failed')
            rows.append(dict(epsilon=str(epsilon), assumed_general_multiplier_kappa=str(call_saving),
                unchanged_outer_kappa=str(resulting), improves_assumed_kappa=False,
                primitive_saving_needed_for_target_1e_minus_4=str(F(1, 10000)/epsilon)))
    return dict(rows=rows,
        premise='Complete selected-width primitive cost O(V*d^gamma*polylog(d)); p/d rounds and d=p^epsilon, 0<epsilon<1.',
        deduction='outer exponent=1-epsilon*(1-gamma); an assumed general multiplier gamma=1-kappa_call yields only epsilon*kappa_call.',
        limitations='Not a lower bound on fixed kernels, other outer architectures, nonlinear couplings, or every realizable same-width recurrence.')


def audit_case(contract):
    started = time.monotonic()
    g = independent_geometry(contract)
    n, D, M, k = g['n'], g['d'], g['L'], g['kernel']
    if sum(k) != -1:
        raise ValueError('Core character sum failed')
    for i in range(M):
        for j in range(M):
            product = sum(k[(i-ell) % M]*(k[(j-ell) % M]-1) for ell in range(M))
            if product != (D if i == j else 0):
                raise ValueError('Signed core inverse matrix failed')
    for row in range(D):
        for column in range(D):
            exponent = (g['output_order'][row] & g['input_order'][column]).bit_count() & 1
            expected = 1-2*exponent
            observed = 1 if row == 0 or column == 0 else k[(row-column) % M]
            if expected != observed:
                raise ValueError('Independently reordered full Walsh matrix failed')
            # A*diag(D,K)*B evaluated explicitly, including both borders.
            lower = [(-sum(k) if column == 0 else k[(ell-(column-1)) % M]) for ell in range(M)]
            factored = ((D if column == 0 else 0) - sum(lower)) if row == 0 else lower[row-1]
            if factored != observed:
                raise ValueError('Zero-border factorization failed')
    digest = sha256()
    checks = 0
    for bank in range(3):
        for address in range(D):
            initial = [[ZERO]*D for _ in range(3)]
            initial[bank][address] = (F(1), F(1))
            x1, _ = transform(initial[0], g)
            sink = [add(y, x) for y, x in zip(initial[1], x1)]
            source, _ = transform(x1, g, True)
            dirty, _ = transform(initial[2], g)
            expected_sink = [add(y, z) for y, z in zip(initial[1], tensor_apply(initial[0], n))]
            expected_dirty = tensor_apply(initial[2], n)
            if source != initial[0] or sink != expected_sink or dirty != expected_dirty:
                raise ValueError('Complete independent Gaussian dirty word failed')
            digest.update(json.dumps([bank, address, [[text_gaussian(z) for z in arr]
                for arr in (source, sink, dirty)]], separators=(',', ':')).encode())
            checks += 1
    rng = random.Random(20261008+n)
    all_fields = [[(F(rng.randrange(-100, 101), 16), F(rng.randrange(-100, 101), 8))
                  for _ in range(D)] for _ in range(3)]
    transformed, receipts = transform(all_fields[0], g)
    source, _ = transform(transformed, g, True)
    dirty, _ = transform(all_fields[2], g)
    sink = [add(y, z) for y, z in zip(all_fields[1], transformed)]
    if (source != all_fields[0] or dirty != tensor_apply(all_fields[2], n) or
        sink != [add(y, z) for y, z in zip(all_fields[1], tensor_apply(all_fields[0], n))]):
        raise ValueError('Mixed arbitrary-dirty Gaussian replay failed')
    controls = []
    single = [ZERO]*D
    single[0] = ONE
    expected = tensor_apply(single, n)
    for corruption in ('omit D border scale', 'omit border sum'):
        wrong, _ = transform(single, g, corruption=corruption)
        if wrong == expected:
            raise ValueError('Matched border corruption was not detected')
        controls.append(corruption)
    # Wrong inverse sign/orientation is independently detected at matrix level.
    wrong_inverse = [k[j]-1 for j in range(M)]
    if all(sum(k[(i-ell) % M]*wrong_inverse[(ell-j) % M] for ell in range(M)) ==
           (D if i == j else 0) for i in range(M) for j in range(M)):
        # Small m-sequences can be reversal-invariant; truncation still fails.
        wrong_inverse[0] += 2
    if all(sum(k[(i-ell) % M]*wrong_inverse[(ell-j) % M] for ell in range(M)) ==
           (D if i == j else 0) for i in range(M) for j in range(M)):
        raise ValueError('Wrong inverse-kernel negative control was not detected')
    controls.append('wrong inverse-kernel orientation or coefficient')
    digits, leftover, _ = signed_product_digits([7]*M, [1]*M, 2)
    ordinary = [7*min(j+1, 2*M-1-j, M) for j in range(2*M-1)]
    if not leftover and digits == ordinary:
        raise ValueError('Insufficient balanced radix was not rejected')
    controls.append('insufficient radix guard')
    _, zero_receipts = core([ZERO]*M, g)
    if not all(z['variable_numeric_bits'] == 0 and z['reserved_input_bits_each'] >= M for z in zero_receipts):
        raise ValueError('Zero numeric integer must retain the complete physical positions')
    controls.append('zero numeric integer still reserves all M physical positions')
    return dict(active_bits=n, dimension=D, core_length=M, geometry_contract_match=True,
        complete_word_basis_columns=checks, Gaussian_basis_value=['1','1'], mixed_three_bank_fields_pass=True,
        basis_digest=digest.hexdigest(), exact_nonrecursive_real_integer_products_per_word=6,
        sample_forward_products=receipts, signed_inverse_denominator=D,
        packing_slices=packing_slice_ledger(g), negative_controls=controls,
        seconds=time.monotonic()-started,
        scope='Exact finite algebra and nonrecursive integer products. Python gathers, slicing, normalization and native tape costs remain explicit interface obligations.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--small', action='store_true')
    args = parser.parse_args()
    source = Path(__file__).resolve()
    hashes = {str(path.relative_to(TOPIC)): sha256(path.read_bytes()).hexdigest()
              for path in (source, FIXTURE)}
    fixture = json.loads(FIXTURE.read_text())
    cases = fixture['cases'][:1] if args.small else fixture['cases']
    started = time.monotonic()
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        native_threads_per_worker=1, source_and_input_sha256=hashes,
        producer_source_sha256=fixture['producer_source_sha256'],
        producer_certificate_sha256=fixture['producer_certificate_sha256'],
        cases=[c['n'] for c in cases], seeds='20261008+n; slice fixtures use 20261008+1000*n+payload_bits',
        independence='No producer imports; polynomial long division, exhaustive Gram inverse, Walsh dot entries, signed monomial encoding and tensor entries are reconstructed here.')
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(audit_case, cases))
    if any(sha256((TOPIC/path).read_bytes()).hexdigest() != value for path, value in hashes.items()):
        raise ValueError('Effective source/input changed during the attempt')
    result = dict(status='INDEPENDENT FINITE ALGEBRA AND SCOPED COST AUDIT PASS', cases=results,
        exponent_ledger=scoped_exponent_ledger(), seconds=time.monotonic()-started,
        scope='No native transform, faster fixed-kernel multiplier, or all-size exponent is certified.')
    if args.output:
        (args.output/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(status=result['status'], cases=len(results),
        complete_word_basis_columns=sum(c['complete_word_basis_columns'] for c in results),
        seconds=result['seconds'], scope=result['scope']), sort_keys=True))


if __name__ == '__main__':
    main()
