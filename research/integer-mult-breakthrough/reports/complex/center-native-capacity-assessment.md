# The center basis has conditional target room, with a tight release budget

Status: **EXACT MOMENTS OF EXPLICIT HYPOTHETICAL LEDGERS**. These are capacity
diagnostics. No favorable native compiler, larger exponent or kappa is supplied.

## Assumed complete profile

For v=binom(h,5), N=v^2 and m=h^2, declare W=2N+2vR. The diagnostic uses
the existing candidate k5 master profile, with external children

    2vR at m-h, 2N at (h-1)^2, 4N at h-1, N at 1,

and local rank mass `2v(hR+L0)`, where L0=q(h-2)+4 and q=binom(h,2).
The complete total is `Wm-N+2vL0`. The scalar basis has not been shown to
inherit this profile: all role streams, dirty copies, source/sink phases,
inverse calls and local routing must eventually agree with the same program.

Two independent budget assumptions are assessed. R=0 is an unattained
zero-extra-helper idealization. The other declares R equal to the scalar
basis addition count plus four times its swaps plus its scales. This is a
conservative gate-count proxy, not evidence that those gates become that many
actual auxiliary roles. It is about twelve v. Existing data banks might be
used in place, while their actual address transitions can still cost too much.

For each assumption, one local distribution places all rank mass at width one
(largest moment); the other fills width-h children and one remainder (smallest
moment for that mass and width cap). Complete exact rational log/exp intervals
separate each root from a 10^-12 grid. Scalar counts and every hypothetical
child multiplicity are retained in the result files.

## Target-crossing capacity

The diagnostic target is b=20/189981, about 1.05274e-4. It is the complex
threshold needed by the previously analyzed balanced assembly to reach
kappa=1e-4 if its other hypotheses also hold. It is not an unconditional
conversion from b to kappa for the new architecture.

| h | Expanded-gate R/v | Root with local rank one | Root with local rank h | Extra local rank allowance/v at target, rank-one case |
| --- | ---: | ---: | ---: | ---: |
| 16 | 11.7065 | 0.000085470204..205 | 0.000139807463..464 | -0.0265133 |
| 20 | 11.8006 | 0.000154922712..713 | 0.000255206374..375 | 0.0894289 |
| 24 | 11.8587 | 0.000156202931..932 | 0.000258666452..453 | 0.1163684 |
| 28 | 11.8954 | 0.000143518731..732 | 0.000238635696..697 | 0.1065380 |

Decimals are display values; complete strict rational brackets are in the
[repaired run](../../runs/20261009T000131Z-complex-center-leverage-repaired/protocol.json).
At h20/24/28 even the worst permitted local residual placement crosses this
diagnostic target. At h16 only the optimistic distribution does. This selects
h20 and h24 for chronology work before broad parameter sweeps.

The zero-helper idealization has worst-distribution complex roots around
0.001773 at h20, 0.001806 at h24 and 0.001670 at h28. These are unattained
complex-component capacities. They neither establish R=0 in the master
profile nor remove the binary primitive and outer recovery restrictions.
They are not kappa claims.

## Paid release comparison in the same units

An extra local rank loss Delta adds `2v*Delta` rank-one width units. With f
packed columns under this explicitly f-linear macro, it adds `2v*Delta*f`
actual rank units. The normalized moment remains the same. The allowance is
measured per local copy, not a fraction of a globally free frame change.

At h20, q=190 and the rank-one allowance is about 1386.5 per local copy.
Existing L0 is 3424. A new q-feature one-direction charge would be 190,
whereas adding q full-width charges costs qh=3800 and does not fit. A closed
full-to-zero-to-full feature excursion costs 2qh=7600 and also does not fit.
If an independently correct copied or endpoint-sharing implementation
REPLACES L0 by qh, its net increase is only 376 and fits. Replacing it by
2qh increases the loss by 4176 and fails. Neither replacement is implemented
here. Existing center charges cannot be paid twice, and a return transition
cannot be deleted merely because a scalar quotient has small rank.

At h24, the allowance is about 4946.1, while qh=6624. A one-output release
costs v=42504 and fails by much more. At h28 the allowance is about 10470.5
and qh=10584, already just too high if added to the existing baseline. These
comparisons explain why exact continuation and sharing are decisive.

The coordinator's coherent release lemma independently gives an excess bound
of at least 2*rho, with rho the fitting-matrix minimum rank, ABOVE its specified
geometric endpoint baseline. It is not automatically an extra Delta on top of
this macro's existing rank. In the single h-dimensional five-label space, the
paired-minor bound gives rho>=36 at h20, so the necessary excess is at least72
rank units. This is much less than a closed qh release upper charge and does
not prove any construction approaching the lower bound.

In a bulk h*f space, losing one diagonal direction can invalidate containment
of an entire f-dimensional source label block, yet add only one scalar row
to the proof's released space. Consequently the general release proof gives
2*rho, not automatically 2*f*rho. The f factor above belongs to the DECLARED
replicated macro. A stronger lower bound needs a separate separability proof.
No tensor-lifted minrank bound is used to reject a bulk compiler here.

The synthesis track separately proves that using identical B on both banks
and paired middle copies still forces full stock rank through a crossed
endpoint triangle, regardless of scalar cancellation. That simple chronology
is a retained negative. Paid permuted ports or a different shared release word
must change its actual incidences; renaming quotient coordinates is insufficient.

## Signed interval repair and recovery

The [first attempt](../../runs/20261008T235856Z-complex-center-leverage/protocol.json)
has correct root and target-moment calculations. Its negative h16 rank-one
allowance used positive-numerator division ordering and produced a reversed
interval. That allowance certificate is invalid. Originals were not changed.

The fresh run takes the minimum and maximum of all four numerator/positive-
slope endpoint quotients, correctly enclosing positive and negative allowances.
The [recovery patch](../../fixtures/complex/center-leverage-negative-bound-recovery.patch)
recreates the complete earlier source at SHA-256
`7afadf342d16599dccce9e05053cce4e8343c6ae968b2bdb88351872c912e044`.
It was tested on an ignored temporary copy; the working source was preserved.

## Reproduction and scope

```sh
python3 -B research/integer-mult-breakthrough/code/complex/test_center_native_leverage.py
python3 -B research/integer-mult-breakthrough/code/complex/center_native_leverage.py \
  --h 20 --output /tmp/fresh-center-capacity.json
```

Only the standard library is required. Bounded tests check the negative
allowance, exact integer loss threshold, one-release-per-output rejection and
moment invariance of the declared f-linear profile. An independent actual
native ledger remains required before promoting this capacity to a result.
