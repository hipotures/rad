# Q4 Strata v0.1.32 — raport końcowy

Status: kampania i przegląd zakończone. Wyniki negatywne pozostają jawne: opcjonalny Q4-fast nie przeszedł upstream gate, a cztery tury agent128 nie osiągnęły256 tokenów. Nie oznacza to pomyślnego przejścia każdego testu. Pełny audyt: evidence/final-manual-review.json; automatyczne kontrole: completion-audit.md.

HEAD `c499bd102e7a4135c0de389dcfe38c399759ccc8`, tagv0.1.32, defaultbuild; Unsloth revision `38bb39ee97821de2c9009abb7e93950eec396e66`. Stara kampania v0.1.31 zachowana podq4-max-sweep; stare runy z PSS1Hz są EXCLUDED_TELEMETRY_PSS, nie użyte do selekcji. Hardware/driver/CUDA/kernel/PCIe: environment.json. Release/source/help audit: release-delta.md. Hostsource/KVgeometry/counter scopes: architecture-notes.md.

Każdy rawresult przechowuje runtime/modelidentity, topology i pełny config/command. PSS tylko poza clockiem requestu; około1Hz RSS/CPU/RAM/GPU/power/PCIe/I/O. RAM_used=MemTotal−MemAvailable, RSS/PSS osobno. Null oznacza niedostępny counter. Warmup/smoke/diagnostyka nie są mierzoną komórką finalnej macierzy.

1. **Co poprawiło v0.1.32?** Kontrolowane porównanie całego runtime z identycznymi requestami/K24/INT8/prefillauto pokazuje niewielki wzrost PP: 31400 actual: +2.68%, 63400 actual: +1.36%, 127000 actual: +0.76%, 259500 actual: +0.36%. Zyski finalnego tuningu są osobnym NOT_CONTROLLED_A_B. Release dodaje równoległy refill oraz opcjonalne nowe ścieżki; sam wynik nie izoluje przyczyny do jednego patcha.

2. **Zmiana Q4 PP** 31400 actual: +2.68%, 63400 actual: +1.36%, 127000 actual: +0.76%, 259500 actual: +0.36%. Pełne wyniki i best-config before/after: comparison-upgrade.md/.csv/.json. Przy małych deltach uwzględnij rozrzut runów; nie traktuj ich jako dowodu dużego przyspieszenia.

3. **Zmiana Q4 TG** Finalne best-config TG zmieniło się z98.7 na105.5 przy64K (+6.89%), z86.9 na106.6 przy128K (+22.67%) i z92.1 na95.0 przy256K (+3.15%). To NOT_CONTROLLED_A_B, uwzględniające nowy tuning i system prompt. TG ma wyraźny rozrzut i zależy od promptu/adaptive placement oraz MTP. Kontrolowane pary i finalne best-config wartości są oddzielone w tabeli upgrade; zmiany split/KV/prefill/workers/MTP nie są efektem samego upgrade.

4. **Czy multi-GPU prompt fix pomaga 2×4090?** Przy K24/full arena/INT8/prefillauto widać powyższe niewielkie dodatnie mediany PP; przy259500 actual delta wynosi +0.36%. Nie wykonano prywatnego cofnięcia wyłącznie tego patcha, więc jest to whole-version A/B. Duży wzrost PP przy większym chunku stanowi osobny tuning.

5. **Czy Q4-fast build jest wart używania?** Nie został dopuszczony do modelowych pomiarów: STRATA_MMQ_KQUANTS=ON skompilował się, ale upstreamowy test numeryczny Q4_K gate/up-1 zgłosił unwritten/non-finite output. Zachowano logi, nie patchowano engine. Nie ma uczciwego wyniku speedA/B ani podstaw do production recommendation tego builda; default został użyty.

6. **Najlepszy layer split** Wśród przetestowanych K20/22/24/26 i auto wygrał SPLIT-K24-confirm-v0132; final K=24. TOP2 potwierdzono trzema runami po warmupie. To lokalne optimum w badanym zakresie, nie dowód globalnego optimum wszystkich48granic.

7. **Najlepszy prefill** Wybrano jawne 16384; argument32768 upstream zmniejszał do16384. Obie potwierdzone polityki dawały bardzo podobne PP; jawny16384 nie polega na automatycznej redukcji. Final argument=16384, actualchunk/borrowedslots zapisane w startupach oraz allocation evidence.

8. **Czy STRATA_SPLIT_OWN ma sens?** Screening64/128K nie osiągnął >5% przewagi względem default. Tryb silnie zmniejsza dostępny expert cache przez osobne bufory; jest NON_BIT_IDENTICAL_OPT_IN i pozostaje osobno. --no-prefill-borrow również przegrało screening. Domyślna ścieżka zachowana do tuningu.

9. **Najlepszy KV przy128/256K** Final KV=k8v4; oryginalna selekcja szybkości KV: DEFAULT_RUNTIME_KV_OPTION. K8V4 wygrał selekcję szybkości. Osobna walidacja INT8 również miała krótką odpowiedź agent64 i nie dowodzi większej stabilności. Finalna decyzja i wszystkie ograniczenia: production-selection.json; nie jest to controlled A/B ani dowód jakości/stabilności ogólnej. Wszystkie legalne INT8/K8V4/Q4_0/rotatedINT8 miały screening n2 na obu kontekstach, TOP2 n3. Wybór według geometrycznej średniej potwierdzonych TG; alternatywne wyjścia oraz textdiff zapisane osobno, bez założenia jakościowej równoważności. K8V4 nie łączono z kv-resident.

10. **Najlepsze MTP** Final spec=3, min-p=0.3; spec2/3/4/5 miały po2 requesty z actual1024output, TOP2 po3. MTP OFF jest UNSUPPORTED_BY_CURRENT_UPSTREAM dla tego nativepack/serve; nie podaję wymyślonego raw-non-MTP ani speedupu względem OFF. Normal counters obejmują MTP i suffix lookup.

11. **Workers / PCIe / min-p** Final pool-workers=12, pcie-frac=0.28, spec-min-p=0.3. Upstream calibrator: {'--pool-workers': '10'}; default {'pcie_frac': 0.28, 'spec_min_p': 0.5, 'pool_workers': 15}. Lokalne64K screens były sekwencyjne, bez Cartesianproduct; zwycięski zestaw potwierdzony warmup+3.

12. **PP/TG przy32/64/128/256K** Tabela główna poniżej zawiera mediany dokładnie3runów/actualcontext,256output,greedy,zero reuse,max262144. Prompt API count zgadza się z tokenizerem; occupancy nie pochodzi z configuredcontext.

13. **Long-decode TG** actual63400+4096: TG 85.60; actual127000+4096: TG 83.90; actual127000+8192: TG 81.20; zachowane niepełne próby: actual127000, 6324/8192 output, TG 81.20, naturalny stop. Pełny 8K pochodzi z osobno oznaczonego jednego powtórzenia tego samego zadania i sampling z nowym nonce; nie ignorowano EOS. Podano rzeczywiste długości wybranego konfiguracji. Osobna INT8 próba8K zakończyła się po6777 i nie wchodzi do pełnych8K. K8V4 pierwszy8K stop6324 i jedno pełne powtórzenie8192 są zachowane oddzielnie. Sampling temp1/top_p0.95/top_k20. Rolling/cumulativeTG na wykresie oraz normal acceptance z upstream trace; trace overhead jest w timingach.

