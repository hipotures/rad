#!/usr/bin/env python3
"""Run current visual acceptance; the former mechanical checker is retained separately."""
import argparse,datetime
from pathlib import Path
from common import REVIEW
from visual_acceptance import main
if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--url',default='http://127.0.0.1:8765');a.add_argument('--output',type=Path,default=REVIEW/'results/visual-audit'/('browser-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')));x=a.parse_args();main(x.url,x.output)
