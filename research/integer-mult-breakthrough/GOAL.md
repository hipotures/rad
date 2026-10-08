# Integer multiplication: structural routes beyond kappa = 1e-4

## Mission

Start a new exploratory mathematical research campaign. Seek substantially stronger conditional bounds of the form

    T(n) = O(n (log n)^(1-kappa))

with a first major target **kappa >= 1e-4**, followed by mechanisms that could support 1e-3 or larger. These are research objectives, not promised outcomes. The model remains the stated fixed finite-alphabet, fixed-number-of-tapes framework unless an alternative model is explicitly separated as an auxiliary result.

Do not continue the old policy of chasing every incremental public record. Find mechanisms that can change the attainable scale. A useful outcome may be a new primitive, a rigorous conditional transfer, an exact counterexample to a tempting shortcut, or a scoped upper bound that redirects the search. Do not manufacture a headline exponent to satisfy the target.

Follow this directory's AGENTS.md. This is the new CPU research campaign; the other machine does not need to participate or exchange files.

## Start from evidence, not a clean-room restart

The branch starts from CPU checkpoint `def95e9c12f62a41fc7a50af13d5dcc87ce13d79`. Prior work is available under:

- `../integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/joint-frame/`
- `../integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/inverse/`
- `../integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/layout/`

Use these as read-only libraries of completed results, code, negative controls, and unresolved questions. In particular, the latest joint-frame README explicitly leaves the stronger CPU transfer as an OPEN integration obligation. Earlier optimistic prose is not authority to promote it.

Do not reopen all historical logs or rerun all historical tests. Inspect the relevant summary, exact dependency, and failure record for the question at hand. Any reusable component must retain its actual verification scope.

The user intends to stop the previous CPU campaign. Do not operate a shared checkout while its old coordinator is still writing. Use this branch in an isolated worktree when necessary; never reset or overwrite old work. This directive does not authorize killing unidentified processes or touching the other machine.

## First research question: what actually blocks 1e-4?

Build a compact mathematical map of the limiting inequalities and the operations that cause them. Distinguish:

- a proved obstruction within a precisely stated model;
- the limit of a frozen finite network;
- a conservative certificate or sufficient inequality;
- a restriction imposed only by the current implementation;
- an unproved assumption.

A concrete starting example is the inherited balanced assembly. With binary saving a, complex saving b, and stopping parameter beta, it requires

    a < (1-beta) b,       kappa < a/(1+a).

At b = 717/10^7 and beta = 1/20, these imply a strict ceiling below approximately 6.8110360663e-5 for that frozen setup. In that same setup, kappa >= 1e-4 requires at least

    a > 1/9999,
    b > 20/189981  (with beta = 1/20),

plus all the other strict margins. These are necessary conditions for this assembly, not a general impossibility theorem. The source pin is in input-manifest.json.

Determine whether the complex certificate b is already close to its full characteristic root, whether a stronger certificate exists, and which parameters or constructions must actually change. Reducing beta alone cannot reach 1e-4 while b remains 7.17e-5. Conversely, finding a much better binary circuit may be a valuable component even before the complex side catches up; do not discard it merely because the unchanged outer assembly cannot yet use it.

For each proposed family, write an optimistic but honest bound or sensitivity model for its attainable end-to-end gain before launching a large sweep. Mark hypothetical component costs as hypothetical. If the family cannot reach the target under its own frozen assumptions, change those assumptions explicitly or retain it only as a supporting component.

## Parallel initial portfolio

Launch at least four scientifically different lines of investigation where supported. These are starting questions, not an exhaustive menu or compulsory implementations. Replace weak directions and invent additional ones freely.

### A. Complex primitives and phase machinery

Investigate substantially stronger complex networks, not only binary graphs. Reconstruct the complete complex characteristic and assess slack in its current certificate. Explore shared complex subcomputations, different combinatorial families, arities, stopping choices, or reversible phase decompositions.

Keep Gaussian-dyadic arithmetic, residual phases, normalization, scalar gates, dirty auxiliary restoration, and precision charges explicit. Binary XOR improvements cannot be copied to the complex stage without a semantic argument. First seek exact small constructions and mechanisms that scale, not unmotivated exhaustive scans of one old parameter.

### B. Wider circuit and reversible synthesis spaces

Investigate whether the current cancellation-free, pair/triple, local-frame, or region-by-region restrictions conceal much better implementations of the required map. Possible tests include cancellation-allowing XOR synthesis, global linear-signal bases, cross-region joint synthesis, and different input/output combinatorial representations.

