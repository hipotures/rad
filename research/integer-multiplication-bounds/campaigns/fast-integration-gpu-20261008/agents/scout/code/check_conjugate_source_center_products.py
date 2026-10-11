#!/usr/bin/env python3
"""Derive conjugate DATA and copied-center invariants from primitive vectors."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
from itertools import combinations
import json
from pathlib import Path


def address(vector, beta):
    return [x-beta*sum(vector) for x in vector]


def gram(vector):
    return sum(x*x for x in vector)-sum(vector)**2/9


def verify(vector, beta, star, h):
    norm = gram(vector)
    assert norm
    a = address(vector, beta)
    b = [x/norm for x in address(vector, star)]
    conjugate_a = address(vector, star)
    conjugate_b = [x/norm for x in address(vector, beta)]
    assert sum(x*y for x, y in zip(a, b)) == 1
    assert all(a+b+conjugate_a+conjugate_b)
    products = [x*y for x, y in zip(a, b)]
    assert products == [x*y for x, y in zip(conjugate_a, conjugate_b)]
    # Full projectors transpose. This proves no ordered auxiliary NE profile
    # identity and does not substitute for recomputing local transition ranks.
    assert all(a[i]*b[j] == conjugate_a[j]*conjugate_b[i]
               for i in range(h) for j in range(h))
    return products


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    cases = []
    for h, beta in ((23, F(1, 15)), (25, F(7, 207))):
        star = (1-9*beta)/(9*(1-h*beta))
        assert beta+star-h*beta*star == F(1, 9)
        source_count = 0
        for t in combinations(range(h), 3):
            vector = [F(int(i in t)) for i in range(h)]
            assert gram(vector) == 2
            products = verify(vector, beta, star, h)
            source_count += 1
        representative = [F(int(i < 3)) for i in range(h)]
        p = verify(representative, beta, star, h)
        for common in range(h):
            vector = [F(int(i == common))+F(2, h-9) for i in range(h)]
            assert gram(vector) == F(-4, h-9)
            verify(vector, beta, star, h)
        center = [F(int(i == 0))+F(2, h-9) for i in range(h)]
        center_products = verify(center, beta, star, h)
        cases.append({'h': h, 'beta': str(beta), 'conjugate': str(star),
                      'source_triples_checked': source_count,
                      'copied_centers_checked': h,
                      'source_inside_outside_products': [str(p[0]), str(p[3])],
                      'center_common_outside_products': [str(center_products[0]),
                                                         str(center_products[1])]})
    result = {
        'utc': datetime.now(timezone.utc).isoformat(),
        'status': 'PASS PRIMITIVE CONJUGATE SOURCE/COPIED-CENTER PRODUCT INVARIANTS',
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'cases': cases,
        'algebra': 'L_beta L_star=H0=I-J/9. For each unchanged primitive source or center v, primal=L_beta v and dual=L_star v/(v^T H0 v); conjugation swaps these factors. All coordinate products remain equal and the projector transposes.',
        'DATA_scope': 'A closed DATA formula depending on normalized coordinate products and fixed physical row/column geometry is identical for either conjugate. Actual source permutation, source/sink dispatch, center spaces and paid word interfaces must still be bound separately.',
        'limitations': 'No equality of ordered auxiliary NE profiles follows from projector transposition. Actual local profiles, literal word interfaces and full recurrence assembly remain separate gates; no kappa is claimed.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
