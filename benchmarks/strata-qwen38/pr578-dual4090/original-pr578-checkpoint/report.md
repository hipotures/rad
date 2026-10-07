# IQ3_S · PR578 · 2× RTX4090

## Status

Controlled local comparison on frozen same upstream base. Every headline is decode tok/s after warmup with MTPspec4/min-p0.5; suffixOFF unless explicitly labeled LOOKUP-ON. Model unchanged; normal sm89 Release CUDA.

## Source/build/tests

Main/base99f3dbd0b21d1401b3769e0c0d963913607f380b; openPRheadb28121ff6ef117bec2558b3ece7e188dd33a2b7e. Clean merge, no conflicts. FreshCONTROL andPR checkout; no pushes. Each raw contains binarySHA256, sourceHEAD, fullcommand/config, modelrevision and tokenIDs hash.

BothCTest suites:56pass,2skip,4environment failures (Q2_0PLEfixture absent, legacy experts.bin fixtures absent,256MiBmlock test exceeding8MiBhard limit). BothPythonserve suites197tests,9skip,OK. No real correctness failure observed. Tests are not described as allpassing. Details:test-status.json and logs/.

## Correctness

10 paired greedy cases, identicalinputIDs, actualoutputIDs saved. Malformed flags: 0. First divergences recorded; autoregressive positional agreement is not teacher-forced top1. NaN debug path enabled only in correctness, none observed. No easy serve/native optimized-helper KLdump available. Outputs manually inspected for evident corruption; no qualityranking.

## Primary32K · suffixOFF

|Config|PPmedian|TGmedian|TGmin/max|TTFTs|accepted/window|suffixaccepted|CPUfallback entries¹|helperentries|overlap²|CPU%³|GPU0%|GPU1%|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|LS-A|4585.5|140.8|131.7/164.3|6.933|1.846|0|1616|—|—|59.5|66.0|57.5|
|LS-B|4603.0|139.6|134.3/144.3|6.904|1.815|0|961|—|—|59.5|38.5|49.5|
|PR-LS|4533.4|133.9|101.6/164.8|7.082|1.846|0|1616|—|—|95.8|38.0|55.0|
|H-OLD|2397.6|98.9|98.1/103.4|13.181|1.793|0|5034|7704|—|95.0|94.0|9.0|
|H-OPT|2388.9|95.7|94.3/101.1|13.227|1.667|0|369|19014|—|66.3|88.0|5.0|
|H-OPT-FIXED|2399.0|93.0|92.3/103.3|13.176|1.667|0|369|19014|—|66.0|87.5|5.7|

