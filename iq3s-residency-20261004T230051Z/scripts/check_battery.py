"""Check known numeric/schema invariants without judging overall model quality."""
import argparse,json,pathlib,re
from lab import save
ap=argparse.ArgumentParser();ap.add_argument('path');a=ap.parse_args();base=pathlib.Path(a.path)
rows=json.loads((base/'summary.json').read_text());answers={n:(base/'raw'/f'case{n}-response.txt').read_text() for n in range(1,11)}
checks={'10cases_retained':len(rows)==10,'all_same_input_ids':all(r['same_input_ids'] for r in rows),'no_reported_nonfinite':all(not r['nonfinite_reported'] for r in rows),'all_answers_nonempty':all(x.strip() for x in answers.values()),'product1776':'1776' in answers[1],'equationx8':bool(re.search(r'x\s*=\s*8\b',answers[2]))}
for n,expected in [(9,{'name':'test','count':3,'enabled':True}),(10,[{'id':1,'square':1},{'id':2,'square':4},{'id':3,'square':9}])]:
    try:checks[f'strict_JSON{n}']=json.loads(answers[n])==expected
    except json.JSONDecodeError:checks[f'strict_JSON{n}']=False
result={'state':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'identical_visible_answers':sum(r['same_visible_output'] for r in rows),'limitations':'Ground-truth checks are narrow. All text differences remain for source/numerical diagnosis; noLLMjudge, quality ranking or universal parity claim.'}
save(base/'ground-truth-checks.json',result);print(json.dumps(result,indent=2))
if result['state']!='PASS':raise SystemExit(1)
