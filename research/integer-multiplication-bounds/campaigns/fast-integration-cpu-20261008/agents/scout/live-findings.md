# Actionable public changes

This ledger records new mathematical or proof-status changes rather than every unchanged observation. All times are UTC on 2026-10-08. Public claims remain conditional and are not accepted as a complete theorem solely from their checks.

| Observed | Source and author | Pinned head | Mechanism / claimed saving | Proof status at observation |
| --- | --- | --- | --- | --- |
| 12:43 | [PR 36](https://github.com/CrocSwap/integer-mult-bounds/pull/36), icekylinx | `11817ccacb564bb7f98789c20dc11d3fece207e3` | Copied retained-center schedule, `(25,23)` bit graph; `kappa=3.84569e-5` | Written conditional proof and finite reconstructions; inherited unchanged checks reused |
| 12:43 | [PR 37](https://github.com/CrocSwap/integer-mult-bounds/pull/37), Rohan Arun | `cb86e50e9a07685068874d8e4174b2e6c209b95c` | PR 36 plus reversed `(23,25)` corners, data `9*[1]+[21,17,481]`; `kappa=3.850771033e-5` | Draft; full inherited rerun pending |
| 12:43 | [Swapnil round five](https://github.com/Swapnil-jain/integer-mult-kappa/tree/c2c2f279d93643e5ff3fe121a0fbc68e0e6f4007), Swapnil Jain | `c2c2f279d93643e5ff3fe121a0fbc68e0e6f4007` | Common flag, cheaper side circuit, finer side/data batching; `kappa=309575208081/(2*10^16)` | Finite arithmetic checked in Lean under explicit analytic premises; full algorithm conditional |
| 12:53 | [PR 38](https://github.com/CrocSwap/integer-mult-bounds/pull/38), Dominik Scholz | `cc794077f6c103e24ec0939be765cd1521239aab` | PR 36 plus fixed `I+J` local bases, complete original-envelope transitions; data `26*[1]+[21,481]`; bit `a=19432631/(5*10^11)`, final `kappa=3.886224e-5` | Draft; producer/moment/common-basis checks passed, full inherited rerun pending |
| 12:53 | PR 37, Rohan Arun | `2f7578affce416ad4b6c41f3438ebb734f66a899` | Scientific construction unchanged; validation receipt added | Ready for review; claims 182 inherited tests, 12 focused tests and 18 historical patch checks passed |
| 13:02 | [PR 39](https://github.com/CrocSwap/integer-mult-bounds/pull/39), Rohan Arun | `50e54ece17afa4bd3cccd1927e9cdea5098038c2` | Only middle `L25=I+J`, common generic rational `L23`, reversed data `9*[1]+[21,17,481]`; bit `a=3886826921/10^14`, final `kappa=3.886675852e-5` | Draft; portable replay and 10 focused controls passed; full inherited rerun pending |
| 13:02 | PR 38, Dominik Scholz | `605323bab4ba330de3d1785dc5b3ecb14e8ab747` | Scientific construction unchanged; validation receipt added | Ready; claims 170 inherited tests, both selected producer rebuilds and 19 patch checks passed |
| 13:11 | PR 39, Rohan Arun | `70ae24129649f6d6d4ec6360962a80c3c42a38f1` | Scientific construction unchanged; validation receipt added at 13:05:47 | Ready; claims 192 inherited tests, 10 focused controls and 18 patch checks passed |

All PRs in this table retain Apache-2.0 notices; their imported RaD interfaces retain CC0 notices. PR 36 credits Paureel, Swapnil Jain, Zhihao Chen, Rohan Arun, Dominik Scholz and earlier producers for distinct dependencies. PR 37/38/39 compositions inherit those mechanisms rather than independently adding their exponent savings.

The broader direct fork/search intake also found [platypii's Lean project](https://github.com/platypii/integer-mult-bounds-lean), whose public head moved through finite optimized-circuit and forward-frame proofs. It is work in progress; no new leading algorithmic bound was identified there. [Fernando's independent TypeScript report](https://github.com/fernandoeeu/integer-mult-bounds/blob/097b96a7eba8/independent/ts/prs/REPORT.md) checks finite earlier PRs through 16 and expressly leaves analytic obligations open. It does not review PRs 36–39.

The initial source snapshots and PR 38/39 snapshots are listed in [input-manifest.json](input-manifest.json). Readiness-only follow-up heads are identified above and in the observation files; no duplicate whole snapshot is necessary where scientific files are unchanged.
