# Exact dyadic unitary restrictions and an arity-three escape

Status: EXACT FINITE EVIDENCE, with separately stated elementary analytical
lemmas. This is an auxiliary circuit model, not an integer-multiplication
lower bound and not an improved multiplier.

## Question and model

Can a compiler restricted to exact Gaussian-dyadic two-coordinate unitary
gates gain new parameters by changing normalized butterfly angles? Can its
ordinary in-place gate count gain a power of a logarithm?

The row restriction below applies to `Z[i,1/2]`, exact unitary gates, and two
complex coordinates. It excludes larger arity, Gaussian rationals with odd
denominators, and nonunitary intermediate circuits. The entropy restriction
additionally concerns ordinary in-place gates acting on an explicit matrix.
Compressed recursive bulk operations have different costs and obligations.

## Two-coordinate row classification

Write `a=(A+iB)/2^k`, `b=(C+iD)/2^k`. Unit row norm means

`A^2+B^2+C^2+D^2=4^k`.

For `k>=2`, reduction modulo four says either all four integers are even or
all four are odd. The all-odd case has square sum four modulo eight, while
`4^k` is zero modulo eight, so it is impossible. Divide every coordinate by
two and descend. For `k=1`, a square sum of four consists of a single
coordinate `+/-2`, or four coordinates `+/-1`. The case `k=0` is an axis.

Thus every normalized two-coordinate Gaussian-dyadic row is monomial or
balanced: `(abs(a)^2,abs(b)^2)` is `(1,0)`, `(0,1)`, or `(1/2,1/2)`.
Each row with nonzero balanced coordinates has real and imaginary parts
`+/-1/2`. Increasing dyadic precision introduces no continuously adjustable
angle in this exact two-coordinate model.

This is an elementary all-denominator argument, not a conclusion from
enumerating a few denominators. The finite discriminator enumerated every
signed row with denominators `2^k`, `0<=k<=7`, including unreduced rows. It
found eight rows at `k=0` and 24 at every `1<=k<=7`, with exactly the stated
norm splits. No exceptions occurred.

## Entropy restriction and its boundary

Nir Ailon's [2013 primary paper](https://arxiv.org/abs/1305.4745v1) proves that
an in-place circuit of two-coordinate unitary gates for a flat normalized
Fourier transform needs at least `N log2(N)/2` gates. Its entropy potential
is `Phi(M)=-sum |M_ij|^2 log2(|M_ij|^2)`.
The [2014 extension](https://arxiv.org/abs/1403.1307v5) gives a
condition-dependent restriction for nonunitary transformations; those
hypotheses must be checked before applying that result.

An elementary extension of the two-row argument uses an `r`-row block:
unitarity preserves each column's mass in the block, and dividing that mass
among `r` coordinates changes its entropy by at most that mass times
`log2(r)`. The block's total mass is `r`. Hence one such gate changes Phi by
at most `r log2(r)`, and a flat map needs at least
`N log2(N)/(r log2(r))` gates. Fixed arity changes a constant in this explicit
unitary gate model. This extension is an analytical deduction, not formal
verification of a general circuit lower bound.

Exact Gaussian-dyadic Walsh butterflies of sizes 2, 4, 8, 16 and 32 were
replayed over rational real and imaginary parts. Their full Gram matrices
are identities, every output squared modulus is `1/N`, and every literal
two-row gate increases Phi by exactly two. They attain the scoped bound.

The negative control `diag(2,1/2)` is nonunitary. Applying its inverse to
reach the identity increases the same potential by `15/2` in one two-row
step. This rejects an illicit extension of the unitary step bound to arbitrary
basis changes. Unitarity only at the final output is insufficient.

## A concrete escape and what it does not establish

Three balanced Gaussian-dyadic gates, on pairs `(0,1)`, `(0,2)`, `(0,1)`,
give a unitary three-coordinate macro with squared first-row magnitudes
`(5/8,1/8,1/4)`. Its exact scalar matrix and every intermediate Gram matrix
are checked in [wider_unitary.py](../../code/obstructions/wider_unitary.py).
Larger arity therefore escapes the two-coordinate angle classification
already at three coordinates. All three literal gates remain paid; this
observation alone changes neither the fixed-arity entropy scale nor kappa.

The original pinned multiplication manuscript distinguishes its Gaussian-
dyadic scalar ring from its binary label field. Its translation kernel
`a I+b X` has `a=(1+i)/2`, `b=(1-i)/2`; its bulk network also uses nonunitary
copy, gather, scatter and dirty restoration. The manuscript's use of ordinary
Hadamard matrices as identities does not assert that their irrational
coefficients are separately executed Gaussian-dyadic scalar gates. These
facts prevent the auxiliary restrictions above from refuting that framework.

The productive next question is whether a wider or nonunitary primitive
changes the complete residual/phase child distribution while keeping paid
normalization, precision, source/sink semantics and restoration. That remains
a HYPOTHESIS for the complex and transfer tracks.

## Reproduction, review and confidence

Run from the breakthrough worktree root:

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/unitary_dyadic.py --self-test
python3 -B research/integer-mult-breakthrough/code/obstructions/unitary_dyadic.py --workers 4 --max-row-power 7 --max-butterfly-power 5 --output /NEW/ignored/path/results.json
python3 -B research/integer-mult-breakthrough/code/obstructions/wider_unitary.py
```

The output path must be fresh. Standard-library Python 3.11+ is sufficient.
The run protocol is [retained here](../../runs/20261008T2112Z-unitary-dyadic/protocol.json).
The five corruption/ring/scope controls passed before the four-worker run.
Internal independent review by the synthesis agent checked the parity descent,
sign multiplicities, finite replay and nonunitary boundary; no logical defect
was found in the stated scope. Confidence is high for these exact finite and
elementary scoped facts. No physical network, full recurrence transfer, formal
proof package or external human peer review is claimed.

Sources: Ailon, arXiv:1305.4745v1 (2013-05-21), and arXiv:1403.1307v5
(2014-07-24), accessed 2026-10-08; original multiplication manuscript
`openai/math@adc7f1241b42e322a6451854ab7e4b4c146bf78a`, section 3,
blob `cdb0ba527aa8df5d57c151183fd3893c1a7e21ab`.
The row descent and arity-three discriminator were authored by Codex as
model-assisted research; novelty is unassessed.
