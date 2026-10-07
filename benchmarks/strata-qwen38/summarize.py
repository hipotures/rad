#!/usr/bin/env python3
"""Write results without inventing measurements for unavailable model cells."""
import csv
import json
from pathlib import Path
import statistics

BASE=Path(__file__).resolve().parent
RES=BASE/'results'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

MODELS=['IQ3_S','UD-Q4_K_XL']
CONTEXTS=['32K','64K','128K','256K']
FIELDS=['actual_prompt_tokens','generated_tokens','final_kv_occupancy_tokens','pp_tps','tg_tps',
        'prompt_processing_wall_s','decode_wall_s','ttft_s','total_wall_s','acceptance_pct',
        'draft_tokens','accepted_tokens','mean_accepted_length','mean_committed_length',
        'peak_rss_gib','peak_ram_used_gib','min_mem_available_gib','peak_vram0_gib','peak_vram1_gib']

def load(path,default=None):
    return json.loads(path.read_text()) if path.exists() else default

def fmt(value,digits=1):
    return '—' if value is None else f'{value:.{digits}f}'

def table(headers, rows):
    return '| '+' | '.join(headers)+' |\n|'+'|'.join(['---']*len(headers))+'|\n'+'\n'.join('| '+' | '.join(str(x) for x in row)+' |' for row in rows)+'\n'

def disk_bytes(root):
    files=[p for p in root.rglob('*') if p.is_file()]
    return sum(p.stat().st_size for p in files)

