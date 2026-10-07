#!/usr/bin/env python3
"""Phase summaries from collected one-second telemetry, with sampling limits."""
from pathlib import Path
import json
import re
import statistics

BASE=Path(__file__).resolve().parent
RES=BASE/'results'
rows=[]
for context in ['32K','64K','128K','256K']:
    records=[json.loads((RES/'raw'/f'IQ3_S-{context}-{n}.json').read_text()) for n in [1,2,3]]
    samples=[json.loads(line) for n in [1,2,3] for line in (RES/'telemetry'/f'IQ3_S-{context}-{n}.jsonl').read_text().splitlines()]
    for phase in ['reading','generating']:
        ss=[s for s in samples if s.get('metrics',{}).get('live',{}).get('state')==phase]
        hardware=[s['metrics'].get('hardware',{}) for s in ss]
        def mean(values):return statistics.mean(values) if values else None
        row={'context':context,'phase':phase,'samples':len(ss),
            'system_cpu_pct_mean':mean([s['system_cpu_pct'] for s in ss]),
            'process_cpu_pct_mean':mean([sum(p['cpu_pct'] for p in s['processes']) for s in ss]),
            'gpu_pcie_rx_mib_s_mean':mean([h['gpu_pcie_rx_mb'] for h in hardware if h.get('gpu_pcie_rx_mb') is not None]),
            'gpu_pcie_rx_mib_s_max':max((h['gpu_pcie_rx_mb'] for h in hardware if h.get('gpu_pcie_rx_mb') is not None),default=None),
            'gpu_pcie_tx_mib_s_mean':mean([h['gpu_pcie_tx_mb'] for h in hardware if h.get('gpu_pcie_tx_mb') is not None]),
            'pcie_current_width_observed':sorted({h['gpu_pcie_width'] for h in hardware if h.get('gpu_pcie_width') is not None})}
        for index in [0,1]:
            gs=[g for s in ss for g in s.get('gpus',[]) if g['index']==index]
            row[f'gpu{index}_util_pct_mean']=mean([g['util_pct'] for g in gs])
            row[f'gpu{index}_power_w_mean']=mean([g['power_w'] for g in gs])
        rows.append(row)
def table(headers,rr):
    return '| '+' | '.join(headers)+' |\n|'+'|'.join(['---']*len(headers))+'|\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in rr)
analysis={'phase_summary':rows,'decode_diagnostics':{},'expert_file_reads_all_zero':True,'first_request_pp_ranges':{}}
for context in ['32K','64K','128K','256K']:
    log=(RES/'raw'/f'IQ3_S-{context}-2-engine.log').read_text()
    analysis['decode_diagnostics'][context]=re.search(r'strata decode timing:.*',log)[0]
    rr=[json.loads((RES/'raw'/f'IQ3_S-{context}-{n}.json').read_text()) for n in [1,2,3]]
    analysis['first_request_pp_ranges'][context]=[r['pp_tps'] for r in rr]
    analysis['expert_file_reads_all_zero'] &= all(r['expert_tiers']['file_blobs']==0 and r['expert_tiers']['file_mb']==0 for r in rr)