14. **Agentic multi-turn latency** start63400: initial TTFT 21.54s, turns1–10 medianTTFT 4.69s, medianTG 84.50 tok/s; start127000: initial TTFT 31.84s, turns1–10 medianTTFT 4.12s, medianTG 87.25 tok/s. Zachowano niepełne sesje K8V4 128K: turn8 stop188 i turn5 stop95. INT8 również miał krótką odpowiedź235 w sesji64K, więc nie został automatycznie uznany za stabilniejszy. Finalna sesja128K kontynuuje po normalnym EOS i zapisuje wszystkie10 tur w jednym engine; odpowiedzi poniżej256 są osobno raportowanym niespełnieniem celu, nie pełnym sukcesem długości. Bez EOS suppression i bez intra-session restartu. Każda sesja to jeden nieprzerwany engine i11requestów, zwykły prefixreuse. Jest to symulacja na prawdziwych fragmentach repozytorium, nie działająca integracja OpenCode ani wykonanie proponowanych przez model patchy.

15. **Compaction128K/250K** actual127000 → 2013 summary tokens: 56.70s total (TTFT 34.70s); actual250000 → 2219 summary tokens: 71.45s total (TTFT 47.43s). Transcript z rzeczywistych zapisanych sesji i odpowiedzi; krótka historia/decyzje zostają kompletne, rozmiar ogranicza jedynie starsze duże fragmenty repo. Oldruntime control używa identycznego payloadu w nowym namespace, oba konfiguracje podano jako NOT_CONTROLLED_A_B.

16. **Czy decode ma expert SSD reads?** Normal logical expert file fetches w finalnej macierzy: zero we wszystkich12runach. Full native RAM arena przechowuje cały routed set; CPU misses korzystają z RAM. Odczyty PLE/embedding i fizyczny hostSSD za virtiofs są osobne. Zero file_blobs nie dowodzi zera wszystkich fizycznych SSD reads całego procesu.

17. **Bottleneck** Ocena opiera się na normal decode-stage timings, osobnej diagnostyce prompt kernels oraz GPU/CPU/PCIe telemetry. GPU-reach wait zawiera oczekiwanie na pracę/transfery, nie stanowi samego czasu kernela; nie wolno sumować zachodzących timeline obu GPU jako wall time. Dokładne linie diagnostyczne znajdują się poniżej. Storage ekspertów nie jest per-token źródłem przy fullarena/zerofilefetch; pozostałe odczyty fizycznego hosta nie są przypisane. PP ogranicza przede wszystkim ścieżka obliczeń GPU: w diagnostyce128K GEMM gate/up+down zajmował27.7% GPU timeline, dequant11.1%, a wait copy4.4%; przy256K odpowiednio26.5%,10.6% i3.6%, przy rosnącym QSA select9.0%. Reprezentatywny128K prefill obciąża obie GPU blisko100% przez większość pracy, około300–350W, przy dużo mniejszym CPU niż w decode. TG ogranicza mieszana ścieżka verify i synchronizacja CPU/GPU: verify około18–22ms z około21–25ms/window, GPU-reach wait około6–7.5ms oraz istotna praca CPU fallback; CPU dochodzi do około1300% (100% to jeden wątek). PCIe Gen4x8/PHB uczestniczy w transferach, lecz te counters nie dowodzą jego saturacji ani jednej wyłącznej przyczyny. Nie jest to bottleneck per-token SSD streaming ekspertów. PLE host timer obejmuje gather, enqueue i projekcje oraz może kumulować się między wywołaniami; nie jest osobnym pomiarem odczytu dysku; nie sumowano go z GPU wall.

18. **Q4 jako praktyczny model OpenCode vsIQ3_S** Zmierzono koszty read/reuse/longdecode/compaction Q4 i dwa kontrolne konteksty IQ3. Są to dane do wyboru modelu pod latency i RAM; wyższy bitrate nie dowodzi lepszej jakości. Odpowiedzi trzech identycznych qualitypromptów zapisano do ręcznego porównania. Nie orzekam, że Q4 jest jakościowo lepszy. Q4 jest używalny pod względem szybkości: final TG105.5 przy64K i95.0 przy256K, long decode81–86, kolejne agentic TTFT około4–5s oraz compaction57/71s przy128K/250K. IQ3 na v0.1.32 jest szybszy i oszczędniejszy: TG126.3/108.0 oraz PP5306.4/5623.0 przy64K/256K, RAM około59GiB zamiast82GiB Q4. Z samych wyników wydajności wybieram IQ3 dla latency i RAM; nie ma podstaw nazwać Q4 lepszym praktycznym modelem bez ręcznego porównania odpowiedzi. Q4128K agentic miał cztery krótkie odpowiedzi103/171/97/13; ostatnia zawierała tylko nagłówek. Przyczyna jest nierozstrzygnięta; nie przypisuję jej KV ani runtime. INT8 też miał krótki stop235. IQ3 agentic nie był ponownie testowany, więc nie ma kontrolnego dowodu jego większej niezawodności.

19. **Finalny configQ4** configs/production-Q4.json, defaultbuildv0.1.32, fullRAMarena, obie4090, K=24, prefill=16384, KV=k8v4, spec=3, workers=12, pcie=0.28, min-p=0.3. Wszystkie envoptins i pełne args w configu. Wyboru produkcyjnego nie nazywam jakościowo równoważnym do innych KV bez ręcznego przeczytania savedquality.

20. **Finalny configIQ3_S** configs/production-IQ3_S.json zachowuje poprzedni najlepszy config i istniejące modele/MTP; zmienia runtime do osobnego v0.1.32. Wykonano tylko64K×3 i256K×3. Auto wybrało K=25 w obu wersjach; pełne args/profile/MTP/tokenizer/GPU są identyczne. Prompty mają różne nonce i nie są paired payloads; nie robiono nowego pełnego tuningu IQ3.

## Finalna macierz actualcontext

RAM/VRAM to mediana requestowych peaków, MTP accept to mediana normal accepted/offered. Trzy runy/wiersz.

| Actual prompt | PP tok/s | TG tok/s | TTFT s | RAM GiB | VRAM0 GiB | VRAM1 GiB | MTP accept % |
|---|---|---|---|---|---|---|---|
| 31400.00 | 3446.00 | 108.20 | 9.20 | 81.84 | 23.29 | 23.48 | 67.30 |
| 63400.00 | 4474.90 | 105.50 | 14.32 | 82.08 | 23.30 | 23.49 | 66.06 |
| 127000.00 | 4964.60 | 106.60 | 25.85 | 82.51 | 23.30 | 23.49 | 74.00 |
| 259500.00 | 5570.50 | 95.00 | 47.10 | 82.75 | 23.30 | 23.49 | 66.82 |

## Porównanie upgrade

