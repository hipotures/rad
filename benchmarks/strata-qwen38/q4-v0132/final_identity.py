"""Explicit final selection routing; original candidate files remain immutable."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent

def selection():
    path=ROOT/'production-selection.json'
    if not path.exists():return {}
    value=json.loads(path.read_text())
    assert value['status']=='SELECTED_FROM_VERIFIED_EVIDENCE'
    return value

def final_label():
    selected=selection()
    if selected:return selected['matrix_label']
    path=ROOT/'final-matrix-attempt.json'
    return json.loads(path.read_text())['label'] if path.exists() else 'FINAL-v0132-Q4'

def final_config_path():
    return Path(selection().get('config',str(ROOT/'configs/FINAL-v0132-Q4.json')))

def final_config_name():
    return final_config_path().stem

def long_summary_path():
    return Path(selection().get('long_summary',str(ROOT/'raw/long-decode-done.json')))

def phase_terminal_path(phase):
    selected=selection()
    return Path(selected.get('phase_terminals',{}).get(phase,str(ROOT/'raw'/f'phase-{phase}-terminal.json')))


def require_phase(phase):
    path=phase_terminal_path(phase)
    value=json.loads(path.read_text())
    accepted=selection().get('accepted_phase_statuses',{}).get(phase,['COMPLETE'])
    assert value['status'] in accepted, f'{phase}: {path} status {value["status"]}'
    return path