(RES/'analysis.json').write_text(json.dumps(analysis,indent=2))
text=['# Interpretacja telemetrii',
    'Dane dotyczą IQ3_S. Q4 nie uruchamia się w wymaganej konfiguracji resident RAM + multi-GPU; brak pomiarów Q4 nie jest pomiarem zerowej wydajności.',
    '## CPU/GPU/PCIe',
    'Runtime wybrał split 25/23. Probe host→device: 13.4 GB/s na każdej GPU. Bieżąca szerokość linku z NVML wynosi x8, generacja 4 pod obciążeniem (maksymalna raportowana szerokość urządzenia: x16). NVML z serwera agreguje RX/TX obu kart; tych wartości nie należy przypisywać jednej GPU.',
    table(['ctx','phase','samples','system CPU %','process CPU %','GPU0 util %','GPU1 util %','PCIe RX mean MiB/s','PCIe RX max MiB/s'],
        [[r['context'],r['phase'],r['samples']]+[round(r[k],1) if r[k] is not None else '—' for k in ['system_cpu_pct_mean','process_cpu_pct_mean','gpu0_util_pct_mean','gpu1_util_pct_mean','gpu_pcie_rx_mib_s_mean','gpu_pcie_rx_mib_s_max']] for r in rows]),
    'Prefill: CPU średnio około 7–13% całej VM, GPU aktywne, silny strumień PCIe i wysokie piki RX. Wskazuje to na ścieżkę GPU + transfery ekspertów po PCIe; CPU nie wygląda na główny limit PP. Same te dane nie rozdzielają jednoznacznie czasu jąder GPU od transferów/pipeline i nie dowodzą wyłącznego bottlenecku PCIe.',
    'Decode: duża zajętość CPU (około 58–67% VM) współwystępuje z małym udziałem czasu CPU ekspertów w logach. W reprezentatywnym 128K verify wynosi 19.52 ms/window, GPU-reach wait 8.18 ms, per-layer host 0.58 ms, stage 1.75 ms; przy 256K: verify 21.20 ms, GPU-reach wait 9.01 ms, per-layer host 0.57 ms, stage 1.87 ms. To przemawia za dominacją ścieżki verify GPU i synchronizacji/host staging, nie matematyki CPU ekspertów. Wysokie CPU% może obejmować polling i oczekiwanie; nie należy utożsamiać go z kosztem obliczeń ekspertów. Bez profilu Nsight/ablation brak podstaw do bardziej precyzyjnego rozdzielenia. Nie wykonywano dodatkowego strojenia ani ablation poza kampanią.',
    'Decode trwa tylko około 2 s przy 256 output tokens: zwykle 2–3 próbki na request. Uśrednione utilization/power decode są orientacyjne; normalne liczniki runtime i czasy silnika są silniejszą podstawą niż pojedyncza próbka GPU.',
    '## Storage i RAM',
    'Wszystkie 12 requestów IQ3_S raportuje `file_blobs=0`, `file_mb=0`: brak odczytów ekspertów z plików w decode. IQ3_S używa pełnego przypiętego expert arena około 46.84 GiB; `ram_blobs=0` w tym trybie nie oznacza braku RAM, ponieważ ten licznik dotyczy odrębnego mapped resident source. PLE pozostaje w domyślnym trybie direct i może czytać małe wiersze z plików; zerowe odczyty ekspertów nie oznaczają zerowego całkowitego I/O.',
    '`/srv/ai` jest virtiofs. Guest disk/read_bytes nie pozwala dowieść braku fizycznych odczytów SSD hosta. Nie ma danych o odczytach Q4 w generation, ponieważ start jest odrzucony przed READY. Nie można potwierdzić pełnego resident zestawu Q4 ani odpowiedzieć empirycznie, czy jego misses trafiałyby do SSD w działającym runtime.',
    'Najniższe MemAvailable w całej mierzonej kampanii: ponad 101 GiB; guard 12 GiB nie został aktywowany. Median peak RAM used: około 58.3–59.2 GiB. VRAM peak około 23.30 / 23.42 GiB. Brak OOM.',
    '## Zmienność i PP >1000',
    'IQ3_S przekroczył 1000 PP token/s w każdym mierzonym runie 128K i 256K (najniższe odpowiednio 4024.4 i 4556.8). Mediany 5827.3 i 5841.0. TG mediany 114.9 i 109.4 token/s. TTFT mediany 22.05 i 44.92 s.',
    'Pierwszy request nowej długości bywał wolniejszy w PP mimo reuse=0: 64K 3258.9/5438.7/5439.0; 128K 4024.4/5827.3/5833.2; 256K 4556.8/5841.0/5842.3. Runtime zachowuje wybrane bufory, grafy i cache ekspertów między requestami, zgodnie z normalną metodą Strata. Nie resetowano procesu przed każdą komórką. Mediany opisują ten protokół z jednym warmup dla modelu; nie są cold-prefill ani dowodem identycznej szybkości pierwszego requestu dowolnej długości. Unikalny nonce i reuse=0 eliminują ponowne wykorzystanie KV promptu, ale nie cache sprzętowych/grafów/ekspertów.',
    '## Q4 i używalność',
    'Brak realnego porównania spowolnienia Q4/IQ3_S: wymagany resident-budget + layer split jest odrzucony przez upstream 0.1.31. Q4 nie jest dostępny dla wymaganego workload na obu GPU w tym przypiętym runtime. Nie wyciągamy z tego wniosków o jakości ani o wydajności Q4 na działającym backendzie. Quality sanity jest osobno w `quality/`; bez rankingu automatycznego.']
(RES/'analysis.md').write_text('\n\n'.join(text)+'\n')
print('Wrote analysis.json and analysis.md')
