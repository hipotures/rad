'use strict';
// Retrospective views consume the existing immutable generation/service assets.
const viewNames={overview:'Experiments',residency:'Residency state',slots:'Physical VRAM slots',churn:'Swaps & churn',startup:'Startup resident-set decay',expert:'Expert lifecycle',oracle:'CURRENT ↔ future',demand:'Expert demand',classes:'Physical size classes',predictor:'AUC → lifecycle → outcomes',lease:'Lease evidence'};
const urlControls={run:'runA',compare:'runB',gpu:'gpu',layer:'layer',class:'byteClass',expert:'expert',experts:'expertSubset',time:'time',smooth:'smooth',metric:'globalMetric',comparison:'comparison',counts:'normalize',scope:'slotScope',limit:'slotLimit'};
function readURL(){
 const q=new URLSearchParams(location.search);state.page=viewNames[q.get('view')]?q.get('view'):'overview';
 for(const [key,id] of Object.entries(urlControls)){if(!q.has(key)||!$(id))continue;const value=q.get(key);
  if(key==='run'||key==='compare'){if(value&&!state.catalog.runs.some(r=>r.id===value)){state.urlError=`Unknown canonical ${key} ID: ${value}`;continue;}}
  const node=$(id);if(key==='class'&&!node.querySelector('option[value="'+Number(value)+'"]')&&Number(value)>0)node.append(option(value,fmt(Number(value))+' B'));if(node.tagName==='SELECT'&&![...node.options].some(o=>o.value===value))continue;node.value=value;
 }
 for(const id of ['smooth','slotLimit'])if($(id))$(id).value=Math.max(1,Math.min(id==='smooth'?256:256,Number($(id).value)||1));
 if($('expert').value!=='')$('expert').value=Math.max(0,Math.min(511,Math.round(Number($('expert').value))));
 const lo=Number(q.get('from')),hi=Number(q.get('to'));state.range=q.has('from')&&q.has('to')&&Number.isFinite(lo)&&Number.isFinite(hi)&&hi>lo?[lo,hi]:null;
 includeInitial=q.get('initial')!=='0';state.leaseShort=Math.max(0,Number(q.get('short')??4)||0);state.leaseLong=Math.max(0,Number(q.get('long')??64)||0);state.focus=q.get('focus')==='1';state.snapshot=q.get('snapshot')==='1';$('focus').checked=state.focus;$('changedSlots').checked=q.get('changed')!=='0';activateTab();
}
function writeURL(){
 if(!state.catalog)return;const q=new URLSearchParams();q.set('view',state.page);
 for(const [key,id] of Object.entries(urlControls))if($(id)&&$(id).value!=='')q.set(key,$(id).value);
 if(state.range){q.set('from',Number(state.range[0].toFixed(7)));q.set('to',Number(state.range[1].toFixed(7)));}
 if(state.page==='lease'){if(!includeInitial)q.set('initial','0');q.set('short',state.leaseShort??4);q.set('long',state.leaseLong??64);}if($('focus').checked)q.set('focus','1');if(state.snapshot)q.set('snapshot','1');if(!$('changedSlots').checked)q.set('changed','0');
 history.replaceState(null,'','/?'+q.toString());
}
function presentation(){
 const focused=$('focus').checked;document.body.classList.toggle('focus-mode',focused);document.body.classList.toggle('snapshot-mode',!!state.snapshot);state.focus=focused;
 const cards=[...$('content').querySelectorAll('.card')];let primary=state.page==='oracle'?2:1;
 cards.forEach(c=>c.classList.toggle('secondary',focused&&(!c.querySelector('.js-plotly-plot')||primary--<=0)));
 if(!focused&&['predictor','residency','oracle'].includes(state.page)){const plotCards=cards.filter(c=>c.querySelector('.js-plotly-plot')),keep=state.page==='oracle'?2:1;const extra=plotCards.slice(keep);if(extra.length){const details=document.createElement('details');details.className='extra-evidence';details.innerHTML='<summary>More retained charts and exact evidence ('+extra.length+' plots)</summary>';extra.forEach(c=>details.append(c));$('content').append(details);}}
 $('toggleFocus').textContent=focused?'Show filters and all evidence':'Focus primary evidence';
 // Keep the explicit focused view identity and selected range in the screenshot.
 const identity=document.createElement('div');identity.className='view-identity';identity.textContent=`${viewNames[state.page]} · ${state.A?.id||'catalog'}${state.B?' ↔ '+state.B.id:''} · GPU ${$('gpu').value||'both'} · L${$('layer').value} · E${$('expert').value||'all'} · class ${$('byteClass').value||'all'} · ${axis()}${state.range?' '+state.range.map(v=>fmt(v,3)).join('…'):': full request'} · smooth ${$('smooth').value}`;
 $('content').prepend(identity);if(state.page!=='overview')$('filterSummary').textContent=`A: ${state.A?.id||'none'} · B: ${state.B?.id||'none'} · GPU ${$('gpu').value||'both'} · L${$('layer').value} · E${$('expert').value||'all'} · class ${$('byteClass').value||'all'} · ${axis()}`;rangeControls();if(state.urlError)note(esc(state.urlError));document.title=`${viewNames[state.page]} | Golden Swap Experiment Atlas`;writeURL();
}
function navigate(view){state.page=view;activateTab();window.scrollTo({top:0,behavior:'instant'});return render();}
function matchRun(a){
 if(!a)return null;const matches=state.catalog.runs.filter(r=>r.id!==a.id&&r.detail&&r.alignment_id===a.alignment_id&&r.campaign===a.campaign);
 const desired=a.policy==='REPLAY_CURRENT'||!a.future?['ORACLE_FULL','FULL_ORACLE','future-feasible','future-nextuse']:['REPLAY_CURRENT','CURRENT','native'];
 return matches.find(r=>desired.includes(r.policy)&&r.attempt===a.attempt)||matches.find(r=>desired.includes(r.policy))||null;
}
function aggregatePage(){
 const name=viewNames[state.page];intro(`${name} — chronological evidence unavailable for this run`,`<strong>${esc(state.A.id)}</strong> is an aggregate-only record. ${name} requires retained publication, ownership or demand events; none are invented. This record's aggregate measurements remain in Experiments. Choose a detailed ● trajectory below.`);
 const available=state.catalog.runs.filter(r=>r.detail&&(r.task===state.A.task||r.campaign===state.A.campaign));const preferred=available[0]||state.catalog.runs.find(r=>r.detail&&r.policy==='REPLAY_CURRENT');
 const box=document.createElement('div');box.className='card';box.innerHTML=`<h3>Open an actual ${esc(name)} trajectory</h3><p>Current evidence: ${esc(state.A.evidence_quality)}. Detailed alternatives: ${available.length} in this task or campaign.</p><button id="openDetailed">Open ${esc(preferred?.label||'a detailed run')}</button>`;$('content').append(box);
 $('openDetailed').onclick=()=>{for(const id of ['campaign','task','policy','context','source'])$(id).value='';fillRunSelectors();$('runA').value=preferred.id;$('runB').value='';state.range=null;render();};
}
function eventRange(run){if(!state.range)return [0,run.windows*48];const factor=$('time').value==='event'?1:$('time').value==='percent'?run.windows*48/100:48;return state.range.map(x=>Math.max(0,Math.min(run.windows*48,x*factor)));}
function meanRolling(vals){const n=Math.max(1,Number($('smooth').value)||1);let s=0;return vals.map((v,i)=>{s+=v;if(i>=n)s-=vals[i-n];return $('normalize').value==='raw'?s:s/Math.min(n,i+1);});}
async function churnPanel(title='Churn and required service through time'){
 const traces=[],rows=[['admissions',0,'Admissions',palette[0]],['evictions',0,'Evictions',palette[3]],['repeat_admissions',0,'Readmissions',palette[4]],['copy_bytes',1,'Published copy MB',palette[1]],['local',2,'Local VRAM entries',palette[0]],['cpu',3,'CPU entries',palette[3]],['mapped',3,'Mapped entries',palette[2]],['unknown_nonlocal',3,'Unknown nonlocal',palette[4]]];
 const diff=state.summaryB&&$('comparison').value==='difference'&&state.A.alignment_id===state.B.alignment_id;
 for(const [key,row,name,color] of rows){const a=meanRolling(sumSeries(state.summaryA,state.A,key)).map(v=>key==='copy_bytes'?v/1e6:v),b=state.summaryB?meanRolling(sumSeries(state.summaryB,state.B,key)).map(v=>key==='copy_bytes'?v/1e6:v):null;
  if($('normalize').value==='share'&&row>=2){const total=(s,r)=>meanRolling(['local','cpu','mapped','unknown_nonlocal'].map(k=>sumSeries(s,r,k)).reduce((out,v)=>out.map((n,i)=>n+v[i]),Array(r.windows).fill(0)));const ta=total(state.summaryA,state.A);a.forEach((v,i)=>a[i]=ta[i]?100*v/ta[i]:0);if(b){const tb=total(state.summaryB,state.B);b.forEach((v,i)=>b[i]=tb[i]?100*v/tb[i]:0);}}
  const series=diff?[[state.A,a.map((v,i)=>v-(b[i]??0)),`A − B ${name}`,'solid']]:[[state.A,a,`${state.B?'A ':''}${name}`,'solid'],...(b?[[state.B,b,`B ${name}`,'dot']]:[])];
  for(const [r,values,label,dash] of series){const tr=line(r,values,label,color,name==='Evictions'?(dash==='dot'?'dashdot':'dash'):dash);tr.xaxis=row?'x'+(row+1):'x';tr.yaxis=row?'y'+(row+1):'y';traces.push(tr);}
 }
 const per=$('normalize').value==='raw'?`rolling ${$('smooth').value}-window sum`:$('normalize').value==='share'?'service shares (%), swaps/copy per-window mean':'per-window rolling mean',layout={height:790,margin:{l:82,r:25,t:16,b:125},legend:{orientation:'h',y:-.12,font:{size:11}},hovermode:'x unified'};
 const titles=['Transactions','Copy MB',$('normalize').value==='share'?'Local (%)':'Local entries',$('normalize').value==='share'?'Nonlocal (%)':'Nonlocal entries'];for(let i=0;i<4;i++){const suffix=i?i+1:'';layout['xaxis'+suffix]={domain:[0,1],anchor:'y'+suffix,...(i<3?{showticklabels:false}:{title:axis()}),...(i?{matches:'x'}:{}),...(state.range?{range:state.range}:{})};layout['yaxis'+suffix]={domain:[.78-i*.25,1-i*.25],title:titles[i],gridcolor:'#344054',rangemode:diff?'normal':'tozero'};}
 const el=await chart(`${title} · ${per}`,traces,layout,true,'churn-panel');el.dataset.primary='1';
}
function stateMap(d,run){
 const [lo,hi]=eventRange(run),requested=Math.max(1,Number($('smooth').value)||1)*48,step=Math.max(1,Math.ceil((hi-lo)/900),Math.min(requested,Math.max(1,Math.ceil((hi-lo)/64))));
 const start=Math.floor(lo/step)*step,end=Math.min(run.windows*48,Math.ceil(hi/step)*step),N=Math.max(1,Math.ceil((end-start)/step)),subset=expertSubset();
 const es=$('expert').value!==''?[Number($('expert').value)]:subset?[...subset].sort((a,b)=>a-b):Array.from({length:512},(_,i)=>i),index=new Map(es.map((e,i)=>[e,i])),z=es.map(()=>Array(N).fill(0));
 for(const g of objects(d)){if(g.publish_event==null||!index.has(g.expert))continue;const s=Math.max(start,g.publish_event),t=Math.min(end,g.eviction_event??run.windows*48);if(t<=s)continue;const a=Math.floor((s-start)/step),b=Math.min(N-1,Math.floor((t-start-1e-9)/step));for(let k=a;k<=b;k++)z[index.get(g.expert)][k]+=Math.max(0,Math.min(t,start+(k+1)*step)-Math.max(s,start+k*step))/Math.min(step,end-(start+k*step));}
 const x=Array.from({length:N},(_,i)=>units(start+(i+.5)*step,run));const traces=[{x,y:es,z,type:'heatmap',zmin:0,zmax:1,colorscale:[[0,'#101927'],[.001,'#213444'],[1,'#588c92']],showscale:true,colorbar:{title:'Resident<br>fraction',thickness:10,len:.45},hovertemplate:'Expert %{y}<br>Time %{x:.3f}<br>Fraction of display bin resident %{z:.4f}<extra></extra>'}];
 const paths=[[2,'Local demand','#b2e9c8',2],[3,'CPU fallback',palette[3],4],[4,'Mapped RAM',palette[2],4],[5,'Unknown nonlocal',palette[4],3]];
 for(const [idx,name,color,size] of paths){const cells=new Map();for(const row of d.demand){if(row[0]<start||row[0]>=end||!row[idx]||!index.has(row[1]))continue;const k=Math.floor((row[0]-start)/step),key=row[1]+':'+k;const item=cells.get(key)||[k,row[1],0];item[2]+=row[idx];cells.set(key,item);}const a=[...cells.values()];traces.push({x:a.map(v=>x[v[0]]),y:a.map(v=>v[1]),text:a.map(v=>`${name}: ${v[2]} exact lane entries in display bin`),type:'scatter',mode:'markers',name,marker:{size,color,opacity:idx===2?.55:.85,symbol:idx===2?'circle':'x'},hovertemplate:'Expert %{y}<br>time %{x:.3f}<br>%{text}<extra></extra>'});}
 const gs=objects(d).filter(g=>g.generation>0&&g.publish_event!=null&&index.has(g.expert));for(const [field,name,color,symbol] of [['publish_event','Admission',palette[1],'triangle-right'],['eviction_event','Eviction',palette[3],'line-ns-open']]){const a=gs.filter(g=>g[field]!=null&&g[field]>=start&&g[field]<end);traces.push({x:a.map(g=>units(g[field],run)),y:a.map(g=>g.expert),text:a.map(g=>genHover(g,run)),type:'scatter',mode:'markers',name,marker:{size:3,color,symbol,opacity:.6},hovertemplate:'%{text}<extra></extra>'});}
 return {traces,step,start,end};
}
async function stateHeatmap(title,d,run){const m=stateMap(d,run);return chart(`${title} · ${fmt(m.step/48,3)}-window display bins`,m.traces,{height:720,yaxis:{title:'Expert ID',range:$('expert').value===''?[-1,512]:[Number($('expert').value)-1,Number($('expert').value)+1]},margin:{l:60,r:110,t:15,b:105},legend:{orientation:'h',y:-.12}},true,'state-map');}
async function residencyPrimary(){
 intro(`Residency state — layer ${$('layer').value}`,`Base color is the exact fraction of each displayed logical-time bin spent resident. Markers show local, CPU and mapped demand, admissions and evictions. Binning is display aggregation: exact generation boundaries remain in hover and expert drill-down. Click an expert to inspect all its generations.`);
 const el=state.layerB&&$('comparison').value==='difference'&&state.A.alignment_id===state.B.alignment_id?await differenceState():await stateHeatmap('Residency state · A '+state.A.policy,state.layerA,state.A);el.on('plotly_click',e=>{if(e.points?.length){$('expert').value=Math.round(e.points[0].y);navigate('expert');}});
 if(state.layerB&&$('comparison').value!=='difference')await stateHeatmap('Residency state · B '+state.B.policy,state.layerB,state.B);
}
async function alignedState(){
 if($('comparison').value==='difference'){await differenceState();await churnPanel('Aligned schedule turnover and physical service');return;}
 const aa=stateMap(state.layerA,state.A),bb=stateMap(state.layerB,state.B);let traces=aa.traces.map(t=>({...t,showscale:false,xaxis:'x',yaxis:'y'}));traces.push(...bb.traces.map(t=>({...t,showscale:false,showlegend:false,xaxis:'x2',yaxis:'y2'})));
 const xr=state.range||[units(aa.start,state.A),units(aa.end,state.A)],yr=$('expert').value===''?[-1,512]:[Number($('expert').value)-1,Number($('expert').value)+1];
 await chart('Aligned layer residency · A '+state.A.policy+' ↔ B '+state.B.policy,traces,{height:680,margin:{l:60,r:30,t:55,b:100},xaxis:{domain:[0,.46],title:axis(),range:xr},xaxis2:{domain:[.54,1],title:axis(),range:xr,matches:'x'},yaxis:{domain:[0,1],title:'Expert ID',range:yr},yaxis2:{domain:[0,1],anchor:'x2',range:yr,matches:'y'},annotations:[{text:'A · '+state.A.policy,x:.23,y:1.08,xref:'paper',yref:'paper',showarrow:false},{text:'B · '+state.B.policy,x:.77,y:1.08,xref:'paper',yref:'paper',showarrow:false}],legend:{orientation:'h',y:-.14}},true,'state-map');
 await churnPanel('Aligned schedule turnover and physical service');
}
const slotCache=new Map();
async function slots(){
 intro('Physical VRAM slot ownership',`A row is a device-local physical cache destination, not an expert ID or proposed victim's slot. The safe spare rotates: incoming publishes into the former spare and the withdrawn victim slot becomes the next spare. Blank intervals are unowned in the retained resident map; pending copy is not residency. <a href="/review/provenance/physical-slots.md">Source semantics ↗</a>`);
 const run=state.A,[lo,hi]=eventRange(run),layers=layerNumbers(state.summaryA,run);$('loading').textContent=`Loading physical ownership from ${layers.length} layer chunks…`;
 const chunks=await Promise.all(layers.map(l=>rawLayer(run,l)));
 const pools=new Map();for(const d of chunks)for(const g of objects(d)){if(g.publish_event==null||g.slot==null)continue;const key=`GPU${g.device} · S${g.slot}`;if(!pools.has(key))pools.set(key,[]);pools.get(key).push(g);}
 let ranked=[...pools].map(([key,gs])=>({key,gs:gs.sort((a,b)=>a.publish_event-b.publish_event),changes:gs.filter(g=>g.generation>0&&g.publish_event>=lo&&g.publish_event<hi).length}));
 if($('changedSlots').checked)ranked=ranked.filter(s=>s.changes>0);
 const ex=$('expert').value===''?null:Number($('expert').value),scope=$('slotScope').value;
 if(scope==='layer'||scope==='expert')ranked=ranked.filter(s=>s.gs.some(g=>g.layer===Number($('layer').value)&&(scope!=='expert'||ex==null||g.expert===ex)));
 ranked.sort((a,b)=>b.changes-a.changes||a.key.localeCompare(b.key));const available=ranked.length,shown=ranked.slice(0,Number($('slotLimit').value)||32),segments=[];
 shown.forEach((s,i)=>s.gs.forEach((g,j)=>{const end=g.eviction_event??run.windows*48;if(end<=lo||g.publish_event>=hi)return;segments.push({g,i,end,previous:s.gs[j-1]});}));
 metrics([[pools.size,'physical slot IDs with observed ownership'],[available,'matching changed/selected slots'],[shown.length,'most-changed slots displayed'],[segments.length,'exact intervals in selected range']]);
 if(!shown.length){intro('No slot replacement matches the selected range','Extend the time range or disable changed-slots-only. No event is invented.');return;}
 const colors=segments.map(({g})=>`hsl(${(g.expert*137.508+g.layer*31)%360},52%,58%)`);
 const el=await chart('Physical slot turnover · '+run.policy,[{type:'bar',orientation:'h',textposition:'none',base:segments.map(({g})=>units(Math.max(lo,g.publish_event),run)),x:segments.map(({g,end})=>units(Math.min(hi,end)-Math.max(lo,g.publish_event),run)),y:segments.map(s=>s.i),width:.8,marker:{color:colors,line:{width:0}},text:segments.map(({g,previous})=>genHover(g,run)+`<br>Previous physical owner: ${previous?'L'+previous.layer+'/E'+previous.expert:'none observed'} → L${g.layer}/E${g.expert}`),hovertemplate:'%{text}<extra></extra>',name:'Exact slot occupancy',showlegend:false}],{height:Math.max(480,shown.length*19+150),barmode:'overlay',bargap:0,yaxis:{title:'Device-local physical VRAM slot',tickmode:'array',tickvals:shown.map((_,i)=>i),ticktext:shown.map(s=>s.key+' ('+s.changes+' replacements)'),autorange:'reversed'},xaxis:{title:axis(),range:state.range||[units(lo,run),units(hi,run)]},margin:{l:220,r:25,t:18,b:60}},true,'slot-map');
 el.on('plotly_click',e=>{if(e.points?.length){const s=segments[e.points[0].pointIndex];$('layer').value=s.g.layer;$('expert').value=s.g.expert;navigate('expert');}});
 table(['Slot','Replacements in range','Intervals across observed request'],shown.map(s=>[s.key,s.changes,s.gs.length]));
}
async function predictorPrimary(p,task){
 const ms=p.metrics.filter(x=>(!task||x.task===task)&&x.model==='logistic'),rows=p.live_comparison.filter(x=>!task||x.task===task),tr=[];
 tr.push({x:ms.map(x=>'H'+x.horizon),y:ms.map(x=>x.auc),type:'bar',name:'Frozen logistic AUC',marker:{color:palette[1]},xaxis:'x',yaxis:'y'});
 for(const [i,key,name,color] of [[2,'unused_pct','Completed bytes without observed use',palette[3]],[3,'paired_TG_pct','Paired throughput change vs CURRENT',palette[0]]])tr.push({x:rows.map(x=>x.campaign+' '+x.policy.replace('ORACLE_IN_','')),y:rows.map(x=>x[key]),type:'bar',name,marker:{color},xaxis:'x'+i,yaxis:'y'+i});
 await chart('Predictive signal → lifecycle waste → measured policy outcome',tr,{height:600,margin:{l:65,r:28,t:55,b:150},showlegend:false,xaxis:{domain:[0,.25],title:'Main-window horizon'},yaxis:{domain:[0,1],range:[.4,1],title:'Ranking AUC'},xaxis2:{domain:[.34,.63],anchor:'y2',tickangle:-35},yaxis2:{domain:[0,1],anchor:'x2',title:'Unused completed payload (%)'},xaxis3:{domain:[.74,1],anchor:'y3',tickangle:-35},yaxis3:{domain:[0,1],anchor:'x3',title:'Paired TG change (%)'},annotations:[{x:.12,text:'Native-distribution prediction',xref:'paper',y:1.13,yref:'paper',showarrow:false},{x:.48,text:'Paid residency, Phase 1 → 2',xref:'paper',y:1.13,yref:'paper',showarrow:false},{x:.88,text:'End-to-end result',xref:'paper',y:1.13,yref:'paper',showarrow:false}]},false,'predictor-primary');
 intro('Confirmed lifecycle mechanism, separate from ranking quality',`${fmt(p.phase1_mechanism_fraction*100,6)}% of Phase 1 learned no-use bytes were linked to re-eviction before the intended target. First-use protection changed this transaction lifetime in Phase 2. Oracle incoming and common lifecycle are shared privileges; these bars do not isolate a learning benefit. AUC, bytes and timing use distinct denominators.`);
}
async function expertGenerations(ex,gs,ds){
 const r=state.A,[lo,hi]=eventRange(r),visible=gs.filter(g=>g.publish_event!=null&&(g.eviction_event??r.windows*48)>lo&&g.publish_event<hi).slice(0,160),index=new Map(visible.map((g,i)=>[g.uid,i]));
 if(!visible.length){intro('No published generation in this range','Demand can still be nonlocal; extend the range to inspect admissions.');return;}
 const tr=[{type:'bar',orientation:'h',textposition:'none',base:visible.map(g=>units(Math.max(lo,g.publish_event),r)),x:visible.map(g=>units(Math.min(hi,g.eviction_event??r.windows*48)-Math.max(lo,g.publish_event),r)),y:visible.map((_,i)=>i),width:Math.min(.6,(visible.length+.7)/25),marker:{color:visible.map(g=>g.use_count?palette[0]:palette[3]),line:{width:0}},text:visible.map(g=>genHover(g,r)),hovertemplate:'%{text}<extra></extra>',name:'Resident interval (red = no observed service)',showlegend:false}];
 for(const [field,name,color,symbol] of [['publish_event','Publication',palette[1],'triangle-right'],['first_use_event','First local service',palette[0],'circle'],['eviction_event','Eviction',palette[3],'x'],['release_event','Protection release',palette[2],'diamond-open'],['target','Intended target','#c6d2e7','line-ns-open']]){const a=visible.map((g,i)=>({g,i})).filter(({g})=>g[field]!=null&&g[field]>=lo&&g[field]<=hi);tr.push({x:a.map(({g})=>units(g[field],r)),y:a.map(v=>v.i),type:'scatter',mode:'markers',text:a.map(({g})=>genHover(g,r)),name,marker:{color:field==='first_use_event'?'#ffffff':color,symbol,size:field==='first_use_event'?9:6},hovertemplate:'%{text}<extra></extra>'});}
 for(const [idx,name,color] of [[2,'Later local service',palette[0]],[3,'CPU fallback',palette[3]],[4,'Mapped RAM',palette[2]],[5,'Unknown nonlocal',palette[4]]]){const a=ds.rows.filter(v=>v[idx]&&v[0]>=lo&&v[0]<=hi);tr.push({x:a.map(v=>units(v[0],r)),y:a.map(v=>idx===2&&index.has(v[6])?index.get(v[6]):-1),type:'scatter',mode:'markers',name,text:a.map(v=>`${name} · event ${v[0]} · ${v[idx]} required lane entries · resident uid ${v[6]??'absent'}`),marker:{color,size:6,symbol:idx===2?'circle-open':'line-ns-open'},hovertemplate:'%{text}<extra></extra>'});}
 const labels=visible.map(g=>`gen ${g.generation} / slot ${g.slot}`);const el=await chart(`Expert admission generations · L${$('layer').value}/E${ex} · ${visible.length} in range`,tr,{height:Math.max(430,visible.length*17+170),barmode:'overlay',yaxis:{title:'Actual admission generation / physical slot',tickmode:'array',tickvals:[-1,...visible.map((_,i)=>i)],ticktext:['Nonlocal demand',...labels],range:[visible.length-.5,-1.7]},xaxis:{title:axis(),range:state.range||[units(lo,r),units(hi,r)]},margin:{l:210,r:30,t:20,b:140},legend:{orientation:'h',y:-.26}},true,'generation-map');
 if(visible.length===160)note('First 160 overlapping generations displayed; zoom further for exact remaining generations. All records remain in the source layer asset.');
}

