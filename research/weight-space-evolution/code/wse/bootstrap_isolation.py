"""Outer filesystem namespace for Codex; the privileged broker stays outside over one Unix socket."""
from pathlib import Path
import shutil

from .bootstrap_prepare import TOPIC


def command(home, conversation, address):
    binary=Path(shutil.which('codex')).resolve()
    release=binary.parent
    cmd=['bwrap','--unshare-all','--share-net','--die-with-parent','--new-session','--clearenv',
         '--ro-bind','/usr','/usr','--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64',
         '--symlink','usr/bin','/bin','--proc','/proc','--dev','/dev','--tmpfs','/tmp',
         '--ro-bind',str(release),'/opt/codex/bin','--bind',str(home),'/codex-home',
         '--bind',str(conversation),'/conversation',
         '--ro-bind',str(address),'/transport/lab.sock',
         '--ro-bind',str(TOPIC/'code/wse/bootstrap_proxy.py'),'/transport/proxy.py']
    for name in ('resolv.conf','hosts','nsswitch.conf','ssl','ca-certificates'):
        p=Path('/etc')/name
        if p.exists():cmd+=['--ro-bind',str(p),str(p)]
    cmd+=['--setenv','HOME','/conversation','--setenv','CODEX_HOME','/codex-home',
          '--setenv','PATH','/opt/codex/bin:/usr/bin:/bin','--setenv','TMPDIR','/tmp',
          '--chdir','/conversation']
    return cmd
