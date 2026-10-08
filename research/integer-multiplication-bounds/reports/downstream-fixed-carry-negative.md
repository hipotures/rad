# Fixed common carried endpoint: a scoped negative

Unioning one first-stage endpoint into every middle gate destroys the
available rank deficit when the original data terminals are retained.
This conclusion applies to the literal fixed union construction. It does
not rule out role-specific carries, changed gate charts or changed
terminal contracts.

The exact [source](../code/downstream_carried_endpoint_discriminator.py)
has SHA256 `07b73bd939551b41a9bc774c0411268619257320f283d4dcbab23161da7cfdae`.
The completed [protocol](../runs/20261008T081203Z-downstream-carried-endpoint-negative/protocol.json)
and [certificate](../runs/20261008T081203Z-downstream-carried-endpoint-negative/results/certificate.json)
retain the commands, resource admission and result. Certificate SHA256 is
`b111c5540bb8c3cc31cb5505a68cc2331acf224a57792200c000ede7f1453094`.

Let the fixed carried space be `E=F tensor line(t_C) tensor Q`. The middle
base is `D0=line(t_A)^perp tensor F tensor Q`. The prescribed target for
triple T is `K_T=D0+line(t_A) tensor line(t_T)^perp tensor Q`. Whenever
the metric pairing of t_C and t_T is nonzero, `K_T+E=F tensor F tensor Q`.
The carried gate therefore includes the one-dimensional direction
`line(t_A) tensor line(t_T) tensor Q` excluded by the prescribed final
target. Returning to that target forces at least one decreasing rank.

At ground h, exactly `3 C(h-3,2)` targets are orthogonal to the fixed
triple. Put `v=C(h,3)` and `N_bad=v^2[v-3 C(h-3,2)]`. Signed dimensions
telescope; a descending dimension contributes twice to the excess of
absolute rank over signed change. Including the fixed negative-source
interface, the full rank obeys

`s >= W_new m - N + 2 N_bad`.

At h51, `N_bad=7563823780625` and `2 N_bad-N=6096248545625>0`. Thus the
rank exceeds `W_new m` even if every old central decrease is removed.
Exact positive excesses are retained for h39,49,51,52,53,56. This argument
does not use an assumed old half-deficit budget.

The finite controls explicitly construct rational projectors and test
all 24 targets at h4 and h6, including 26,944 exact matrix entries. The
span dimensions, containment predicates and nondegenerate lost lines
agree with the counting argument. These are local chart controls; a
complete fast primitive at either small ground is not claimed. Execution
used one worker, 1.275 seconds and 22,444 KiB peak RSS, with zero floating
point comparisons.

Reproduce from the topic directory:

```bash
python3 code/downstream_carried_endpoint_discriminator.py --output /tmp/fresh-carried-endpoint.json
```

The next useful carry experiment must change the common chart, associate
different carried subspaces with different roles, or change the terminal
restoration interface. Merely replacing the rank budget by a new role
count cannot avoid this obstruction.