function rangeControls(){const r=state.A;if(!r)return;const bounds=state.range||[0,units(r.windows*48,r)];$('timeFrom').value=Number(bounds[0].toFixed(7));$('timeTo').value=Number(bounds[1].toFixed(7));$('rangeUnits').textContent=axis();}
async function rawLayer(run,l){const url=run.layer_url.replace('{layer}',l);if(!slotCache.has(url))slotCache.set(url,fetch(url).then(r=>{if(!r.ok)throw Error('Missing layer '+url);return r.json();}));while(slotCache.size>144)slotCache.delete(slotCache.keys().next().value);return slotCache.get(url);}
async function initialIdentityService(summary,run){const out=Array(run.windows).fill(0),ls=layerNumbers(summary,run),chunks=await Promise.all(ls.map(l=>rawLayer(run,l)));for(const d of chunks){const gs=objects(d),initial=new Set(gs.filter(g=>g.generation===0).map(g=>g.expert)),first=new Map();for(const g of gs)if(initial.has(g.expert)&&g.first_use_event!=null)first.set(g.expert,Math.min(first.get(g.expert)??Infinity,g.first_use_event));for(const event of first.values())if(event<run.windows*48)out[Math.floor(event/48)]++;}return cumulative(out);}

async function differenceState(){const a=stateMap(state.layerA,state.A),b=stateMap(state.layerB,state.B);if(a.traces[0].x.length!==b.traces[0].x.length)throw Error('Display bins differ; use absolute comparison');const z=a.traces[0].z.map((row,i)=>row.map((v,j)=>v-b.traces[0].z[i][j]));return chart('Residency state difference · A − B',[{...a.traces[0],z,zmin:-1,zmax:1,colorscale:'RdBu',colorbar:{title:'A − B<br>residency',thickness:12},hovertemplate:'Expert %{y}<br>Time %{x:.3f}<br>A − B resident fraction %{z:.4f}<extra></extra>'}],{height:720,yaxis:{title:'Expert ID'},margin:{l:60,r:110,t:15,b:80}},true,'state-map');}
