# Q4 multi-GPU campaign handoff

Goal: finish exactly27 valid final4096-output measurements, three methods ×32K/128K/256K ×3. Same frozen CURRENT0.1.39 source/binary, Q4existing pack. No optimization/predictor/rebuild/modeldownload/productionlauncher changes.

Campaign: /srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/q4-multigpu-20261005T164628Z
Driver: PID1735884, toolsession8090. Writes logs/matrix-driver.log and STATUS.json. It completes allremaining cells serially and stops ownedservers between cells. Read scripts/progress.py or raw/*/*/raw/run*.json for progress. Do not restart/repeat a completed point.
Additional temperature collector: toolsession21789, script scripts/temperature_monitor.py. Stops automatically when identifieddriver exits; verify telemetry/temperature-monitor-finished.json. ExtraNVML query1Hz records missinghelperGPU1temperatures; originalhelper32Krun1 missingGPU1temperature must stayUNAVAILABLE.

Layer choice frozen before final: K24/PCIe.28; screenedautoK24,.28; K22,.28; K26,.28; K24,.37. Exactly1exploratory4096request each, separate fromfinal. Helpers useauto/auto andinitialcapacities must match perprofile.32K5358/7698;128K5299/7696;256Kcheckraw.
Common: CVD0,1 poolspin100µs workers15 spec4/minp.5 INT8KV/kvresident32768 prefillauto suffix0 promptcache0 greedy. Freshserver/cell, saved4096input/64outputwarmup, then3unique savedinputs; sameIDs acrossmethods.
Source6f32ec070f23ced9f50e704d854d775da52591ab; binaryR/builds/control/strata SHAeca9d0d271340a114955d5af8038dbffa139ad096ef0d470bcfea9009d4f8d0d. R=/srv/ai/research/iq3s-residency-20261004T230051Z. Binary --version unsupported; startup/API0.1.39 verified. Packud-q4_k_xl-v0132 isDATAonly; runtimeCURRENT.

When all27 complete and driver exits:
1. R/src/control/.venv/bin/python R/scripts/analyze_q4_multigpu.py --campaign C
2. R/src/control/.venv/bin/python R/scripts/render_q4_report.py --campaign C
3. R/src/control/.venv/bin/python R/scripts/audit_q4_multigpu.py --campaign C
Use fullpaths forR/C above. Analyzeasserts27beforechoosingwinner, freezesharnesscopies, createslaunchers, report/CSV/JSON. Renderwritesreadablecompletefinalreport with recommendationlast. AuditchecksrawIDs,settings,initialcapacityfairness,source/binary/model/protectedoldlaunchers,launchers--check withoutinference, collectorfinished, GPUidle, savesartifacthashes andSTATUSCOMPLETE.
4. Inspect report/table for realresults and materialcaveats; ensure no ownedserver/dmon/collector remains. Verify bothGPUsidle.
5. Markgoalcomplete onlyafterallrequiredworkdone and givePolishfinalwithtable/report/launchcommands, exactlyone recommendationlast.

Known result before256K completion:32K TG mediansLS96.2,original58.0,optimized48.6;128KLS93.0,original53.6,optimized45.0. These are not final recommendation. PP LSfirstfullrequest islowerthanruns2/3 despiteactualreuse0; preserveperrunrange/progression. Conditionaldisplayedhit excludesPCIe/helper. CPUentries exactlookups-hits; nonlocalGPU aggregate includesmapped+helper. Helperreturnedbytes distinctfromsampledPCIebandwidth. ExpertfileDONEdeltas aredecode-scoped0 withfullRAMarena; physicaldisk maybePLE. No preciseexclusiveCPUcompute/spinorpostadaptiveoverlapcounteronfrozenbinary.
