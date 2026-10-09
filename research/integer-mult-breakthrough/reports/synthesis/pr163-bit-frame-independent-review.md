# Independent review of the retained PR163 bit word

This review accepts the rational nested-frame geometry and complete formal \(\mathbb F_2\) chronology of the pinned bit component of [PR163](https://github.com/CrocSwap/integer-mult-bounds/pull/163), at commit `15c702a929b7d640107a95e196186ad74e876c82`. It does not independently establish the odd-local-ring weighted compiler, native tape cost, complex component, complete outer transfer, or the PR's conditional integer-multiplication exponent. The PR head advanced after this review began; these results remain pinned to the stated commit.

The reusable mechanism is operation-frame descent. The selected bit word changes 1,296 common operation frames while preserving the scalar word and workspace stock. It has no workspace alias/reuse pairs. Frame dimensions along each role still telescope to the same first moment, but the distribution of positive child widths changes. This can improve a concave moment without reducing scalar additions or total rank. The scientific question for new synthesis is how to construct admissible frames under both predecessor and future-cap constraints, including changes involving several adjacent gates.

## Independent checks

[pr163_bit_frame_review.py](../../code/synthesis/pr163_bit_frame_review.py) imports no reference executable source. It reads six immutable generated JSON inputs, verifies their SHA-256 values, and uses its own fraction-free elimination, kernel construction, Bareiss determinants and formal bitset replay. It checks the literal centre-first chronology rather than assuming that centre roots are read after all operations.

The completed two-worker review passed:

- all 22,924 used rational frames under \(G=I-J/9\), including source lines, side caps, gauge starts, partner mixing/delivery frames and all operation descents;
- every conservative source-vector direction in all 1,296 changed frames, each changed frame inside its retained original, and both participating roles' actual surrounding chains;
- the complete centre predecessor closure, response supports, current-value gauge deadlines, target cap chains and partner-pair source undo before workspace cleanup;
- every one of the 26,888 formal columns, including arbitrary initial dirty values in all 23,368 workspace roles and all labelled source and target columns;
- rejection of omitted live compensation, an omitted partner output, and source uninjection performed before source-pair undo.

The independent ledger gives \(h=24\), \(v=1760\), \(R=23368\), \(W=26888\), \(m=72\), rank `1,934,000`, copied-centre loss `528`, and deficit `1,936`. Its selected histogram exactly matches the retained component. The complete source/sink map is asserted over \(\mathbb F_2\). The integer lift is a different defining decoder and is not called an integer identity here. Rational frame tests are also distinct from a literal finite odd-local-ring address permutation replay.

Geometry took 7.2545 seconds and the full formal replay with three negative controls took 1.1799 seconds. The protocol requested four workers but used two natural independent tasks. No artificial workload was created.

## Determinant normalization and local-ring boundary

The first review tests high-dimensional rational frames using the smaller annihilator-side form proportional to \(G^{-1}\). Its completed receipt field `new_Gram_determinant_max_bits=63` therefore describes these normalized nondegeneracy witnesses; it is not the maximum determinant of every raw selected basis under \(9G\). The original source and receipt are retained unchanged.

[pr163_bit_frame_witness_v2.py](../../code/synthesis/pr163_bit_frame_witness_v2.py) separately recomputes \(\det(9BGB^\top)\) for every raw supplied new basis. All 1,296 witnesses pass, covering 888 unique raw bases. Their maximum absolute bit length is 73; the ambient cleared determinant `-132944071794787516438935` has 77 bits. All basis denominators are one, and all these nonzero exclusions are below \(2^{80}\). Primes above that bound avoid these new witnesses and the ambient determinant. Unchanged frames still require the inherited exclusions, and local-ring compilation, fallback and native fees remain explicit premises.

## New fixed-neighbor discriminator

The all-size [rational completion theorem](rational-frame-completion-and-paid-chains.md) constructs the attained minimum and maximum dimensions inside a future cap. [pr163_paid_chain_probe.py](../../code/synthesis/pr163_paid_chain_probe.py) applied it to the first 32 retained changed operations, with every other frame fixed, using exact integer-power intervals at \(p=999/1000\).

All 32 lower spans have radical zero. Twenty-four cuts are dimension-locked by both literal neighbors. The remaining eight have minimum/current/maximum dimensions `6/6/8`, predecessor dimensions `5/3`, and following dimensions `22/8`. The retained minimum has local widths `1,16,3,2`; the constructed maximum has `3,14,5`. Exact moment bounds favor the retained minimum in all eight. Thus this bounded experiment finds no further ideal improvement. It neither excludes coordinated frame changes nor proves global optimality. Future search should move connected frame blocks or change chronology, rather than repeatedly optimize these already-locked individual cuts.

## Reproduction and retained evidence

The read-only reference checkout used here is ignored `work/references/20261009T074633Z-pr163/repo`. Its upstream is `https://github.com/chafreaky/integer-mult-bounds`, branch `research/paired-cube-balanced-161`. Recover the pinned revision in a fresh ignored checkout and verify its hash before running the review:

```bash
git clone --no-checkout https://github.com/chafreaky/integer-mult-bounds.git <fresh-reference>
git -C <fresh-reference> fetch origin 15c702a929b7d640107a95e196186ad74e876c82
git -C <fresh-reference> checkout --detach 15c702a929b7d640107a95e196186ad74e876c82
python3 -B research/integer-mult-breakthrough/code/synthesis/pr163_bit_frame_review.py \
  --reference <fresh-reference> --component all --workers 4 --output <fresh-output>
python3 -B research/integer-mult-breakthrough/code/synthesis/pr163_bit_frame_witness_v2.py \
  --reference <fresh-reference> --output <fresh-prime-receipt.json>
python3 -B research/integer-mult-breakthrough/code/synthesis/pr163_paid_chain_probe.py \
  --reference <fresh-reference> --limit 32 --workers 4 --power 999/1000 --output <fresh-output>
```

The six indispensable input hashes are preserved in the review source and run protocols. The reference JSON inputs total approximately 10 MiB uncompressed; the downloaded source checkout is not asserted to be in Git. They are deterministically recoverable from the pinned upstream commit. No foreign producer is executed by the independent review.

Complete original evidence remains at:

- `work/synthesis/20261009T081946Z-pr163-bit-review/results/`;
- `work/synthesis/20261009T082853Z-rational-paid-chain-probe/results/`;
- `work/synthesis/20261009T083644Z-rational-bit-review-bounded/results/`.

The corresponding durable runs preserve exact protocols and compact receipts. Every namespace agrees with its recorded actual UTC start. The first review source SHA-256 is `fcca0d11b8bb52ab39dcecdb38c7d41357abba2203d3a8ef8871ce83b14dc1c3`; the separate raw-basis witness source is `1d2733ed6ed7a625a3db47060ff439730409a28fb21c82244314998589f6c660`.

Self-contained CI can use [verify_pr163_frame_contract.py](../../code/synthesis/verify_pr163_frame_contract.py) and its tracked [fixture](../../fixtures/synthesis/pr163-bit-frame-review-contract.json):

```bash
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_pr163_frame_contract.py
python3 -B research/integer-mult-breakthrough/code/synthesis/verify_rational_frame_completion.py
```

The contract contains three distinct actual cuts: operations `17436`, `20980`, and `27619`, with complete predecessor/future bases and conservative source labels. Four selection criteria were used, but the last changed operation is also the maximum raw-determinant case. The immutable fixture's descriptive `scope` string says four cuts; its explicit three-case list, this correction, and the verifier's three-case shape check are authoritative. These bounded checks do not repeat the entire external scalar word or claim that the full reference checkout is required by CI.
