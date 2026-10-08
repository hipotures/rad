# Selective source-span frames in reversible joint compilation

The final finite construction chooses between the existing actual signed frame and an exact source-span frame at selected locations in the matrix-weighted joint word. It preserves the scalar word, selected carriers, source labels and physical roles of that weighted parent. The change is architectural: it uses the address space required by the actual source incidences, rather than imposing the original core/cover envelope as a lower bound. Choosing the minimum frame everywhere was worse; the profitable construction selects compatible spaces using the complete transition objective, including terminal side components.

## Exact source-span geometry

Write `H0 = I - J/9`, and let

`Gamma_c = {x : sum_i x_i = 3*x_c}`.

Every source incidence vector `w_{c,a,b}` lies in `Gamma_c`. On this whole address space,

`x^T H0 x = sum_{i != c} x_i^2`.

Thus `H0` is positive definite on `Gamma_c`. This identity concerns address vectors. It makes no restriction on the arbitrary array values carried by those vectors.

Construct the outside-vertex graph whose edges are precisely the source pairs `(a,b)` reaching a scalar producer. For each bipartite connected component, choose signs `sigma_i` opposite across every edge, including one component for each isolated vertex. A normal column supported on such a component has outside coordinates `2*sigma_i` and common coordinate `sum_i sigma_i`. It belongs to `Gamma_c` and is orthogonal, under `H0`, to every relevant source incidence: the pairing is `2*(sigma_a + sigma_b)`. Odd-cycle components contribute no normal column. Disjoint normal columns have Gram matrix `4*diag(component_size)`.

The unsigned edge-incidence rank of a connected outside component is its vertex count minus one if it is bipartite, and its vertex count otherwise. Consequently the span of the actual source vectors is exactly

`Gamma_c intersect {x : sum_{i in B} sigma_i*x_i = 0 for every bipartite component B}`.

Its dimension is `h - 1 - number_of_bipartite_components`. The graph helper represents this space as `complemented-signed-one-core-v1`. Its symbols encode normal equations; they are not ordinary positive-frame direction labels.

Let `P_Gamma` be the `H0`-orthogonal projector onto `Gamma_c`, and let `P_normal` project onto the disjoint normal-column span. Since that span lies inside `Gamma_c`,

`P_source_span = P_Gamma - P_normal`

is the actual rational projector. Under the selected nonsingular `L_beta = I - beta*J`, the physical projector is `L_beta*P_source_span*L_beta^-1`. Independent exact Fraction controls compare this subtraction with a direct Gram inverse of a complete integer kernel basis. Native certification then reconstructs all ordered northeast corner ranks and contiguous recursive widths from the literal selected transitions, using proven primes and bounded integer minors.

## Physical and endpoint interfaces

The final mixed word is independently rebuilt from the byte-bound fresh public-source weighted parent and the frozen allocation. Every operation, event and terminal uses its actual selected space. Selected spaces are contained in the old actual frames; the old frames are upper bounds. There is no assertion that an original envelope is contained in a new smaller frame. Every physical continuation has exact containment in its execution direction. Source injections, the protected two-core spaces and copied-center address spaces are retained, and the original scalar outputs and carrier capacities are verified again.

Ordinary outputs satisfy the literal normalized sink equation on every selected integer column:

`mu_T * L_beta * x = (3*sum_{i in T} x_i - sum_i x_i)/6 = 0`.

Their selected ranks may be smaller than `h-2`. The additional endpoint components are paid through the actual `h-rank` singleton count. In the final two words these counts are 11,890 and 15,319. Center spaces retain rank `h-1` and are independently checked by mutual containment against their original spaces.

The literal F2 word is replayed on all 31,261 and 40,954 payload-role basis directions, in both orientations. These counts are not the dimensions of all address components. Arbitrary address-array restoration uses the inherited exact frame-gauge lemma: a common-frame XOR commutes with the shared address gauge; composing the framed operations telescopes to `D_out * (S tensor I_address) * D_in^-1`. The verified auxiliary scalar identity therefore restores every arbitrary auxiliary array when the prescribed endpoint gauges agree. The remaining conditional obligation is the inherited realization and charging of those rational address operations, together with the all-size assembly assumptions. No ridge-array premise or free terminal shrink is introduced.