| Metric | v0.1.31 | v0.1.32 | Delta % | Classification |
|---|---|---|---|---|
| Q4 single GPU resident64K PP | 1539.30 | 1518.30 | -1.36 | NOT_CONTROLLED_A_B |
| Q4 single GPU resident64K TG | 43.40 | 40.90 | -5.76 | NOT_CONTROLLED_A_B |
| Q4 best2GPU actual63400 PP | 2793.20 | 4474.90 | 60.21 | NOT_CONTROLLED_A_B |
| Q4 best2GPU actual63400 TG | 98.70 | 105.50 | 6.89 | NOT_CONTROLLED_A_B |
| Q4 best2GPU actual127000 PP | 2956.70 | 4964.60 | 67.91 | NOT_CONTROLLED_A_B |
| Q4 best2GPU actual127000 TG | 86.90 | 106.60 | 22.67 | NOT_CONTROLLED_A_B |
| Q4 best2GPU actual259500 PP | 3196.60 | 5570.50 | 74.26 | NOT_CONTROLLED_A_B |
| Q4 best2GPU actual259500 TG | 92.10 | 95.00 | 3.15 | NOT_CONTROLLED_A_B |
| Controlled sameK24 actual8000 PP | 1519.75 | 1570.90 | 3.37 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual8000 TG | 105.45 | 95.95 | -9.01 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual16000 PP | 2089.55 | 2156.85 | 3.22 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual16000 TG | 102.80 | 89.80 | -12.65 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual31400 PP | 2546.60 | 2614.90 | 2.68 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual31400 TG | 106.70 | 120.70 | 13.12 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual63400 PP | 3004.00 | 3045.00 | 1.36 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual63400 TG | 92.40 | 106.40 | 15.15 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual127000 PP | 3271.70 | 3296.50 | 0.76 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual127000 TG | 87.30 | 101.10 | 15.81 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual259500 PP | 3508.70 | 3521.30 | 0.36 | CONTROLLED_WHOLE_VERSION_A_B |
| Controlled sameK24 actual259500 TG | 91.70 | 87.50 | -4.58 | CONTROLLED_WHOLE_VERSION_A_B |
| Cold start processREADY single-resident | 104.05 | 137.09 | 31.75 | NOT_CONTROLLED_A_B |
| Cold start processREADY best2GPU | 64.07 | 101.08 | 57.76 | NOT_CONTROLLED_A_B |
| Compaction actual127000 wall s | 61.34 | 56.70 | -7.56 | NOT_CONTROLLED_A_B |
| Compaction actual127000 PP | 3003.50 | 3722.20 | 23.93 | NOT_CONTROLLED_A_B |
| Compaction actual127000 TG | 92.30 | 91.40 | -0.98 | NOT_CONTROLLED_A_B |
| Compaction actual127000 TTFT s | 42.61 | 34.70 | -18.55 | NOT_CONTROLLED_A_B |
| Compaction actual250000 wall s | 109.25 | 71.45 | -34.60 | NOT_CONTROLLED_A_B |
| Compaction actual250000 PP | 3180.60 | 5335.40 | 67.75 | NOT_CONTROLLED_A_B |
| Compaction actual250000 TG | 89.00 | 92.30 | 3.71 | NOT_CONTROLLED_A_B |
| Compaction actual250000 TTFT s | 79.10 | 47.43 | -40.04 | NOT_CONTROLLED_A_B |

Pełne konfiguracje, raw paths i ograniczenia kontroli w comparison-upgrade.json/.csv.

## Agentic start63400

| Turn | Total ctx | Reused | New PP tokens | TTFT s | PP tok/s | TG tok/s | Wall s |
|---|---|---|---|---|---|---|---|
| 0.00 | 63400.00 | 0.00 | 63400.00 | 21.54 | 2983.50 | 83.70 | 33.75 |
| 1.00 | 65087.00 | 63393.00 | 1694.00 | 4.54 | 399.50 | 82.20 | 16.98 |
| 2.00 | 67123.00 | 65080.00 | 2043.00 | 4.87 | 447.00 | 84.80 | 15.92 |
| 3.00 | 69574.00 | 68060.00 | 1514.00 | 4.84 | 335.30 | 84.30 | 13.47 |
| 4.00 | 72216.00 | 70302.00 | 1914.00 | 4.98 | 411.40 | 88.40 | 9.80 |
| 5.00 | 73307.00 | 72643.00 | 664.00 | 3.19 | 233.30 | 86.00 | 9.36 |
| 6.00 | 74851.00 | 73838.00 | 1013.00 | 3.68 | 304.90 | 86.80 | 9.82 |
| 7.00 | 76899.00 | 75385.00 | 1514.00 | 4.92 | 331.20 | 84.70 | 11.73 |
| 8.00 | 79390.00 | 77477.00 | 1913.00 | 5.25 | 393.00 | 82.60 | 11.26 |
| 9.00 | 80552.00 | 79889.00 | 663.00 | 3.24 | 231.70 | 82.10 | 8.80 |
| 10.00 | 82023.00 | 81010.00 | 1013.00 | 3.86 | 292.40 | 83.90 | 10.08 |

## Agentic start127000

| Turn | Total ctx | Reused | New PP tokens | TTFT s | PP tok/s | TG tok/s | Wall s |
|---|---|---|---|---|---|---|---|
| 0.00 | 127000.00 | 0.00 | 127000.00 | 31.84 | 4020.40 | 86.20 | 43.71 |
| 1.00 | 128688.00 | 128023.00 | 665.00 | 3.10 | 234.70 | 88.30 | 14.68 |
| 2.00 | 130726.00 | 128681.00 | 2045.00 | 4.69 | 463.60 | 79.90 | 17.48 |
| 3.00 | 133263.00 | 131749.00 | 1514.00 | 4.56 | 353.70 | 82.60 | 16.83 |
| 4.00 | 136191.00 | 134277.00 | 1914.00 | 4.76 | 429.90 | 86.20 | 16.62 |
| 5.00 | 137879.00 | 137214.00 | 665.00 | 3.25 | 225.00 | 85.30 | 12.51 |
| 6.00 | 139683.00 | 138669.00 | 1014.00 | 3.66 | 304.10 | 92.90 | 4.75 |
| 7.00 | 141299.00 | 139785.00 | 1514.00 | 4.76 | 340.40 | 79.90 | 7.95 |
| 8.00 | 143468.00 | 141554.00 | 1914.00 | 5.28 | 414.50 | 88.90 | 7.19 |
| 9.00 | 144302.00 | 143638.00 | 664.00 | 3.09 | 239.20 | 102.40 | 4.02 |
| 10.00 | 145412.00 | 144398.00 | 1014.00 | 3.68 | 300.70 | 93.10 | 3.81 |

## Agentic negative output-length outcomes

| Startctx | Turn | Actual output | Minimum target | Finish |
|---|---|---|---|---|
| 127000.00 | 6.00 | 103.00 | 256.00 | stop |
| 127000.00 | 8.00 | 171.00 | 256.00 | stop |
| 127000.00 | 9.00 | 97.00 | 256.00 | stop |
| 127000.00 | 10.00 | 13.00 | 256.00 | stop |

All turns continued in the same engine; these rows do not satisfy256 minimum and are not relabelled as full-output success.

## Quality / parity / needle

BezLLMjudge, bez rankingu jakości. Fullresponses+SHA256+textdiff w quality/<variant>/; źródłowe exactAPIpayloads w quality/requests/ i source-manifest.json.

| Variant | Status | Text identical to reference | Output tokens |
|---|---|---|---|
| v0132-resident-default | COMPLETE | 0.00 | 569 / 1561 / 3322 |
| v0132-layer-default | COMPLETE | 0.00 | 474 / 1775 / 2420 |
| v0132-layer-own | COMPLETE | 0.00 | 586 / 1544 / 2204 |
| v0132-layer-no-borrow | COMPLETE | 0.00 | 585 / 1809 / 2482 |
| v0132-layer-rotated-int8 | COMPLETE | 0.00 | 473 / 1680 / 2288 |
| v0132-layer-k8v4 | COMPLETE | 0.00 | 556 / 1753 / 3212 |
| v0132-layer-q4_0 | COMPLETE | 0.00 | 580 / 2262 / 2706 |
| v0132-final | COMPLETE | 0.00 | 560 / 2130 / 2611 |

Upstreamneedle: seed7, te same words/depths/question/greedy40, tokenizer-sizing zamiast characterestimate. Found jest mechanicznym kryterium upstreamu.

