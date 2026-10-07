"""Read current upstream ideas with gh; never replace the frozen experimental base."""
import json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
out={}
for key,endpoint in [('main','repos/Niko1221/Strata/commits/main'),('recent','repos/Niko1221/Strata/commits?per_page=12')]:
 data=json.loads(subprocess.check_output(['gh','api',endpoint],timeout=60))
 if key=='main':out[key]={'sha':data['sha'],'date':data['commit']['committer']['date'],'message':data['commit']['message'],'url':data['html_url']}
 else:out[key]=[{'sha':r['sha'],'message':r['commit']['message'],'url':r['html_url']} for r in data]
(ROOT/'sources/upstream-inspection.json').write_text(json.dumps(out,indent=2)+'\n')
print(out['main']['sha'],out['main']['message'].splitlines()[0])
