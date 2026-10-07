"""Preserve the E011 analyzer; create a five-phase derivative for the new diagnostic."""
from lab import ROOT
p=ROOT/'scripts/analyze_coordination_waits.py'
assert not p.exists()
s=(ROOT/'scripts/analyze_miss_waits.py').read_text()
for old,new in [('len(groups)*4','len(groups)*5'),('range(4)','range(5)'),("'3':'CPU-completion waitM kernel only'","'3':'CPU-completion waitM kernel only','4':'GPU resident planning and demand doorbell'")]:
    assert s.count(old)==1,(old,s.count(old));s=s.replace(old,new)
p.write_text(s)
p=ROOT/'scripts/coordination_waits_test.cpp';assert not p.exists()
s=(ROOT/'scripts/miss_waits_test.cpp').read_text()
assert 'phase<4' in s;s=s.replace('phase<4','phase<5')
s=s.replace('==72','==90').replace('PASS 72 spans','PASS 90 spans')
p.write_text(s)
print('Saved separate five-phase analyzer and captured-event fixture')