¹ CPU entries derived approximately from normal log rounded per-layer-window means ×48layers×verifywindows. DistinctCPU expert count and routedentry count are separate. ² FinalspeeddiagnosticsOFF; overlap measured separately in DIAG runs. Missing metrics stayunknown. ³ System100%=all16vCPU; process100%=onevCPU.1Hzdecode samples sparse for256output. PCIe hardware counters in telemetry/*pcie-dmon.log; timing-aligned aggregates are supplemental.

## Fairness / initialcache

AutoPR:8586actualprimaryslots+11796helperslots=20382initial residents. NumericprimaryCLI6567 reproduces actual8586 because upstream converts max-blob budget into variable-sized slots. Original/optimized correctness startup captured identicalprimaryIDs/helperIDs andzerooverlap. Mainhelper configurations must match actualcounts beforewarmup; see layouts and fairness-audit.json. Auto/fixed comparisons use physicalcapacity, notmatchingCLI numerals.

Old4096payload is warmup only. Its natural EOS may generate fewer than256; perwarmup outputcount is retained and notused in headline medians. All measured fixedlength requests with<256, reuse!=0, incorrectactualcount remainINVALID. No discarded request is silently replaced.

## Cache diagnostics / transfers

|Config|TGmediandiagnostic|startup overlap|afterwarmup|afterrun3|helperreturnedMiB|helperwaitms|
|---|---:|---:|---:|---:|---:|---:|
|H-OLD-DIAG|103.5|0|571|2073|60.9|99.0|
|H-OPT-DIAG|91.0|0|0|0|139.4|106.5|

Instrumentation consists solely of default-off boundary cache snapshots; no new hot-pathper-token counters. All headlines instrumentationOFF regardless of observednoise. Differences in residentIDs are netchanges, notall adaptation swaps. Quantizationskips notcounted. Nativehelperreturnedbytes counter approximates logprecision0.1MiB; it is notwholePCIetraffic.

## Finalcontextmatrix · suffixOFF

|Config|Actualinput|validruns|PP|TG|TTFT|CPUfallback¹|helperentries|CPU%|GPU0%|GPU1%|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|H-OPT-FINAL|31400|3|2400.7|95.4|13.161|485|18784|77.7|89.5|6.0|
|H-OPT-FINAL|63400|3|2408.6|84.1|26.461|294|27724|53.7|93.3|5.3|
|H-OPT-FINAL|127000|3|2358.2|82.4|54.106|485|22147|77.2|91.0|6.7|
|H-OPT-FINAL|259500|3|2281.9|76.2|114.213|369|25567|64.8|95.0|5.0|
|LS-A-FINAL|31400|3|4595.1|135.1|6.913|998|—|59.4|41.0|63.5|
|LS-A-FINAL|63400|3|5361.4|126.9|11.965|1067|—|51.7|38.7|64.7|
|LS-A-FINAL|127000|3|5668.8|119.2|22.667|840|—|68.2|41.5|50.0|
|LS-A-FINAL|259500|3|5684.4|114.3|46.160|931|—|83.2|43.0|50.0|

Same literaloldpayloads acrossconfig at31400/63400/127000/259500. Eachcontext warmup then3requests; contextsmatrix hasadaptivecachehistory preserved within freshserver perconfig. Onlyvalid256output/reuse0 requests count. No 3-runmedian claimed whenvalidcount<3.

## Secondary lookupON / steadydecode

|Config|Actualinput|Outputkind|Validruns|PP|TG|TGmin/max|TTFT|suffixaccepted|
|---|---:|---|---:|---:|---:|---:|---:|---:|
|H-OLD-FAIR64-LOOKUP-ON|31400|256|3|2399.1|98.8|90.1/110.2|13.177|35|
|H-OPT-LOOKUP-ON|31400|256|3|2404.3|94.5|91.5/99.7|13.146|41|
|H-OPT-STEADY2048|31400|2048|3|2436.0|75.3|74.6/78.4|12.975|0|
|LS-A-LOOKUP-ON|31400|256|3|4649.5|135.6|131.5/136.5|6.835|27|
|LS-A-STEADY2048|31400|2048|3|4673.9|158.8|153.3/161.0|6.806|0|

Steadydecode is a distinct workload, shared deterministicsavedprompt andsuffixOFF. --prompt-cache0 prevents repeatedprompt reuse; nothistoricalAB. Allactual2048output required; earlyEOSnegative retained. Main32K benchmarks a code-agent workload;10short math/prose correctness requests arenot a formal mixed/math speedbenchmark. Therefore no workload-general codevsMathwinner claim.

## Historical / author references

Historicaloldv0.1.31:PP4652.5/TG131.2. v0.1.38exactoldreplay:PP4580.4/TG131.7;TG111.7/147.5/131.7,secondlookup173/173. HISTORICAL/NOT_CONTROLLED_A_B; differsautoPCIefraction andwarm/cachehistory. Never used ascleancontrol forPR attribution.

AuthorPRbody dual4090v0.1.37:originalhelper88.07/85.15 mixed/code;layersplit126.86/146.95;optimized143.35/197.58. Differentworkload/config; requests/scriptsnotaddedbyPR. No expectations ofmatchingabsolutethroughput.

## Limitations

No tensorweights changes/newmodeldownloads. No exactteacherforcedKL/top1 output. Per-tokenquantizationskip counter unavailable; no inventedcount. Netcachechanges do notcounttransientswaps. Guest virtiofsfile/counter telemetry cannotprovephysicalhostSSDreads. CPU/GPU1Hzphaseaverages andPCIetimealignmentapproximate, particularly2sdecode. NoPSSpolling1Hz. Negativeattempts andwarmups arepreserved.

## Analysis

Primary32K optimizedhelper H-OPT: 95.7TG vs layer split LS-A: 140.8TG; delta-32.03%. CompareH-OLDvsH-OPT/FIXED atmatchedinitialcapacity to attributeoptimizationeffect. PR-LSguard separates inactivePRfromtopology.

## RECOMMENDATION

KEEP_LAYER_SPLIT

Recommendation remains provisional until context/steadydecode andsame-capacityaudits are complete; allvalues reproducible from rawrecords andscriptanalyze.py.
