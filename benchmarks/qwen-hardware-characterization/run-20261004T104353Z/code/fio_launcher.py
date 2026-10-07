#!/usr/bin/env python3
"""Pinned fio launch safety and independent full-file CRC readback outside write timing."""
import json,os,pathlib,subprocess,sys
root=pathlib.Path(__file__).resolve().parent;native=root/'deps/fio/.native/fio';args=sys.argv[1:]
options={x.split('=',1)[0]:x.split('=',1)[1] for x in args if x.startswith('--') and '=' in x}
if '--filename' not in options:os.execv(str(native),[str(native)]+args)
file=pathlib.Path(options['--filename']);parent=file.parent.resolve();job=options.get('--name','job')
if file.is_symlink() or file.parent!=parent or file.name not in ['corpus.bin','write.bin'] or not file.is_file():raise RuntimeError('Unsafe non-regular/non-owned benchmark path')
if not (parent.name.startswith('scratch-') or parent.name.startswith('hwchar-scratch-')):raise RuntimeError('Not a private scratch directory')
if '/' in job or '..' in job:raise RuntimeError('Unsafe auxiliary job name')
cmd=[str(native),'--thread=1','--verify_state_save=0','--aux-path='+str(parent)]+args
if options.get('--rw')!='write':os.execv(str(native),cmd)
p=subprocess.Popen(cmd);_,status,usage=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status)
(parent/(job+'.rusage.json')).write_text(json.dumps({'scope':'native fio write job, including startup/warmup/end-fsync, excludes independent readback','user_seconds':usage.ru_utime,'system_seconds':usage.ru_stime,'rss_peak_bytes':usage.ru_maxrss*1024,'minor_faults':usage.ru_minflt,'major_faults':usage.ru_majflt,'voluntary_context_switches':usage.ru_nvcsw,'involuntary_context_switches':usage.ru_nivcsw,'guest_block_input_operations':usage.ru_inblock,'guest_block_output_operations':usage.ru_oublock,'returncode':p.returncode},indent=2)+'\n')
if p.returncode:raise SystemExit(p.returncode)
verification=parent/(job+'.postverify.json')
verify=[str(native),'--name='+job+'-postverify','--filename='+str(file),'--readonly','--allow_file_create=0','--rw=read','--bs=1m','--size=256m','--ioengine=psync','--thread=1','--direct=1','--verify=crc32c','--verify_only=1','--verify_fatal=1','--verify_write_sequence=0','--verify_header_seed=0','--verify_state_load=0','--verify_state_save=0','--aux-path='+str(parent),'--output-format=json','--output='+str(verification)]
p=subprocess.run(verify,stdout=subprocess.DEVNULL,stderr=sys.stderr,timeout=30)
if p.returncode:
 print('VERIFICATION_FAILED: fio CRC32C full-file readback',file=sys.stderr);raise SystemExit(2)
data=json.loads(verification.read_text())
if any(j['error'] or j['read']['io_bytes']!=256*(1<<20) for j in data['jobs']):
 print('VERIFICATION_FAILED: incomplete fio CRC32C readback',file=sys.stderr);raise SystemExit(2)