| Actualctx | Depth % | Found | Answer |
|---|---|---|---|
| 31400.00 | 10.00 | YES | meadow-copper-504 |
| 31400.00 | 50.00 | YES | falcon-quartz-940 |
| 31400.00 | 90.00 | YES | willow-cobalt-696 |
| 127000.00 | 10.00 | YES | falcon-saffron-138 |
| 127000.00 | 50.00 | YES | quartz-tundra-528 |
| 127000.00 | 90.00 | YES | quartz-glacier-192 |
| 259500.00 | 10.00 | YES | tundra-falcon-946 |
| 259500.00 | 50.00 | YES | willow-glacier-745 |
| 259500.00 | 90.00 | YES | falcon-juniper-150 |

## Normal timing evidence

Request-local decode summaries; per-stage lines mogą być cumulative i nie są tu przedstawiane jako perrequestcost.
```text
strata decode timing: 115 windows, avg T 2.90, 2.23 tokens/window, 24.67 ms/window = verify 22.36 (GPU-reach wait 6.58 + per-layer host 3.56 [plan 0.08 actq 0.55 jobs 0.24 CPU 5.68] + stage 1.73) + commit/emit 0.60 + draft 1.69; per layer-window: CPU experts 1.04 (1.13 entries), VRAM hits 27.82, PCIe 0.09
strata decode timing: 108 windows, avg T 2.85, 2.37 tokens/window, 22.23 ms/window = verify 20.03 (GPU-reach wait 6.88 + per-layer host 2.19 [plan 0.07 actq 0.37 jobs 0.17 CPU 3.55] + stage 1.23) + commit/emit 0.52 + draft 1.66; per layer-window: CPU experts 0.99 (1.06 entries), VRAM hits 27.39, PCIe 0.08
strata decode timing: 106 windows, avg T 2.87, 2.42 tokens/window, 22.16 ms/window = verify 19.98 (GPU-reach wait 6.96 + per-layer host 2.50 [plan 0.07 actq 0.38 jobs 0.17 CPU 3.77] + stage 0.84) + commit/emit 0.52 + draft 1.65; per layer-window: CPU experts 1.08 (1.18 entries), VRAM hits 27.38, PCIe 0.12
strata decode timing: 112 windows, avg T 2.93, 2.29 tokens/window, 24.26 ms/window = verify 22.01 (GPU-reach wait 7.26 + per-layer host 2.91 [plan 0.09 actq 0.36 jobs 0.20 CPU 4.47] + stage 1.37) + commit/emit 0.55 + draft 1.68; per layer-window: CPU experts 1.09 (1.23 entries), VRAM hits 27.94, PCIe 0.11
strata decode timing: 108 windows, avg T 2.94, 2.37 tokens/window, 23.78 ms/window = verify 21.57 (GPU-reach wait 7.48 + per-layer host 2.73 [plan 0.07 actq 0.40 jobs 0.18 CPU 4.07] + stage 1.04) + commit/emit 0.52 + draft 1.68; per layer-window: CPU experts 1.20 (1.35 entries), VRAM hits 27.97, PCIe 0.13
strata decode timing: 115 windows, avg T 2.86, 2.23 tokens/window, 23.43 ms/window = verify 21.24 (GPU-reach wait 7.40 + per-layer host 2.24 [plan 0.09 actq 0.37 jobs 0.20 CPU 3.48] + stage 1.21) + commit/emit 0.52 + draft 1.66; per layer-window: CPU experts 0.93 (1.03 entries), VRAM hits 27.52, PCIe 0.06
strata decode timing: 107 windows, avg T 2.90, 2.39 tokens/window, 21.44 ms/window = verify 19.24 (GPU-reach wait 6.13 + per-layer host 2.80 [plan 0.08 actq 0.38 jobs 0.19 CPU 4.11] + stage 1.32) + commit/emit 0.53 + draft 1.66; per layer-window: CPU experts 1.27 (1.41 entries), VRAM hits 27.43, PCIe 0.13
strata decode timing: 115 windows, avg T 2.83, 2.23 tokens/window, 20.57 ms/window = verify 18.42 (GPU-reach wait 6.06 + per-layer host 2.49 [plan 0.06 actq 0.38 jobs 0.18 CPU 3.54] + stage 1.21) + commit/emit 0.51 + draft 1.64; per layer-window: CPU experts 1.11 (1.24 entries), VRAM hits 27.02, PCIe 0.09
strata decode timing: 115 windows, avg T 2.85, 2.23 tokens/window, 21.47 ms/window = verify 19.24 (GPU-reach wait 6.04 + per-layer host 2.66 [plan 0.08 actq 0.60 jobs 0.25 CPU 3.68] + stage 1.54) + commit/emit 0.56 + draft 1.65; per layer-window: CPU experts 0.96 (1.06 entries), VRAM hits 27.37, PCIe 0.09
strata decode timing: 114 windows, avg T 2.91, 2.25 tokens/window, 22.75 ms/window = verify 20.56 (GPU-reach wait 6.46 + per-layer host 2.80 [plan 0.07 actq 0.39 jobs 0.18 CPU 4.40] + stage 1.64) + commit/emit 0.52 + draft 1.67; per layer-window: CPU experts 1.29 (1.50 entries), VRAM hits 27.46, PCIe 0.16
strata decode timing: 108 windows, avg T 2.93, 2.37 tokens/window, 22.47 ms/window = verify 20.21 (GPU-reach wait 6.37 + per-layer host 2.65 [plan 0.10 actq 0.55 jobs 0.23 CPU 3.69] + stage 1.95) + commit/emit 0.56 + draft 1.68; per layer-window: CPU experts 0.87 (0.98 entries), VRAM hits 28.21, PCIe 0.07
strata decode timing: 118 windows, avg T 2.85, 2.17 tokens/window, 20.56 ms/window = verify 18.39 (GPU-reach wait 6.54 + per-layer host 1.67 [plan 0.06 actq 0.38 jobs 0.15 CPU 2.37] + stage 1.36) + commit/emit 0.50 + draft 1.66; per layer-window: CPU experts 0.68 (0.73 entries), VRAM hits 27.70, PCIe 0.05
```

