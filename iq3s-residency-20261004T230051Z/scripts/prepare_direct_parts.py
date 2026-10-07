"""Declare a small source-supported execution candidate, conditional on coordination diagnosis."""
from lab import ROOT,save
out=ROOT/'experiments/E023-direct-parts/v1'
assert not out.exists()
save(out/'protocol.json',{'question':'Can native routedGPUoutputs write directly into final expert rows, avoiding whole-buffer zero/copy plushit-add without changing arithmetic/routing or CPUownership?',
 'source_evidence':'native_expert_grouped writesent_dst[e] rowofout; currentfullyresidentpathalreadywritesparts_outdirectly. Mixedpathwriteshit_out, copiesCPUbuffer/zerosGPUrows, thenaddsGPUresults. Existingcopy_rows_from_mapped actuallyZEROSGPUrows, so it cannotbe reusedunmodified as a preserve copy.',
 'change':'FrozenCURRENT cache/hostdispatch, notE019suppress-host-plan. DefaultoffSTRATA_LAB_DIRECT_PARTS. DirectVRAMandmappednativegroupedoutputs to parts_out; newGPUrow-preservingCPUcopy touchesonlynonGPUplanrows; omitmoe_hit_add. Existingexpertkernels,grouporder,routingweights/reduction,MTP,KV,workers,K/PCIe/capacities unchanged.',
 'invariants':'ActualGPUplanP.dst[0,counts[1]) includesallVRAM+mappedentries; CPUrowsarethecomplement. Eachrowwrittenoncebeforemoereduce. GPUwaitA/B/Mdependenciesremainoriginal. No withinwindowcachepolicy/IDpublication changes. Wrongnonlocal routing stillCPU/mappedfallback.',
 'scope':'FrozennativeIQ3_SserialG1contiguousK25dualsplitonly; rejecthelper/wholemodels/allresident/batch/geometryoutsidescope. DefaultOFForiginalkernelsandbranches unchanged. No extraGPUmemory; hit_out remainsallocated forfaircapacity accounting.',
 'funnel':'AfterE021samebinaryphase evidence, buildseparatecleananddiagnosticdirs. NewtwoGPUrowownershipCUDAgraphfixture(allGPU/allCPU/mixed), fulltests/Python/realIQ,10greedycases, strictfullprofileoutput/router/heat/headparity. Retainall failures. Native+0scatter vsdirectassignment signedzero can differ; investigate any realarithmetic/outputdivergence.',
 'finite_confirmation':'Ifvalid:onefreshserver/profile,same64warmup+threefixed4096requests. ReuseE002reference. A genuine samebinaryOFFguard maybepredeclared onlyifbenefitneedsattribution; never renamed extra unchangedreps.',
 'budget':'NoextraGPU/CPUstate beyondnewkernelfunction; oldhit_outallocationretained. Sameexpertbytes/classes/total24GiBenvelope. NewCUDAmodule/binarylayout remains potentialtimingconfound, notreason toassumegain.',
 'completion':'Exactrowownership/correctness plusboundedbothprofilelatency/TG orretainednegative. No fakeguaranteed2%estimate fromsumming unrelatedeventmedians, no normaluserlauncher switch.'})
save(out/'overrides.json',{'env':{'STRATA_LAB_DIRECT_PARTS':'1'},'expert_policy':'Original CURRENT EMA/host planning; no E019 combination','extra_explicit_GPU_bytes':0})
print(out)
