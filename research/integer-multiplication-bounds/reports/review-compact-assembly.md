# Independent compact recurrence and composition audit

The new compact-control recurrence and both saved composition rows pass
independent exact arithmetic. With the independently promoted 484,264-role
bit circuit, accepted shared 629,617-role complex circuit and accepted
phase-cell Gaussian inverse, the tight conditional witness is

```
kappa = 3111277520532267774488444782831 / (2*10^39).
```

It exceeds 18.742635665857034 times the new upstream 83/10^12 bound and
2^-30, and remains below 2^-29. It is a changed-estimate composition using
the separately pinned compact-control proof, whose [independent transfer
review](review-compact-controls.md) is positive within retained contracts.
It is not a formal proof of the full multiplication machine or a universal
optimality result.

## Method and evidence

[review_compact_assembly.py](../code/review_compact_assembly.py) imports only
previous independent reviewer count/logarithm routines. It never imports
the composition producer. [The repaired terminal run](../runs/20261008T013650Z-review-compact-assembly-repaired/)
checks 738 exact stopped recurrences, separately recomputes the original
h25 complex counts, and audits both supplied campaign rows. It used Python
3.14.4; `/usr/bin/time -v` measured 0.14 seconds and 22,240 KiB maximum RSS.

The first run stopped at a reviewer input conversion: the upstream paired
certificate stores h as a JSON string, and the adapter initially passed it
to math.comb. The failed source/trace are preserved in
[its own run](../runs/20261008T014400Z-review-compact-assembly/). The repair
only converts h and side-role count to integers, with a fresh run/output.
The failed run name was selected ahead of its actual start; exact timestamps
in its protocol are authoritative. No mathematical result was overwritten.

Each campaign row has 34 independently recomputed strict conditions, in
addition to checking positivity of all 36 producer slacks. Counts, exact
independent logarithm enclosures, all seven margins, stopped guard constants,
the active minimum, decimal-grid kappa, all five numeric cutoffs, and the
three-branch model ceiling agree. Finite graph replay is deliberately a
separate input: this audit consumes the previously completed full 484,264
promotion and accepted complex transfer rather than repeating them.

## Correct compact recurrence

For normalized time F(e), exact complete-row splitting gives

```
F(e) <= (s/W) F(e/m) + O(G^tau e^tau + 1),
F(e) = O(e) for e < d^beta,
G = O(log p).
```

At level j the nonconstant internal contribution is
O(G^tau e^tau ((s/W)/m^tau)^j). For any admitted strict
log_m(s/W)<sigma<1, the all-root bound has exponent

```
chi = tau + (1-beta)*max(sigma-tau,0).
leaf = sigma + beta*(1-sigma).
reservation = max(1-c,0).
```

If sigma<=tau, every level is bounded by its root term. If sigma>tau,
the last internal node still has size at least d^beta, so its level factor
is at most a fixed constant times d^((1-beta)(sigma-tau)). Leaf size is
below d^beta and the leaf exponent 1-sigma is positive, so the leaf bound
has the stated orientation. Additive 1 charges are absorbed at internal
nodes. Base-m pieces and logarithmic field widths add fixed powers of log p,
which strict lambda/lambda-prime gaps absorb.

The independent controls execute full integer recurrences at radix m=64,
tau=1/2, beta=1/3, d=64^(3k), G=(k+1)^2 and branching factors 4,8,16,
covering sigma=1/3,1/2,2/3 and every root 64^n up to d, for k=1..12.
Bottom-up recurrence values agree with an independently summed tree and
the appropriate internal/leaf bounds. These are genuine stopped leaves,
including roots already below threshold. No K^tau charge is present in the
new movement contract. Adding it would change the root cost by an unbounded
factor for K=64^k. The previous quadratic estimate is therefore not being
silently reinterpreted.

## Original new-upstream regression

The original complex h25 values independently recompute to
v=2300, m=15625, N=12167000000, W=58645352620000,
L=10315500000, s=916333630984500000 and
eta=14/3464399375. Exact reviewer logarithm series confirm that this supports
1-sigma=418/10^12. The retained paired bit circuit supports
1-tau=296/10^11. The new stopped guard and displayed parameters reproduce
the seven margins and

