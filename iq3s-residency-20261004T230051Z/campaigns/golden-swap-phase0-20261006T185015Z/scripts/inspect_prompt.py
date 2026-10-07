"""Show a frozen natural prompt, its provenance and actual token occupancy."""
import argparse,json,pathlib
C=pathlib.Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('task',nargs='?');a.add_argument('--full',action='store_true');v=a.parse_args();m=json.load(open(C/'benchmark-manifest.json'))
if not v.task:
 for t in m['tasks']:print(t['task_id'],t['family'],t['split'],t['context_limit'],t['actual_input_tokens'])
else:
 t=next(x for x in m['tasks'] if x['task_id']==v.task);p=json.load(open(t['payload']['path']));print(json.dumps({k:t[k] for k in ['source_group','split','license','source_revision','length_method','context_limit','actual_input_tokens','output_cap','tool_execution']},indent=2));print('INSTRUCTION:',t['instruction'])
 for msg in p['messages']:print('\n'+msg['role'].upper()+'\n'+(msg['content'] if v.full else msg['content'][:1200]+'\n[Full text: '+t['payload']['path']+']'))
