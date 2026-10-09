# Singleton quotient roots and paid complete copies

The mixed-root component forms every singleton half-cube sum with one
paid rank-one read per output. It retains the independent dirty seeds of
all source helpers and quotient roots, and changes the premises of the
[pure-helper fanout bound](pure-source-singleton-fanout-release-bound.md).
This is a complete finite formation component, not a complete side word
or an integer-multiplication exponent certificate.

## Ports and construction

For odd k, take the 2^k labels that select one coordinate from each of k
pairs in h=2k coordinates. Write n=2^k. Their span Q has dimension k+1.
The half-cube with code bit j equal to b spans a literal subspace E_(j,b)
of dimension k, contained in Q. These subspaces may be degenerate; every
use refers to the same pinned **actual** canonical operator F_E, including
its routing, affine offsets, quadratic chirps and global unit.

The persistent roles are n original sources, n arbitrary dirty source
helpers, q=k+1 additional arbitrary dirty quotient roots, and 2k existing
arbitrary dirty singleton aggregate roots. Sources start at C_U, while
the other roles start at identity. Source helpers and quotient roots
finish at F_full=C_h; original sources also finish at C_h. Aggregate
root (j,b) finishes at F_E_(j,b). No original source is changed by a
scalar gate.

The quotient coordinates are TOTAL and the k selector-one sums. An
incidence gather adds every helper to TOTAL and to each selector-one
root specified by its code. At identity, first gather the old helper
values, subtract each desired quotient response from its aggregate
through a complete owned read, and undo the gather. The selector-zero
response is prepared in the existing selector-one root by negation
and addition of TOTAL, then restored with the inverse two scalar gates.
This retains its independent root seed and does not presume clean roots.

Inject each original source into its own helper at their common C_U.
Process sources in a fixed order. All quotient roots follow the same
growing span of processed source labels. Move each newly processed
helper to that identical actual frame, add its incidence, and retire it
to full. The quotient roots finish this pass at F_Q.

For each singleton aggregate, prepare its quotient response, move its
recipient from identity to F_E_(j,b), make one complete owned copy of
the prepared root, and transform the copy by

    F_E_(j,b) F_Q^-1.

This relative operator has exactly one C child because E_(j,b) has
codimension one in Q. Add the copied value to the recipient, dispose of
the owned scratch semantically, and undo the complementary preparation.
The original quotient root stays at F_Q. The early negative response
has traveled with the entire recipient state to F_E_(j,b), so the late
read cancels precisely the same old root/helper response. Generic F_E
operators are not assumed to be convolutions.

Finally move quotient roots to full and undo the incidence gather from
the still-held full source helpers. Move unchanged original sources to
full and subtract each from its helper. Every independent dirty seed is
therefore restored at its specified physical endpoint. In virtual
coordinates the only change is

    aggregate_(j,b) += sum_(code_j=b) original_source_code.

The actual aggregate output is F_E_(j,b) applied to that entire sum,
including its original aggregate seed. The inverse reverses all scalar,
frame and owned-read events chronologically. It uses no grouped source
cleanup or mutable-source preimage shortcut.

## Paid rank and stock

There are W=2n+(k+1)+2k persistent roles. With these exact endpoints,
their dimension-growth baseline is

    B = h W - n - 2k(h-k).

All persistent frame paths attain this baseline. Each of the 2k late
owned reads adds one paid rank; the 2k early owned reads have rank zero
but still require complete scalar read/copy/erase work. The total rank
is B+2k. There is at most one concurrent owned copy buffer. Its complete
payload is conditional native scratch, not an omitted persistent scalar
bank and not an uncharged extra full-volume array.

| k | h | sources | extra quotient roots | persistent roles | endpoint baseline | paid rank |
|---|---|---|---|---|---|---|
| 1 | 2 | 2 | 2 | 8 | 12 | 14 |
| 3 | 6 | 8 | 4 | 26 | 130 | 136 |
| 5 | 10 | 32 | 6 | 80 | 718 | 728 |

The extra singleton fee is 2k/2^k per source per core. Across three
cores it is 2.25v for k=3 and 0.9375v for k=5. The latter leaves a
possible first-moment margin below 2v; it does not establish that margin
for a complete word. Additional quotient-root stock is (k+1)/2^k per
core, and aggregate continuation beyond these literal bucket endpoints
is still required. The originals have already reached full: a later
data/K continuation cannot also inherit their original line-to-cap
paths without a joint chronology.

## Exact finite evidence

