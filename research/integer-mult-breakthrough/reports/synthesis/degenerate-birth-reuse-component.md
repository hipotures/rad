# Literal birth reuse through a degenerate frame

A dead helper can start a second virtual life through a genuinely
degenerate actual common frame, with exact birth-cut compensation and
arbitrary dirty restoration. In the finite control the stock drops 8 to 7
and the recursive rank drops 28 to 24; its framed endpoint deficit stays 4.
This combines slot reuse with a nongraph Clifford frame, rather than
changing a public campaign's parameter.

The source labels are `U=(1,7)` in a four-bit address space and the target
labels are `T=(8,14)`. Their common support `E=span(1,7)` has dimension 2
and radical `span(6)` of dimension 1. Both targets are orthogonal to E.
The actual chosen `F_E` is the generic dyadic Clifford
`D^-1 P Htilde_2 P^-1 D^-1`, with `D=diag(i^weight)` and the exact routing
columns in the
[contract fixture](../../fixtures/synthesis/degenerate-birth-reuse-contract.json).
It is not replaced by a symmetric projector or a free frame label.

Two input helpers a,b have early zero-frame negative responses `(1,2)`
and `(1,3)` respectively. They move to the source lines, receive x0,x1,
then move to the actual common E frame. Both sinks also move to E.
The node helper's clean program has two lives:

1. Birth at E, form `r+=a+b`, and read `y0+=r`.
2. Birth at E, form `r+=2a+3b`, and read `y1+=r`.

The backward derivative must **cut** the helper's response at the later
birth. Its two birth responses are `(1,0)` and `(0,1)`. Physically no
helper is reset. At each birth its actual old virtual value g remains,
and the corresponding response times g is subtracted from the currently
common-frame sinks. The second g includes the old source contribution as
well as arbitrary dirty offsets. It cannot be treated as fresh independent
garbage. The net clean maps are

```text
y0 += x0+x1
y1 += 2x0+3x1.
```

All helpers finish at full. Reverse every real source injection and
workspace shear in true chronological reverse order at full. This restores
their original virtual dirty values. Their physical outputs are
`C_full` times those values; raw identity is not the target. The reused
recipient has no direct source injection. Its clean values arise from
already available helper operands at the common birth frame.

In the baseline, the two node lives use separate helpers. Each has one
`zero -> E -> full` path of total rank 4. Reusing the same helper avoids one
complete path. The other source/sink and input-helper paths stay explicit:

| Case | Stock | Width1 | Width2 | Width3 | Rank | Capacity | Deficit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Separate node helpers | 8 | 6 | 8 | 2 | 28 | 32 | 4 |
| Reused node helper | 7 | 6 | 6 | 2 | 24 | 28 | 4 |

[degenerate_birth_reuse_probe.py](../../code/synthesis/degenerate_birth_reuse_probe.py)
imports no public birth-reuse producer. It independently derives CUT
responses, executes the actual canonical coefficient matrices and binds
them to literal frame gate specifications. The motivating birth-cut lemma
was inspected read-only at PR127 commit
`ca8725485a822769f24c2e4e9b8955b31a42b044`; the local scalar/circuit and
Gaussian word here are newly authored.

Four workers completed the
[actual-time run](../../runs/20261009T020541Z-synthesis-degenerate-birth-reuse/report.md).
The f1 cases check all 128 baseline and all 112 reused physical basis columns.
The f2 cases check all 8 and 7 origin bank columns and three complete Gaussian
dyadic fields each. No origin-only covariance promotion is made. Both
f1 and f2 detect nonzero source-dependent old values at the reused birth.
Omitting the second response or failing to cut the backward response at
the second birth corrupts the complete dirty/source operator. The wrong
raw-identity dirty target is also rejected.

Reproduce from the dedicated worktree root:

```bash
python3 research/integer-mult-breakthrough/code/synthesis/degenerate_birth_reuse_probe.py \
  --workers 4 --output research/integer-mult-breakthrough/work/synthesis/<fresh-actual-UTC>-degenerate-birth-reuse/results
```

The 20-file standard-library source closure is pinned by the run protocol.
The contract retains every literal common-frame word, routing column,
affine transition map, quadratic input/output phase, and direction of each
one-child adapter. Frame and transition matrix hashes bind these compact
specifications to the exact coefficient matrices used in the replay.

This is a complete finite side component, with all affine routes, phase
gauges and selected columns retained. It does not compute an identity
shear or signed exchange on all label pairs, supply native fixed-tape or
all-size precision bounds, or prove a new kappa. Its mathematical leverage
is a strictly broader reusable common-frame class. The next test is whether
a full side/birth network can exploit degenerate frames without forcing
the canonical repair that erased the previous framed shear's saving.
