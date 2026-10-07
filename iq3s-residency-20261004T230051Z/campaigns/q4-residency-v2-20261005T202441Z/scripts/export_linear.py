"""Freeze CPU-only learned scorer constants for C++, retaining original checkpoint hash."""
import numpy as np,hashlib,json
from campaign import C,save
z=np.load(C/'checkpoints/linear.npz');lines=['// Development-only trained, separately calibrated Q4 Expert-Jev-inspired linear scorer.','#pragma once','namespace strata::research::q4_linear {']
for name in ['indices','mean','std','coef']:
 x=z[name];ty='int' if name=='indices' else 'float';s=','.join(str(int(v)) if name=='indices' else format(float(v),'.9g')+('f' if '.' in format(float(v),'.9g') or 'e' in format(float(v),'.9g') else '.0f') for v in x)
 lines.append(f'inline constexpr {ty} {name}[{len(x)}]={{'+s+'};')
for name in ['intercept','cal_slope','cal_intercept']:
 v=float(z[name]);s=format(v,'.9g');lines.append('inline constexpr float '+name+'='+s+('f' if '.' in s or 'e' in s else '.0f')+';')
lines.append('}')
p=C/'scripts/templates/q4_linear_constants.hpp';p.write_text('\n'.join(lines)+'\n')
save(C/'phase-b/learned/export.json',{'checkpoint_sha256':hashlib.sha256((C/'checkpoints/linear.npz').read_bytes()).hexdigest(),'header_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'features':'13 basic numeric fields, causal previous completed windows','CPU_only':True})
