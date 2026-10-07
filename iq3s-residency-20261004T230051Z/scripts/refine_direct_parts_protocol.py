"""Correct the unbuilt scope after reading the actual two-group MTP split."""
import shutil
from lab import ROOT, load, save
base=ROOT/'experiments/E023-direct-parts/v1'
assert not (base/'build').exists() and not (base/'protocol-initial.json').exists()
shutil.copy2(base/'protocol.json',base/'protocol-initial.json')
p=load(base/'protocol.json')
p['scope']='Frozen native IQ3_S serial contiguous K25 dual split; both original G1 and G2 token groups, no concurrent slots. No helper/full-resident models or other geometry. Group output pointers and destination IDs are already relative to each group.'
p['refinement']='Before building, source line561 shows speculative split uses two groups for T>=2. Rejecting G2 would make this candidate unusable. Preserve both groups; test exclusive group row slices in the captured two-device fixture. No algorithm change outside each group.'
save(base/'protocol.json',p)
