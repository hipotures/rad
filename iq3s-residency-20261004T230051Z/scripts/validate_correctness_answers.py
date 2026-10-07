"""Small ground-truth checks, not an LLM judge or automatic model quality ranking."""
import json
from lab import ROOT, save
base=ROOT/'experiments/E006-frequency/correctness-r2/correctness';result={}
for variant in ['control','frequency-v1-ready']:
    path=base/variant/'raw'
    answers={n:(path/f'case{n}-response.txt').read_text() for n in range(1,11)}
    checks={'math_product_answer_contains1776':'1776' in answers[1],
            'linear_equation_answer_contains_x8':'x = 8' in answers[2],
            'strict_JSON_case9':json.loads(answers[9])=={'name':'test','count':3,'enabled':True},
            'strict_JSON_case10':json.loads(answers[10])==[{'id':1,'square':1},{'id':2,'square':4},{'id':3,'square':9}],
            'all_answers_nonempty':all(x.strip() for x in answers.values())}
    result[variant]={'checks':checks,'state':'PASS' if all(checks.values()) else 'FAIL','scope':'Limited exact-output/schema/numeric checks. Code/prose differences inspected and retained; no general semantic proof or quality ranking.'}
save(base.parent/'ground-truth-checks.json',result)
assert all(r['state']=='PASS' for r in result.values())
print(json.dumps(result,indent=2))
