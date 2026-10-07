"""Frozen symmetric perturbation gate and one constrained intervention rule."""
import statistics


def perturbation_gate(pairs):
    decode = [p['decode_change_pct'] for p in pairs]
    wall = [p['wall_change_pct'] for p in pairs]
    return {
        'complete_pairs': len(pairs),
        'median_decode_change_pct': statistics.median(decode) if decode else None,
        'median_wall_change_pct': statistics.median(wall) if wall else None,
        'pass': len(pairs) == 3 and abs(statistics.median(decode)) <= 3
                and abs(statistics.median(wall)) <= 3
                and sum(abs(d) > 5 or abs(w) > 5 for d, w in zip(decode, wall)) < 2
                and all(abs(d) <= 10 and abs(w) <= 10 for d, w in zip(decode, wall)),
        'scope': 'Symmetric small-N engineering gate; all observations retained',
    }


def notify_tail(wait_end_ns, notify_unlock_return_ns, wait_cpu_begin_ns, wait_cpu_end_ns):
    """One fixed scenario preserves all observed wait CPU and required worker work."""
    cpu = max(0, wait_cpu_end_ns - wait_cpu_begin_ns)
    return max(0, wait_end_ns - notify_unlock_return_ns - cpu)
