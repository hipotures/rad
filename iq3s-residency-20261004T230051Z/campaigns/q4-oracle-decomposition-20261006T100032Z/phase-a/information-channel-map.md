# Information channel map, version 1

One logical unit is one full main-model verifier routed-layer T-by-10 batch invocation. Event = window*48+layer, with recorded model role, absolute token positions, speculative lanes and shapes retained. Current logical event is n. Bounded queries see events through n+H **inclusive**; H+1 is unknown. No individual expert serialization. FULL sees only the remaining finite tape, never a guard tail.

| Query / action | Channel | Scope |
|---|---|---|
| Candidate route enumeration | E and I | n+lead through n+min(64,I), inclusive |
| Incoming first next-use | IncomingFutureView | >=n+1 through n+I |
| Incoming count/value | IncomingFutureView | through min(n+I,n+768); v3 utility calculation retained |
| Resident victim next-use / ranking | VictimFutureView | >=n through n+V |
| Victim damage/count | VictimFutureView | through min(n+V,n+768) |
| Five initial spare donors | VictimFutureView | V at event 0, charged inside timed decode |
| Publication-time victim re-selection | VictimFutureView | V at actual publication boundary |
| Physical copy / completion / ownership / cancellation | Actual observed state | no future next-use; unchanged v3 scheduler |
| Reader/protection set | P, separately declared common channel | entire current verifier window; at most 47 forward layer invocations, plus already executed layers |
| Replay engine/router/branch/QSA overrides | Evaluator | full tape to execute identical work, inaccessible as utility |

**P is a common safety-privileged policy hint retained from v3**, not an undeclared I/V privilege. It can reject victims appearing later in the current window even when I or V is 4/16. Results at those small horizons are conditional on P. H64 and larger already encompass all forward P demand. Never weaken necessary reader protection to enforce a research budget. Initial first-window protection is the same common P channel.

Unknown-beyond-H differs from finite-tape-end. Unknown victim next-use uses the unchanged causal fallback H+1-log1p(observed heat), with expert-ID iteration tie-breaking. No hidden full-future tie or cached utility survives a role change. The old bounded next(at) allowed at+H, causing an incoming n+H+1 endpoint; v1 consistently uses n+H. Near the finite tape end, explicit finite-end state is distinct from horizon censoring. This is a versioned information repair, not a new allocator or policy optimization. Unrestricted full mode is unchanged.

Critical structural result: default deadline strategy stops after its **first feasible candidate**. Its computed .05*(incoming uses - victim uses) never ranks two feasible actions. Therefore I>=64 does not alter deterministic selection when V is fixed, despite reducing future-query CPU work. The incoming lifetime channel is dormant in this scheduler; a null I64 effect cannot establish that a future reuse-aware policy needs no incoming-lifetime predictor. The optional old reuse strategy is NOT enabled in this campaign.

Future index is built outside request timing in RAM, in both replay arms. Online query costs/copies/publication are charged. Index construction time and estimated index bytes are retained; raw observations/tape remain evaluator evidence. No runtime work/math/tape schema change, no copy worker changes, no extra GPU memory.

Tests: typed-view endpoint, suffix noninterference, role isolation; real-tape legacy-full victim/candidate equivalence and I64 equivalence across 1,205 decision points; real copy/reader/publication/cancellation fixture. The full runtime source diff is restricted to the oracle information header and a new typed-view header.
