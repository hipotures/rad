'use strict';
const $=id=>document.getElementById(id);
const state={catalog:null,page:'overview',A:null,B:null,summaryA:null,summaryB:null,layerA:null,layerB:null,charts:[],epoch:0,linkedBusy:false,cache:new Map(),range:null};
let pendingRender=false,renderPromise=null,includeInitial=true;
const palette=['#7bd5c6','#82b3fc','#f3bd63','#f78d99','#bba0ed','#83ce90'];
const fmt=(x,d=0)=>x==null?'unknown':Number(x).toLocaleString(undefined,{maximumFractionDigits:d});
const gb=x=>x==null?'unknown':fmt(x/1e9,3);
const esc=x=>String(x??'unknown').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function note(s){$('notice').innerHTML=s;}
async function data(url){if(!state.cache.has(url)){state.cache.set(url,fetch(url).then(r=>{if(!r.ok)throw Error(`HTTP ${r.status}: ${url}`);return r.json();}).then(async v=>{
 if(v.demand_url){const base=await data(v.demand_url),byExpert=new Map(),overrides=new Map(v.service_exceptions.map(a=>[a[0],a.slice(1)]));
  for(const g of objects(v)){if(g.publish_event==null)continue;if(!byExpert.has(g.expert))byExpert.set(g.expert,[]);byExpert.get(g.expert).push(g);}
  for(const vs of byExpert.values())vs.sort((a,b)=>a.publish_event-b.publish_event||a.uid-b.uid);
  v.demand=base.map(([ev,e,count],i)=>{if(overrides.has(i))return [ev,e,...overrides.get(i)];const vs=byExpert.get(e)||[];let lo=0,hi=vs.length;while(lo<hi){const m=(lo+hi)>>1;if(vs[m].publish_event<=ev)lo=m+1;else hi=m;}const g=vs[lo-1],uid=g&&(g.eviction_event==null||ev<g.eviction_event)?g.uid:null;return [ev,e,uid==null?0:count,0,0,uid==null?count:0,uid];});
 }return v;
 }));while(state.cache.size>32){const old=[...state.cache.keys()].find(k=>k!==url&&k!=='data/catalog.json');if(!old)break;state.cache.delete(old);}}return state.cache.get(url);}
function objects(d){return d.generations.map(a=>Object.fromEntries(d.columns.map((k,i)=>[k,a[i]])));}
function units(ev,run){return $('time').value==='event'?ev:$('time').value==='percent'?100*ev/(run.windows*48):ev/48;}
function axis(){return $('time').value==='event'?'Routed-layer invocation':$('time').value==='percent'?'Observed request (%)':'Verifier window';}
function option(value,label){const n=document.createElement('option');n.value=value;n.textContent=label;return n;}
function filtered(){return state.catalog.runs.filter(r=>['campaign','task','policy'].every(k=>!$(k).value||r[k]===$(k).value)&&
  (!$('context').value||String(r.context||r.profile||'unknown')===$('context').value)&&(!$('source').value||r.source_group===$('source').value));}