Use SAT/SMT, integer programming, exact linear algebra, or custom searches when useful. An optimum proved for a tiny instance is local to that instance and model. A circuit with fewer XORs is not automatically a faster physical network: bind it to admissible frames, literal reversible words, source/sink semantics, and paid transitions before promoting it.

### C. Coupled recurrences and different analytic transfers

Study whether the dependence between the binary and complex stages can be changed. Explore alternative mutually recursive primitives, asymmetric stopping rules, different conversion paths, and changed CRT/Gaussian/FFT organization.

Account for every conversion and prove well-founded recursive size decrease. No circular improved-multiplier oracle, free bit permutation standing in for nonlinear CRT, or unpaid movement of complete payloads is allowed. Use the prior CPU guarded-CRT and packed-Gaussian work critically: its open integration boundary is an explicit research task, not an already available theorem.

If a new algorithm changes the sufficient inequalities, derive a new ledger from its operations. Do not require every new architecture to satisfy the old 47-row ledger, and do not claim those old obligations disappear without replacement proofs.

### D. Independent obstruction hunting and literature-led alternatives

Search broadly outside the current PR chain: original integer-multiplication research, structured transforms, linear-circuit complexity, reversible synthesis, rank-profile methods, and relevant approximation/precision theory. Prefer primary sources and executable original implementations.

Turn each promising source into a concrete lemma to test, a small exact model, a counterexample search, or a measured primitive. Distinguish general lower bounds from restrictions of our representation. Challenge the other tracks' hidden costs and offer alternative mechanisms rather than only reviewing their prose.

Do not make this a permanent paper-summary agent. The track must generate experiments or mathematical deductions and may launch its own approximately four-worker jobs.

## Explore widely without creating idle bureaucracy

Use multiple local subagents. A default experiment gets about four CPU workers. Four or more such experiments may overlap on this 12-slot host; CPU oversubscription is explicitly allowed under the memory and disk safeguards in AGENTS.md. No 100% CPU target applies.

Start with cheap discriminators, then expand the families that show plausible leverage. Run independent seeds, schedules, representations, or mathematical assumptions in parallel; duplicate configurations are not independent ideas. Continue developing hypotheses while computations run.

A short reconnaissance is sufficient to launch the first exploratory jobs. Do not spend the first phase building infrastructure, synchronizing every fork, or repeating a complete baseline campaign. Local solvers and scientific dependencies may be installed when needed. Ordinary primary-source browsing and proof work are also valid uses of time.

When one hypothesis fails, preserve the counterexample or scoped bound and explore another. Do not declare the entire objective impossible because one construction or a named longstanding problem resists an initial attempt.

## Verification proportional to the claim

For discovery, use fast numerical or modular screens with explicit uncertainty. Before accepting a finite improvement, obtain exact scalar/phase identities, correct input and output maps, lawful capacity and causality, and independent replay of the actual program where applicable.

Before claiming a full conditional exponent, reconstruct the complete child distributions and scalar charges, prove moment bounds with rigorous enclosures, retain every source and exceptional case, and check the relevant physical, precision, routing, setup, normalization, and recovery obligations. Distinguish a finite certificate from an all-size theorem. Do not infer exact rational ranks solely from agreement at a few primes.

A new mechanism deserves independent criticism by a subagent that did not author it, plus targeted negative controls. Preserve disproved shortcuts. Do not present model-assisted internal review as external human peer review or formal verification.

## Deliverables and scientific progress

Keep a lightweight hypothesis portfolio and bottleneck map, then add only the source, configurations, run records, proofs, counterexamples, and reproduction material actually needed. Follow the root storage policy and the local ignore rules.

For each live line record: what assumption it changes, why its potential gain is large enough, the next decisive test, current evidence, and its continuation criterion. Separate improvements to a component from improvements to the final kappa.

Milestones are:

1. Identify at least one credible route not capped below 1e-4 by unchanged assumptions.
2. Obtain exact finite or analytical evidence for its decisive mechanism.
3. Integrate the necessary binary, complex, and transfer improvements with explicit assumptions.
4. Independently review a conditional result at or above 1e-4, or record a precise obstruction and move to a different route.
5. Continue toward larger scales after a successful milestone.

Commit and push useful milestones and failures to this research branch. Keep attribution to every imported method, with source revisions and AI-assistance disclosures. Do not open an upstream PR automatically. This campaign has no fixed deadline and does not stop merely because another public PR reports a better score.