```
Gmin = 333833/(4*10^15),
Gmin - 83/10^12 = 1833/(4*10^15) > 0.
```

The general guard requires L<N for the complex network, not the rational
bit source-rank condition L<N/2. The h25 values satisfy the former and fail
the latter, so these conditions cannot be conflated.

## Campaign rows and scoped limit

Write a=1-tau, b=1-sigma, x=1-beta, q=1-lambda-prime. The accepted campaign
counts establish b>a. The internal exponent is consequently tau. The
actual seven margins are

```
g1 = 1-epsilon*(1+c),       g2 = epsilon*a*c,
g3 = epsilon*q,             g4 = a*(1-epsilon),
g5 = min(1-epsilon-delta,r-delta),
g6 = 1-epsilon-delta,        g7 = epsilon.
```

The guard has C1=1+4x+zeta. The strict recurrence gaps require q<a and
q<b*x; reservations require q<c. The tight row takes c=1-2^-64,
q=a*(1-2^-63), x=(q/b)*(1+2^-64),
epsilon=(1-2^-64)/max(1+c+q,C1), r=(1-epsilon)/2, delta=r/8.
Every displayed gap is positive with exact fractions; no floating threshold
is used. The leaf/guard beta is about 0.752 and legitimately uses the new
general-beta depth proof. It does not modify an older checker restricted
to beta>=0.9.

For any admitted positive minimum saving G, q<a gives G<epsilon*a.
Movement requires c>=G/(epsilon*a), while prefix cost gives
G<=1-epsilon*(1+c). Together they imply
G<=a*(1-epsilon)/(1+a). Balancing with G<=epsilon*a proves
G<=a/(2+a).

Leaf plus guard gives G<epsilon*b*x and epsilon*(1+4x)<1, hence
G<b*(1-epsilon)/4. Balancing this with epsilon*a gives
G<=a*b/(4*a+b); balancing it with epsilon*b (x<1) gives G<=b/5.
Thus this declared parameter family's scoped upper bound is

```
U(a,b) = min(a/(2+a), a*b/(4*a+b), b/5).
```

Each branch is nondecreasing in both primitive savings. Independent upper
logarithm enclosures therefore supply a valid rational upper ceiling.
For the current b>4a/(1+a), the active branch is a/(2+a). It is approached
with c→1, q→a, x→a/b and epsilon→1/(2+a); the guard is then strictly slack,
and the reviewed phase constraints also stay strict. The producer's current
prefix-branch limit is consequently justified within this family. It is
not a lower bound for other circuits or integer multiplication algorithms.

## Cutoffs and one corrected wording issue

The tight row's five checked log2(b_input) cutoffs are gamma28,
logarithmic-alpha257, phase-cell73, compact-controls577, and full-guard97328.
The common numeric parameter cutoff is 97328. This does not include the
unspecified eventual BHP prime threshold, descriptor/record domination and
strict logarithm absorption; those additional thresholds remain explicit.

The v1 producer comment used K>=8L+40 for real L=log2(b_input). Since
p=6b_input, the unconditional ceiling inequality is
ceil(log2 p)<=L+4, so K>=8L+48 is sufficient. The independently checked
stronger comparison is

```
2^floor(577/3) >= 32*577+192.
```

The actual margin is enormous, and the function
2^(L/km)/(32L+192) increases for L>=2km. Together with
K>=b_input^(epsilon*c)/4, this proves the intended cutoff for every real
L>=577. The numerical witness and cutoffs do not change. The producer was
not edited; its owner was informed and preserved v1 while adding the
stronger statement to a fresh adapter. This was a local explanatory
constant omission, not a counterexample to the candidate.

Reproduce using the original saved v1 certificate:

```bash
python3 -B research/integer-multiplication-bounds/code/review_compact_assembly.py \
  --certificate research/integer-multiplication-bounds/runs/20261008T012400Z-downstream-compact-composition/results/certificate.json \
  --reference /path/to/upstream-compact-control-6e564879 \
  --output /fresh/path/compact-assembly-review.json
```

The code refuses an existing output and records source/input hashes. The
companion transfer report states the precision, finite-tape, complete-field,
dirty-scratch and separate-complex-arity dependencies. The original pinned
theorem remains conditional in exactly that broader sense.
