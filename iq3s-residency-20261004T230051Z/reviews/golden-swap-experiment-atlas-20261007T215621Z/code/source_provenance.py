"""Retain precise startup source excerpts without importing a source checkout."""
import argparse
import subprocess
from common import *

def main(runtime):
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=runtime,text=True).strip()
    assert commit=='95fba2541a57fe6be8290faa639f493c7b8e895f'
    base='6f32ec070f23ced9f50e704d854d775da52591ab'
    regions={
        'src/program/generate.cpp':[(373,409),(1905,1920),(2647,2692),(2850,2874),(3304,3322),(3455,3503),(3508,3554)],
        'src/core/expert_cache.cpp':[(23,78),(81,109)],
        'tools/make_profile.py':[(66,90)],
        'include/strata/research/q4_oracle.hpp':[(90,145)]}
    rows=[]
    for rel,spans in regions.items():
        f=runtime/rel;text=f.read_text();lines=text.splitlines()
        original=subprocess.run(['git','show',f'{base}:{rel}'],cwd=runtime,text=True,capture_output=True)
        snippets=[]
        for lo,hi in spans:
            s='\n'.join(lines[lo-1:hi])
            snippets.append(dict(first_line=lo,last_line=hi,text=s,occurs_unchanged_in_serving_base=s in original.stdout if original.returncode==0 else None))
        rows.append(dict(file=rel,sha256=digest(f),source_commit=commit,serving_base_has_file=original.returncode==0,excerpts=snippets))
    save(REVIEW/'provenance/startup-code.json',dict(runtime_commit=commit,serving_base=base,
        upstream='https://github.com/Niko1221/Strata',files=rows,
        interpretation='Line numbers refer to the pinned derivative; equality checks identify unchanged serving-base logic. Oracle additions require retained campaign patches.'))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime',type=Path,required=True);main(p.parse_args().runtime)