Osobne diagnostyczne128/256K prefille (nieperformancewinners):
```text
strata prefill timing: 16384 tokens, GPU timeline 2445 ms, wall 2487 ms, host staging 383 ms: embed+steps 50 (2.1%) hc read 181 (7.4%) gdn 161 (6.6%) qsa proj 99 (4.0%) qsa indexer 0 (0.0%) qsa select 23 (0.9%) qsa attn 212 (8.7%) router+shared 40 (1.6%) host grouping 41 (1.7%) gather 40 (1.6%) wait copy 184 (7.5%) dequant 283 (11.6%) gemm gate/up 450 (18.4%) gemm down 271 (11.1%) combine 103 (4.2%) gdn conv+gates 39 (1.6%) gdn recurrence 174 (7.1%) gdn out proj 97 (4.0%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 9 ms, after each chunk (the draft layer, progress) 42 ms, PLE 0 ms
strata prefill timing: 16384 tokens, GPU timeline 2449 ms, wall 2505 ms, host staging 401 ms: embed+steps 50 (2.0%) hc read 181 (7.4%) gdn 160 (6.5%) qsa proj 99 (4.0%) qsa indexer 0 (0.0%) qsa select 46 (1.9%) qsa attn 225 (9.2%) router+shared 39 (1.6%) host grouping 31 (1.3%) gather 42 (1.7%) wait copy 161 (6.6%) dequant 284 (11.6%) gemm gate/up 450 (18.4%) gemm down 269 (11.0%) combine 103 (4.2%) gdn conv+gates 38 (1.6%) gdn recurrence 173 (7.1%) gdn out proj 97 (3.9%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 8 ms, after each chunk (the draft layer, progress) 55 ms, PLE 0 ms
strata prefill timing: 16384 tokens, GPU timeline 2454 ms, wall 2511 ms, host staging 420 ms: embed+steps 50 (2.0%) hc read 181 (7.4%) gdn 160 (6.5%) qsa proj 99 (4.0%) qsa indexer 0 (0.0%) qsa select 79 (3.2%) qsa attn 225 (9.2%) router+shared 39 (1.6%) host grouping 21 (0.8%) gather 39 (1.6%) wait copy 150 (6.1%) dequant 283 (11.5%) gemm gate/up 447 (18.2%) gemm down 268 (10.9%) combine 103 (4.2%) gdn conv+gates 39 (1.6%) gdn recurrence 173 (7.1%) gdn out proj 97 (3.9%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 8 ms, after each chunk (the draft layer, progress) 57 ms, PLE 0 ms
strata prefill timing: 16384 tokens, GPU timeline 2480 ms, wall 2539 ms, host staging 439 ms: embed+steps 50 (2.0%) hc read 181 (7.3%) gdn 160 (6.5%) qsa proj 99 (4.0%) qsa indexer 0 (0.0%) qsa select 110 (4.4%) qsa attn 225 (9.1%) router+shared 39 (1.6%) host grouping 24 (1.0%) gather 39 (1.6%) wait copy 141 (5.7%) dequant 284 (11.4%) gemm gate/up 447 (18.0%) gemm down 270 (10.9%) combine 103 (4.1%) gdn conv+gates 38 (1.6%) gdn recurrence 173 (7.0%) gdn out proj 97 (3.9%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 8 ms, after each chunk (the draft layer, progress) 59 ms, PLE 0 ms
strata prefill timing: 16384 tokens, GPU timeline 2504 ms, wall 2567 ms, host staging 459 ms: embed+steps 50 (2.0%) hc read 180 (7.2%) gdn 160 (6.4%) qsa proj 99 (4.0%) qsa indexer 0 (0.0%) qsa select 140 (5.6%) qsa attn 226 (9.0%) router+shared 39 (1.6%) host grouping 27 (1.1%) gather 40 (1.6%) wait copy 138 (5.5%) dequant 282 (11.3%) gemm gate/up 444 (17.7%) gemm down 268 (10.7%) combine 103 (4.1%) gdn conv+gates 39 (1.5%) gdn recurrence 173 (6.9%) gdn out proj 97 (3.9%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 11 ms, after each chunk (the draft layer, progress) 60 ms, PLE 0 ms
strata prefill timing: 16384 tokens, GPU timeline 2530 ms, wall 2681 ms, host staging 478 ms: embed+steps 50 (2.0%) hc read 180 (7.1%) gdn 160 (6.3%) qsa proj 99 (3.9%) qsa indexer 0 (0.0%) qsa select 170 (6.7%) qsa attn 226 (8.9%) router+shared 39 (1.6%) host grouping 21 (0.8%) gather 39 (1.6%) wait copy 147 (5.8%) dequant 279 (11.0%) gemm gate/up 443 (17.5%) gemm down 265 (10.5%) combine 103 (4.1%) gdn conv+gates 38 (1.5%) gdn recurrence 173 (6.8%) gdn out proj 97 (3.8%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 11 ms, after each chunk (the draft layer, progress) 149 ms, PLE 0 ms
strata prefill timing: 16384 tokens, GPU timeline 2570 ms, wall 2942 ms, host staging 498 ms: embed+steps 50 (2.0%) hc read 180 (7.0%) gdn 160 (6.2%) qsa proj 99 (3.8%) qsa indexer 0 (0.0%) qsa select 199 (7.8%) qsa attn 226 (8.8%) router+shared 39 (1.5%) host grouping 39 (1.5%) gather 39 (1.5%) wait copy 140 (5.4%) dequant 279 (10.9%) gemm gate/up 443 (17.2%) gemm down 265 (10.3%) combine 103 (4.0%) gdn conv+gates 39 (1.5%) gdn recurrence 173 (6.7%) gdn out proj 97 (3.8%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 9 ms, after each chunk (the draft layer, progress) 372 ms, PLE 0 ms
strata prefill timing: 12305 tokens, GPU timeline 2434 ms, wall 2679 ms, host staging 516 ms: embed+steps 38 (1.5%) hc read 135 (5.5%) gdn 125 (5.1%) qsa proj 77 (3.2%) qsa indexer 0 (0.0%) qsa select 168 (6.9%) qsa attn 170 (7.0%) router+shared 31 (1.3%) host grouping 13 (0.5%) gather 28 (1.2%) wait copy 408 (16.8%) dequant 281 (11.6%) gemm gate/up 395 (16.2%) gemm down 254 (10.4%) combine 77 (3.2%) gdn conv+gates 29 (1.2%) gdn recurrence 130 (5.3%) gdn out proj 75 (3.1%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 8 ms, after each chunk (the draft layer, progress) 245 ms, PLE 0 ms
strata prefill timing: 126993 tokens, GPU timeline 20233 ms, wall 23591 ms, host staging 508 ms: embed+steps 1092 (5.4%) hc read 1404 (6.9%) gdn 1254 (6.2%) qsa proj 771 (3.8%) qsa indexer 1 (0.0%) qsa select 943 (4.7%) qsa attn 1742 (8.6%) router+shared 307 (1.5%) host grouping 340 (1.7%) gather 306 (1.5%) wait copy 880 (4.4%) dequant 2255 (11.1%) gemm gate/up 3509 (17.3%) gemm down 2101 (10.4%) combine 793 (3.9%) ple 134 (0.7%) gdn conv+gates 298 (1.5%) gdn recurrence 1348 (6.7%) gdn out proj 753 (3.7%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 225 ms, waiting for each chunk 0 ms, after each chunk (the draft layer, progress) 0 ms, PLE 30289 ms
strata prefill timing: 16384 tokens, GPU timeline 2442 ms, wall 2494 ms, host staging 882 ms: embed+steps 50 (2.1%) hc read 181 (7.4%) gdn 161 (6.6%) qsa proj 99 (4.1%) qsa indexer 0 (0.0%) qsa select 23 (0.9%) qsa attn 212 (8.7%) router+shared 40 (1.6%) host grouping 31 (1.3%) gather 40 (1.6%) wait copy 192 (7.9%) dequant 284 (11.6%) gemm gate/up 448 (18.3%) gemm down 271 (11.1%) combine 103 (4.2%) gdn conv+gates 39 (1.6%) gdn recurrence 174 (7.1%) gdn out proj 97 (4.0%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 8 ms, after each chunk (the draft layer, progress) 52 ms, PLE 0 ms
strata prefill timing: 16384 tokens, GPU timeline 2446 ms, wall 2502 ms, host staging 903 ms: embed+steps 50 (2.0%) hc read 181 (7.4%) gdn 160 (6.6%) qsa proj 99 (4.1%) qsa indexer 0 (0.0%) qsa select 46 (1.9%) qsa attn 225 (9.2%) router+shared 39 (1.6%) host grouping 23 (0.9%) gather 39 (1.6%) wait copy 167 (6.8%) dequant 285 (11.6%) gemm gate/up 448 (18.3%) gemm down 271 (11.1%) combine 103 (4.2%) gdn conv+gates 38 (1.6%) gdn recurrence 173 (7.1%) gdn out proj 97 (4.0%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 7 ms, after each chunk (the draft layer, progress) 55 ms, PLE 0 ms
strata prefill timing: 16384 tokens, GPU timeline 2458 ms, wall 2517 ms, host staging 924 ms: embed+steps 50 (2.0%) hc read 181 (7.4%) gdn 160 (6.5%) qsa proj 99 (4.0%) qsa indexer 0 (0.0%) qsa select 80 (3.2%) qsa attn 225 (9.2%) router+shared 39 (1.6%) host grouping 27 (1.1%) gather 39 (1.6%) wait copy 147 (6.0%) dequant 283 (11.5%) gemm gate/up 447 (18.2%) gemm down 268 (10.9%) combine 103 (4.2%) gdn conv+gates 38 (1.6%) gdn recurrence 173 (7.0%) gdn out proj 97 (3.9%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 8 ms, after each chunk (the draft layer, progress) 59 ms, PLE 0 ms
strata prefill timing: 16384 tokens, GPU timeline 2481 ms, wall 2539 ms, host staging 943 ms: embed+steps 50 (2.0%) hc read 181 (7.3%) gdn 160 (6.5%) qsa proj 99 (4.0%) qsa indexer 0 (0.0%) qsa select 110 (4.4%) qsa attn 226 (9.1%) router+shared 39 (1.6%) host grouping 22 (0.9%) gather 39 (1.6%) wait copy 139 (5.6%) dequant 285 (11.5%) gemm gate/up 448 (18.0%) gemm down 271 (10.9%) combine 103 (4.1%) gdn conv+gates 38 (1.6%) gdn recurrence 173 (7.0%) gdn out proj 97 (3.9%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 8 ms, after each chunk (the draft layer, progress) 58 ms, PLE 0 ms
strata prefill timing: 16384 tokens, GPU timeline 2504 ms, wall 2562 ms, host staging 965 ms: embed+steps 50 (2.0%) hc read 181 (7.2%) gdn 160 (6.4%) qsa proj 99 (4.0%) qsa indexer 0 (0.0%) qsa select 140 (5.6%) qsa attn 226 (9.0%) router+shared 39 (1.6%) host grouping 22 (0.9%) gather 40 (1.6%) wait copy 141 (5.6%) dequant 282 (11.3%) gemm gate/up 444 (17.7%) gemm down 267 (10.7%) combine 103 (4.1%) gdn conv+gates 38 (1.5%) gdn recurrence 173 (6.9%) gdn out proj 97 (3.9%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 9 ms, after each chunk (the draft layer, progress) 58 ms, PLE 0 ms
strata prefill timing: 16384 tokens, GPU timeline 2532 ms, wall 2584 ms, host staging 987 ms: embed+steps 50 (2.0%) hc read 180 (7.1%) gdn 160 (6.3%) qsa proj 99 (3.9%) qsa indexer 0 (0.0%) qsa select 170 (6.7%) qsa attn 226 (8.9%) router+shared 39 (1.6%) host grouping 28 (1.1%) gather 39 (1.6%) wait copy 140 (5.5%) dequant 280 (11.1%) gemm gate/up 444 (17.5%) gemm down 265 (10.5%) combine 103 (4.1%) gdn conv+gates 39 (1.5%) gdn recurrence 173 (6.8%) gdn out proj 97 (3.8%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 7 ms, after each chunk (the draft layer, progress) 52 ms, PLE 0 ms
strata prefill timing: 16384 tokens, GPU timeline 2564 ms, wall 2634 ms, host staging 1008 ms: embed+steps 50 (2.0%) hc read 180 (7.0%) gdn 160 (6.3%) qsa proj 99 (3.9%) qsa indexer 0 (0.0%) qsa select 200 (7.8%) qsa attn 226 (8.8%) router+shared 39 (1.5%) host grouping 33 (1.3%) gather 39 (1.5%) wait copy 139 (5.4%) dequant 280 (10.9%) gemm gate/up 442 (17.3%) gemm down 264 (10.3%) combine 103 (4.0%) gdn conv+gates 39 (1.5%) gdn recurrence 173 (6.8%) gdn out proj 97 (3.8%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 12 ms, after each chunk (the draft layer, progress) 67 ms, PLE 0 ms
strata prefill timing: 16384 tokens, GPU timeline 2585 ms, wall 2655 ms, host staging 1032 ms: embed+steps 50 (1.9%) hc read 180 (7.0%) gdn 160 (6.2%) qsa proj 99 (3.8%) qsa indexer 0 (0.0%) qsa select 227 (8.8%) qsa attn 226 (8.7%) router+shared 39 (1.5%) host grouping 21 (0.8%) gather 39 (1.5%) wait copy 140 (5.4%) dequant 281 (10.9%) gemm gate/up 444 (17.2%) gemm down 266 (10.3%) combine 103 (4.0%) gdn conv+gates 38 (1.5%) gdn recurrence 173 (6.7%) gdn out proj 97 (3.7%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 7 ms, after each chunk (the draft layer, progress) 70 ms, PLE 0 ms
strata prefill timing: 16384 tokens, GPU timeline 2635 ms, wall 2705 ms, host staging 1052 ms: embed+steps 50 (1.9%) hc read 180 (6.8%) gdn 160 (6.1%) qsa proj 99 (3.8%) qsa indexer 0 (0.0%) qsa select 256 (9.7%) qsa attn 227 (8.6%) router+shared 39 (1.5%) host grouping 36 (1.4%) gather 39 (1.5%) wait copy 147 (5.6%) dequant 279 (10.6%) gemm gate/up 445 (16.9%) gemm down 265 (10.1%) combine 103 (3.9%) gdn conv+gates 39 (1.5%) gdn recurrence 173 (6.6%) gdn out proj 97 (3.7%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 12 ms, after each chunk (the draft layer, progress) 68 ms, PLE 0 ms
strata prefill timing: 16384 tokens, GPU timeline 2654 ms, wall 2721 ms, host staging 1074 ms: embed+steps 50 (1.9%) hc read 180 (6.8%) gdn 160 (6.0%) qsa proj 99 (3.7%) qsa indexer 0 (0.0%) qsa select 289 (10.9%) qsa attn 227 (8.6%) router+shared 39 (1.5%) host grouping 28 (1.1%) gather 39 (1.5%) wait copy 137 (5.2%) dequant 281 (10.6%) gemm gate/up 444 (16.7%) gemm down 267 (10.1%) combine 103 (3.9%) gdn conv+gates 38 (1.5%) gdn recurrence 173 (6.5%) gdn out proj 97 (3.6%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 6 ms, after each chunk (the draft layer, progress) 67 ms, PLE 0 ms
strata prefill timing: 16384 tokens, GPU timeline 2682 ms, wall 2741 ms, host staging 1095 ms: embed+steps 50 (1.9%) hc read 180 (6.7%) gdn 160 (6.0%) qsa proj 99 (3.7%) qsa indexer 0 (0.0%) qsa select 316 (11.8%) qsa attn 227 (8.5%) router+shared 39 (1.5%) host grouping 30 (1.1%) gather 39 (1.5%) wait copy 149 (5.5%) dequant 277 (10.3%) gemm gate/up 439 (16.4%) gemm down 263 (9.8%) combine 103 (3.8%) gdn conv+gates 38 (1.4%) gdn recurrence 173 (6.5%) gdn out proj 97 (3.6%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 11 ms, after each chunk (the draft layer, progress) 57 ms, PLE 0 ms
strata prefill timing: 16384 tokens, GPU timeline 2710 ms, wall 2781 ms, host staging 1117 ms: embed+steps 50 (1.8%) hc read 180 (6.7%) gdn 160 (5.9%) qsa proj 99 (3.6%) qsa indexer 0 (0.0%) qsa select 348 (12.8%) qsa attn 227 (8.4%) router+shared 39 (1.5%) host grouping 31 (1.1%) gather 39 (1.5%) wait copy 138 (5.1%) dequant 279 (10.3%) gemm gate/up 444 (16.4%) gemm down 265 (9.8%) combine 103 (3.8%) gdn conv+gates 39 (1.4%) gdn recurrence 173 (6.4%) gdn out proj 97 (3.6%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 9 ms, after each chunk (the draft layer, progress) 70 ms, PLE 0 ms
strata prefill timing: 16384 tokens, GPU timeline 2741 ms, wall 2818 ms, host staging 1136 ms: embed+steps 50 (1.8%) hc read 180 (6.6%) gdn 160 (5.9%) qsa proj 99 (3.6%) qsa indexer 0 (0.0%) qsa select 374 (13.6%) qsa attn 227 (8.3%) router+shared 39 (1.4%) host grouping 27 (1.0%) gather 39 (1.4%) wait copy 143 (5.2%) dequant 280 (10.2%) gemm gate/up 444 (16.2%) gemm down 266 (9.7%) combine 103 (3.7%) gdn conv+gates 39 (1.4%) gdn recurrence 173 (6.3%) gdn out proj 97 (3.5%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 11 ms, after each chunk (the draft layer, progress) 75 ms, PLE 0 ms
strata prefill timing: 16384 tokens, GPU timeline 2778 ms, wall 2895 ms, host staging 1158 ms: embed+steps 50 (1.8%) hc read 180 (6.5%) gdn 161 (5.8%) qsa proj 99 (3.6%) qsa indexer 0 (0.0%) qsa select 406 (14.6%) qsa attn 228 (8.2%) router+shared 39 (1.4%) host grouping 24 (0.9%) gather 39 (1.4%) wait copy 151 (5.4%) dequant 280 (10.1%) gemm gate/up 443 (15.9%) gemm down 266 (9.6%) combine 103 (3.7%) gdn conv+gates 39 (1.4%) gdn recurrence 173 (6.2%) gdn out proj 97 (3.5%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 2 ms, waiting for each chunk 11 ms, after each chunk (the draft layer, progress) 115 ms, PLE 0 ms
strata prefill timing: 16384 tokens, GPU timeline 2819 ms, wall 3179 ms, host staging 1177 ms: embed+steps 50 (1.8%) hc read 180 (6.4%) gdn 161 (5.7%) qsa proj 99 (3.5%) qsa indexer 0 (0.0%) qsa select 440 (15.6%) qsa attn 228 (8.1%) router+shared 39 (1.4%) host grouping 39 (1.4%) gather 39 (1.4%) wait copy 140 (5.0%) dequant 282 (10.0%) gemm gate/up 444 (15.8%) gemm down 266 (9.4%) combine 103 (3.6%) gdn conv+gates 38 (1.4%) gdn recurrence 173 (6.2%) gdn out proj 97 (3.4%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 10 ms, after each chunk (the draft layer, progress) 359 ms, PLE 0 ms
strata prefill timing: 13733 tokens, GPU timeline 2656 ms, wall 2931 ms, host staging 1195 ms: embed+steps 42 (1.6%) hc read 150 (5.6%) gdn 137 (5.2%) qsa proj 84 (3.2%) qsa indexer 0 (0.0%) qsa select 394 (14.8%) qsa attn 191 (7.2%) router+shared 34 (1.3%) host grouping 16 (0.6%) gather 32 (1.2%) wait copy 281 (10.6%) dequant 282 (10.6%) gemm gate/up 411 (15.5%) gemm down 256 (9.7%) combine 86 (3.2%) gdn conv+gates 32 (1.2%) gdn recurrence 145 (5.5%) gdn out proj 83 (3.1%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 0 ms, waiting for each chunk 9 ms, after each chunk (the draft layer, progress) 274 ms, PLE 0 ms
strata prefill timing: 259493 tokens, GPU timeline 42740 ms, wall 46329 ms, host staging 1157 ms: embed+steps 2114 (4.9%) hc read 2868 (6.7%) gdn 2560 (6.0%) qsa proj 1574 (3.7%) qsa indexer 3 (0.0%) qsa select 3848 (9.0%) qsa attn 3596 (8.4%) router+shared 627 (1.5%) host grouping 734 (1.7%) gather 622 (1.5%) wait copy 1524 (3.6%) dequant 4527 (10.6%) gemm gate/up 7100 (16.6%) gemm down 4246 (9.9%) combine 1620 (3.8%) ple 273 (0.6%) gdn conv+gates 610 (1.4%) gdn recurrence 2758 (6.5%) gdn out proj 1538 (3.6%)
strata prefill timing: host: chunk setup (PLE rows, the expert stream plan) 412 ms, waiting for each chunk 0 ms, after each chunk (the draft layer, progress) 0 ms, PLE 44521 ms
```

