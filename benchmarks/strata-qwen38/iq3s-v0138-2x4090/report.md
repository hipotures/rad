# IQ3_S na Strata v0.1.38 — 2× RTX 4090

Zakończono 12 poprawnych pomiarów oraz 4 warmupy, po jednym dla każdego kontekstu. Wszystkie mierzone requesty wygenerowały 256 tokenów, miały reuse=0 i finish_reason=length. Nie wystąpiły OOM, crash ani niepoprawny stop. Nie zmieniono modelu ani upstreamowego engine; nie wykonano commitów ani pushów.

## Środowisko i konfiguracja

- Tag: v0.1.38; HEAD: `99f3dbd0b21d1401b3769e0c0d963913607f380b`. Checkout: `/srv/ai/strata-v0.1.38`; czysty git status przed i po kampanii.
- Osobny build Release, CUDA, sm_89. Standardowy build; opcjonalne kernela Q4 i tryby eksperymentalne wyłączone. Compiler, CUDA, driver, kernel, CPU, RAM, PCIe topology i pełny CMakeCache zapisano w environment.json oraz evidence/.
- Dwie RTX 4090, po 24 GiB; Ryzen 9 7950X3D, VM 16 vCPU, około 161 GiB RAM, bez swap.
- Model ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF, IQ3_S, rewizja `ed59f92082b1e93c0e96d60a8b11aab089b52f09`. Oba istniejące shardy SHA256 zgodne z oficjalnym manifestem LFS tej rewizji. Wykorzystano istniejący pack, bez pobierania modelu.
- Zachowano wcześniejszy production config: INT8 KV, `--kv-resident 32768`, `--spec 4`, `--spec-min-p 0.5`, `--prefill auto`, `--expert-cache auto`, stary expert profile i MTP. W szczególności KV nadal korzysta z wcześniejszego trybu streaming; nie przeprowadzono tuningu.
- `--layer-split auto`, obie GPU, max context 262144 w każdym punkcie. Brak wizji i experimental speed projection. Serwer benchmarkowy na localhost, port18085.

## Metodologia

Kod agentowy i korpus poprzedniego harnessu Straty. Greedy / temperature0, thinking off, 256 tokenów wyjścia. Każdy request ma unikalny nonce w system prompt oraz ten sam offline/no-tools policy. Liczba tokenów pochodzi z upstreamowego tokenizera z chat template i jest zgodna z usage API. Wszystkie requesty wykonywano sekwencyjnie.

Dla każdego kontekstu: 1 warmup wyłączony ze statystyki + 3 pomiary. PP/TG pochodzą z normalnych timingów engine, TTFT i wall time z zegara klienta. Telemetria RSS/CPU/RAM/GPU/power/PCIe około1Hz; PSS wyłącznie przed i po requestcie, poza mierzonym czasem. Próg abort MemAvailable12GiB. Brak drop_caches; audyt SHA256 i start mogą rozgrzać filesystem cache.

## Główna tabela — mediany z trzech pomiarów

| Actual prompt | PP tok/s | TG tok/s | TTFT s | MTP accept % | Hit rate % | Split K |
|---:|---:|---:|---:|---:|---:|---:|
| 31400 | 4597.4 | 101.8 | 6.977 | 74.29 | 99.40 | 25 |
| 63400 | 5437.3 | 122.6 | 11.809 | 68.49 | 99.40 | 25 |
| 127000 | 5707.1 | 120.5 | 22.503 | 73.89 | 99.40 | 25 |
| 259500 | 5688.5 | 114.7 | 46.115 | 72.25 | 99.50 | 25 |

## Zakres trzech pomiarów

| Actual prompt | PP min | PP mediana | PP max | TG min | TG mediana | TG max |
|---:|---:|---:|---:|---:|---:|---:|
| 31400 | 4591.7 | 4597.4 | 4661.9 | 96.1 | 101.8 | 137.9 |
| 63400 | 5395.8 | 5437.3 | 5437.5 | 118.1 | 122.6 | 126.3 |
| 127000 | 5695.0 | 5707.1 | 5710.6 | 118.3 | 120.5 | 130.3 |
| 259500 | 5688.3 | 5688.5 | 5700.7 | 110.3 | 114.7 | 119.8 |

Rozrzut TG przy32K jest duży:96,1–137,9tok/s. Nie wolno zastępować mediany najszybszą próbą. Unikalny nonce zmienia rzeczywisty prompt i potencjalnie odpowiedź oraz MTP acceptance.

## Eksperci i pamięć

Auto wybrało K=25: GPU0 warstwy0–24, GPU1 warstwy25–47. GPU0 ma10112slotów cache ekspertów (18,23GiB), GPU1 ma8376slotów (16,84GiB), łącznie18488 z24576par ekspertów, około75,2% liczby par. Slot oznacza parę gate/up/down jednego routed eksperta. Prefill tymczasowo pożycza część slotów na bufory; podane liczby są pojemnością cache ze startu, nie gauge chwilowego użycia podczas każdego chunka.

