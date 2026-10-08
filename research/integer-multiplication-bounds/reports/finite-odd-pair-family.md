# Odd bit grounds with movable full orphan pairs

Odd ground h makes each common-point local problem have even size h-1.
The new pairing family uses a special point s=h-1 and fixed pairs on the
other h-1 points. For common p!=s, pair mate(p) with s and move that full
pair among the unaffected global pairs. For common p=s, use the original
fixed pairs. There is no local singleton. The unused position at p=s is
normalized to zero in stable candidate IDs.

The local weighted pair recursion, global disjoint-sum sharing, positive
rational envelope E(C,V), root flow and physical compiler remain unchanged.
H=9I-J is nondegenerate for h!=9. Every gate's source envelope has a common
point, original source copies use triple lines, and all outputs are
orthogonal to their designated targets. A constructive triple matcher
handles the special point and is checked as a bijection whose every image
intersects its source in exactly one point.

The [small discriminator](../runs/20261008T035200Z-finite-odd-pair-discriminator/results/certificate.json)
checks h7 and h11, two full-pair placements each, with complete scalar,
physical rational timeline and all dirty invocation bases. It precedes the
[309-case cohort](../runs/20261008T035600Z-finite-odd-pair-cohort/protocol.json),
which completed without a failed case in 791.393 seconds. Throughput was
1405.622 exact candidates per hour; lifetime peak RSS was 4367084 KiB.
Ground, positions, base, seed, candidate IDs and all exact case certificates
are preserved. Best supported results in that bounded family are:

| h | R | Enclosed saving lower endpoint, decimal display |
|---|---:|---:|
| 43 | 292734 | 2.277799914e-9 |
| 45 | 338161 | 2.781416584e-9 |
| 47 | 388187 | 3.052477319e-9 |
| 49 | 442774 | 3.170911468e-9 |
| 51 | 502265 | 3.187957467e-9 |
| 53 | 566873 | 3.138955982e-9 |

The h51 winner has base2 and vector [0]*6+[24]*25+[0]*20. Its candidate ID
is `19945bccf2127679a684a457425017aade6746e66e51d0955fa7d1ff67cadf0d`,
candidate file SHA256
`a5b91dce64ddb3b1660767fcea13a615df47146d25c88767124ed319c4041c2d`,
and compiled SHA256
`5183963ce3e380f2017eeb51a9f83b7ee406ec8537b9053897464e63bd5e18e9`.
Exact counts are m132651, W453752231686250, D2263379181875,
s60190685022033566875, N9031399015625 and L3384009916875.
The actual role count includes 33451 retained links among 39176 candidates.
Its separately exact rank histogram regresses sum(count*rank)=s=Wm-D.

The [independent full h51 review](../runs/20261008T041200Z-review-odd51/protocol.json)
reconstructs all 70471800 nonzero output coefficients and checks 2897494
physical transitions with a fresh builder and matcher. It passes complete
h7/h11 dirty bases in both orientations and two h7 full shared exchanges.
The finite odd-ground transfer is thus reviewed independently; the exact
downstream multiplication composition is recorded separately. The decimal
saving comparison does not itself assert a final kappa.

Reproduce the constructor and bounded controls using the campaign pinned
reference and math environment, with one BLAS thread:

```bash
python -B code/finite_odd_pair_positions.py --reference <upstream-reference> --h 7 11 --positions -1 0 --base 2 --full --small --output /tmp/odd-controls.json
```

The [fresh420 refinement](../runs/20261008T041100Z-finite-odd-pair-refinement/results/terminal-summary.json)
is now terminal: all420 distinct candidates pass, with all309 predecessor
IDs excluded. It took 1337.755 seconds at 1130.251 verified cases per hour.
The strongest h51 finite screen has R502134 and vector
[0]*8+[23]*26+[0]*17, candidate
`52ce3ca9416394668daacec55e648096fd419747f393391c9bfb7fdcd039f878`.
Its complete case and exact enclosure are retained; it is awaiting separate
independent promotion. A new360-case cross-ground window-transfer cohort is
live under run043400 and is excluded from this terminal publication freeze.
