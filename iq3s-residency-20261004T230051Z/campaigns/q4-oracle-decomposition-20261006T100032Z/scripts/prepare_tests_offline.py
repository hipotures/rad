from pathlib import Path
import re,json,shutil
from owned import C,run
old=Path((C/'previous-campaign.txt').read_text().strip());src=C/'src/decomposition-v1'
legacy=(old/'src/oracle-v3/include/strata/research/q4_oracle.hpp').read_text()
for a,b in [('Q4Oracle','LegacyOracle'),('q4_oracle','legacy_oracle'),('OracleLayer','LegacyLayer'),('OracleEvent','LegacyEvent'),('NativeCopy','LegacyNativeCopy')]:legacy=re.sub(r'\b'+a+r'\b',b,legacy)
(C/'tests/legacy_oracle.hpp').write_text(legacy)
cmd=['g++','-O3','-std=c++20','-pthread','-I'+str(src/'include'),'-I/usr/local/cuda/include',str(C/'tests/information_fixture.cpp'),'-L/usr/local/cuda/lib64','-Wl,-rpath,/usr/local/cuda/lib64','-lcudart','-o',str(C/'tests/information-fixture')]
if not (C/'tests/information-compile').exists():run('information-compile',cmd,timeout=120,area='tests')
import os
env={k:v for k,v in os.environ.items() if not k.startswith('STRATA_')};env.update(STRATA_Q4_TAPE=str(C/'tapes/capture-32k-v3.bin'),STRATA_Q4_TAPE_MODE='replay')
run('information-fixture-run',[C/'tests/information-fixture'],env=env,timeout=240,area='tests')
s=(old/'scripts/offline.cpp').read_text()
s=s.replace('int nx=q4_oracle.next(l,e,0);double s=!horizon?(nx<0?1e12:nx):(nx<0?double(horizon+1)-std::log1p(std::max(0.f,heat[l*512+e])):nx);','double s=q4_oracle.victim_value(l,e,0);')
s=s.replace('std::vector<int> latest_victim(48*512,-1);','std::vector<int> latest_victim(48*512,-1),latest_incoming(48*512,-1);uint64_t target_ready=0,late_useful=0;')
s=s.replace('latest_victim[w.layer*512+v]=w.index;','latest_victim[w.layer*512+v]=w.index;latest_incoming[w.layer*512+w.expert]=w.index;')
s=s.replace('victims+=r[l*512+e]<0&&latest_victim[l*512+e]>=0;', 'victims+=r[l*512+e]<0&&latest_victim[l*512+e]>=0;int k=latest_incoming[l*512+e];if(k>=0&&r[l*512+e]>=0){++q4_oracle.events[k].uses;target_ready+=q4_oracle.events[k].target==ev;late_useful+=q4_oracle.events[k].published_at>q4_oracle.events[k].target;}')
s=s.replace('uint64_t pub=0,late=0,pbytes=0;', 'uint64_t pub=0,late=0,pbytes=0,repeated=0,unused_bytes=0;for(auto&e:q4_oracle.events){repeated+=e.uses>1;unused_bytes+=e.uses==0?e.bytes:0;}')
needle='<<"{\\"mode\\":\\"transfer\\",\\"horizon\\":"<<horizon'
assert needle in s;s=s.replace(needle,'<<"{\\"mode\\":\\"transfer\\",\\"I\\":"<<q4_oracle.incoming_horizon<<",\\"V\\":"<<q4_oracle.victim_horizon<<",\\"E\\":64,\\"protection\\":\\"full_current_window\\",\\"target_ready_demand\\":"<<target_ready<<",\\"late_useful_demand\\":"<<late_useful<<",\\"reused_admissions_entry_based\\":"<<repeated<<",\\"unused_bytes\\":"<<unused_bytes<<",\\"horizon\\":"<<horizon')
(C/'scripts/offline.cpp').write_text(s)
cmd=['g++','-O3','-std=c++20','-pthread','-I'+str(src/'include'),'-I/usr/local/cuda/include',str(C/'scripts/offline.cpp'),'-L/usr/local/cuda/lib64','-Wl,-rpath,/usr/local/cuda/lib64','-lcudart','-o',str(C/'analysis/offline')]
run('offline-compile',cmd,timeout=120,area='tests')
print('TESTS_AND_OFFLINE_READY',flush=True)