## Commands

Uruchamiaj modele pojedynczo. Configi zachowują przypięte localmodels i spec/KV/env; pokazane polecenia nie zostały automatycznie uruchomione jako serwer produkcyjny.
```bash
cd /srv/ai/strata-v0.1.32 && env -u STRATA_SPLIT_OWN -u STRATA_KV_ROT -u STRATA_REFILL_SERIAL -u STRATA_SPEC_COUPLED CUDA_VISIBLE_DEVICES=0,1 .venv/bin/python -m serve.server --engine strata --config /srv/ai/benchmarks/strata-qwen38/q4-v0132/configs/production-Q4.json --host 127.0.0.1 --port 8080
```

```bash
cd /srv/ai/strata-v0.1.32 && env -u STRATA_SPLIT_OWN -u STRATA_KV_ROT -u STRATA_REFILL_SERIAL -u STRATA_SPEC_COUPLED CUDA_VISIBLE_DEVICES=0,1 .venv/bin/python -m serve.server --engine strata --config /srv/ai/benchmarks/strata-qwen38/q4-v0132/configs/production-IQ3_S.json --host 127.0.0.1 --port 8080
```

## Limitations and review

Wykresy: plots/ (PNG/SVG i source-manifest). Summary.csv/json przechowują szczegółowe requesty; counters per-GPU expert share i fizyczneSSD są null gdy upstream/VM ich nie udostępnia. Nie użyto drop_caches. Coldstart=exec→healthREADY świeżego procesu, nie dowód fizycznie zimnego filesystemcache. Nie patchowano upstream ani wag, nie pobierano modeli ponownie, nie commitowano/pushowano.

