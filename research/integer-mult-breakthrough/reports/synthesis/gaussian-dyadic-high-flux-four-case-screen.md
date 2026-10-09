# Gaussian-dyadic high-flux four-case screen

## Question and scope

The preceding [high-flux probe](nonlex-scan-flux-and-native-boundaries.md)
excluded real dyadic unit diagonals modulo three. This fresh discriminator
tests four mixed three-scan topologies at `f=3` over `F_5`, using natural
order `N` and the alternating complement-shear order
`P(j)=j XOR((j AND 1)(2^f-2))`. Prefix is `L` and adjacent difference is `D`.
The model remains a fixed-labeled, one-bank exact zeta factorization with
arbitrary address-diagonal scalars between and outside the scans.

The four topologies are:

| Orders | Scan kinds |
| --- | --- |
| `N,P,N` | `L,D,L` |
| `N,P,N` | `D,L,D` |
| `P,N,P` | `L,D,L` |
| `P,N,P` | `D,L,D` |

This is a deliberately bounded preflight, not a general three-scan sweep.
Other order/type choices, wider fields, arbitrary complex scalar domains,
borrowed banks, and native routing are outside the finite exclusion.

## Why the reduction covers Gaussian-dyadic diagonal words

Let `R=Z[i,1/2]`. There is a ring homomorphism `R -> F_5` with `i -> 2`
and `1/2 -> 3`, since `2^2=-1` and two is invertible in `F_5`.
Every ring unit maps to a nonzero field element.

The coordinator supplied a useful determinant sharpening, independently
accepted here. Every ordered prefix/difference scan has determinant one,
as does `Z_f`. If the complete exact factorization uses only diagonal
entries in `R`, the product of all these entries is exactly one.
In a commutative ring each entry then has an inverse in `R`, namely the
product of all the other entries. Consequently every entry is a ring
unit. Unit diagonals are forced by the exact complete determinant, rather
than imposed as an extra assumption on these Gaussian-dyadic words.

The reduction therefore loses no exact factorization with purely
Gaussian-dyadic diagonal entries in the four stated topologies. General
nonzero complex scales can include reciprocal odd factors and remain
broader. Extra banks, projections and singular response summands change
the determinant premise and are explicitly left open.

## Exact finite result

Each case exhausts `4^7=16,384` normalized nonzero left middle diagonals.
The right middle diagonal is obtained by complete exact homogeneous
kernel parameterization, normalized at its first coordinate. Every
nonzero candidate is tested against the entire target and the derived
outside row/column gauges. Global scalar normalization is absorbed into
the outside gauges, so it omits no field solution.

All four cases are excluded. Together they check 65,536 normalized left
assignments; each worker took approximately 1.68 to 1.86 seconds in the
original run. No nonzero right candidate survived these four zero systems.
Controls bind the Gaussian-unit homomorphism, a nonbinary normalized
kernel, rejection of a forced-zero diagonal, a complete positive `Z_2`
three-prefix reduction, and a corrupted forbidden response. The reusable
verifier also compares its small kernel parameterization against direct
complete enumeration.

Original producer:
[gaussian_unit_nonlex_scan_five.py](../../code/synthesis/gaussian_unit_nonlex_scan_five.py).
Evidence:
[original run](../../runs/20261009T105635Z-synthesis-gaussian-unit-nonlex-five/report.md),
[bounded replay](../../runs/20261009T105859Z-synthesis-gaussian-nonlex-five-bounded/report.md).
The completed original source/protocol/results remain unchanged. Its
initial unit-only wording is retained; the determinant argument is this
separate analytical scope extension, not a silent change to its bytes.

## Reproduction and boundary

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/gaussian_unit_nonlex_scan_five.py --workers 4 --output research/integer-mult-breakthrough/work/synthesis/FRESH-five/results
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_gaussian_unit_nonlex_five.py
```

The verifier accepts an optional fresh-file `--output`, preserves its
complete four-file standard-library source closure, and reruns the actual
normalized finite search and negative controls. A finite positive does
not automatically lift to characteristic zero. These four negatives
neither provide nor rule out a native high-flux transform in another
architecture. Record motion, borrowed guard restoration, prefix
amplification, full grids, and recursive normalization remain paid.

The next changed model allows sums of singular two-scan responses through
an arbitrary dirty helper. It bypasses the one-bank determinant premise
and is preserved separately in
[the response report](singular-two-scan-responses-and-four-entry-separator.md).