def main():
    records=[]
    for p in sorted((RES/'raw').glob('*.json')):
        r=load(p)
        if isinstance(r,dict) and r.get('kind')=='measured': records.append(r)
    summary=[]
    for model in MODELS:
        for context in CONTEXTS:
            rr=[r for r in records if r.get('model')==model and r.get('context')==context and r.get('status')=='OK']
            row={'model':model,'context':context,'measured_runs':len(rr),
                 'status':'OK' if len(rr)==3 else 'Q4_MULTI_GPU_UNSUPPORTED' if model=='UD-Q4_K_XL' else 'INCOMPLETE'}
            for field in FIELDS:
                values=[r[field] for r in rr if r.get(field) is not None]
                row[field]=statistics.median(values) if len(rr)==3 and len(values)==3 else None
            row['actual_prompt_tokens_min']=min((r['actual_prompt_tokens'] for r in rr),default=None)
            row['actual_prompt_tokens_max']=max((r['actual_prompt_tokens'] for r in rr),default=None)
            summary.append(row)
    with (RES/'summary.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(summary[0]))
        writer.writeheader();writer.writerows(summary)
    metadata={}
    for model in MODELS:
        cold=load(RES/'raw'/f'{model}-cold-start.json',{})
        startup=load(RES/'raw'/f'{model}-startup-metrics.json',{})
        engine=startup.get('engine',{})
        metadata[model]={'cold_start_s':cold.get('cold_start_s'),'startup_engine':engine}
    for model,pack in [('IQ3_S','iq3_s'),('UD-Q4_K_XL','ud-q4_k_xl')]:
        metadata[model]['shards_gb']=disk_bytes(Path('/srv/ai/models/strata/models')/model)/1e9
        metadata[model]['pack_gb']=disk_bytes(Path('/srv/ai/models/strata/packs')/pack)/1e9
        metadata[model]['disk_gb']=metadata[model]['shards_gb']+metadata[model]['pack_gb']
        metadata[model]['shared_mtp_gb']=disk_bytes(Path('/srv/ai/models/strata/mtp'))/1e9
    metadata['UD-Q4_K_XL']['status']='Q4_MULTI_GPU_UNSUPPORTED'
    metadata['UD-Q4_K_XL']['failed_start']=load(RES/'raw/Q4-status.json',{})
    metadata['UD-Q4_K_XL']['resident_expert_gib']=None
    # arena_mib is the runtime-reported full host expert arena, not estimated from file bitrate.
    arena=metadata['IQ3_S']['startup_engine'].get('arena_mib')
    metadata['IQ3_S']['resident_expert_gib']=float(arena)/1024 if arena is not None else None
    env=load(RES/'raw/environment.json',{})
    output={'strata_head':(BASE/'STRATA_HEAD').read_text().strip(),'source_version':'0.1.31',
        'summary':summary,'models':metadata,'runs':records,'environment':env}
    (RES/'summary.json').write_text(json.dumps(output,indent=2,ensure_ascii=False))
    figures=RES/'plots';figures.mkdir(exist_ok=True)
    for field,title,ylabel,name in [
        ('tg_tps','Decode vs rzeczywisty kontekst','TG [token/s]','tg-vs-context.png'),
        ('pp_tps','Prefill vs rzeczywisty kontekst','PP [token/s]','pp-vs-context.png'),
        ('ttft_s','TTFT vs rzeczywisty kontekst','TTFT [s]','ttft-vs-context.png'),
        ('peak_ram_used_gib','RAM vs rzeczywisty kontekst','RAM used (total − available) [GiB]','ram-vs-context.png')]:
        fig,ax=plt.subplots(figsize=(9,5))
        for model in MODELS:
            rows=[r for r in summary if r['model']==model and r[field] is not None]
            if rows: ax.plot([r['actual_prompt_tokens'] for r in rows],[r[field] for r in rows],'o-',label=model)
        ax.set(title=title,xlabel='Actual prompt tokens',ylabel=ylabel)
        ax.grid(alpha=.3)
        handles,_=ax.get_legend_handles_labels()
        if handles: ax.legend()
        ax.text(.02,.02,'UD-Q4_K_XL: Q4_MULTI_GPU_UNSUPPORTED',transform=ax.transAxes,va='bottom',fontsize=9,
                bbox={'facecolor':'white','alpha':.85,'edgecolor':'none'})
        fig.tight_layout();fig.savefig(figures/name,dpi=160);plt.close(fig)
    telemetry=RES/'telemetry/IQ3_S-128K-2.jsonl'
    fig,axes=plt.subplots(2,1,figsize=(11,7),sharex=True)
    if telemetry.exists():
        ss=[json.loads(line) for line in telemetry.read_text().splitlines()]
        for gpu in [0,1]:
            points=[(s['monotonic'],g) for s in ss for g in s.get('gpus',[]) if g['index']==gpu]
            if points:
                x=[t-ss[0]['monotonic'] for t,g in points]
                axes[0].plot(x,[g['util_pct'] for t,g in points],label=f'GPU{gpu}')
                axes[1].plot(x,[g['power_w'] for t,g in points],label=f'GPU{gpu}')
        generating=[s['monotonic']-ss[0]['monotonic'] for s in ss if s.get('metrics',{}).get('live',{}).get('state')=='generating']
        if generating:
            for ax in axes: ax.axvspan(min(generating),max(generating),alpha=.1,color='orange',label='decode')
    else:
        axes[0].text(.5,.5,'128K run unavailable',transform=axes[0].transAxes,ha='center')
    axes[0].set(title='IQ3_S: representative 128K run 2',ylabel='GPU utilization [%]')
    axes[1].set(ylabel='Power [W]',xlabel='Elapsed [s]')
    for ax in axes:
        ax.grid(alpha=.3)
        handles,_=ax.get_legend_handles_labels()
        if handles: ax.legend()
    fig.tight_layout();fig.savefig(figures/'gpu-128k.png',dpi=160);plt.close(fig)
    head=output['strata_head']
    lines=['# Strata Qwen3.8-Flash-Next: 2× RTX 4090',
        f'HEAD: `{head}`. Źródła i skompilowany runtime: 0.1.31, CUDA sm_89. Repo nie było aktualizowane podczas kampanii i nie patchowano silnika.',
        'Wymagane porównanie dwóch modeli zostało ograniczone przez upstream: **UD-Q4_K_XL: Q4_MULTI_GPU_UNSUPPORTED**. `--resident-budget-gib 80` włącza `resident_cpu_experts`; runtime 0.1.31 odrzuca ten tryb z dowolnym layer split. Błąd następuje przed ładowaniem wag. Nie wykonano zastępczego testu na jednej GPU ani mmap bez budżetu RAM.',
        'Dowód: [Q4-multi-gpu-probe.log](raw/Q4-multi-gpu-probe.log), [końcowy start z rzeczywistym packiem](raw/Q4-final-probe.log), [config Q4](/srv/ai/benchmarks/strata-qwen38/UD-Q4_K_XL-runtime.json); warunki w `src/program/generate.cpp:1188–1197` i `1282–1288` zamrożonego repo. Końcowy start miał MemAvailable 158.14 GiB, budżet 80 GiB i zakończył się odmową po około 0.72 s; to failed-start time, nie cold_start_s. Q4 nie osiągnął READY, dlatego cold-start, smoke odpowiedzi, benchmark i quality sanity Q4 są niedostępne.',
        '## Środowisko',
        '2× NVIDIA GeForce RTX 4090 (24564 MiB każda), driver 615.71.09; toolkit i dokładne informacje o VM: [environment.json](raw/environment.json). Ryzen 9 7950X3D; VM udostępnia 16 vCPU, 161.13 GiB RAM, bez swap. `/srv/ai` to virtiofs ([mount](raw/storage-mount.txt)); liczniki read_bytes/read_count w gościu nie muszą odzwierciedlać fizycznych odczytów SSD hosta. Strata file_blobs/file_mb są logicznymi odczytami ekspertów, a nie dowodem fizycznego I/O. Istniejące llama.cpp, ExLlamaV3, buun-llama-cpp i modele nie były zmieniane.',
        '## Metoda',
        'Własna kopia upstream `bench/results/2026-09-29-rtx3090-epyc-milan/data/strata-bench.py`; code-agent corpus z przypiętego repo, greedy, thinking off, 256 generated tokens. Każdy pomiar ma unikalny nonce na początku system promptu. Prompty wycinane z korpusu i dobierane przez dokładne tokenizowanie po renderowaniu chat template Strata; licznik API musi zgadzać się z tokenizerem, reuse musi wynosić 0. Brak requestów równoległych. Cele: 31400, 63400, 127000, 259500 prompt tokens; max context stale 262144.',
        'Jeden warmup modelu poza statystyką. Pierwszy pilot 32K zakończył się po 76 tokenach, zapowiadając użycie narzędzi; zachowany jako `raw/pilot-IQ3_S-32K-1.json`, wyłączony ze statystyk. W końcowych promptach jednolicie doprecyzowano offline/no-tools i rozwiniętą odpowiedź z diffem (co najmniej 500 słów), by osiągnąć 256 tokenów bez wyłączania EOS lub zmiany runtime. Mediany tylko dla pełnych 3 poprawnych runów komórki. PP/TG i czasy PP/decode pochodzą z zegara silnika w `/v1/status`, TTFT i całkowity czas z zegara klienta. TTFT obejmuje także obsługę API/tokenizację i pierwszy verify. Telemetria około 1 s: system CPU%, suma RSS procesów, process CPU% (może przekraczać 100%), MemAvailable, RAM total−available, GPU utilization/power/VRAM. Peak RSS i VRAM to maksima próbkowane, a RAM w tabelach to mediana peak RAM used poszczególnych requestów.',
        'MTP: `--spec 4 --spec-min-p 0.5`. Runtime INFO `mtp_max=4`, `spec=6` oznacza maksymalną zaalokowaną pojemność verifiera z domyślnym suffix lookup `lookup=3`; nie zmieniano defaultów Strata. Liczniki accepted/offered obejmują spekulację, w tym domyślny suffix lookup, którego liczniki są też w logach. INT8 KV. Auto expert cache i layer split bez ręcznego strojenia. Diagnostic env `STRATA_DECODE_TIMING=1`, `STRATA_SPLIT_TIMING=1` są upstreamowymi opcjami logowania. Final KV occupancy jest odtworzone z liczników: prompt−1 + verify_rounds + accepted_drafts; to liczba committed pozycji, nie osobny odczyt alokacji KV. Logical context = prompt + generated. Mean accepted length = accepted_drafts / verify_rounds; mean committed length = 1 + ta wartość.',
        'Cold start: pojedynczy świeży exec procesu do `/health` z `loaded=true`; cache plików OS nie był czyszczony. Wartość nie wchodzi do PP/TG. Guard przerywa proces przy MemAvailable <12 GiB. Q4 resident budget docelowo 80 GiB przy dostępnych >110 GiB; mimo wystarczającego RAM jest blokowany przez multi-GPU guard.',
        '## Mediany z 3 runów',
        table(['model','actual ctx','PP t/s','TG t/s','TTFT s','MTP accept %','RAM GiB','VRAM0 GiB','VRAM1 GiB','status'],
              [[r['model'],fmt(r['actual_prompt_tokens'],0),fmt(r['pp_tps']),fmt(r['tg_tps']),fmt(r['ttft_s'],2),fmt(r['acceptance_pct']),fmt(r['peak_ram_used_gib']),fmt(r['peak_vram0_gib']),fmt(r['peak_vram1_gib']),r['status']] for r in summary])]
    for field,title in [('tg_tps','TG [token/s]'),('pp_tps','PP [token/s]')]:
        lines += [f'## {title}',table(['model']+CONTEXTS,[[model]+[fmt(next(r for r in summary if r['model']==model and r['context']==ctx)[field]) for ctx in CONTEXTS] for model in MODELS])]
    lines += ['## Rozmiar i start',table(['model','disk GB (GGUF+pack)','resident experts GiB','cold start s','128K TG','256K TG','128K PP','256K PP'],
        [[model,fmt(metadata[model]['disk_gb']),fmt(metadata[model]['resident_expert_gib']),fmt(metadata[model]['cold_start_s'],2)]+
         [fmt(next(r for r in summary if r['model']==model and r['context']==ctx)[field]) for field,ctx in [('tg_tps','128K'),('tg_tps','256K'),('pp_tps','128K'),('pp_tps','256K')]] for model in MODELS]),
        'Disk GB obejmuje shardy i pack w jednostkach dziesiętnych, bez wspólnego MTP; dokładne rozmiary każdego składnika (także współdzielonego MTP) zawiera `summary.json`. Resident expert GiB dla IQ3_S pochodzi z runtime `arena_mib`. Q4 ma w plikach ~71.7 GiB routed experts, ale brak uruchomionego resident zestawu.',
        '## Konfiguracje i smoke',
        '[IQ3_S startup metrics](raw/IQ3_S-startup-metrics.json) zawierają wybrany split i cache; [engine log](/srv/ai/benchmarks/strata-qwen38/results/raw/IQ3_S-engine.log) zawiera przydziały, probing PCIe oraz KV streaming. [Smoke](raw/IQ3_S-smoke.json), [cold start](raw/IQ3_S-cold-start.json). [Q4 SHA256](raw/q4-sha256.json), [packing](raw/prepare-Q4.log).',
        '## Quality sanity',
        'Trzy krótkie zadania greedy: coding/debug, mathematical/reasoning, repository architecture. [Prompty](quality/prompts.json). Pełne odpowiedzi IQ3_S: [A](quality/IQ3_S/A-coding-debug.txt), [B](quality/IQ3_S/B-mathematical-reasoning.txt), [C](quality/IQ3_S/C-repository-architecture.txt). B i C początkowo trafiły w cap 1536; ponowiono je z tymi samymi promptami i cap 8192, zakończyły się naturalnie przy 1693 i 3488 tokenach. Pierwotne fragmenty zachowane w `quality/IQ3_S/partial/`. A zakończyło się naturalnie przy 750 tokenach. Q4: [powód pominięcia](quality/UD-Q4_K_XL/SKIPPED.txt). Bez automatycznego rankingu i bez wniosków jakościowych z bitratu.',
        '## Wykresy',
        '![TG](plots/tg-vs-context.png)\n\n![PP](plots/pp-vs-context.png)\n\n![TTFT](plots/ttft-vs-context.png)\n\n![RAM](plots/ram-vs-context.png)\n\n![GPU 128K](plots/gpu-128k.png)',
        '## Interpretacja',
        ('IQ3_S: 3/3 poprawnych requestów przy actual ~259500 prompt tokens; 256 tokenów generacji każdy. Stabilność dotyczy tej kampanii, nie wielogodzinnej pracy.' if next(r for r in summary if r['model']=='IQ3_S' and r['context']=='256K')['status']=='OK' else 'IQ3_S: stabilność przy ~260K nie została potwierdzona pełnymi 3 runami; zobacz status i surowe logi.'),
        'UD-Q4_K_XL: nie można ocenić stabilności ~260K, spowolnienia względem IQ3_S ani realnego PP/TG: wymagany resident tryb nie uruchamia się na dwóch GPU w tym upstreamie. Nie ma również danych o SSD podczas decode Q4. Nie należy przenosić wyników jednego RTX 5070 z dokumentacji na ten sprzęt.',
        'IQ3_S PP przy 128K / 256K: '+ ' / '.join(fmt(next(r for r in summary if r['model']=='IQ3_S' and r['context']==ctx)['pp_tps']) for ctx in ['128K','256K'])+' token/s. TG: '+ ' / '.join(fmt(next(r for r in summary if r['model']=='IQ3_S' and r['context']==ctx)['tg_tps']) for ctx in ['128K','256K'])+' token/s.',
        'Bottleneck: PP wskazuje na ścieżkę GPU + transfery ekspertów PCIe (CPU około 7–13% VM, linki aktualnie PCIe 4 x8, probe 13.4 GB/s na kartę, wysoki agregowany RX). Decode dominuje ścieżka verify GPU i synchronizacja/host staging; CPU ekspertów nie wygląda na główny koszt mimo wysokiego CPU%. Brak odczytów plików ekspertów w 12 requestach IQ3_S; PLE nadal może czytać wiersze z storage. Dane nie dowodzą jednego wyłącznego bottlenecku. Dokładne wartości, ograniczenia pomiarów virtiofs/NVML i zmienność runów: [analysis.md](analysis.md), [analysis.json](analysis.json).',
        'Q4 nie jest praktycznie dostępny dla wymaganego agentic/OpenCode workload na 2×4090 + resident RAM w przypiętej wersji. To ograniczenie runtime, a nie ocena jakości lub dowód słabej wydajności quantu.',
        'Nie commitowano i nie pushowano do upstream.']
    (RES/'report.md').write_text('\n\n'.join(lines)+'\n')
    print(f'Wrote {RES}/summary.csv, summary.json, report.md and plots',flush=True)

if __name__=='__main__':main()
