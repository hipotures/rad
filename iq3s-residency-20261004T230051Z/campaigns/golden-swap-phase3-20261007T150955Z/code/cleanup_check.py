"""Read-only final cleanup evidence; never stop a PID from an archived record."""
import pathlib, psutil, socket
from common import *

if __name__ == '__main__':
    no_gpu()
    probe = socket.socket(); probe.settimeout(1)
    connect_result = probe.connect_ex(('127.0.0.1', 18166)); probe.close()
    assert connect_result != 0, 'Experimental serving port still active'
    servers=[]; profilers=[]
    for process in psutil.process_iter(['pid','cmdline']):
        try:
            argv = process.info['cmdline'] or []
            if argv and (argv[0].endswith('/strata') and str(W) in argv[0] or any(x.endswith('/code/serve_capture.py') and str(C) in x for x in argv)):
                servers.append(process.info)
            if argv and pathlib.Path(argv[0]).name == 'nvidia-smi' and 'dmon' in argv:
                profilers.append(process.info)
        except psutil.Error:
            pass
    assert not servers and not profilers
    save(C / 'results/cleanup.json', {'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owned_servers':servers,'telemetry_dmon_processes':profilers,'experimental_port_connect_result':connect_result,'ordinary_launchers_and_previous_files':'24 original files separately hash-verified in scientific audit','GPU_apps':'none','scope':'Read-only current-state verification. No archived PID was used to signal any process.'})
    print('OWNED CLEANUP PASS',flush=True)
