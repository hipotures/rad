#!/usr/bin/env python3
"""Bounded closure for local dirty target pivots and cap interleaving witnesses."""

import cap_interleaved_gossip_probe as gossip
import cap_target_pivot_accumulation as pivot


def verify_gossip_schedule(n, word):
    cubes, targets, caps, compatible = gossip.instance(n)
    required = {(r, t) for r in range(n) for t in range(n) if compatible[r][t]}
    if len(word) != len(required) or set(word) != required:
        raise AssertionError('The interleaving omitted, repeated or added a required read')
    return gossip.replay(caps, targets, word)


def main():
    for n in (2, 3, 4):
        case = gossip.probe(n)
        if not case['zero_excess_schedule_exists']:
            raise AssertionError('The concrete finite zero-excess witness disappeared')
        word = case['zero_excess_schedule']
        verify_gossip_schedule(n, word)
        for corrupt in [word[:-1], word + (word[0],), ((0, 0),) + word[1:]]:
            try:
                verify_gossip_schedule(n, corrupt)
            except AssertionError:
                pass
            else:
                raise AssertionError('An invalid edge set was accepted')
    for j in (3, 4):
        case = pivot.probe(j)
        if not all(case['negative_controls'].values()):
            raise AssertionError('A weighted-cut negative control failed')
    print('PASS local dirty target pivots, retained kernel banks, complete interleaving edge sets and cut/timing negatives')


if __name__ == '__main__':
    main()
