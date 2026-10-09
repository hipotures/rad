# Independent transfer and assembly review of draft PR127

The finite conditional arithmetic in
[PR127](https://github.com/CrocSwap/integer-mult-bounds/pull/127), at commit
`ca8725485a822769f24c2e4e9b8955b31a42b044`, is internally consistent under its
stated inherited interfaces. An independent compact calculation reproduces
the three strict child moments, aggregate birth rebilling, complete scalar
group upper bound, row-stock arithmetic and seven final exponent margins.
It also proves that the next complex grid point fails. This review does not
establish the retained all-size native interfaces, replay the full external
dirty word, or prove an unconditional multiplication exponent.

The user supplied the draft on 2026-10-09. The coordinator obtained a detached,
read-only checkout and executed its unchanged package separately. The present
reviewer inspected source and data without executing or importing external
producer code. The coordinator's full package reproduction and source pins
are preserved in
[its independent receipt](../obstructions/pr127-reproduction-and-birth-reuse.md).

## Independent finite checks

The [retained input](../../fixtures/transfers/pr127-transfer-input.json) records
six upstream file hashes and the exact head. It retains all three child
histograms, the previous complex histogram, 49 aggregated birth-rank classes,
the scalar bill and expected exact assembly values. The full 2,108 pair list
and graph are omitted from this compact fixture; obtain those immutable files
from the pinned upstream checkout. Aggregation preserves counts by `(e,s)`;
it does not independently certify the actual donor/recipient containment,
liveness or identity of individual pairs.

The [independent source](../../code/transfers/pr127_transfer_review.py) uses
standard-library rational arithmetic and previously reviewed independent
interval helpers. Four processes verify the three selected moments and the
next complex point. For a profile with selected width m, complete stock W and
child multiplicities n_t, the tested moment is

```text
Phi(1-b) = sum_t [n_t*t/(W*m)] * exp(b*log(m/t)).
```

Range-reduced 40-term positive atanh series bound logarithms. Degree-eight
Taylor expansions with explicit positive tails bound exponentials. Every
comparison uses rational interval endpoints; decimal displays are not the
decision procedure. The new complex moment is below one at
`b=11242073/10^11`, with gap approximately `1.663e-12`. At
`b+1/10^11`, its lower endpoint exceeds one by approximately `8.19e-13`.
Thus the negative control proves failure rather than merely failing to
prove success. The coarse bit and ordinary leaf moments also contract at
their selected parameters.

For h=24, v=choose(24,3)=2,024 and m=576, each contained birth reuse at ranks
`0<=e<=s<24` removes `2v` copies of children `24-e` and `552+s`, adds `2v`
copies of `s-e` when nonzero, and removes `2v` physical role units. Applying
all 49 aggregated classes exactly reconstructs the new histogram:

| Quantity | Independent result |
|---|---:|
| Reuses | 2,108 |
| Virtual auxiliary roles | 28,705 |
| Physical auxiliary roles | 26,597 |
| Complete stock W | 115,857,808 |
| Weighted child rank | 66,732,235,328 |
| Deficit `W*m-rank` | 1,862,080 |
| Largest child | 574 |

The raw deficit remains unchanged because every removed stock unit also
removes exactly m units of weighted rank. The moment improves through both
the distribution of child widths and the paid physical-stock normalization.

The literal readout bill uses denominator 42, including the odd factor 21,
and maximum numerator 55. This is a Gaussian-rational common-grid interface;
it is not a circuit over only `Z[i,1/2]`. Complete temporary copies, integer
unit additions, parking/discard scans and chronological scalar wrappers are
included in the supplied upper bound. Independently reconstructed values are
`readout_copy_scan_bill=47,369,383`, `local_scalar_upper=48,069,997`, and
`G=3,113,921,927,424`. The last value follows from
`16*(2v*local_scalar_upper + 8v^2)`. These are fixed mathematical upper
bounds, not measured time or memory requirements.

The three finite guard inequalities pass using
`E=64*(W+m+G+1)^3`, `B=rank+E` and `C0=32*m*B^2`. The sum of halving-depth
times wire-label bits is 15,561: coarse bit depth 367 at 27 bits, ordinary
leaf depth 9 at 28 bits, and new complex depth 200 at 27 bits. At declared
row degree 32,000 the arithmetic gap is `6389/25`. This checks a proposed
allocation bound; it does not implement that complete-row allocation on a
fixed tape set.

## What supplies the threshold crossing

The inherited bit supplier has coarse saving `620523/5,000,000,000` and
ordinary leaf saving `384599/10^10`. Its stopped atom fraction `1/1000`
gives

```text
actual_bit_saving
  = (999/1000)*(620523/5,000,000,000)
    + (1/1000)*(384599/10^10)
  = 1240189553/10^13
  = 0.0001240189553.
```

This changed conditional supplier already exceeds `10^-4`. It is based on
Swapnil Jain's round-seven bit word and the retained opposite-bank rule that
replaces a complete projector residual by one reversed child of its rank.
The new PR127 runner consumes a frozen compact bit profile and checks its
moment. It does not regenerate the inherited bit word or establish that
opposite-bank native implementation from scratch. The original stopped
product notes contain older example constants; their interface construction
is being reused with this separate, newer profile.

The supported bit parameter is deliberately lowered to
`11242061657927/10^17`, below both this actual supplier and
`(1-10^-6)*b` with an additional `10^-12` buffer. The assembly selects
`eta=10^-8`, `q=a*(1-2*eta)`, `c=q*(1+eta)` and
`epsilon=(1-eta)/(1+c+q)`. Independently recomputing the seven final margins
gives a minimum `epsilon*q`; the strict grid choice is

```text
kappa = 11239534209971/10^17 = 0.00011239534209971.
```

Every one of the seven retained margin expressions agrees exactly with the
upstream candidate and strictly exceeds this kappa. The next `10^-17` grid
point is rejected by an exact rational comparison. This compact reviewer
does not independently duplicate the package's complete set of 47 auxiliary
constraints; the coordinator's unmodified package reproduction covers those.
Neither computation proves the inherited analytic or machine hypotheses.

The campaign's earlier ceiling for its frozen bit constant therefore does
not refute PR127. Conversely, the new coarse bit interface cannot simply be
substituted into a different circuit ledger. Its reversed-child factorization,
atom adapters, ordinary wrapper and complete spectators are part of its
separate contract.

## Birth reuse and paid potential

The scalar birth-cut identity is a structural mechanism worth pursuing.
For a recipient whose clean construction begins at zero, let D be its exact
future output response, stopping before any later birth of the same physical
role. A dirty implementation instead starts from actual value g and subtracts
D*g immediately. The subsequent response of that offset is exactly D*g, so
it cancels. Here g may depend on earlier source injections or already aliased
roles. Cleanup must reverse the actual full chronological word; collecting
all negative source injections at the end is generally incorrect after
reuse.

In this package, the recipient is an untouched deferred role and the donor
has completed its last gate and every terminal read. The donor's final frame
E is contained in the recipient birth frame sigma. Its actual value is raised
to sigma and read through the recipient's existing negative response before
the future virtual life is aliased. A residual with equal characteristic
vectors and `E!=sigma` is explicitly excluded because the needed alternating
normal form is not supplied. Recipients with initial source injection are
also excluded by the actual matching contract. These boundaries matter when
trying to reuse new per-edge side helpers.

The coordinator's general paid-moment lemma is sound. Put
`C=s-e`, `a_child=h-e` and `b_child=m-h+s`, with `m>h` and `0<=e<=s<h`.
Both removed widths lie strictly between C and m, and their sum is m+C.
For `p=1-b` with `0<b<1`, strict concavity therefore yields

```text
Delta = a_child^p + b_child^p - C^p > m^p.
```

If an old moment numerator A satisfies `A<=W*m^p`, then for a single legal
reuse and `W>1`, comparing `(A-Delta)/(W-1)` against `A/W` reduces to
`W*Delta>A`, which holds. For d replicated paid units use `A-d*Delta` and
`W-d`, with `W>d`; the same comparison follows. This accepts the algebra
under the exact complete-stock and literal-merge premises. A free reset,
unpaid readout, incomplete inverse or illegal containing frame would break
the application.

## Retained assumptions and review limit

The draft expressly retains analytic estimates, exact recovery, prime
selection, copied streams, residual-to-child normal forms, translated gauges,
complete-row products and fixed-tape implementation. Its odd grid is stated
as `2^-P*21^-K`, with completed children preserving the incoming odd exponent.
The finite inequalities and uniform fixed constants do not by themselves
prove arbitrary dirty complete-row endpoints, long-record routing, all-size
atom interfaces or setup and prime thresholds. The present review accepts
the scoped finite arithmetic and the conditional merge-potential deduction.
It does not close those obligations or establish campaign success at this
kappa.

## Reproduction and provenance

Run from the new worktree:

```sh
python3 research/integer-mult-breakthrough/code/transfers/pr127_transfer_review.py --workers 4
```

The bounded CI command is the same source with `--workers 1`; it checks all
four compact moment tasks. No external repository or downloaded input is
needed for this retained compact reproduction. The runtime closure is the
reviewer, its config and fixture, plus independent
`encoding_slack.py` and its imported `conditioned_frame_review.py`. The config
pins both helpers. To obtain the omitted graph and full pair list, clone the
fork identified in the coordinator's source pins, check out the exact head,
and verify the six upstream file hashes recorded in the fixture.

The actual-time four-worker attempt is
[20261009T020330Z-transfer-pr127-assembly-review](../../runs/20261009T020330Z-transfer-pr127-assembly-review/report.md).
It takes 0.3024 seconds and preserves compact protocol and results. Its source
hash is `1ea75303d494f3e62e6edbdcbc5aba5943a7770365598e3a1b1135e0f6f0e0b8`;
fixture hash is
`99fe5b4310fa5d0ae3681548df56d6706bcb1fe7a3d54d5d8005bc07d6586db3`.
The full external word is independently reproduced by the coordinator, not
by this compact reviewer. Both scopes remain explicit.
