# Short-record monotone splitting with counted tape motion

Status: **EXACT FINITE TAPE-TRAJECTORY EVIDENCE** and an
**INDEPENDENT CONDITIONAL COMPONENT LEMMA**. This strengthens a specific
sequential split interface. It does not verify a complete guarded CRT
program, the Gaussian transfer or a multiplication exponent.

The old guarded CRT report used an O(b^2) metadata placeholder per record
for a monotone split and required much wider coefficient records to absorb
it. A direct linear scan of the binary address counter against its interval
template reduces that placeholder to O(b). This already fits records of
width Q=Theta(b); an O(1) numeric countdown or uncharged random access is
unnecessary.

## Read-only baseline and changed interface

The final old campaign baseline is
[guarded-crt-batching.md at 0aea6335](https://github.com/hipotures/rad/blob/0aea633524d6e54e21c077fb6af0bbc6aaa37a81/research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/inverse/reports/guarded-crt-batching.md),
SHA-256 `dad93d966d43a3378c24d83225b611bd52ecb7790a820841eb94054385bdda5d`.
Its complete immutable source record is
[short-record-CRT-source.json](../../configs/transfers/short-record-CRT-source.json).
The source is a read-only reference; no old code or campaign instructions
are imported into this execution.

That baseline separately proves or proposes guarded independent rotations,
repeated-source BIT fanout, inactive bank layouts, polynomial inverses,
sparse repair and sequential valid-interval splitting. Its shorter-record
scope remains an open integration boundary. The present program replaces
only the metadata implementation of the last sequential split. It does
not establish the preceding nonlinear permutations by a bit relabeling.

For each independent node, let positive valid lengths be S_L,S_R and
binary capacities T_L,T_R. The old field has valid scalar range
`0<=k<S_L*S_R` inside capacity `T_L*T_R`. The new ordered fields are
`(B,A)` with `0<=B<S_R`, `0<=A<S_L`, capacities `(T_R,T_L)`, and

```text
k = A+S_L*B  ->  B*T_L+A.
```

The image is strictly increasing on the valid interval. Within one B block
it increases by one; the next block increases by
`T_L-(S_L-1)>0`. Simultaneously splitting independent nodes preserves
Cartesian lexicographic order. The old and new padded binary boxes have
exactly the same total capacity. Therefore the next valid old payload and
next valid new address always correspond. The algorithm reads every old
record once, discards only known-zero invalid records, copies each valid
complete record to the next valid new address and writes explicit zero
records at invalid new addresses.

## Finite-symbol counter and template algorithm

Let B be the sum of the binary field widths, T the complete box capacity
and Q the complete payload width. Every field has at least one bit, so its
delimiter count is at most B. Two independent scanners represent the old
and new boxes. Each uses a mutable binary counter tape and an immutable
bound-template tape, with aligned field delimiters. The whole counter
increments by ordinary ripple carry, then returns to its starting marker.
It contains no Python numeric coordinate value used to choose a payload.

To test a field, scan its counter and bound bits from least to most
significant. The comparison has three states: less, equal or greater. A
later differing bit is more significant and replaces the current state.
At a delimiter, accept the field iff it is less than its bound. A separate
finite-symbol delimiter flag accepts a full interval S=T, whose endpoint
needs one more binary bit than the field itself. Combine the field tests
with a boolean AND. Scan both tapes completely and return both heads to
their start. The scanner does O(B) moves, reads and fixed-state operations
per record.

The consumer invokes each scanner once for each address in its complete
box. Its counter traversal has O(T) total bit changes and return motion:
the j-th bit changes O(T/2^j) times, and field delimiters are crossed only
at their corresponding carry boundaries. Even the coarser O(B) per-record
increment bound suffices here. The entire metadata body costs O(T*B).

The input and output payload heads each move sequentially through complete
records. A record delimiter ends the bit copy, so the consumer does not
need a free numeric payload-width loop. Invalid destination slots copy a
Q-bit zero template and return that template head. The final source tail
is consumed, both payload heads rewind, and every metadata/zero workspace
is erased with its return motion charged. These operations cost O(T*Q).
The total is

```text
O(T*(Q+B)+poly(B)).
```

Thus Q>=B yields O(V+poly(B)), where `V=T*Q` is the full padded payload
volume. Interval products, capacities and templates are constructed once
by separately paid polynomial descriptor setup. This is not a claim about
free arithmetic on every record. Seven tapes and a fixed finite alphabet
suffice independent of the number of fields. The code is a literal
trajectory model, not a formally compiled transition table.

## Actual finite trajectories

The [new source](../../code/transfers/monotone_split_tapes.py) uses only the
standard library. Every operational head move is a single-cell step;
every cell read and write is counted. The metadata/template initialization
count describes its specified straight write-and-return trace. Scalar
construction of those known words remains separate setup work. The
numerical coordinate/division helpers occur only in immutable fixture
generation and the independent output oracle, outside the consumer.

Four workers complete 376,832 binary records in 8.736 seconds. Every
output payload, delimiter and padding bit matches the independently
generated nonlinear source-to-destination map; the original input is
preserved. The experiment counts comparisons, crossed metadata,
template returns, ripple carries, complete payload reads/writes,
zero-template returns, input/output rewinds and workspace erase.

| Case | B | Q | Records | Metadata head moves | Payload/zero head moves | All counted steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Two balanced nodes | 16 | 16 | 65,536 | 10,506,604 | 5,614,934 | 31,414,581 |
| Three unequal nodes | 15 | 16 | 32,768 | 5,382,972 | 3,181,758 | 16,880,589 |
| Full intervals and unit bounds | 14 | 16 | 16,384 | 2,378,060 | 1,418,280 | 7,458,779 |
| Longer node fields | 18 | 20 | 262,144 | 46,301,644 | 26,197,378 | 140,370,373 |

The first case has exactly Q=B. Its 1,048,576 payload bits incur about
29.96 counted steps per bit. These are exact simulated step counts, not
physical execution benchmarks or an O(1) metadata assertion. The full
per-tape counters and hashes are retained in the
[compact result](../../runs/20261008T233720Z-transfer-monotone-split-tapes/results/summary.json).
No result fields are omitted; its raw path, bytes and hash are preserved.

Negative controls reject deletion of a nonzero invalid input, reject an
interval's excluded endpoint and test the full-capacity delimiter flag.
Invalid padding may be discarded only after it is known zero. In
particular an earlier guarded nonlinear program can create real payloads
at invalid intermediate addresses; its exact repair must finish before
this split scan begins.

There is no guarded rotation or exceptional address set in this component.
Its exception-repair count is explicitly zero. This absence is a scope
boundary, not a claim that preceding guarded repairs have zero cost.

## Separate sparse-key arithmetic accounting

The old report's complete inverse/key algorithm has the explicit loose
bound `O(b^4*polylog(b))` per exceptional record. If a separately proved
globally bijective guarded program agrees with its ideal map outside a
preserved exceptional set of density `delta=O(b^-5)`, the total key
arithmetic is

```text
O(delta*M*b^4*polylog(b))
  = O(V*b^-2*polylog(b))   when Q=Omega(b), V=M*Q.
```

It need not be absorbed into Q separately at every ordinary base record.
This is a conditional arithmetic deduction, not a finite replay of the
old inverse/key algorithm in the new program. It uses the proved density,
the actual polynomial key algorithm and every exceptional record.

Extraction/reinsertion scan the complete array for O(V) work. A stable
binary radix repair with b-bit keys and full Q-bit payloads costs
`O(delta*M*(Q+b)*b)=O(delta*V*b)` when Q=Omega(b). This includes full
payload moves on every radix pass. Globally correct repair still requires
an exact ideal/actual inverse key and a proved invariant bad set; a
sampled preservation check or table gather cannot substitute for them.
The untouched complete spectator suffix needed for prefix-controlled
rotation arithmetic must also remain present and be paid as in the
old interface. Those bank and routing premises are unchanged.

Consequently the old Q=d^18, epsilon>1/2 assumptions are unnecessary for
these **two specific metadata charges**, under the replacement split
scan and the stated sparse-density hypotheses. This does not remove
them from every other numerical, bank or transfer obligation. No full
short-record guarded CRT theorem is promoted until the same actual
program, layouts, complete records, shape bands and repairs satisfy
all its interfaces independently.

## Leverage and next discriminator

A full guarded CRT composition retaining Q=Theta(b) could remove a
record-width restriction without adding address bits. Combined with
the independently reviewed endpoint-aware native guard, it may permit
more flexible outer parameters. The frozen complex moment still cannot
reach kappa=1e-4; this component does not change that fact.

The next test is actual sparse-key/repair execution at short records,
keeping the old polynomial inverse and real bad predicate, followed by
an independent bank-layout and complete movement review. Gaussian
precision, field permutations and all-size recovery remain separate.
This new component and analysis were developed with OpenAI Codex and
do not constitute external peer review or formal verification.

## Reproduction

From the breakthrough worktree root:

```sh
python3 -B research/integer-mult-breakthrough/code/transfers/monotone_split_tapes.py \
  --workers 1 --small
```

The bounded source-only check covers 1,152 complete records and all controls.
The full four-worker command, seeds, finite alphabet, measured operations,
source hash and baseline pin are recorded in the
[protocol](../../runs/20261008T233720Z-transfer-monotone-split-tapes/protocol.json).
Use a fresh output path for every attempt. The baseline is an obtainable
reference, not a dependency required by the finite tape check.