Peak RAM systemowy: 59.59GiB. Peak VRAM GPU0/GPU1: 23.29/23.42GiB. Model i pack zachowały size/mtime. Normalne liczniki decode wykazały 0 file blobs i 0 MB odczytów ekspertów we wszystkich12runach. Nie jest to dowód braku wszelkich odczytów fizycznego storage hosta: PLE i virtiofs są osobnymi mechanizmami.

## Obciążenie podczas decode

Tabela podaje medianę średnich z trzech runów. Systemowe CPU100% oznacza wszystkie16vCPU; process CPU100% oznacza jeden logiczny CPU i może przekraczać100%. Decode256 trwa około2–3s, więc faza ma tylko2–3próbki1Hz na run. Próbki przy granicy TTFT mogą obejmować fragment końca prefill. To orientacyjna telemetria, nie długotrwały test obciążenia.

| Actual prompt | CPU system mean % | CPU process mean % | GPU0 util % | GPU1 util % | GPU0 W | GPU1 W |
|---:|---:|---:|---:|---:|---:|---:|
| 31400 | 62.2 | 985.5 | 43.7 | 62.7 | 132.8 | 170.3 |
| 63400 | 49.8 | 791.8 | 31.5 | 73.5 | 132.2 | 183.3 |
| 127000 | 69.8 | 1109.8 | 41.0 | 51.0 | 146.1 | 174.6 |
| 259500 | 86.8 | 1384.7 | 42.0 | 49.5 | 162.3 | 183.2 |

CPU nadal bywa blisko pełnego obciążenia: największa zarejestrowana próbka systemowa 97.3%, a pojedyncze vCPU osiągały100%. Nie zaobserwowano systemowego100% w próbkach1Hz, co nie wyklucza krótkich peaków między próbkami.

PCIe RX/TX z nvidia-smi dmon zapisano w telemetry/IQ3S-v0138-pcie-dmon.log i przeliczono per request w raw JSON jako PCIe_aggregates. Dopasowanie faz jest przybliżone do±1s. To transfery GPU, nie licznik I/O konkretnych ekspertów.

## Porównanie ze starymi wynikami — NOT_CONTROLLED_A_B

Zweryfikowane raw v0.1.32 zawierają tylko64K i256K. Wartości32K i128K wcześniej opisywane jako0.1.32 pochodzą faktycznie z kampanii0.1.31. Poniżej są jawnie oznaczone. Nowe prompty/nonce oraz offline policy nie są identycznymi payloadami; nie jest to izolowane A/B samego runtime.

| Stara wersja | Actual prompt | Stare PP | Nowe PP | Delta PP % | Stare TG | Nowe TG | Delta TG % |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0.1.31 | 31400 | 4652.5 | 4597.4 | -1.18 | 131.2 | 101.8 | -22.41 |
| 0.1.32 | 63400 | 5306.4 | 5437.3 | +2.47 | 126.3 | 122.6 | -2.93 |
| 0.1.31 | 127000 | 5827.3 | 5707.1 | -2.06 | 114.9 | 120.5 | +4.87 |
| 0.1.32 | 259500 | 5623.0 | 5688.5 | +1.16 | 108.0 | 114.7 | +6.20 |

W dostępnych punktach0.1.32 PP wzrosło nieznacznie:64K +2,47%,256K +1,16%. TG przy64K spadło o2,93%, przy256K wzrosło o6,20%. Różnice promptów, acceptance i naturalny rozrzut nie pozwalają przypisać tych zmian wyłącznie aktualizacji runtime.

## Referencja1× RTX5090 — NOT_CONTROLLED_A_B

Użyto wskazanych przez użytkownika wartości referencyjnych170,4 i152,5tok/s. Nie zweryfikowano niezależnie ich opublikowanych raw requestów. To inna maszyna i potencjalnie inny config; procenty są tylko porównaniem liczbowym, nie czystym A/B sprzętu.

| Actual prompt | 1×5090 TG referencyjne | 2×4090 TG mediana | Różnica % |
|---:|---:|---:|---:|
| 31400 | 170.4 | 101.8 | -40.26 |
| 259500 | 152.5 | 114.7 | -24.79 |

## Weryfikacja i artefakty

- 12/12 poprawnych measured requests, 4 warmupy wyłączone ze statystyk. Brak invalid/negative requests.
- Niezależny audyt payloadów, usage, stop reason, nonców, command/config/provenance i logów: evidence/independent-final-audit.json.
- Każdy raw result zawiera HEAD, version, build variant, model revision, pełną komendę/config, actual tokens, metryki i ścieżkę telemetrii. Prompty, pełne odpowiedzi, SSE chunks, status, metrics i log engine zachowane w raw/.
- summary.csv: mediany oraz pełne zakresy. summary.json: podsumowania, wszystkie12raw results, CPU/GPU/power/PCIe, porównania i audyt.
- Po kampanii serwer zatrzymano, obie GPU są wolne. Checkout0.1.38 pozostał czysty, starszych checkoutów/wyników nie nadpisano.