## Full data and paid stock

The selected bases are `beta23=1/15` and `beta25=-1/15`. The source injections and their two coordinate products are unchanged by coframe selection. Their inverse products are `(2,-40)` and `(25/12,-50)`. The explicitly checked coordinate permutations induce bijections on all lexical triples. Thus the complete previously certified 4,073,300-pair DATA family transfers by the exact source-pair map, after the actual source and copied-center interfaces have been checked. Its one-front histogram remains `9*N` width-one, `N` width-17, `N` width-21 and `N` width-481 children. This uses the new negative-basis full-family certificate, not an older `7/207` histogram.

The finite stock audit recounts the literal two words: `4*M + 2*J + 2*V` local XORs, copied centers and all global bank exchanges. It gives `R23=27,719`, `R25=36,354`, `W=136,283,234`, total recursive rank `78,361,012,650`, and paid local XOR steps `3,022,020,600`. The conservative bit scalar bound is `3,034,434,850`, dominated by the inherited phase scalar bound by `1,758,916,622`. Coframe selection preserves the role count and total rank mass while changing the complete child-width distribution.

## Frozen evidence and reproduction

- Graph source-only receipts: `../graph/results/final-explicit-coframe-source-only-2317-h{23,25}.json`.
- Source-bound native wrappers: `../geometry/results/selected-source-bound-finite-coframe-axis-{23,25}-20261008T2322.json`.
- Independent exact controls: `../geometry/results/final-finite-milp-actual-coframe-controls-20261008T2316.json`.
- Complete DATA: `gpu-parameter-results/one15-minusone15-uniform-data-certificate-20261008T2226.json`.
- Stock/interface receipt: `gpu-parameter-results/final-finite-milp-mixed-coframe-source-center-data-scalar-stock-20261008T2324-attempt2.json`.
- Executable verifier: `code/audit_mixed_coframe_word_interfaces.py`; its receipt records every helper and selected input hash.

The final fresh source command is recorded by the graph reproduction helper. By default it downloads and rebuilds pinned public source; the present finite receipt explicitly reuses a hash-verified, already completed fresh weighted-parent replay. The allocation never uses the weaker partial candidate as its source parent. After regenerating the graph words, native profiles and complete DATA certificate, run the interface verifier with the two graph receipts, the two source-bound wrappers, the pinned PR62 snapshot, `--beta23 1/15` and `--beta25=-1/15`. A fresh output path is mandatory. The first local invocation used relative paths against an absolute-path fixture binding and failed before mathematical checks; the verifier now resolves those paths, and the retained second attempt is the successful finite receipt.

This receipt establishes the finite source, frame, endpoint, DATA and stock interfaces. The final accepted exponent requires the separately bound full moments, all 47 strict constraints, seven margins and independent adversarial acceptance controls. Analytic routing, resampling, precision, prime setup and fixed-tape assumptions remain conditional.

## Attribution

This extends Avi Eisenberg's interval strips and core-aware pair assembly in [PR62](https://github.com/CrocSwap/integer-mult-bounds/pull/62), pinned at `ad0f25ff7b23cff7f08ad237c2254e6ecf74257e`, using eumemic's joint reversible frame compilation in [PR57](https://github.com/CrocSwap/integer-mult-bounds/pull/57), pinned at `cd350f76c9bc01489ec83568bded532cb69be938`. Alejandro Zarzuelo Urdiales' [PR61](https://github.com/CrocSwap/integer-mult-bounds/pull/61), pinned at `afb7cb67d1858641315cfbf4ac768ee64a8eff3a`, supplies the public parameter-refined comparison. The source-partition, cloning, signed-frame and rational-basis mechanisms developed earlier in this research are separate contributions. Credit remains due to Rohan Arun and every directly imported predecessor, including Avi Eisenberg's PR53 and Chafik Boukhalfa's PR54. All inherited licenses and AI-assistance disclosures remain applicable; this note and its verifier were produced with AI assistance.
