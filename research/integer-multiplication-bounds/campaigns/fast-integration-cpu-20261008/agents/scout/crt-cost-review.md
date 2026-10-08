# CRT cost audit: axis reversal is not the modular layout map

Reviewed 2026-10-08 around 13:49 UTC against the eligible public source
CrocSwap PR40 science commit `43f59ff533598762cbc43a5e14af2bbbc76fabbd`,
its inherited upstream08-assembly.tex, notes/nonadjacent-axis-note.tex,
and Swapnil commit `c2c2f279d93643e5ff3fe121a0fbc68e0e6f4007`.
This identifies an unresolved full-composition row; it does not criticize the
new packed Gaussian, locality or deferred Fourier lemmas.

## Two distinct maps

The known coordinate permutation reverses the padded mixed-radix axis order.
The arbitrary-coordinate router, and Swapnil's selected-bit Idea E', improve
that reversal. Its map is a fixed permutation of named binary slots.

The actual algebraic CRT layout is different. Write
`P_i=product_(j<i)s_j`, `mu_i=P_i^-1 mod s_i`, and ordinary digit index
`k=sum_i a_i P_i`. The tensor residue coordinates are

`b_i=a_i+mu_i*sum_(j<i)a_j P_j mod s_i`.

The source handles this triangular arithmetic map by d controlled rotations
of the valid intervals `[0,s_i)`, preserving padding. Controls precede their
target; descending i keeps them original. Each rotation copies the target
and its entire spectator suffix, paying O(V). Preparing its offsets once per
prefix is negligible, but that setup calculation does not remove its payload
scan. Inverse rotations have the same cost.

The source explicitly retains this charge: upstream08-assembly.tex lines889--890
states that the d CRT rotations cost O(dV), and nonadjacent-axis-note.tex line107
states the same after improving axis reversal. Swapnil stack-notes.tex Idea E'
addresses reversing CRT axis order, not performing all modular residue updates
in one known-bit route. The historical arbitrary router also expressly excludes
sorting by unrelated computed keys.

An independent exact discriminator strengthens this distinction.
[code/check_crt_bit_permutation.py](code/check_crt_bit_permutation.py) enumerates
540 valid addresses in four coprime shapes. The actual CRT map changes binary
Hamming weight on386 of them; every pure permutation of named binary slots
preserves that weight. For example, in source lengths(3,5), valid coordinate
(1,0) maps to(1,2), changing weight1 to2. Thus even on valid payload addresses
the arithmetic map cannot be silently replaced by axis reversal or another
bit-slot permutation. The retained [certificate](crt-bit-invariant.json)
also verifies CRT bijection and its recovered-control inverse. This invariant
does not rule out a new arithmetic router or nonlinear reversible circuit.

Reproduce from the repository root with:

```sh
python3 -B research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/scout/code/check_crt_bit_permutation.py --output <fresh-output.json>
```

## Consequence if the old rotations remain

With V=Theta(n), d=Theta(b^epsilon), this row costs n b^epsilon and requires
`kappa<1-epsilon`. The deferred Fourier row requires `kappa<epsilon*q`,
where q<a_bit. Their joint supremum is a_bit/(1+a_bit), even if all new Gaussian
and halo costs are improved. Assigning the entire CRT map exponent tau without
a separately proved replacement is invalid. A conditional theorem that newly
assumes such a router must name it as a new unproved premise; it cannot present
that premise as the inherited coordinate-router contract.

For clarity, the strict algebra is `kappa<min(1-epsilon,epsilon*q,a_bit)` with
q<a_bit. If kappa were at least a_bit/(1+a_bit), the first inequality would
force epsilon<1/(1+a_bit), while the second would force
kappa<epsilon*a_bit<a_bit/(1+a_bit), a contradiction. Conversely the two
limiting rows have supremum a_bit/(1+a_bit) as q approaches a_bit from below
and epsilon approaches1/(1+a_bit). This is a scoped cost obstruction, not a
lower bound for every integer-multiplication algorithm.

The coordinating agent was alerted immediately. A new joint arithmetic CRT
movement argument or another exact ordinary-convolution layout may resolve this
obligation. At the time of this audit no such argument had been independently
reviewed. The later [guarded CRT review](guarded-crt-review.md) supports a new
independent-node arithmetic batching lemma under the inherited primitives;
its completed schedules can remove this particular row. The scoped ceiling
above still applies to the original individual-rotation schedule.

## Long-precision source chirps do admit a different accounting

For the target chirp the phase numerator is one integer
`-sum_i s_i j_i^2 (r/t_i) mod 2r`. Every new t_i divides r, and log r=O(ell).
Computing all d terms with O(b)-bit metadata costs at most O(d b^2) per record,
absorbed by Q=d^18 for epsilon>1/2. Evaluate the SINGLE summed phase exponential
to Q-bit precision and apply it once to the coefficient. This removes d
independent Q-bit phase multiplications/evaluations. Its scalar multiplier and
exponential cost still needs its stated established bound, including logarithms
or an arbitrarily small fixed positive exponent. This valid metadata refinement
does not repair the separate d full-payload CRT rotations.

## Primary literature follow-up

Harvey and van der Hoeven's *Polynomial Multiplication over Finite Fields in
Time O(n log n)*, JACM69(2), article12, 2022,
[DOI](https://doi.org/10.1145/3505584), gives an explicit Turing-machine CRT
payload permutation in AppendixA.3 and a multivariate generalization in
CorollaryA.8. Its [author preprint](https://www.texmacs.org/joris/ffnlogn/ffnlogn.pdf)
has the same relevant derivation. LemmaA.4 splits two coprime factors using a
matrix transposition followed by row cyclic rotations. LemmaA.5 iterates those
splits. CorollaryA.8 bounds the complete multivariate conversion by
O(s_R*volume*log(volume)). This proves the right kind of machine result but
does not provide O(V polylog log(volume)) or eliminate the present d payload
scans. Replacing only its transpositions by an improved bit router does not
remove its actual arithmetic rotations.

Joris van der Hoeven's *Faster Chinese remaindering*,
[author source](https://www.texmacs.org/joris/chinese/chinese.html), addresses
scalar multi-modular reduction/reconstruction in the deterministic multitape
model. That scalar arithmetic problem differs from rearranging an entire array
of arbitrary coefficient payloads according to CRT index keys; it is not a
ready payload movement contract. No applicable faster joint CRT theorem was
identified by these primary-source checks.
