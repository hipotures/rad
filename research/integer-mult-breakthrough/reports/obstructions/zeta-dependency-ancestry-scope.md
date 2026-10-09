# Exact zeta endpoints do not determine computational ancestry

Status: **EXACT FINITE MODEL DISTINCTION**. This supplies no shorter zeta
word, general lower bound, native implementation or multiplication exponent.

The primary reference is Joan Boyar and Magnus Gausdal Find,
[Cancellation-Free Circuits in Unbounded and Bounded Depth](https://arxiv.org/abs/1305.3041),
arXiv1305.3041v2,17October2014, Section6. It proves the exact
h*2^(h-1) cancellation-free bound for the subset-zeta/Sierpinski family.
Its discussion separates this model from unrestricted cancellation and
mentions a weaker ancestry restriction. Its reported finite XOR experiments
are prior evidence, not executable certificates imported by this campaign.
The versioned PDF and acquisition receipt are pinned independently; a paper
or downloaded dependency is not required for the authored finite checks.

## Two different predicates

Our scalar row model versions each destination after an addition. Its
coefficient row is updated with the signed coefficient, while its ancestry
set is the union of both parent sets. Coefficients can cancel; a path through
an earlier version remains a path. No numerical rank is used as a substitute
for that graph predicate.

For every h>=1, start with the ordinary Yates row-add word for Z_h. Prepend
the two updates x_0+=x_(2^(h-1)) and x_0-=x_(2^(h-1)). Their complete
endpoint is the identity. The resulting exact operator is still Z_h, so its
upper-right block is zero, yet right-to-left ancestry is present. This
all-size elementary counterexample adds two gates; it saves no work. It
shows why a triangular final operator cannot justify a forbidden-ancestry
assumption for an arbitrary cancellation-allowing program.

The four-worker [complete finite run](../../runs/20261009T062256Z-zeta-dependency-ancestry/)
uses h1/h2/h4/h7, all150 operator columns and four arbitrary Gaussian fields.
Every endpoint and chronological inverse agrees exactly. Omitting the
cancelling return changes the full operator and is rejected. All aligned
recursive-block ancestry violations are checked; their counts and complete
ancestry hash are retained. Integer coefficient equality acts on arbitrary
Gaussian payloads without a numerical tolerance or a finite-field lift.

## A separately charged four-input cancellation example

An exhaustive immutable-signal XOR DAG search starts from the four singleton
inputs and retains every newly computed signal with free fanout. Its targets
have supports3,7,15,14. The unrestricted minimum is4 gates; the disjoint-parent
minimum is5. The exhausted frontier counts through those depths are
1,6,27,89,259 and1,6,27,89,211,343 respectively. This independently replays
the small model gap illustrated in the primary paper. It does not prove an
unrestricted zeta minimum or a Gaussian native bound.

For Gaussian data, a separate reversible lift performs b+=a, c+=b, d+=c,
then negates a and adds d to it. Reading registers in order b,c,d,a gives
the four target sums. Its explicit ledger is four row additions, one unit
sign and one fixed output permutation. The true reversed word restores all
arbitrary input columns. Removing the sign or pretending the final register
order already matches is rejected. Neither the clean DAG's free fanout nor
its signal stock is inherited as a free native reversible resource.

## Research implication and reproduction

A search restricted to monotone support or forbidden ancestry may remove
exactly the cancellation mechanism it is meant to test. The correct next
question is which deliberate excursions, dyadic divisions and complete
dirty returns can improve a fully charged primitive. A triangular endpoint
alone is insufficient evidence either for or against that mechanism.

The generator and interpretation were authored with AI assistance. Internal
review and exact finite execution remain distinct from formal verification.
From the worktree root, use a fresh output directory:

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/zeta_dependency_ancestry.py \
  --workers 4 --output research/integer-mult-breakthrough/work/REPRO-UNIQUE/zeta-ancestry
```

The bounded form is `--workers 1 --bounded`. It uses h1/h3 and the same exhaustive
four-input comparison. Standard-library Python3.11+ suffices. No native tape
time, memory stock theorem or improved characteristic is certified.
