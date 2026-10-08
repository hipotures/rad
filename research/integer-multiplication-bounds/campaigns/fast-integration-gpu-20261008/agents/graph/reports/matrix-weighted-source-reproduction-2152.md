# Matrix-weighted carrier allocation with actual signed frames

This checkpoint changes the carrier matching and the resulting physical XOR
word. It keeps Avi Eisenberg's pinned PR #62 scalar DAG and the selected
positive signed frame family, then recompiles using eumemic's PR #57
invertible binary synthesis and paid signal reclamation. Rohan Arun's earlier
carrier matching, the source partition and cloning predecessors, and the
full attribution chain in the public PR #62 source are inherited. Matrix
costs guide discovery; no weighted optimum is claimed. Prepared with AI
assistance under the inherited Apache-2.0 licensing framework.

The selected gain-first words have R23=27,719 and R25=36,354. The second
axis differs from the earlier physical word by one paid role; its denominator
must therefore also change. Their raw word digests are

```
h23 6f9c33370d171d407e3be66becc65f86adde884b37b3add15f22efe78121e71c
h25 5f4a4496af267f2e44efb0d67cfd450fe14e7ec841cfa457527b814206f78a93
```

Fresh source reconstruction uses the public construction commit
`ad0f25ff7b23cff7f08ad237c2254e6ecf74257e`, regenerates the rank-first
intermediate parents at budgets 3,584/5,120, proves their exact scalar outputs,
and independently derives the frozen multifamily signed frames. It then
checks each carrier against source coefficients and use lists, including
the incoming unit-row index, unique recipient use, strict chronology,
actual frame containment and donor linear independence. A carrier list is a
mathematical choice certificate, not a replacement for these checks.

The complete new physical words are regenerated after those checks. An
independent literal checker reconstructs all source and sink supports,
physical transitions and paid roles, and restores every binary dirty role
in both orientations. The recorded comparison against discovered transition
bytes is an additional identity check. The all-array claim retains the
conditional common-frame compiler transfer described in
[the dirty-address proof-scope note](common-frame-dirty-address-transfer-2048.md).
CRT matrix profiles, full source-pair DATA geometry, stock, moments,
47 assembly constraints and seven margins are separate acceptance evidence.
This source note alone does not certify a new exponent.

The portable matching inputs are
[h23](../fixtures/selected-matrix-weighted-carriers-h23.json) and
[h25](../fixtures/selected-matrix-weighted-carriers-h25.json), containing
33,441 and 48,074 selected source/use/row triples. Their sizes are 528,580 and
776,140 bytes and their SHA256 digests are

```
h23 835899e9425924f960a4f1decb2a937d2fee46d033c989ff102590b4f4e4a2a1
h25 d2123be9945cf1be89c5c41e1cb2b12f7547c08e247e0d9c52d6b98d8c76c326
```

The certificates contain no machine paths. The fresh reproduction path needs
no discovery cost table, saved candidate word, transition binary or native
discovery executable. In the repository root, set `TASK_SOURCE` to a pinned
public source snapshot and `TASK_REPRO` to a fresh external execution root.
Public input may be obtained automatically with `gh repo clone
CrocSwap/integer-mult-bounds` followed by an ordinary Git checkout of the
pinned commit; no manual transfer is needed. Then run:

```bash
TASK_GRAPH=research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008/agents/graph
python3 "$TASK_GRAPH/code/source_only_matrix_weighted_joint.py" \
  --source "$TASK_SOURCE" \
  --choices-file "$TASK_GRAPH/fixtures/joint-common-multifamily-reproduction-2107.json" \
  --h 23 --work "$TASK_REPRO/h23" --output "$TASK_REPRO/h23-receipt.json" \
  --expected-word-sha256 6f9c33370d171d407e3be66becc65f86adde884b37b3add15f22efe78121e71c \
  --selected-matching "$TASK_GRAPH/fixtures/selected-matrix-weighted-carriers-h23.json"
python3 "$TASK_GRAPH/code/source_only_matrix_weighted_joint.py" \
  --source "$TASK_SOURCE" \
  --choices-file "$TASK_GRAPH/fixtures/joint-common-multifamily-reproduction-2107.json" \
  --h 25 --work "$TASK_REPRO/h25" --output "$TASK_REPRO/h25-receipt.json" \
  --expected-word-sha256 5f4a4496af267f2e44efb0d67cfd450fe14e7ec841cfa457527b814206f78a93 \
  --selected-matching "$TASK_GRAPH/fixtures/selected-matrix-weighted-carriers-h25.json"
```

Each attempt must use fresh output names. The expected roles are 27,719 and
36,354; the regenerated signed transition digests are
`23e78e32602993681d9768f67a404d52b8e5b555f6a7b8ec3573fbe3e5a7952b`
and `b8ad609d37430e0bffa036268bdd8594ad764c6fd65d284e4bb94e99fcca40fd`.
Optional `--profile-transitions` checks exact bytes when a separately produced
profile input is available. Omitting it explicitly records that no such
comparison was requested, while all source, word and transition reconstruction
still runs.

The helper also emits original scalar-region envelope metadata. Those
smaller core/cover envelopes are not asserted to form a legal address
schedule for the new matching. Enlarging this new physical word requires
deriving its new compatibility closure and proving containment of the
actual selected signed spaces; an old unsigned template cannot be silently
substituted.

Evidence: [fresh h23 reconstruction](../results/joint-matrix-weighted-Q-source-only-23.json),
[fresh h25 reconstruction](../results/joint-matrix-weighted-Q-source-only-25.json),
[clean selected-only h23 reproduction](../results/joint-matrix-weighted-clean-selected-2152-h23.json),
[clean selected-only h25 reproduction](../results/joint-matrix-weighted-clean-selected-2157-h25.json),
[exact authored dependency manifest](../fixtures/matrix-weighted-selected-regeneration-manifest-2210.json),
[source-only constructor](../code/source_only_matrix_weighted_joint.py), and
[discovery allocation](../code/matrix_weighted_joint_carriers.py).

The complete selected matching lists are published as unsplit gzip evidence in
`evidence/matrix-weighted-selected-carriers-2216/`. Before the selected-only
commands, decompress each complete file to its original fixture path using
`published_selected_input_recovery` in the dependency manifest. SHA256 and
all original bytes are preserved. These row-level inputs use the repository
text-evidence publication path; the raw originals remain unchanged locally.
