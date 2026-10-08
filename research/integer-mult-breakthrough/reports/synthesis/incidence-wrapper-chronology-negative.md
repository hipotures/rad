# An exact incidence-basis wrapper with a noncontracting favorable ledger

**Status: EXACT FINITE WORD; REFUTED WITHIN THE STATED CHRONOLOGY. No improved primitive or multiplication exponent is claimed.**

The shared target/center twist is a valid component. This report tests a concrete way to use it: replace the exactly-one side map by the binary identity `E1=I+B^T B`, where B is point/triple incidence. The resulting full dirty wrapper is exact. Even after granting every center gather and scatter transition zero cost, its complete local rank moment cannot support a positive saving. The obstruction is the cost of the direct self term together with its actual boundary frames.

## The scalar and projected programs

There are v=binomial(h,3) input banks x, v output banks y, v primary auxiliary banks u, v side auxiliary banks s, and h center auxiliary banks t. All auxiliaries and initial outputs contain independent arbitrary dirty payload functions. Thus W=4v+h is the complete stock.

Define a triangular scalar mixer and scatter by

```text
M: t <- t + B u;  s <- s + B^T t + u.
J: y <- y + s + B^T t.
```

Over binary payloads, their source/output map is `JM=I`: the two `B^T B` contributions cancel. M has 7v CNOTs and J has 4v CNOTs. These are pointwise operations at a common frame.

Use the source-line projector P_T, the target complement F_T=I-P_T, and the point-total envelope H_c from the independently replayed pinned rational geometry. The complete physical word is:

1. At the common zero frame, run M, J, and M inverse to establish the dirty echo.
2. Frame the primary u_T at P_T, side s_T at F_T, and center t_c at H_c. Inject x_T into u_T at their common P_T frame.
3. Gather into each center using a literal source excursion P_U -> H_c -> P_U. The two rank-(h-2) partial swaps are paid for each incidence.
4. Apply the shared twisted center scatter into s. Its center and target factors are rank one and are both explicitly undone.
5. For each T, move u_T from P_T to F_T by one width-h partial swap and add it to s_T. Keep this move applied, absorbing its inverse into the final auxiliary cleanup.
6. Grow y_T to F_T, add s_T into y_T, and apply the shared center scatter into y.
7. Complete all auxiliaries to the common full frame and run M inverse there.
8. Complete x_T to the full frame and inject it into u_T again.

Every literal CNOT has equal actual endpoint frames. In particular, the self term is not allowed to copy from P_T to F_T for free. Its transport is

```text
S(P_T) S(F_T) = S(full).
```

All rank-counted operations are actual invertible address maps. The observed forward payload law is

```text
x_T(a) -> x_T(S(F_T) a)
y_T(a) -> y_T(S(F_T) a) + x_T(S(full) a)
every auxiliary d(a) -> d(S(full) a).
```

The binary plus sign denotes XOR of independent arbitrary payload functions. The checker also reverses and transposes the collected physical events and verifies the corresponding transposed source/sink law. It uses the actual program, including all permutations, rather than relabeling its symbolic output.

## The favorable rank ceiling

Same-width calls are permitted under the [complete depth and row-budget mechanism](../transfers/same-width-row-budget.md). The v width-h self calls have stock ratio v/(4v+h)<1. That condition permits them as dependencies; it does not establish contraction of the full moment.

Delete all gather and shared-scatter transitions, granting them zero cost. A primary's remaining chronology is

```text
zero -> P_T -> F_T -> full,
rank charges 1, h, 1.
```

The inverse of the self transport has already been absorbed into cleanup: its final charge is rank one, not another width-h call. Every side and center auxiliary still needs total rank h. The two data boundary banks contribute 2v(h-1). Therefore the optimistic histogram is

```text
n_1     = 3v+h,
n_(h-1) = 3v+h,
n_h     = v,
sum_r n_r r = (4v+h)h = Wh.
```

For any positive saving a, the normalized local rank moment is