function fillRunSelectors(){
 const rs=filtered(),oldA=$('runA').value,oldB=$('runB').value;
 $('runA').replaceChildren();$('runB').replaceChildren(option('','No comparison'));
 for(const r of rs){const label=`${r.detail?'●':'○'} ${r.label} · ${r.campaign.split('-2026')[0]}`;$('runA').append(option(r.id,label));$('runB').append(option(r.id,label));}
 if(rs.some(r=>r.id===oldA))$('runA').value=oldA;
 else {const r=rs.find(r=>r.detail&&r.campaign.startsWith('golden-swap-phase2')&&r.policy==='ORACLE_IN_HISTORY_TC')||rs.find(r=>r.detail);if(r)$('runA').value=r.id;}
 if(rs.some(r=>r.id===oldB))$('runB').value=oldB;
 $('filterSummary').textContent=`${rs.length}/${state.catalog.runs.length} records visible · ● exact selected trajectory · ○ aggregate-only repetition`;
}
function intro(title,text){const n=document.createElement('div');n.className='intro';n.innerHTML=`<h2>${esc(title)}</h2><p>${text}</p>`;$('content').append(n);return n;}
function metrics(items){const n=document.createElement('div');n.className='metric-grid';n.innerHTML=items.map(([v,l])=>`<div class="metric"><strong>${esc(v)}</strong><span>${esc(l)}</span></div>`).join('');$('content').append(n);}
function card(title,kind=''){const n=document.createElement('div');n.className='card';n.innerHTML=`<h3>${esc(title)}</h3><div class="chart-tools"><button data-export="png">PNG</button><button data-export="svg">SVG</button></div><div class="chart ${kind}"></div>`;$('content').append(n);return n.querySelector('.chart');}
async function chart(title,traces,extra={},timelike=true,kind=''){
 const el=card(title,kind),light=document.documentElement.classList.contains('light');
 const layout={paper_bgcolor:light?'#fff':'#18202d',plot_bgcolor:light?'#fff':'#18202d',font:{color:light?'#192839':'#e6edf5',size:11},
   margin:{l:62,r:25,t:16,b:62},legend:{orientation:'h',y:-.18},hovermode:'closest',dragmode:'zoom',
   xaxis:{title:timelike?axis():undefined,gridcolor:light?'#d6dee9':'#344054',...(timelike&&state.range?{range:state.range}:{} )},
   yaxis:{gridcolor:light?'#d6dee9':'#344054'},...extra};
 await Plotly.newPlot(el,traces,layout,{responsive:true,displaylogo:false,scrollZoom:true,modeBarButtonsToAdd:['pan2d','resetScale2d','toImage'],toImageButtonOptions:{format:'png',filename:'golden-swap-atlas'}});
 state.charts.push({el,timelike});
 el.parentElement.querySelectorAll('[data-export]').forEach(b=>b.onclick=()=>Plotly.downloadImage(el,{format:b.dataset.export,filename:'golden-swap-atlas',width:1500,height:800}));
 if(timelike){
  el.on('plotly_relayout',e=>{
   if(!$('linked').checked||state.linkedBusy)return;
   let range=e['xaxis.range']||[e['xaxis.range[0]'],e['xaxis.range[1]']];
   const reset=e['xaxis.autorange'];if(!reset&&(range[0]==null||range[1]==null))return;
   state.range=reset?null:range;state.linkedBusy=true;
   Promise.all(state.charts.filter(c=>c.timelike&&c.el!==el).map(c=>Plotly.relayout(c.el,reset?{'xaxis.autorange':true}:{'xaxis.range':range}))).finally(()=>state.linkedBusy=false);
  });
  el.on('plotly_hover',e=>{
   if(!$('linked').checked||state.linkedBusy||!e.points?.length)return;
   const x=e.points[0].x;if(typeof x!=='number')return;state.linkedBusy=true;
   for(const c of state.charts.filter(c=>c.timelike&&c.el!==el)){
    try {Plotly.Fx.hover(c.el,{xval:x});}catch(_){}
   }state.linkedBusy=false;
  });
 }
 return el;
}
function table(headers,rows,onSelect,limit=500){
 const wrap=document.createElement('div');wrap.className='table-wrap';let sorted=rows.slice(),direction=1;
 const render=()=>{wrap.innerHTML=`<table><thead><tr>${headers.map(h=>`<th>${esc(h)}</th>`).join('')}</tr></thead><tbody>${sorted.slice(0,limit).map((r,i)=>`<tr data-row="${i}">${r.map(v=>`<td>${esc(v)}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
 wrap.querySelectorAll('th').forEach((n,i)=>n.onclick=()=>{direction=-direction;sorted.sort((a,b)=>direction*(typeof a[i]==='number'&&typeof b[i]==='number'?a[i]-b[i]:String(a[i]??'').localeCompare(String(b[i]??''))));render();});
 if(onSelect)wrap.querySelectorAll('tbody tr').forEach(n=>n.onclick=()=>onSelect(sorted[Number(n.dataset.row)]));};render();$('content').append(wrap);
 if(rows.length>limit){const n=document.createElement('p');n.className='explanation';n.textContent=`Showing ${limit} sorted rows of ${rows.length}; sorting uses all rows. Exact per-layer values remain downloadable.`;$('content').append(n);}return wrap;
}
function layerNumbers(summary,run){let ls=Array.from({length:48},(_,i)=>i);if($('gpu').value!=='')ls=ls.filter(l=>(l>= (run.split||24))===Boolean(Number($('gpu').value)));
 if($('byteClass').value)ls=ls.filter(l=>summary.initial_quality[l].byte_class===Number($('byteClass').value));return ls;}
function sumSeries(s,run,col){const i=s.series_columns.indexOf(col),ls=layerNumbers(s,run),out=Array(run.windows).fill(0);
 for(const l of ls)for(let w=0;w<out.length;w++)out[w]+=s.all_layer_series[l][w][i];return out;}
function smooth(v,rolling=true){const n=Math.max(1,Math.min(256,Number($('smooth').value)||1)),out=[];let sum=0;
 for(let i=0;i<v.length;i++){sum+=v[i];if(i>=n)sum-=v[i-n];out.push($('normalize').value==='perWindow'?sum/Math.min(i+1,n):sum);}return out;}
function cumulative(v){let n=0;return v.map(x=>(n+=x));}
function line(run,v,name,color,dash='solid'){return {x:v.map((_,i)=>units(i*48+47,run)),y:v,type:'scatter',mode:'lines',name,line:{color,dash,width:1.5},hovertemplate:`${esc(name)}<br>%{x:.3f}: %{y:,.4g}<extra></extra>`};}
function compareValues(a,b,name,color=palette[0]){
 if(b&&$('comparison').value==='difference'&&state.A.alignment_id===state.B.alignment_id)
  return [line(state.A,a.map((v,i)=>b[i]==null?null:v-b[i]),`A − B ${name}`,color)];
 return [line(state.A,a,`A ${name}`,color),...(b?[line(state.B,b,`B ${name}`,color,'dot')]:[])];
}
function pairedLines(col,options={}){
 const transform=options.cumulative?cumulative:options.raw?x=>x:smooth;
 const a=transform(sumSeries(state.summaryA,state.A,col)),b=state.summaryB?transform(sumSeries(state.summaryB,state.B,col)):null;
 if($('comparison').value==='difference'&&b){
  if(state.A.alignment_id!==state.B.alignment_id){note('A − B is disabled for different logical workloads. Choose matching replay tapes or inspect absolute values.');return [line(state.A,a,'A '+col,palette[0])];}
  return [line(state.A,a.map((v,i)=>b[i]==null?null:v-b[i]),`A − B ${col}`,palette[2])];
 }return [line(state.A,a,'A '+col,palette[0]),...(b?[line(state.B,b,'B '+col,palette[1],'dot')]:[])];
}
async function overview(){
 intro('A browser for the actual research record',`${state.catalog.counts.experiments} experiment namespaces · ${fmt(state.catalog.counts.runs)} retained run records · ${fmt(state.catalog.counts.detailed_runs)} detailed trajectories · ${fmt(state.catalog.counts.expert_lifecycles)} generation records. Click a row to make it Run A. Counts are main routed work; MTP paths are not silently added.`);
 metrics([[state.catalog.counts.experiments,'included experiments'],[state.catalog.counts.detailed_runs,'selected detailed trajectories'],[fmt(state.catalog.counts.expert_lifecycles),'initial + admitted generations'],['0','new GPU inference requests']]);
 table(['Run','Campaign','Date','Model / runtime SHA','Task','Policy','Profile / input / output','Future','Slots','Admissions','Evictions','Copy GB','Local %','CPU','Mapped','Decode s','TG','Evidence'],filtered().map(r=>[r.id,r.campaign.split('-2026')[0],r.date,`${r.model} / ${r.source_sha?.slice(0,10)||'unknown'}`,r.task,r.policy,`${r.context||r.profile||'?'} / ${r.input??'?'} / ${r.output??'?'}`,r.future?'privileged future':'causal/native',r.resident_slots,r.promotions,r.evictions,gb(r.copy_bytes),r.local_pct==null?'unknown':fmt(r.local_pct,2),r.cpu,r.mapped,r.decode_s==null?'unmeasured':fmt(r.decode_s,3),r.tok_s==null?'unmeasured':fmt(r.tok_s,2),r.evidence_quality]),row=>{$('runA').value=row[0];state.page='residency';activateTab();render();},1000);
 const n=document.createElement('div');n.className='intro';n.innerHTML='<h3>What is included, and why</h3>'+state.catalog.experiments.map(e=>`<p><a href="/sources/${esc(e.report)}" target="_blank">${esc(e.title)}</a> — ${esc(e.reason)}</p>`).join('');$('content').append(n);
}
function genHover(g,run){return `${run.label}<br>L${g.layer} / E${g.expert} · GPU${g.device}<br>generation ${g.generation} / uid ${g.uid} · slot ${g.slot}<br>class ${fmt(g.byte_class)} B<br>trigger ${g.trigger??'unknown'} → target ${g.target??'unknown'}<br>publish ${g.publish_event??'unpublished'} · first ${g.first_use_event??'none observed'} · last ${g.last_use_event??'none observed'}<br>evict ${g.eviction_event??'end-censored'} · release ${g.release_event??'unmeasured'} · expiry ${g.expiry_event??'unmeasured'}<br>uses ${g.use_count} / distinct invocations ${g.distinct_use_count}<br>victim L${g.victim_layer??'?'} / E${g.victim??'?'}<br>copy ${gb(g.copy_bytes)} GB · ${g.copy_us==null?'DMA-only unknown':fmt(g.copy_us,2)+' us host-bracket copy'}<br>${g.status}`;}
function expertSubset(){const raw=$('expertSubset').value.trim();if(!raw)return null;const out=new Set();for(const part of raw.split(',')){const m=part.trim().match(/^(\d+)(?:-(\d+))?$/);if(!m)continue;for(let e=Number(m[1]);e<=Math.min(511,Number(m[2]??m[1]));e++)out.add(e);}return out;}
function residencyTraces(d,run){
 const expert=$('expert').value===''?null:Number($('expert').value),subset=expertSubset(),gs=objects(d).filter(g=>g.publish_event!=null&&(expert==null||g.expert===expert)&&(!subset||subset.has(g.expert)));
 const traces=[];
 for(const initial of [true,false]){let x=[],y=[],text=[];for(const g of gs.filter(g=>(g.generation===0)===initial)){
   const end=g.eviction_event??run.windows*48;x.push(units(g.publish_event,run),units(end,run),null);y.push(g.expert,g.expert,null);const h=genHover(g,run);text.push(h,h,'');
  }traces.push({x,y,text,type:'scatter',mode:'lines',name:initial?'Decode-initial generation':'Admitted generation',line:{width:3,color:initial?'#8291a5':palette[0]},hovertemplate:'%{text}<extra></extra>'});}
 for(const [field,name,symbol,color] of [['publish_event','Publication','triangle-right',palette[1]],['first_use_event','First local service','circle',palette[0]],['eviction_event','Eviction','x',palette[3]],['release_event','Protection release','diamond-open',palette[2]]]){
  const a=gs.filter(g=>g[field]!=null&&(field!=='publish_event'||g.generation>0));traces.push({x:a.map(g=>units(g[field],run)),y:a.map(g=>g.expert),text:a.map(g=>genHover(g,run)),type:'scatter',mode:'markers',name,marker:{symbol,size:6,color},hovertemplate:'%{text}<extra></extra>'});}
 if(expert!=null){for(const [idx,name,color] of [[2,'Local demand',palette[0]],[3,'CPU fallback',palette[3]],[4,'Mapped host',palette[2]],[5,'Unassigned nonlocal',palette[4]]]){
   const a=d.demand.filter(r=>r[1]===expert&&r[idx]>0);traces.push({x:a.map(r=>units(r[0],run)),y:a.map(()=>expert),text:a.map(r=>`${name} · event ${r[0]} · ${r[idx]} lane entries · resident uid ${r[6]??'absent'}`),type:'scatter',mode:'markers',name,marker:{symbol:idx===2?'circle-open':'line-ns-open',size:9,color},hovertemplate:'%{text}<extra></extra>'});}}
 return traces;
}
async function residency(){
 intro('Resident intervals, with admission generations',`Layer ${$('layer').value}. Horizontal intervals show actual publication → withdrawal. Startup means the attested decode boundary; use the Startup page for the earlier process profile fill. Select an expert to overlay every observed service entry. A null end is finite-request censoring.`);
 const el=await chart('Run A · '+state.A.label,residencyTraces(state.layerA,state.A),{yaxis:{title:'Expert ID',range:[$('expert').value===''?-3:Number($('expert').value)-2,$('expert').value===''?514:Number($('expert').value)+2]}},true,'tall');
 el.on('plotly_click',e=>{if(e.points?.length){$('expert').value=Math.round(e.points[0].y);state.page='expert';activateTab();render();}});
 if(state.layerB)await chart('Run B · '+state.B.label,residencyTraces(state.layerB,state.B),{yaxis:{title:'Expert ID',range:[$('expert').value===''?-3:Number($('expert').value)-2,$('expert').value===''?514:Number($('expert').value)+2]}},true,'tall');
 await globalHeatmap($('globalMetric').value,'Full-model '+$('globalMetric').selectedOptions[0].text+' by layer × logical time');
}
async function globalHeatmap(metric,title){
 const s=state.summaryA,r=state.A,col=s.series_columns.indexOf(metric),bin=Math.max(1,Number($('smooth').value)||1),ls=layerNumbers(s,r),x=[],z=[];
 for(let w=0;w<r.windows;w+=bin)x.push(units(w*48,r));
 const value=(sum,l,w)=>metric==='nonlocal'?sum.all_layer_series[l][w].slice(4,7).reduce((a,b)=>a+b,0):sum.all_layer_series[l][w][col];
 for(const l of ls){let row=[];for(let w=0;w<r.windows;w+=bin){let n=0;for(let j=w;j<Math.min(r.windows,w+bin);j++)n+=value(s,l,j);row.push(n);}z.push(row);}
 const difference=state.summaryB&&$('comparison').value==='difference'&&state.A.alignment_id===state.B.alignment_id;
 if(difference){for(let i=0;i<ls.length;i++)for(let k=0;k<z[i].length;k++){let v=0;for(let j=k*bin;j<Math.min(state.B.windows,(k+1)*bin);j++)v+=value(state.summaryB,ls[i],j);z[i][k]-=v;}}
 const el=await chart(title+(difference?' · A − B':' · A'),[{x,y:ls,z,type:'heatmap',colorscale:difference?'RdBu':'Viridis',...(difference?{zmid:0}:{}),hovertemplate:`Layer %{y}<br>${axis()} %{x:.2f}<br>${metric} in ${bin}-window bin: %{z:,}<extra></extra>`}],{yaxis:{title:'Layer'},margin:{l:55,r:80,t:15,b:55}},true,'tall');
 el.on('plotly_click',e=>{if(e.points?.length){$('layer').value=Math.round(e.points[0].y);state.page='residency';activateTab();render();}});
}
async function churn(){
 intro('Swap volume and repeated admissions',`Counts use complete generations, not routed lane entries. Rolling values use ${$('smooth').value} windows. The byte series counts published ordinary payload at its visibility event; issued/unpublished and mandatory restoration are retained separately in provenance. Aggregate veto totals have no invented per-window timeline.`);
 await chart('Admissions and evictions', [...pairedLines('admissions'),...pairedLines('evictions')]);
 await chart('Published copy payload per rolling interval (bytes)',pairedLines('copy_bytes'));
 await chart('Cumulative admitted copies',pairedLines('admissions',{cumulative:true}));
 await chart('Cumulative published payload (bytes)',pairedLines('copy_bytes',{cumulative:true}));
 await chart('Repeat admissions and late publications',[...pairedLines('repeat_admissions'),...pairedLines('late_publications')]);
 await chart('Observed protected occupancy',pairedLines('protected',{raw:true}));
}
async function startup(){
 intro('Process startup → decode boundary → turnover',`The shared profile is consumed in file order after K24 ownership filtering. CUDA slots are assigned sequentially, with real per-layer blob sizes until the VRAM byte budget stops the prefix. Heat does not re-sort the process fill. Fixed warmup and native prefill occur before the tape boundary. <a href="/review/provenance/startup-selection.md" target="_blank">Exact code, tie handling and provenance ↗</a>`);
 const s=state.summaryA,r=state.A,ls=layerNumbers(s,r),total=ls.reduce((n,l)=>n+s.initial_quality[l].residents,0);
 metrics([[fmt(total),'decode-initial resident identities in filter'],[fmt(s.process_startup?.replaced_before_decode),'profile identities changed before decode'],[fmt(s.spare_donors),'timed spare withdrawals'],[s.process_startup?.jaccard_decode_initial==null?'unknown':fmt(s.process_startup.jaccard_decode_initial*100,2)+'%','profile / decode-set Jaccard (whole run)']]);
 const denom=total||1,tr=[];
 for(const [col,name,c] of [['initial_survivors','Original generation survives',palette[0]],['initial_members_resident','Initial identity currently resident',palette[1]],['initial_used','Initial generation served locally',palette[2]],['initial_demanded','Initial identity demanded at least once',palette[4]]]){
  const bt=state.summaryB?layerNumbers(state.summaryB,state.B).reduce((n,l)=>n+state.summaryB.initial_quality[l].residents,0):null;
  tr.push(...compareValues(sumSeries(s,r,col).map(x=>100*x/denom),bt?sumSeries(state.summaryB,state.B,col).map(x=>100*x/bt):null,name,c));}
 const bt=state.summaryB?layerNumbers(state.summaryB,state.B).reduce((n,l)=>n+state.summaryB.initial_quality[l].residents,0):null;
 tr.push(...compareValues(sumSeries(s,r,'initial_survivors').map(x=>100*(1-x/denom)),bt?sumSeries(state.summaryB,state.B,'initial_survivors').map(x=>100*(1-x/bt)):null,'Cumulatively replaced',palette[3]));
 tr.push(...compareValues(sumSeries(s,r,'initial_demanded').map(x=>100*(1-x/denom)),bt?sumSeries(state.summaryB,state.B,'initial_demanded').map(x=>100*(1-x/bt)):null,'Never yet demanded','#95a2b7'));
 await chart('Startup set survival and usefulness (%)',tr,{yaxis:{title:'Percent of selected decode-initial set',range:$('comparison').value==='difference'?[-100,100]:[0,100]}});
 const mem=sumSeries(s,r,'initial_members_resident'),res=sumSeries(s,r,'resident_count');
 const bmem=state.summaryB?sumSeries(state.summaryB,state.B,'initial_members_resident'):null,bres=state.summaryB?sumSeries(state.summaryB,state.B,'resident_count'):null;
 await chart('Initial / actual resident-set Jaccard',compareValues(mem.map((v,i)=>v/(total+res[i]-v)),bmem?bmem.map((v,i)=>v/(bt+bres[i]-v)):null,'Jaccard',palette[0]),{yaxis:{range:$('comparison').value==='difference'?[-1,1]:[0,1]}});
 const horizons=[1,4,16,64,256,r.windows],early=horizons.map(h=>{let q=ls.map(l=>s.initial_quality[l].quality.find(x=>x.windows===h));return [h,q.reduce((n,v)=>n+(v?.demanded||0),0),q.reduce((n,v)=>n+(v?.served_before_eviction||0),0),total];});
 table(['First windows','Initial identities demanded','Served locally before eviction','Total initial identities'],early);
 const d=state.layerA,first=new Map();for(const v of d.demand)if(!first.has(v[1]))first.set(v[1],v[0]);
 const initial=new Set(objects(d).filter(g=>g.generation===0).map(g=>g.expert)),ideal=new Set(d.future_frequency_reference);
 await chart('Selected-layer startup vs full-tape frequency reference',[
  {x:horizons,y:horizons.map(h=>100*[...initial].filter(e=>first.has(e)&&first.get(e)<h*48).length/initial.size),name:'Decode initial demanded',type:'scatter',mode:'lines+markers'},
  {x:horizons,y:horizons.map(h=>100*[...ideal].filter(e=>first.has(e)&&first.get(e)<h*48).length/ideal.size),name:'Retrospective fixed frequency set',type:'scatter',mode:'lines+markers'}],
  {xaxis:{title:'First verifier windows (log scale)',type:'log'},yaxis:{title:'Percent of same per-layer slot count demanded'}},false);
 intro('Meaning of the frequency reference','This is a retrospective static set: same selected-layer slot count, full observed tape lane-frequency descending, expert ID breaks ties. It is not the live full-oracle scheduler, a startup intervention, or an achievable latency result.');
 intro('Layer startup placements',`Process-fill reference below is reconstructed from the immutable ranked file and attested slot counts; per-slot class parity is validated. It is not an observation of warmup demand. The decode table sorts experts by measured use, eviction and reloads. Click any expert to inspect it.`);
 table(['Expert','Profile slot','Global rank','First measured demand event','Still present at decode boundary'],state.layerA.process_startup||[],row=>{$('expert').value=row[0];state.page='expert';activateTab();render();},512);
 const rows=state.layerA.startup_table.slice().sort((a,b)=>(a[4]!=null)-(b[4]!=null)||(b[6]-a[6]));
 table(['Expert','Decode slot','Bytes','First demand','First local service','Eviction','Demand after eviction','Reloads','Total lane demand'],rows,row=>{$('expert').value=row[0];state.page='expert';activateTab();render();},512);
 await chart('Initial residents and admissions by layer',[{x:s.initial_quality.map(x=>x.layer),y:s.initial_quality.map(x=>x.residents),name:'Decode initial',type:'bar'},
  {x:s.initial_quality.map(x=>x.layer),y:s.all_layer_series.map(a=>a.reduce((n,w)=>n+w[0],0)),name:'Published admissions',type:'bar'}],{barmode:'group',xaxis:{title:'Layer'}},false);
}
function reuseInfo(d,expert){const rows=d.demand.filter(x=>x[1]===expert),evs=rows.map(x=>x[0]),gaps=evs.slice(1).map((x,i)=>x-evs[i]);const sorted=gaps.slice().sort((a,b)=>a-b);
 return {rows,evs,gaps,median:sorted.length?sorted[Math.floor(sorted.length/2)]:null,max:gaps.length?Math.max(...gaps):null};}
async function expert(){
 let ex=$('expert').value===''?state.layerA.demand[0]?.[1]??0:Number($('expert').value);$('expert').value=ex;
 const ds=reuseInfo(state.layerA,ex),gs=objects(state.layerA).filter(g=>g.expert===ex),r=state.A;
 const lifetime=gs.reduce((n,g)=>n+(g.publish_event==null?0:(g.eviction_event??r.windows*48)-g.publish_event),0);
 intro(`Layer ${state.layerA.layer} / expert ${ex}`,`All generations and required demand on the selected tape. Resident time and reuse gaps are logical routed invocations. A long idle interval is observational lease evidence; it is not an exclusive latency estimate.`);
 metrics([[gs.filter(g=>g.publish_event!=null).length,'resident generations'],[fmt(lifetime/48,2),'observed resident windows'],[fmt(ds.rows.reduce((n,x)=>n+x[3]+x[4]+x[5],0)),'nonlocal lane entries'],[Math.max(0,gs.filter(g=>g.generation>0&&g.publish_event!=null).length-(gs.some(g=>g.generation===0)?0:1)),'observed readmissions'],[fmt(ds.max==null?null:ds.max/48,2),'longest inter-demand gap (windows)'],[fmt(ds.median==null?null:ds.median/48,2),'median gap (windows)'],[gb(gs.reduce((n,g)=>n+g.copy_bytes,0)),'issued copy GB']]);
 await chart('All residency intervals and local/CPU/mapped demand',residencyTraces(state.layerA,r),{yaxis:{title:'Expert ID',range:[ex-1,ex+1]}},true,'tall');
 if(state.layerB)await chart('Matching Run B expert',residencyTraces(state.layerB,state.B),{yaxis:{title:'Expert ID',range:[ex-1,ex+1]}},true,'tall');
 await chart('Required lane entries by service path',[2,3,4,5].map((idx,i)=>({x:ds.rows.map(x=>units(x[0],r)),y:ds.rows.map(x=>x[idx]),type:'bar',name:['Local VRAM','CPU','Mapped RAM','Unknown nonlocal'][i],marker:{color:palette[i]}})),{barmode:'stack',yaxis:{title:'Lane entries'}},true);
 table(['Generation','Slot','Issue','Publication','First use','Last use','Eviction','Release','Uses','Distinct calls','Victim','Copy B','Status'],gs.map(g=>[g.generation,g.slot,g.issue_event,g.publish_event,g.first_use_event,g.last_use_event,g.eviction_event,g.release_event,g.use_count,g.distinct_use_count,g.victim,g.copy_bytes,g.status]),null,1000);
 await chart('Inter-demand gaps',[{x:ds.gaps.map(x=>x/48),type:'histogram',name:'Observed gaps',nbinsx:40,marker:{color:palette[0]}}],{xaxis:{title:'Verifier windows between distinct layer invocations'},yaxis:{title:'Count'}},false);
}
async function oracle(){
 intro('Current versus future-informed schedules',`Early IQ3_S/E004 and Q4 v2 models retained demand but modeled transfer cadence; their nonlocal CPU/mapped subdivision and throughput are unmeasured. Q4 live-oracle later ran full native computation with the same tape, real copy queues and five charged spares. Oracle incoming + causal victim arms retain privileged current-window protection. Full oracle is a feasible scheduler, not an optimal upper bound.`);
 if(!state.B||!state.summaryB){note('Choose a detailed ● Run B, or use “Choose matching current / oracle”.');return;}
 const exact=state.A.alignment_id===state.B.alignment_id;
 metrics([[exact?'Shared logical source':'Different logical sources','alignment'],[state.A.policy,'Run A policy'],[state.B.policy,'Run B policy'],[`${fmt(state.A.decode_s,3)} / ${fmt(state.B.decode_s,3)}`,'retained decode seconds A / B']]);
 if(!exact)note('These runs are not a matched replay pair. Normalized time is descriptive; differences cannot be attributed to policy.');
 else if(state.A.campaign!==state.B.campaign||state.A.binary_sha256!==state.B.binary_sha256||state.A.attempt!==state.B.attempt)note('Logical work matches; these retained timings come from different campaigns, binaries or blocks. The overlay describes residency. Use the original paired analyses for performance attribution.');
 await chart('Admissions over time',pairedLines('admissions'));
 await chart('Cumulative copied bytes',pairedLines('copy_bytes',{cumulative:true}));
 await chart('Required nonlocal lane entries',[...pairedLines('cpu'),...pairedLines('mapped'),...pairedLines('unknown_nonlocal')]);
 await serviceChart();
 const a=sumSeries(state.summaryA,state.A,'initial_survivors'),b=sumSeries(state.summaryB,state.B,'initial_survivors');
 await chart('Uninterrupted initial-generation survival',[line(state.A,a,'A',palette[0]),line(state.B,b,'B',palette[1],'dot')]);
 const gsA=objects(state.layerA),gsB=objects(state.layerB),W=Math.min(state.A.windows,state.B.windows),similar=[];
 for(let w=0;w<W;w++){const ev=w*48+47;const resident=gs=>new Set(gs.filter(g=>g.publish_event!=null&&g.publish_event<=ev&&(g.eviction_event==null||g.eviction_event>ev)).map(g=>g.expert));const aa=resident(gsA),bb=resident(gsB);const inter=[...aa].filter(x=>bb.has(x)).length;similar.push(inter/(aa.size+bb.size-inter));}
 await chart(`Layer ${state.layerA.layer} A/B resident-set Jaccard`,[line(state.A,similar,'A/B set similarity',palette[4])],{yaxis:{range:[0,1]}});
 await chart('Run A layer schedule',residencyTraces(state.layerA,state.A),{yaxis:{range:[$('expert').value===''?-3:Number($('expert').value)-2,$('expert').value===''?514:Number($('expert').value)+2]}},true,'tall');
 await chart('Run B layer schedule',residencyTraces(state.layerB,state.B),{yaxis:{range:[$('expert').value===''?-3:Number($('expert').value)-2,$('expert').value===''?514:Number($('expert').value)+2]}},true,'tall');
 const reference=await data('/evidence/analysis-detail-v1/resident-set-comparisons.json.gz'),matches=reference.pairs.filter(p=>p.campaign===state.A.campaign&&p.alignment_id===state.A.alignment_id);
 if(matches.length){intro('Which policy resembles the retained future reference?','Whole-model identity similarity is computed at every verifier-window end. A closer set is not necessarily more useful: popular residents can dominate Jaccard while a few missed experts cause most fallback. References retain their own scheduler semantics. This panel uses all devices/classes.');
  await chart('Whole-model similarity to the common future reference',matches.map((p,i)=>{const r=state.catalog.runs.find(r=>r.id===p.A);return line(r,p.series.map(([n,d])=>n/d),`${p.policy} → ${p.reference_policy}`,palette[i%palette.length]);}),{yaxis:{title:'Identity Jaccard',range:[0,1]}});
  table(['Policy','Reference','Mean Jaccard','Median Jaccard','Source semantics'],matches.slice().sort((a,b)=>b.mean_jaccard-a.mean_jaccard).map(p=>[p.policy,p.reference_policy,p.mean_jaccard,p.median_jaccard,p.kind]));}
}
async function serviceChart(){const tr=[];for(const [r,s,prefix] of [[state.A,state.summaryA,'A'],[state.B,state.summaryB,'B']]){if(!s)continue;const cs=['local','cpu','mapped','unknown_nonlocal'].map(k=>sumSeries(s,r,k));
 for(let i=0;i<4;i++){let vals=smooth(cs[i]);if($('normalize').value==='share'){const den=smooth(cs[0].map((_,j)=>cs.reduce((n,c)=>n+c[j],0)));vals=vals.map((v,j)=>den[j]?100*v/den[j]:0);}
 const name=['VRAM','CPU','mapped','unknown'][i];
 if(prefix==='B'&&$('comparison').value==='difference'&&state.A.alignment_id===state.B.alignment_id){const a=tr[i];a.y=a.y.map((v,j)=>vals[j]==null?null:v-vals[j]);a.name='A − B '+name;}
 else tr.push(line(r,vals,`${prefix} ${name}`,palette[i],prefix==='B'?'dot':'solid'));}}
 return chart('Main required work by physical service path',tr,{yaxis:{title:$('normalize').value==='share'?'Percent of common routed denominator':'Lane entries'}});}
async function demand(){
 const d=state.layerA,r=state.A,bin=Math.max(1,Number($('smooth').value)||1),bins=Math.ceil(r.windows/bin),mat=Array.from({length:512},()=>Array(bins).fill(0));
 for(const row of d.demand)mat[row[1]][Math.floor(row[0]/(48*bin))]+=row[2]+row[3]+row[4]+row[5];
 intro('Working-set evolution',`Exact demand is aggregated for display into ${bin}-window bins. Every required routed lane remains in the downloadable layer data. Adjacent-set Jaccard describes workload stability; it is independent of residency policy on an identical tape.`);
 let display=mat,diff=state.layerB&&$('comparison').value==='difference'&&state.A.alignment_id===state.B.alignment_id;
 if(diff){display=mat.map(row=>row.slice());for(const row of state.layerB.demand)display[row[1]][Math.floor(row[0]/(48*bin))]-=row[2]+row[3]+row[4]+row[5];}
 const el=await chart(`Layer ${d.layer} expert demand · ${diff?'A − B':'A'}`,[{x:Array.from({length:bins},(_,i)=>units(i*bin*48,r)),y:Array.from({length:512},(_,i)=>i),z:display,type:'heatmap',colorscale:diff?'RdBu':'Viridis',...(diff?{zmid:0}:{}),hovertemplate:'Expert %{y}<br>time %{x:.2f}<br>lane entries in bin %{z:,}<extra></extra>'}],{yaxis:{title:'Expert ID'}},true,'tall');
 if(state.layerB&&!diff){const mb=Array.from({length:512},()=>Array(Math.ceil(state.B.windows/bin)).fill(0));for(const row of state.layerB.demand)mb[row[1]][Math.floor(row[0]/(48*bin))]+=row[2]+row[3]+row[4]+row[5];await chart('Run B expert demand',[{x:mb[0].map((_,i)=>units(i*bin*48,state.B)),y:Array.from({length:512},(_,i)=>i),z:mb,type:'heatmap',colorscale:'Viridis'}],{yaxis:{title:'Expert ID'}},true,'tall');}
 el.on('plotly_click',e=>{if(e.points?.length){$('expert').value=e.points[0].y;state.page='expert';activateTab();render();}});
 const active=[],jac=[];let prev=new Set();for(let i=0;i<bins;i++){const a=new Set(mat.flatMap((row,e)=>row[i]>0?[e]:[]));active.push(a.size);const intersection=[...a].filter(e=>prev.has(e)).length;jac.push(i?intersection/(a.size+prev.size-intersection):null);prev=a;}
 await chart('Rolling active experts and adjacent-window overlap',[{x:active.map((_,i)=>units(i*bin*48,r)),y:active,name:'Distinct experts / bin',type:'scatter',mode:'lines',line:{color:palette[0]}},
 {x:jac.map((_,i)=>units(i*bin*48,r)),y:jac,name:'Adjacent-set Jaccard',type:'scatter',mode:'lines',yaxis:'y2',line:{color:palette[2]}}],{yaxis:{title:'Active-set size'},yaxis2:{overlaying:'y',side:'right',range:[0,1],title:'Jaccard'}});
 await serviceChart();await globalHeatmap('cpu','CPU fallback by layer × time');
}
async function classes(){
 const s=state.summaryA,r=state.A;intro('Physical capacity is not a homogeneous pool','Three routed blob classes exist in Q4. GPU1 has no 3,993,600-byte class under K24. Slot compatibility and ownership constrain every exchange; a large class is not interchangeable with a smaller one. IQ3_S uses its own retained byte classes.');
 table(['GPU','Blob class bytes','Physical slots before spare withdrawal','Charged bytes'],s.capacity.flatMap(d=>Object.entries(d.classes).map(([k,n])=>[d.device,Number(k),n,Number(k)*n])));
 const tr=[],byteTr=[];for(const cls of [...new Set(s.initial_quality.map(x=>x.byte_class))]){const values=(sum,run,col)=>{let v=Array(run.windows).fill(0);for(const l of layerNumbers(sum,run).filter(l=>sum.initial_quality[l].byte_class===cls))for(let w=0;w<v.length;w++)v[w]+=sum.all_layer_series[l][w][col];return smooth(v);};
  tr.push(...compareValues(values(s,r,0),state.summaryB?values(state.summaryB,state.B,0):null,`${fmt(cls)} B admissions`,palette[tr.length%palette.length]));
  byteTr.push(...compareValues(values(s,r,2),state.summaryB?values(state.summaryB,state.B,2):null,`${fmt(cls)} B copied bytes`,palette[byteTr.length%palette.length]));}
 await chart('Admissions by physical class',tr);await chart('Published copy bytes by physical class',byteTr);
 const gs=objects(state.layerA);await chart('Selected-layer resident lifetime by generation class',[{x:gs.filter(g=>g.generation>0&&g.publish_event!=null).map(g=>((g.eviction_event??r.windows*48)-g.publish_event)/48),type:'histogram',name:`${fmt(state.layerA.byte_class)} B`,marker:{color:palette[0]},nbinsx:50}],{xaxis:{title:'Observed verifier-window lifetime'},yaxis:{title:'Generations; end-censored included'}},false);
}
async function predictor(){
 const p=await data('/evidence/browser-v1/predictor.json.gz');
 intro('AUC → victim choice → paid transaction → latency','Return-risk AUC is a conditional ranking metric on sampled native residents. It does not price a new policy’s admission lifetime, queue, copier or planner. The frozen model omitted admission age. Incoming demand and current-window protection remain oracle privileges.');
 const task=state.A?.task;const ms=p.metrics.filter(x=>!task||x.task===task);const chosen=ms.length?ms:p.metrics;
 table(['Task','Model','Horizon windows','AUC','Brier','Positive fraction','Observed rows','Censored rows'],chosen.map(x=>[x.task,x.model,x.horizon,x.auc,x.brier,x.positive_fraction,x.n,x.censored]));
 await chart('Retained return-risk AUC by horizon', [...new Set(chosen.map(x=>x.model))].map((m,i)=>({x:chosen.filter(x=>x.model===m).map(x=>`${x.task} H${x.horizon}`),y:chosen.filter(x=>x.model===m).map(x=>x.auc),type:'bar',name:m,marker:{color:palette[i]}})),{xaxis:{title:'Task / main-window horizon'},yaxis:{title:'Retained AUC',range:[.4,1]},barmode:'group'},false);
 const cal=chosen.filter(x=>x.model==='logistic');await chart('Calibration from retained bins',[{x:[0,1],y:[0,1],type:'scatter',mode:'lines',name:'Calibrated reference',line:{dash:'dot',color:'#95a2b7'}},...cal.map((x,i)=>({x:x.bins.map(b=>b.prediction),y:x.bins.map(b=>b.observed),text:x.bins.map(b=>`n ${b.n} · Brier ${x.brier.toFixed(4)}`),type:'scatter',mode:'lines+markers',name:`${x.task} H${x.horizon}`,hovertemplate:'Pred %{x:.3f}<br>Observed %{y:.3f}<br>%{text}<extra></extra>',line:{color:palette[i%palette.length]}}))],{xaxis:{title:'Predicted return probability'},yaxis:{title:'Observed return fraction'}},false);
 await chart('Empirical ROC from retained per-sample predictions',p.roc.filter(x=>!task||x.task===task).map((x,i)=>({x:x.fpr,y:x.tpr,type:'scatter',mode:'lines',name:`${x.task} H${x.horizon}`,line:{color:palette[i%palette.length]}})),{xaxis:{title:'False positive rate'},yaxis:{title:'True positive rate'}},false);
 intro('Transaction funnel — denominators matter','These stages are not all one nesting chain. Candidate enumeration includes repeated scans, guard totals may count candidates or protected residents, and admissions are transactions. Use each label’s unit. Unknown candidate counts remain unknown. The terminal byte partition is disjoint.');
 for(const f of p.funnels.filter(x=>!task||x.task===task).slice(0,8)){
  const n=document.createElement('div');n.className='card';n.innerHTML=`<h3>${esc(f.label)}</h3><div class="funnel">${f.stages.map(v=>`<div class="stage"><small>${esc(v.unit)}</small><strong>${fmt(v.value)}</strong>${esc(v.stage)}</div>`).join('')}</div><p class="explanation">${esc(f.scope)}</p>`;$('content').append(n);
 }
 const rows=p.live_comparison.filter(x=>!task||x.task===task);table(['Task','Campaign','Policy','Median copy GB','Unused / completed %','Median CPU+mapped','Median paired TG change %','Planner ms','Score ms'],rows.map(x=>[x.task,x.campaign,x.policy,x.copy_GB,x.unused_pct,x.nonlocal,x.paired_TG_pct,x.planner_ms,x.score_ms]));
 await chart('Retained paired throughput change against contemporary CURRENT',rows.filter(x=>x.paired_TG_pct!=null).map((x,i)=>({x:[x.task+' '+x.campaign+' '+x.policy],y:[x.paired_TG_pct],type:'bar',name:x.policy,showlegend:false,marker:{color:palette[i%palette.length]}})),{xaxis:{title:'Original same-block comparisons; no new timing experiment'},yaxis:{title:'Median within-block TG change (%)'}},false);
 await chart('Paid bytes without observed use: before and after first-use control',rows.map((x,i)=>({x:[x.task+' '+x.campaign+' '+x.policy],y:[x.unused_pct],type:'bar',name:x.policy,marker:{color:x.campaign==='Phase 1'?palette[3]:palette[0]},showlegend:false})),{xaxis:{title:'Retained live condition'},yaxis:{title:'No-observed-use / completed ordinary payload (%)'}},false);
 const rankings=p.ranking.records.filter(x=>!task||x.task===task);
 await chart('Sampled victim ranking: early return avoided',[
  {x:rankings.map(x=>x.task+' '+x.model),y:rankings.map(x=>100*x.uniform_return_le4),type:'bar',name:'Uniform sampled resident'},
  {x:rankings.map(x=>x.task+' '+x.model),y:rankings.map(x=>100*x.sampled_selected_return_le4),type:'bar',name:'Minimum sampled risk'}],
  {barmode:'group',xaxis:{title:'Native candidate distribution; not live interventions'},yaxis:{title:'Return within four windows (%)'}},false);
 const cs=p.selection.candidates;
 await chart('Development/calibration policy cost proxy',cs.map((x,i)=>({x:[x.policy+' threshold '+x.threshold],y:[x.calibration_mean_proxy],type:'bar',name:x.policy,showlegend:false,marker:{color:palette[i%palette.length]}})),
  {xaxis:{title:'Inherited operating points; lower proxy is better'},yaxis:{title:'Assumed cost proxy; not measured latency'}},false);
 const vs=p.funnels.filter(x=>x.label.startsWith('Phase 2')&&(!task||x.task===task));
 await chart('Actually binding Phase 2 guard conditions', ['Cost veto','Protection exclusion','Capacity / cap veto','Risk veto'].map((stage,i)=>({x:vs.map(x=>x.label),y:vs.map(x=>x.stages.find(s=>s.stage===stage)?.value??null),name:stage,type:'bar',marker:{color:palette[i]}})),
  {barmode:'group',xaxis:{title:'Block 1; units differ as declared in funnel'},yaxis:{title:'Recorded count (log scale)',type:'log'}},false);
 table(['Calibration task / policy','Threshold 0.2 vs 0.5','Risk veto at 0.5'],p.threshold_sensitivity.map(x=>[x.task+' / '+x.policy,x.same_decisions_02_05?'Identical action hashes':'Different actions',x.risk_veto_05]));
 table(['Development block','TC ON/OFF TG ratio','Completion-wall ratio','OFF copy GB','ON copy GB','OFF unused GB','ON unused GB'],p.lifecycle_ablation.map(x=>[x.block,x.TG_ON_over_OFF,x.wall_ON_over_OFF,x.OFF_copy_GB,x.ON_copy_GB,x.OFF_unused_GB,x.ON_unused_GB]));
 const direct=p.history_logistic.filter(x=>!task||x.task===task);
 await chart('Direct history versus logistic under common first-use control',[{x:direct.map(x=>x.task+' block '+x.block),y:direct.map(x=>100*(x.history_TG_over_logistic-1)),name:'History TG change relative to logistic',type:'bar',marker:{color:palette[0]}}],
  {xaxis:{title:'Same counterbalanced live block'},yaxis:{title:'Paired TG difference (%)'}},false);
 table(['Run','Mean protected experts','Nonlocal lane entries at cap','Routed calls at cap','Interpretation'],p.protection_opportunities.filter(x=>!task||x.label.startsWith(task)).map(x=>[x.label,x.mean_protected_total,x.nonlocal_entries_at_cap_for_active_class,x.routed_invocations_at_cap,'Opportunity exposure; not proved preventable admission or exclusive regret']));
 intro('Where ranking signal is lost',`Phase 1’s ${fmt(p.phase1_mechanism_fraction*100,6)}% of learned no-use bytes were generation-linked re-eviction before their intended first target. Phase 2’s common protection repaired this lifecycle, and history matched the frozen logistic closely. Cost/protection caps and planner work remained; avoided CPU/mapped lane counts are not exact saved latency. Phase 3 memoization removed repeated queries without a confirmed incremental practical gain. Phase 4’s tracing-neutrality gate failed, so acknowledgment sums cannot be read as latency savings.`);
 if(p.samples?.length){const sample=p.samples.filter(x=>x.task===(task||p.samples[0].task));await chart('Per-sample risk and observed return gap (deterministic display sample)',sample.map((s,i)=>({x:s.prediction,y:s.return_gap_windows,mode:'markers',type:'scatter',name:`${s.task} H${s.horizon}`,marker:{size:4,opacity:.35,color:palette[i%palette.length]},hovertemplate:'Risk %{x:.3f}<br>Observed next-return gap %{y:.2f} windows<extra></extra>'})),{xaxis:{title:'Frozen logistic probability'},yaxis:{title:'Observed return gap; finite-label censoring applies'}},false);}
 table(['Counter','Interpretation'],p.missing.map(x=>[x,'Unmeasured / not reconstructible from retained records']));
}
async function lease(){
 intro('Observed lifetimes and reuse — no TTL policy has been implemented','This view provides evidence for designing an expert-specific lease. Select thresholds to highlight possible short/long-lived patterns. End-resident generations are right-censored. A next demand after eviction is an observed return, not proof that retaining that expert was the best competing decision.');
 const d=state.layerA,r=state.A,gs=objects(d).filter(g=>(includeInitial||g.generation>0)&&g.publish_event!=null),ri=new Map();
 for(const row of d.demand){if(!ri.has(row[1]))ri.set(row[1],[]);ri.get(row[1]).push(row[0]);}
 const life=gs.map(g=>((g.eviction_event??r.windows*48)-g.publish_event)/48),distinct=gs.map(g=>g.distinct_use_count);
 const control=document.createElement('div');control.className='card controls-inline';control.innerHTML=`<label><input id="includeInitial" type="checkbox" ${includeInitial?'checked':''}> Include startup observations (prior age unknown)</label><label>Short lifetime ≤ windows <input id="shortLife" type="number" value="4" min="0"></label><label>Persistent lifetime ≥ windows <input id="longLife" type="number" value="64" min="0"></label><span id="leaseSummary"></span>`;$('content').append(control);
 $('includeInitial').onchange=()=>{includeInitial=$('includeInitial').checked;render();};
 const summarize=()=>{const short=Number($('shortLife').value),long=Number($('longLife').value);$('leaseSummary').textContent=`${gs.filter((g,i)=>life[i]<=short).length} short observations · ${gs.filter((g,i)=>life[i]>=long).length} long observations · ${gs.filter(g=>!g.use_count).length} no observed service · exploratory labels only`;};summarize();$('shortLife').oninput=summarize;$('longLife').oninput=summarize;
 table(['Exploratory observation','Count','Interpretation'],[
  ['No observed local service',gs.filter(g=>!g.use_count).length,'Investigate do-not-admit; censoring and lateness must be separated.'],
  ['Short useful observed lifetime',gs.filter((g,i)=>g.use_count>0&&life[i]<=Number($('shortLife').value)).length,'Potential short lease; future returns and competing demand still matter.'],
  ['Long lifetime with repeated service',gs.filter((g,i)=>g.distinct_use_count>1&&life[i]>=Number($('longLife').value)).length,'Potential long lease; inspect idle gaps.'],
  ['Resident at observation end with repeated service',gs.filter(g=>g.eviction_event==null&&g.distinct_use_count>1).length,'Potential persistent/pinned working set; not an optimal allocation label.']]);
 const el=await chart('Generation lifetime × distinct useful invocations',[{x:life,y:distinct,text:gs.map(g=>genHover(g,r)),customdata:gs.map(g=>g.expert),type:'scatter',mode:'markers',name:'Observed generations; startup diamonds',marker:{symbol:gs.map(g=>g.generation===0?'diamond':'circle'),size:gs.map(g=>5+2*g.copy_bytes/3072000),color:gs.map(g=>g.eviction_event==null?2:g.previous_generation==null?0:1),cmin:0,cmax:2,showscale:true,colorbar:{title:'Observation',tickvals:[0,1,2],ticktext:['First generation','Readmission','End-censored'],thickness:12},colorscale:[[0,palette[0]],[.5,palette[3]],[1,palette[2]]],opacity:.65},hovertemplate:'%{text}<extra></extra>'}],{xaxis:{title:'Observed resident lifetime (windows)'},yaxis:{title:'Distinct local-service invocations'},margin:{l:62,r:150,t:20,b:60}},false);
 el.on('plotly_click',e=>{if(e.points?.length){$('expert').value=e.points[0].customdata;state.page='expert';activateTab();render();}});
 const first=gs.filter(g=>g.first_use_event!=null).map(g=>(g.first_use_event-g.publish_event)/48),uses=gs.map(g=>g.distinct_use_count),gaps=[],next=[],idle=[];
 for(const g of gs){const evs=(ri.get(g.expert)||[]).filter(e=>e>=g.publish_event&&e<(g.eviction_event??r.windows*48));const ag=evs.slice(1).map((e,i)=>(e-evs[i])/48);gaps.push(...ag);const untilEnd=evs.length?((g.eviction_event??r.windows*48)-evs.at(-1))/48:life[gs.indexOf(g)];idle.push(Math.max(untilEnd,...ag,0));
  if(g.eviction_event!=null){const n=(ri.get(g.expert)||[]).find(e=>e>=g.eviction_event);if(n!=null)next.push((n-g.eviction_event)/48);}}
 for(const [name,values,xlabel] of [['Publication → first local use',first,'Windows'],['Observed resident lifetime',life,'Windows; finite-tail censoring'],['Distinct uses per admission',uses,'Distinct layer invocations'],['In-residency inter-demand reuse gaps',gaps,'Windows'],['Longest observed idle interval',idle,'Windows'],['Eviction → next observed demand',next,'Windows; non-return tails excluded']])await chart(name,[{x:values,type:'histogram',nbinsx:40,marker:{color:palette[0]},name}],{xaxis:{title:xlabel},yaxis:{title:'Count'}},false,'short');
 const copy=gs.filter(g=>g.copy_us!=null&&g.eviction_event!=null).flatMap(g=>{const n=(ri.get(g.expert)||[]).find(e=>e>=g.eviction_event);return n==null?[]:[{gap:(n-g.eviction_event)/48,cost:g.copy_us,expert:g.expert}];});
 await chart('Return gap versus observed host-bracket copy time',[{x:copy.map(x=>x.gap),y:copy.map(x=>x.cost),text:copy.map(x=>'Expert '+x.expert),type:'scatter',mode:'markers',marker:{size:5,color:palette[1]},hovertemplate:'%{text}<br>Gap %{x:.2f} windows<br>Host copy bracket %{y:.2f} us<extra></extra>'}],{xaxis:{title:'Eviction to next observed demand (windows)'},yaxis:{title:'Copy+completion observation (us), not DMA-only'}},false);
}
function activateTab(){document.querySelectorAll('#tabs button').forEach(b=>b.classList.toggle('active',b.dataset.page===state.page));}
async function render(){
 pendingRender=true;if(renderPromise)return renderPromise;
 state.busy=true;renderPromise=(async()=>{try{while(pendingRender){pendingRender=false;await renderNow();}}finally{renderPromise=null;state.busy=false;}})();return renderPromise;
}
async function renderNow(){
 const epoch=++state.epoch;state.charts.forEach(c=>Plotly.purge(c.el));state.charts=[];$('content').replaceChildren();note('');$('loading').textContent='Loading selected evidence…';
 state.A=state.catalog.runs.find(r=>r.id===$('runA').value);state.B=state.catalog.runs.find(r=>r.id===$('runB').value);
 $('provenanceContent').innerHTML=`<p><a href="/review/provenance/event-schema.md" target="_blank">Field meanings and missing evidence ↗</a></p><p>${state.A?`<a href="/sources/${esc(state.A.source_result)}" target="_blank">Original result ↗</a> · <a href="/sources/${esc(state.A.report)}" target="_blank">Original report ↗</a>`:'Choose a run'}</p><pre>${esc(JSON.stringify(state.A,null,2))}</pre>`;
 try{
  if(state.page==='overview'){await overview();$('loading').textContent='';return;}
  if(state.page==='predictor'){await predictor();$('loading').textContent='';return;}
  if(!state.A?.summary_url){intro('This record has aggregate evidence',`Detailed trajectories were selected by first retained task/policy identity, not by timing. This repetition remains fully indexed. Choose a ● run for a chronological journal.`);$('loading').textContent='';return;}
  state.summaryA=await data(state.A.summary_url);
  for(const cls of new Set(state.summaryA.initial_quality.map(v=>v.byte_class)))if(![...$('byteClass').options].some(o=>Number(o.value)===cls))$('byteClass').append(option(cls,fmt(cls)+' B'));
  const permitted=layerNumbers(state.summaryA,state.A);if(!permitted.length){intro('No layers match this device and class','This physical pool has no matching layers. Change the GPU or byte-class filter.');$('loading').textContent='Empty physical filter';return;}
  if(!permitted.includes(Number($('layer').value)))$('layer').value=permitted[0];
  const la=Number($('layer').value);const req=[Promise.resolve(state.summaryA),data(state.A.layer_url.replace('{layer}',la))];
  if(state.B?.summary_url)req.push(data(state.B.summary_url),data(state.B.layer_url.replace('{layer}',la)));
  const loaded=await Promise.all(req);if(epoch!==state.epoch)return;
  [state.summaryA,state.layerA,state.summaryB,state.layerB]=loaded;if(!state.B?.summary_url){state.summaryB=null;state.layerB=null;}
  $('filterSummary').textContent=`A: ${state.A.label} · B: ${state.B?.label||'none'} · GPU ${$('gpu').value||'both'} · L${la} · E${$('expert').value||'all'} · ${axis()} · ${$('smooth').value}-window display · exact drill-down`;
  $('provenanceContent').innerHTML=`<p class="small">${esc(state.A.campaign)} · ${esc(state.A.kind)} · ${esc(state.A.evidence_quality)} · ${fmt(state.summaryA.generations)} generation records. <a href="${esc(state.A.layer_url.replace('{layer}',la))}" target="_blank">Current exact layer JSON</a></p><p class="small">${esc(state.summaryA.native_boundary)}<br>${esc(state.summaryA.restoration)}</p><pre>${esc(JSON.stringify({identities:state.A,transaction_partition:state.summaryA.partition,field_schema:state.layerA.columns,validation:state.summaryA.validation,original_sources:state.summaryA.provenance,unknown:state.summaryA.unknowns},null,2))}</pre>`;
  const pages={residency,churn,startup,expert,oracle,demand,classes,lease};await pages[state.page]();
  if(epoch!==state.epoch)return;$('loading').textContent=`Loaded ${fmt(state.layerA.generations.length)} layer generations and ${fmt(state.layerA.demand.length)} exact expert-demand batches.`;
 }catch(e){if(epoch===state.epoch){$('loading').textContent='Evidence loading failed';note(esc(e.message));console.error(e);}}
}
async function init(){
 state.catalog=await data('data/catalog.json');for(const k of ['campaign','task','policy']){const vals=[...new Set(state.catalog.runs.map(r=>r[k]))].sort();vals.forEach(v=>$(k).append(option(v,k==='campaign'?v.split('-2026')[0]:v)));}
 [...new Set(state.catalog.runs.map(r=>String(r.context||r.profile||'unknown')))].sort().forEach(v=>$('context').append(option(v,v)));
 [...new Set(state.catalog.runs.map(r=>r.source_group))].sort().forEach(v=>$('source').append(option(v,v)));
 for(let l=0;l<48;l++)$('layer').append(option(l,'Layer '+l));for(const n of [3072000,3584000,3993600])$('byteClass').append(option(n,fmt(n)+' B'));
 for(const id of ['campaign','task','policy','context','source'])$(id).onchange=()=>{fillRunSelectors();state.range=null;render();};
 for(const id of ['runA','runB','gpu','layer','byteClass','expert','expertSubset','time','comparison','smooth','normalize','globalMetric'])$(id).onchange=()=>{if(id==='time'||id==='runA')state.range=null;if(id==='expert'&&$('expert').value!=='')$('expert').value=Math.max(0,Math.min(511,Math.round(Number($('expert').value))));render();};
 document.querySelectorAll('#tabs button').forEach(b=>b.onclick=()=>{state.page=b.dataset.page;activateTab();render();});
 $('theme').onclick=()=>{document.documentElement.classList.toggle('light');$('theme').textContent=document.documentElement.classList.contains('light')?'Dark theme':'Light theme';render();};
 $('reset').onclick=()=>{state.range=null;state.linkedBusy=true;Promise.all(state.charts.filter(c=>c.timelike).map(c=>Plotly.relayout(c.el,{'xaxis.autorange':true}))).finally(()=>state.linkedBusy=false);};
 $('match').onclick=()=>{const a=state.catalog.runs.find(r=>r.id===$('runA').value);if(!a)return;
  const other=state.catalog.runs.find(r=>r.id!==a.id&&r.detail&&r.alignment_id===a.alignment_id&&r.campaign===a.campaign&&(a.future?(!r.future||r.policy==='REPLAY_CURRENT'):(r.policy==='ORACLE_FULL'||r.policy==='FULL_ORACLE'||r.policy.includes('ORACLE')||r.policy==='future-nextuse'||r.policy==='future-feasible')));
  if(other){for(const id of ['policy'])$(id).value='';fillRunSelectors();$('runA').value=a.id;$('runB').value=other.id;state.page='oracle';activateTab();render();}else note('No detailed matched current/oracle counterpart in this campaign; select another recorded replay family.');};
 fillRunSelectors();await render();window.atlas=state;
}
init().catch(e=>{$('loading').textContent='Atlas initialization failed';note(esc(e.message));console.error(e);});