Przegląd wizualny wszystkich21 wykresów, korekta odfiltrowania smoke/warmup na wykresie splitu oraz potwierdzenia TOP2 MTP: evidence/plots-visual-review.json. Pełne zakresy i niezależne audyty actualtokens/payloads/diffs/provenance: completion-audit.md i evidence/. Wyniki negatywne oraz unsupported są wynikami eksperymentów, nie deklaracją ich pomyślnego przejścia.

## Existing IQ3_S quality reference

Archivedoriginalanswers only; no newIQ3qualityrequest. Alloriginalrequest fields matchQ4 exceptmodelalias. Partialoldanswers are not used. SourceHEADassociation andcanonicalrawpaths are explicit in thearchive manifest; no retrospective metadata fabrication, qualityscore or ranking.

| Prompt | Actual output tokens | Existing IQ3answer | Literaldiff vs Q4final |
|---|---|---|---|
| A-coding-debug | 750.00 | /srv/ai/benchmarks/strata-qwen38/q4-v0132/quality/IQ3_S-v0131-existing/A-coding-debug.txt | /srv/ai/benchmarks/strata-qwen38/q4-v0132/quality/IQ3_S-v0131-existing/A-coding-debug-vs-Q4-v0132-final.diff |
| B-mathematical-reasoning | 1693.00 | /srv/ai/benchmarks/strata-qwen38/q4-v0132/quality/IQ3_S-v0131-existing/B-mathematical-reasoning.txt | /srv/ai/benchmarks/strata-qwen38/q4-v0132/quality/IQ3_S-v0131-existing/B-mathematical-reasoning-vs-Q4-v0132-final.diff |
| C-repository-architecture | 3488.00 | /srv/ai/benchmarks/strata-qwen38/q4-v0132/quality/IQ3_S-v0131-existing/C-repository-architecture.txt | /srv/ai/benchmarks/strata-qwen38/q4-v0132/quality/IQ3_S-v0131-existing/C-repository-architecture-vs-Q4-v0132-final.diff |

