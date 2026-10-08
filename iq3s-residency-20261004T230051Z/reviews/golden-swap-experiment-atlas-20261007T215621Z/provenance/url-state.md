# URL-addressable Atlas and read-only discovery

Base: `http://192.168.100.207:8765/`. The same relative links work on a portable clone's server. `/gallery` is the recommended entry point.

| Parameter | Meaning |
|---|---|
| view | `overview`, `residency`, `slots`, `churn`, `startup`, `expert`, `oracle`, `demand`, `classes`, `predictor`, `lease` |
| run / compare | Canonical IDs returned by `/api/runs`; compare is optional |
| gpu | `0`, `1`; omit for both |
| layer | Routed layer `0..47` |
| class | Exact blob bytes; omit for all classes |
| expert / experts | Single `0..511` ID or comma/range subset such as `3,17,100-120` |
| from / to | Visible range in the selected logical units; both required |
| time | `window`, `event`, `percent`; event = window × 48 + layer |
| smooth | Rolling/bin control in verifier windows, 1–256; heatmap adapts display bins to the zoom |
| metric | Global layer/time map quantity, such as admissions or CPU work |
| comparison | `absolute` or `difference` (A−B); exact shared logical work required for differences |
| focus | `1` hides secondary plots and filters; the header restores them |
| snapshot | `1` disables sticky navigation and Plotly toolbar for deterministic captures; PNG/SVG buttons remain |
| counts | `raw` rolling sum, `perWindow` rolling mean, `share` service percentage; transaction/copy units remain explicit |
| scope / limit / changed | Physical slot scope `all`, `layer`, `expert`; displayed most-changed count, 1–256; changed `0` includes unchanged slots |
| initial / short / long | Lease initial-observation toggle and exploratory lifetime thresholds in windows |

Application controls and Plotly time zoom serialize state with `history.replaceState`. Loading a normalized URL in a fresh browser reconstructs the same numerical plot signature. Changing pages intentionally retains filters; the visible identity strip exposes them. `All experts in layer` clears a retained expert restriction.

Read-only JSON endpoints:

```text
GET /api/views
GET /api/runs
GET /api/runs?task=code-archive
GET /api/matches?run=golden-swap-phase2--code-archive-block1-REPLAY_CURRENT
GET /api/interesting?run=golden-swap-phase2--code-archive-block1-REPLAY_CURRENT
```

Matches require a nonempty alignment identity. The response separates same-campaign, same-binary and same-attempt evidence; null means unavailable. Interesting selections rank observed admissions only and expose top layers/experts, not optimal leases or measured gains. Unknown IDs and endpoints return 404. No arbitrary filesystem or mutation API exists.
