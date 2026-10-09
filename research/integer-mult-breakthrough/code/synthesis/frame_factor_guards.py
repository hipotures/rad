"""Validate finite factors before invoking the retained uint16 engine."""


def guard_graph(edges, unary, table, constant=0, order=None):
    vertices = len(unary)
    domain = len(table)
    if not 0 < vertices or not 0 < domain < 65535:
        raise ValueError('Finite factor vertex/domain count is invalid')
    if not isinstance(constant, int) or not 0 <= constant < 65535:
        raise ValueError('Finite factor constant must be a nonnegative uint16 charge')
    for name, rows, width in [('distance', table, domain), ('unary', unary, domain)]:
        if any(len(row) != width for row in rows):
            raise ValueError('Finite factor ' + name + ' table has an invalid shape')
        if any(not isinstance(value, int) or not 0 <= value < 65535
               for row in rows for value in row):
            raise ValueError('Finite factor ' + name + ' charge is outside uint16')
    if order is not None and sorted(order) != list(range(vertices)):
        raise ValueError('Finite factor elimination order is not a permutation')
    maximum = max(value for row in table for value in row)
    total = constant + sum(max(row) for row in unary)
    for edge in edges:
        if len(edge) != 3:
            raise ValueError('Finite factor edge must contain two vertices and a weight')
        a, b, weight = edge
        if any(not isinstance(value, int) for value in edge):
            raise ValueError('Finite factor edge fields must be integers')
        if not 0 <= a < b < vertices or weight < 1:
            raise ValueError('Finite factor edge has invalid vertices/weight')
        total += weight * maximum
    if total >= 65535:
        raise ValueError('Complete nonnegative charge bound exceeds uint16')
    # Each original factor enters precisely one accumulated factor. Its
    # minimum is nonnegative and no larger than the original factor maxima.
    # Thus this full original-factor bound protects every partial sum as
    # well as the final replay, even if the lower-level parser narrows ints.
    return dict(vertices=vertices, frame_domain=domain,
                global_nonnegative_charge_bound=total)
