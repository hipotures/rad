"""One complete typed text export per original journal, never size-based chunks."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from export_trace import D,value
from inspect_oracle import E,L,N
from trace_io import P,H,read_gpu

def main():
    q=argparse.ArgumentParser();q.add_argument('--raw-root',required=True,type=Path);q.add_argument('--output',required=True,type=Path);a=q.parse_args()
    a.output.mkdir(parents=True,exist_ok=False);manifest=[]
    for point in sorted(a.raw_root.iterdir()):
        if not (point/'episode.json').exists():continue
        dest=a.output/point.name;dest.mkdir()
        for kind,suffix,dtype in [('admission','-admissions.bin',E),('layer','-layers.bin',L),('native','-native.bin',N),('lifecycle','-lifecycle.bin',D),('publication','-publication-trace.bin',P),('producer','-producer-trace.bin',H),('gpu0','-gpu0-trace.bin',None),('gpu1','-gpu1-trace.bin',None)]:
            source=point/'raw'/('oracle'+suffix)
            if not source.exists():continue
            out=dest/(source.name.removesuffix('.bin')+'.jsonl');sha=hashlib.file_digest(source.open('rb'),'sha256').hexdigest()
            with out.open('x') as f:
                def emit(x):f.write(json.dumps(x,separators=(',',':'))+'\n')
                emit({'type':'schema','version':2,'request':point.name,'original_source_count':1,'partition':'Original independently recorded journal; no size-based subdivision'})
                if dtype is not None:
                    emit({'type':'source','record_type':kind,'path':str(source),'sha256':sha,'bytes':source.stat().st_size,'dtype':dtype.descr})
                    for row in np.fromfile(source,dtype):emit({'type':kind,**{name:value(row[name]) for name in dtype.names}})
                else:
                    g=read_gpu(source);emit({'type':'gpu_header','device':g['device'],'header':g['header'].tolist(),'source':str(source),'sha256':sha})
                    for k,rows in enumerate(g['rows']):
                        for row in rows:emit({'type':'gpu','device':g['device'],'kind':k,**{name:value(row[name]) for name in rows.dtype.names}})
                emit({'type':'end','source_files':1})
            manifest.append({'source':str(source),'source_bytes':source.stat().st_size,'source_sha256':sha,'text':str(out.relative_to(a.output)),'text_bytes':out.stat().st_size,'text_sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest()})
        print('EXPORTED_COMPLETE_JOURNALS',point.name,flush=True)
    (a.output/'source-manifest.json').write_text(json.dumps({'partition':'One original journal per export, fixed by original instrumentation streams before compression; no original file split or modified','files':manifest},indent=2)+'\n')
if __name__=='__main__':main()