```text
M(a) = sum_r [n_r r/(Wh)] (h/r)^a > 1.
```

At a=0 it is exactly one; at a>0 its rank-one and rank-(h-1) terms grow strictly. Removing scalar costs cannot repair this. A remaining-depth budget can resolve termination but cannot turn this noncontracting moment into the required contraction.

The literal histogram includes the transitions optimistically deleted above:

```text
n_1     = 7v+5h,
n_(h-2) = 6v,
n_(h-1) = 3v+h,
n_h     = v,
sum_r n_r r = Wh + 4(v+h) + 6v(h-2).
```

There are 38v paid CNOTs. The checker compares its collected permutation events against this derived histogram, then verifies exact strict moment lower bounds at a=1/9999 and a=1/999. At h=23 the favorable mass is 163,461 on stock W=7,107; at h=25 it is 230,625 on stock W=9,225. Both equal their capacity.

This is a new local model derived from the explicit word, not a deleted obligation or small patch to the old 47-inequality controller. The favorable statement concerns this chronology and these complementary boundary frames. It is not a general lower bound for cancellation circuits, nonstationary frames, full Clifford/Lagrangian frames, altered source/sink geometry, or a different stock organization.

## Exact finite evidence and negative controls

Four independent workers checked (h,q)=(5,7),(5,11),(6,11),(7,13) in about 2.81 seconds. Each case covers all q^(2h) addresses symbolically and every independent source, output, and dirty auxiliary function. Matrix composition and cancellation of the group-algebra rows establish these finite equalities without enumerating the address cube.

There are eight complete positive forward/transposed replays and sixteen matched negative replays. Erasing the self transport violates common-frame gating and changes the payload law. Using the old primary cleanup after keeping the full self transport leaves incorrect dirty payloads. Each corruption supplies a literal single-nonzero-payload address witness and unequal expected/corrupted bits. The checker also rejects any charged rank that differs from the exact rank of the corresponding address map minus identity.

The native h=23/25 evidence here is an exact integer favorable/actual ledger, with the all-h algebraic chronology argument above. The full symbolic finite word was tested only at h=5,6,7. No native compiled routing, precision transfer, or all-size tape program is claimed. The usual ambient/denominator exclusions remain necessary; h=9 is not covered as a nondegenerate rational frame.

## Interpretation and continuation

The scalar low-rank incidence identity does not save this physical controller. Once its direct self term is transported lawfully, the source/sink boundary saving is spent even under highly favorable center assumptions. Repeating XOR searches or increasing h within this word cannot change that equality.

The shared twist remains available for a different chronology where target factors telescope with necessary operations or where the direct self term is avoided. More general quadratic or Clifford frames change the geometry and gate interface, and require their own physical word and complete cost ledger. They are not excluded by this example.

## Reproduction and provenance

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/incidence_dirty_wrapper.py \
  --workers 4 --output research/integer-mult-breakthrough/work/synthesis/NEW-RUN/results
```

- [Source](../../code/synthesis/incidence_dirty_wrapper.py), importing [shared_twist_factorization.py](../../code/synthesis/shared_twist_factorization.py) and [global_incidence.py](../../code/synthesis/global_incidence.py).
- [Source-hash protocol, complete receipts and negative witnesses](../../runs/20261008T220227Z-synthesis-incidence-wrapper/results/).
- The eight-phase wrapper and every-address group-algebra verification method are read-only reference methods from the CPU checkpoint's `joint-frame/agents/scout/code/framed_word_group_ring_v2.py`; the pinned geometry is the PR58/PR48/copied-center predecessor chain already recorded by the component reports. This new incidence mixer, paid chronology, exact implementation and favorable negative were developed with OpenAI Codex. No external novelty or formal-verification claim is made.

Only Python's standard library is required. The original local receipt is retained in ignored `work/synthesis/20261008T220227Z-incidence-wrapper/results`; the durable copy preserves every essential numerical, scalar-map, rank and negative-control result.
