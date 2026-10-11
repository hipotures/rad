# Upstream review comments

Review comments for CrocSwap/integer-mult-bounds #448 (head `359022bc`) and
#480 (head `668c7dd0`). They draw on sections 1 and 2 of the
[batch report](../report.md). The user posted both on 2026-10-11 from these
files:

| PR | File | Posted comment |
|---|---|---|
| #448 | [pr448.md](pr448.md) | https://github.com/CrocSwap/integer-mult-bounds/pull/448#issuecomment-6113791847 |
| #480 | [pr480.md](pr480.md) | https://github.com/CrocSwap/integer-mult-bounds/pull/480#issuecomment-6113805810 |

The agent's permission policy blocked it from posting, so the user posted the
comments with absolute paths:

```bash
gh pr comment 448 -R CrocSwap/integer-mult-bounds --body-file <this directory>/pr448.md
gh pr comment 480 -R CrocSwap/integer-mult-bounds --body-file <this directory>/pr480.md
```

Both comments end with the attribution "This analysis was carried out by Claude
Opus 5.5 (Anthropic) under human supervision."

## Replies (checked 2026-10-11 21:40 UTC)

The author of #448, #480 and #494 (higherbeing) accepted the finding within
minutes:
[#448 reply](https://github.com/CrocSwap/integer-mult-bounds/pull/448#issuecomment-6113842081),
[#480](https://github.com/CrocSwap/integer-mult-bounds/pull/480#issuecomment-6113842267),
[#494](https://github.com/CrocSwap/integer-mult-bounds/pull/494#issuecomment-6113842488).

- They state that #448 §2 and §7 take the split action `D_a^A ⊗ D_b^B` as
  given, which presupposes a multi-stream register interface that the hub
  never states. The realisation that exists is the two-register control.
- Their own estimate prices that control as a net loss: about +5,000 cost
  units per invocation for the extra registers, against about 2,100 saved,
  on #448's bit template. This estimate is theirs; it was not checked here.
- They retitled #448, #480 and #494 as "Under review (split-residual
  interface) ... not established" and left them as drafts, with the packages
  intact. They also name #450, #453, #464 and #469 as resting on the same
  slot.
- #499 (another author, opened 21:32 UTC) stacks on #494 and still claims
  1.452948511251494e-3. Its body calls the slot disputed.
