#!/usr/bin/env python3
"""Attach the research agent's direct image review and preserve screenshot provenance.

These judgments record actual inspection of the named captures, not an automatic
inference from DOM state or pixel counts. Re-running capture requires a new review.
"""
import datetime,json,shutil
from pathlib import Path
from common import REVIEW,save,digest,work_root

AFTER={
 'overview':('POOR','The complete 335-row catalog still requires horizontal scrolling and filtering. It is an inventory, not the recommended evidence entry point; the prominent gallery supplies that entry point.'),
 'residency':('GOOD','The visible primary plot encodes resident fraction and distinct local/CPU/mapped demand. Dense 512-expert detail requires zoom; the former Gantt is secondary.'),
 'churn':('GOOD','The four aligned axes visibly separate transactions, copy MB, local and nonlocal work. Admissions and withdrawals have different colors and dash styles.'),
 'startup':('GOOD','The first chart distinguishes generation survival, identity return, demand, local service and cumulative replacement; supporting tables remain below it.'),
 'expert':('GOOD','Actual generations occupy separate rows, with first service, target, publication, withdrawal and nonlocal demand visibly distinct. The selected expert is explicit.'),
 'oracle':('GOOD','A matching retained run is selected automatically, and synchronized state panels and churn/service axes display the policy differences. A one-expert selection remains a deliberate drill-down.'),
 'demand':('GOOD','Expert demand, adjacent working-set overlap and service paths render with clear titles and scales. Binning is labeled.'),
 'classes':('GOOD','The physical capacity table and class-specific admission/copy series are readable and preserve the absent GPU1 large class.'),
 'predictor':('POOR','The new primary AUC/lifecycle/timing panel is readable, but the unfocused page still contains a long technical funnel/table section. The curated focus deep link is GOOD and is the recommended view.'),
 'lease':('GOOD','The lifetime/use scatter and distributions have visible units and censoring qualifications. The threshold table now reflects the chosen values.'),
 'slots':('GOOD','Physical destinations and owner replacements are legible on separate rows. Exact owner and victim details are in hover; the displayed most-changed-slot limit is explicit.')}

def main():
 root=REVIEW/'results/visual-audit';utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
 release=root/'release-pages/visual-audit.json';v=json.loads(release.read_text())
 for row in v['pages']:
  row['human_readability'],row['reason']=AFTER[row['page']]
  row['direct_image_inspection']=True
 v['state']='DIRECT_IMAGES_REVIEWED_WITH_EXPLICIT_READABILITY_LIMITS';v['reviewed_at']=utc;save(release,v)
 acceptance=root/'release-acceptance-v2/acceptance.json';a=json.loads(acceptance.read_text())
 for row in a['curated']:
  row['state']='PASS_WITH_DIRECT_IMAGE_INSPECTION';row['human_readability']='GOOD';row['direct_image_inspection']=True
 a['state']='PASS_WITH_DIRECT_IMAGE_INSPECTION';a['reviewed_at']=utc;save(acceptance,a)
 # Whole BEFORE/AFTER captures, all focused plots, the failure reproducer, the
 # twelve gallery derivatives and final edge checks are durable. Duplicate
 # intermediate/viewport captures remain complete local evidence with hashes.
 selected=set()
 for name in ['before','release-pages']:
  data=json.loads((root/name/'visual-audit.json').read_text())
  for row in data['pages']:
   selected.add(row['screenshot']);selected.update(row['focused_screenshots'])
 for path in [root/'before-navigation',REVIEW/'figures/curated',root/'edge-checks-v3']:
  selected.update(str(p.relative_to(REVIEW)) for p in path.rglob('*.png'))
 before=json.loads((root/'before/visual-audit.json').read_text())
 summary={'state':'COMPLETE_VISUAL_REVIEW','utc':utc,'before':'results/visual-audit/before/visual-audit.json','after':str(release.relative_to(REVIEW)),
  'before_pages':len(before['pages']),'after_pages':len(v['pages']),'curated_views':12,'curated_acceptance':str(acceptance.relative_to(REVIEW)),
  'navigation_diagnosis':'results/visual-audit/before-navigation/diagnosis.json','data_validation':'results/visual-audit/data-validation.json',
  'readability_after':{p:r[0] for p,r in AFTER.items()},'published_visual_pngs':len(selected),'published_png_bytes':sum((REVIEW/p).stat().st_size for p in selected),
  'method':'Actual UI navigation over HTTP, full-page and focused screenshots, direct image inspection by the research agent, numerical plot signatures and fresh-context URL reconstruction. DOM/Plotly existence is insufficient.',
  'new_gpu_inference':0,'operator_interaction_required':False}
 save(root/'visual-audit.json',summary)
 external=work_root()/'raw/visual-captures';external.mkdir(parents=True,exist_ok=True);inventory=[]
 paths=list(root.rglob('*.png'))+list((REVIEW/'figures/curated').glob('*.png'))
 for p in sorted(paths):
  rel=str(p.relative_to(REVIEW));published=rel in selected
  destination=external/rel
  if not published:
   destination.parent.mkdir(parents=True,exist_ok=True)
   if destination.exists():assert digest(destination)==digest(p)
   else:shutil.copyfile(p,destination)
  inventory.append({'review_path':rel,'bytes':p.stat().st_size,'sha256':digest(p),'published':published,
   'local_original':str(p if published else destination),'recovery':'Git' if published else 'Local complete derivative, no off-host backup; recapturable from retained source/data, but exact intermediate pixels may depend on that version.'})
 inventory_path=work_root()/'derived'/('visual-screenshot-inventory-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json')
 if inventory_path.exists():raise SystemExit('Refuse existing completed screenshot inventory')
 save(inventory_path,{'utc':utc,'files':inventory,'published':len(selected),'local_only':len(inventory)-len(selected),'ordinary_png_limit_bytes':1048576})
 save(root/'screenshot-retention.json',{'utc':utc,'published':len(selected),'bytes':summary['published_png_bytes'],'captured_total':len(inventory),'local_only':len(inventory)-len(selected),
  'inventory_source':str(inventory_path),'inventory_sha256':digest(inventory_path),
  'publication_note':'All ten original pages and eleven final pages have complete full-page captures plus all important focused charts. The original oversized predictor page has a complete frozen-source lower-DPR capture; no image or journal was split to evade a limit. Duplicate intermediate/viewport captures and oversized gallery captures remain intact locally.'})
 ignore=REVIEW/'.gitignore';text=ignore.read_text();marker='# Visual review: duplicate/intermediate captures are retained in the local manifest.'
 if marker in text:text=text.split(marker)[0].rstrip()+'\n'
 text+='\n'+marker+'\n/results/visual-audit/**/*.png\n'
 text+=''.join('!/'+p+'\n' for p in sorted(selected) if p.startswith('results/'))
 ignore.write_text(text)
 print('DIRECT_IMAGE_REVIEW_RECORDED',len(selected),'durable PNGs',summary['published_png_bytes'],'bytes',flush=True)

if __name__=='__main__':main()
