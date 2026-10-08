# Sharing target and center factors in a global address scatter

**Status: EXACT AUXILIARY PRIMITIVE. No integrated physical controller, recurrence improvement or new kappa is claimed.**

The global incidence circuit failed a naive unpaid replacement of the point-total and target hyperplanes. Their rank-two mismatch nevertheless has structure: it is the sum of a target-only rank-one factor and a center-only rank-one factor. Those factors can be shared across the whole scatter rather than paid separately on every source/target edge. This supplies a concrete dynamic alternative to the stationary joint-frame ansatz.

## Exact factorization

Let P_T be the source-triple line projector and H_c the point-total envelope projector for c in T. Define K_c=I-H_c. Then P_T and K_c are rank-one mutually orthogonal projectors. The pinned rational formulas give

    K_c = q_c ell_c^T / [-12(h+1)],
    q_c = (3h-7)*1 + (h-9)e_c,
    ell_c = 3(h+1)e_c - 4*1.

Direct inner products ell_c^T w_T and z_T^T q_c are zero. Thus P_T K_c=K_c P_T=0 and H_c commutes with I-P_T despite those hyperplanes being incomparable.

For a projector P, let S(P) exchange the projected components of two address banks:

    S(P) = [[I-P, P], [P, I-P]].

It is an involution. Orthogonal projector factors commute and multiply as S(P)S(Q)=S(P+Q). Hence

    S(H_c)S(I-P_T) = S(P_T)S(K_c).

The target factor depends only on T and the center factor only on c.

## A literal shared word

The primitive has h center payload functions t_c and v=binomial(h,3) target payload functions y_T, each indexed by an address in an odd field to power 2h. All functions are arbitrary; center values and initial targets may be dirty. The desired update is

    y_T(a) ^= sum_{c in T} t_c(S(H_c)S(I-P_T) a),
    every t_c is restored.

Execute the following paid sequence:

1. Permute every center function by S(K_c).
2. Permute every target function by S(P_T).
3. Apply the 3v ordinary scalar CNOTs y_T ^= t_c for c in T.
4. Apply the target permutations again.
5. Apply the center permutations again.

The two target permutations restore every initial target function. Their conjugation supplies the target factor on each incoming center. The center permutations similarly restore all arbitrary center values. Exact row-permutation algebra yields the desired update for every address and every initial payload, including dirty banks.

The literal word has 2(h+v) rank-one partial-address permutations and 3v ordinary CNOTs. An explicit unshared implementation that independently conjugates each read-only CNOT on its source has 6v rank-two partial-address permutations and 3v CNOTs. Their rank-mass counts are 2(h+v) and 12v respectively. At h=23 and25 these are 3,588 versus21,252, and4,650 versus27,600. This comparison is between two specified auxiliary scatter implementations; it does not compare an accepted native controller or measured machine runtime.

## Evidence and controls

Every incident rational projector factor is checked for h=6,7,23,25. The complete finite odd-field word is replayed symbolically at (h,q)=(6,11) and(7,13), covering all q^(2h) addresses and arbitrary independent payload functions without enumerating that many addresses. Exact equality of symbolic row sums is sufficient to establish the update. Omitting either target or center inverse is rejected with an explicit single-payload address witness and expected/corrupted output bits.

The finite-field matrices are invertible actual address maps, not merely rank counts. Native h=23/25 factor checks are exact rational identities for every triple/common-point pair; this run does not supply the complete native h23/h25 source-injection/wrapper word. The underlying algebra extends to odd fields where all relevant denominators and ambient nondegeneracy factors are invertible, but the campaign's pinned prime/setup and routing contracts must still be preserved in an integrated result.

The strengthened-negative four-worker run completed in approximately 0.4 seconds. The prior unstrengthened local run retained the same positive factorization checks; it is a redundant exploratory record in ignored work and is not claimed as a separately published certificate.

## Expected leverage and the decisive next test

This factorization lifts the assumption that every target/common-point mismatch is implemented independently. Its potential gain is large enough to matter as a component. The smaller auxiliary scalar role counts already pass the first binary target in a hypothetical favorable frozen ledger; achieving that gain physically now depends on how the shared target factors interact with mandatory data endpoints.

The continuation test is a complete source/sink/dirty group-algebra wrapper that places the target-only S(P_T) factors next to already required endpoint permutations and checks exact telescoping. Any factors that survive must be charged. A standalone 2(h+v) rank budget cannot simply be added to or deleted from the old ledger: source-copy requirements, owned adapters, exterior banks, endpoint ranks and normalization must be rederived. If the per-target factors remain additional to the old controller, their cost can exceed its small N-L deficit and reject the frozen architecture despite the sixfold local comparison.

The new Gaussian quadratic rank-metric frame direction pursued by the coordinator is complementary. It may implement nonnested differences with different scalar/phase costs. The present result is an odd-field address partial-swap identity, not a conversion of it into a complex phase primitive.

## Reproduction and provenance

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/shared_twist_factorization.py \
  --workers 4 --output research/integer-mult-breakthrough/work/synthesis/NEW-RUN/results
```

- [Source](../../code/synthesis/shared_twist_factorization.py), importing [global_incidence.py](../../code/synthesis/global_incidence.py).
- [Complete receipt and negative witnesses](../../runs/20261008T215017Z-synthesis-shared-twist/results/), with all effective source hashes in the protocol.
- Projectors and partial-swap semantics come from the pinned PR58/PR48 and copied-center predecessor chain. The group-algebra proof method follows the read-only CPU control at `joint-frame/agents/scout/code/framed_word_group_ring_v2.py` in RaD checkpoint def95e9c12f62a41fc7a50af13d5dcc87ce13d79. The shared factorization and paid scatter sequence were developed with OpenAI Codex; no external novelty or formal-verification claim is made.

Only standard-library Python is required. No original source, model payload, solver or environment is copied into the durable tree.