## Separate complete INT8 validation matrix

Eachcandidate has3actual requests percontext with256 output/greedy/no reuse. Independentnonces/cacheplacement/order: NOT_CONTROLLED_A_B. INT8agent64short235 prevents a claim of greater stability. This table does not change selectedK8V4 results.

| Actualprompt | K8V4 PP | INT8 PP | K8V4 TG | INT8 TG | K8V4 TTFT | INT8 TTFT |
|---|---|---|---|---|---|---|
| 31400.00 | 3446.00 | 3416.80 | 108.20 | 107.60 | 9.20 | 9.28 |
| 63400.00 | 4474.90 | 4429.60 | 105.50 | 109.80 | 14.32 | 14.46 |
| 127000.00 | 4964.60 | 5172.90 | 106.60 | 102.60 | 25.85 | 24.81 |
| 259500.00 | 5570.50 | 5609.60 | 95.00 | 97.30 | 47.10 | 46.79 |

## Separate final selection and retained candidates

```json
{
  "status": "SELECTED_FROM_VERIFIED_EVIDENCE",
  "created": 1790914242.48814,
  "matrix_label": "FINAL-v0132-Q4-attempt2",
  "config": "/srv/ai/benchmarks/strata-qwen38/q4-v0132/configs/FINAL-v0132-Q4.json",
  "long_summary": "/srv/ai/benchmarks/strata-qwen38/q4-v0132/raw/long-decode-done.json",
  "agent_labels": {
    "63400": "AGENT-63400-v0132",
    "127000": "AGENT-127000-v0132-natural-eos-session"
  },
  "phase_terminals": {
    "agent128": "/srv/ai/benchmarks/strata-qwen38/q4-v0132/raw/phase-agent128-natural-outcomes-terminal.json"
  },
  "accepted_phase_statuses": {
    "agent128": [
      "COMPLETE",
      "MEASURED_WITH_SHORT_TURNS"
    ]
  },
  "classification": "TESTED_K8V4_SPEED_FINALIST_WITH_NEGATIVE_LENGTH_OUTCOMES",
  "rationale": "K8V4 won confirmed speedselection and completed finalmatrix/long lengths. Full11-request128K lifecycle now measured, recording any below256 naturalEOS as negative outputlength outcomes without masking, suppression, or process restart. INT8 fullmatrix/long and agentdiagnostics preserved separately: agent64 short235; no proof of increased stability or quality. This selection is not a claim of universal correctness or suitability; literal qualityparity and downstreamworkloads remain required.",
  "controlled_AB": false,
  "agentic_output_minimum_met": false,
  "negative_output_outcomes": [
    {
      "raw": "/srv/ai/benchmarks/strata-qwen38/q4-v0132/raw/AGENT-127000-v0132-natural-eos-session-turn6.json",
      "turn": 6,
      "generated_tokens": 103,
      "status": "SHORT_OUTPUT_BELOW_REQUIRED256",
      "retained": true
    },
    {
      "raw": "/srv/ai/benchmarks/strata-qwen38/q4-v0132/raw/AGENT-127000-v0132-natural-eos-session-turn8.json",
      "turn": 8,
      "generated_tokens": 171,
      "status": "SHORT_OUTPUT_BELOW_REQUIRED256",
      "retained": true
    },
    {
      "raw": "/srv/ai/benchmarks/strata-qwen38/q4-v0132/raw/AGENT-127000-v0132-natural-eos-session-turn9.json",
      "turn": 9,
      "generated_tokens": 97,
      "status": "SHORT_OUTPUT_BELOW_REQUIRED256",
      "retained": true
    },
    {
      "raw": "/srv/ai/benchmarks/strata-qwen38/q4-v0132/raw/AGENT-127000-v0132-natural-eos-session-turn10.json",
      "turn": 10,
      "generated_tokens": 13,
      "status": "SHORT_OUTPUT_BELOW_REQUIRED256",
      "retained": true
    }
  ],
  "INT8_not_promoted": "/srv/ai/benchmarks/strata-qwen38/q4-v0132/evidence/int8-agent64-short-review.json",
  "retained_original_manifests": [
    "final-matrix-attempt.json",
    "agent-attempts.json"
  ],
  "evidence": [
    "/srv/ai/benchmarks/strata-qwen38/q4-v0132/evidence/final-matrix-progress-independent-audit.json",
    "/srv/ai/benchmarks/strata-qwen38/q4-v0132/evidence/long-progress-independent-audit.json",
    "/srv/ai/benchmarks/strata-qwen38/q4-v0132/evidence/agent-natural-outcomes-independent-audit.json",
    "/srv/ai/benchmarks/strata-qwen38/q4-v0132/evidence/int8-agent64-short-review.json"
  ]
}
```

K8V4 wybrano według potwierdzonej szybkości. Obie wcześniejsze niepełne sesje128K188/95 pozostają zachowane. Pełna sesja128K ma jawnie zapisane ewentualne krótkie tury, które nie spełniają minimum256. INT8 long8K6777 i agent64short235 pozostają osobno; nie dowodzą większej stabilności ani przyczynowości KV.

## Final matrix prompt policy and retained failure

Original FINAL-v0132-Q4 attempt stopped after read_file tool-call EOS at118 outputtokens in the first32K measured request. All original raw/log/telemetry files are preserved and excluded from the256-output final matrix. FINAL-v0132-Q4-attempt2 adds an explicit offline/no-tools instruction to the SYSTEM message; corpus, usertask, greedy sampling, requested lengths, unique nonces and tokenizer sizing are unchanged. No engine patch, tool-choice workaround or EOS suppression was used. Best-config old/new comparisons are NOT_CONTROLLED_A_B, including this prompt-policy difference. Exact old/new policies and config/script revisions: final-matrix-attempt.json and recovery/final-attempt1/. Quality requests and paired version controls remain literal originals.

## IQ3_S runtime upgrade controls

Previous CLI/profile/MTP/tokenizer/GPU configuration retained; actual auto K25 in both versions. n3 per row, actual256 generated, greedy, zero reuse. Different nonce prompts: not paired payload A/B.

| Actual prompt | v0131 PP | v0132 PP | v0131 TG | v0132 TG | v0132 TTFT s | v0132 RAM GiB |
|---|---|---|---|---|---|---|
| 63400.00 | 5438.70 | 5306.40 | 116.20 | 126.30 | 12.09 | 58.69 |
| 259500.00 | 5841.00 | 5623.00 | 109.40 | 108.00 | 46.66 | 59.25 |
