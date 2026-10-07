from pathlib import Path
import json
from final_identity import selection
def agent_label(target):
    selected=selection()
    if selected:return selected['agent_labels'][str(target)]
    path=Path(__file__).resolve().parent/'agent-attempts.json'
    labels=json.loads(path.read_text()).get('labels',{}) if path.exists() else {}
    return labels.get(str(target),f'AGENT-{target}-v0132')