The unchanged producer is
[singleton_quotient_copies.py](../../code/synthesis/singleton_quotient_copies.py),
SHA b1e3d9688d59a8c1cb78f31063520a3cff226242c8d7bba10d490d595c6e05b9.
It uses three pinned in-repository geometry/frame sources and the Python
standard library. It compiles every retained relative frame to its
actual one-child normal form, with complete tableau/global-unit checks.

The full four-worker run began at 2026-10-09T12:24:38.143418+00:00 and
passed in 94.1491 seconds. It checked all 32 k=1 physical basis columns
and all 1,664 k=3 physical basis columns, their complete inverses, dense
four-Gaussian-field inputs, and a k=3 two-column field case. The latter
contains 4,096 addresses and 851,968 complete signed field values per
forward word. It is a full dense field check, not an all-column test at
that size. Exact linearity extends the complete k=3 one-column basis
check to all Gaussian inputs in that finite model.

A separate unchanged-producer test began at
2026-10-09T12:29:05.880597+00:00 and passed in 165.0161 seconds. It
checked k=5 at all 1,024 addresses of every one of the 80 persistent
roles, with four arbitrary Gaussian fields and varying dyadic grids:
655,360 signed values per forward word. It also checked the entire
inverse and all corruption controls. It does not enumerate all k=5
physical basis columns. The full k=5 scalar matrix has 6,400 entries;
the two-direction prefix audit checks both complete matrices.

Every field case rejects omission of the early dirty response, omission
of the late copy transform, cropping other Gaussian fields from the
owned copy, corruption of a global fourth-root constant, and corruption
of an affine offset. The two-column case repeats global phases per
selected column, rather than paying a phase once for the whole tensor.

The original complete contract export contains all 980 chronological
events and all 175 distinct actual adapters across k=1/3/5. The compact
[contract index](../../fixtures/synthesis/singleton-quotient-contract-index.json)
identifies its full raw path/hash for gzip publication of the unchanged
complete JSON. The export is regenerated by
[export_singleton_quotient_contract.py](../../code/synthesis/export_singleton_quotient_contract.py).

## Precision, buffers and native boundary

The separate
[prefix audit](../../code/synthesis/audit_singleton_quotient_prefix.py)
finds forward and inverse virtual scalar prefix row L1 maxima 5, 17 and
65, equal to 2n+1. Every scalar prefix is integral. These are common-frame
virtual coefficient matrices, not native tape motion or an internal
child precision bound.

For D=2^(hf) physical addresses and input Gaussian coefficient modulus at
most B0, the completed actual canonical wrappers are unitary, so these
scalar bounds give the coarse analytical component bound
(2n+1)sqrt(D) B0. Every literal affine/phase/Htilde/C wrapper prefix is
also unitary. This adds hf/2+log2(2n+1)+O(1) magnitude bits; it is not
a width-independent infinity-norm bound. In the forward word, with input
grid exponent p0, the initial source decode has grid at most p0+f, a
completed canonical bank at most p0+(h+1)f, and a single compiled child
wrapper can use the coarse temporary grid p0+(2h+1)f. An arbitrary input
to the inverse can need p0+hf for its initial endpoint decode, at most
p0+2hf for a completed bank, and the coarse temporary grid p0+3hf.
These bounds use the exact one-child canonical representatives. The
supplied child implementation's own prefix and rounding contract must
still be charged separately.

Observed complete field cases have maximum bank fractional bits 4,
6, 9 and 8 for k1/f1, k3/f1, k3/f2 and k5/f1 respectively. These are
finite observations for the retained input grids, not uniform guard
claims. Every owned copy carries all signed fields and its common grid.
Native complete copy/read/erase, buffer return/cleanup, fixed-tape
layout, wrapper routing, and sufficient long-record precision are
conditional interface obligations. Python scratch disposal is not a
tape erasure implementation.

## Reproduction and remaining discriminator

Run the bounded actual-operator probe and exact prefix audit from the
new worktree:

```bash
python3 -B research/integer-mult-breakthrough/code/synthesis/singleton_quotient_copies.py --workers 4 --bounded
python3 -B research/integer-mult-breakthrough/code/synthesis/audit_singleton_quotient_prefix.py
```

Omit `--bounded` for the full k1/k3/f2 producer run. Both commands accept
a fresh optional `--output <file>`. The contract exporter requires a
fresh `--output <file>`. The recorded k5 field command invokes the same
unchanged producer's `probe((5,1,'fields',False))`; its exact inline
command is retained with its run protocol and raw command file.

Higher-J aggregates are not supplied by the singleton quotient basis.
Independent separate-copy queries for all such outputs may themselves
consume the full rank deficit. The next useful question is whether
joint mixed preparation and cap/source chronology can retain this
singleton saving while avoiding separate materialization of every
higher-J kernel output. No kappa improvement is asserted.
