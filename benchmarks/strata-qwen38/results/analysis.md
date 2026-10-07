# Interpretacja telemetrii

Dane dotyczą IQ3_S. Q4 nie uruchamia się w wymaganej konfiguracji resident RAM + multi-GPU; brak pomiarów Q4 nie jest pomiarem zerowej wydajności.

## CPU/GPU/PCIe

Runtime wybrał split 25/23. Probe host→device: 13.4 GB/s na każdej GPU. Bieżąca szerokość linku z NVML wynosi x8, generacja 4 pod obciążeniem (maksymalna raportowana szerokość urządzenia: x16). NVML z serwera agreguje RX/TX obu kart; tych wartości nie należy przypisywać jednej GPU.

| ctx | phase | samples | system CPU % | process CPU % | GPU0 util % | GPU1 util % | PCIe RX mean MiB/s | PCIe RX max MiB/s |
|---|---|---|---|---|---|---|---|---|
| 32K | reading | 18 | 6.8 | 100.3 | 63.9 | 84.4 | 18457.2 | 27671.9 |
| 32K | generating | 6 | 58.5 | 931.9 | 34.2 | 59.5 | 9257.7 | 27435.8 |
| 64K | reading | 41 | 7.5 | 102.6 | 58.0 | 72.6 | 13198.5 | 27631.0 |
| 64K | generating | 6 | 58.0 | 922.3 | 33.0 | 56.0 | 4717.0 | 13723.2 |
| 128K | reading | 73 | 9.3 | 122.1 | 69.0 | 81.7 | 15467.6 | 29221.2 |
| 128K | generating | 9 | 66.4 | 1057.4 | 36.3 | 61.4 | 5029.8 | 13744.3 |
| 256K | reading | 145 | 12.5 | 157.7 | 80.0 | 85.6 | 16607.2 | 28098.2 |
| 256K | generating | 8 | 66.7 | 1062.6 | 33.5 | 56.1 | 2181.1 | 13730.5 |

Prefill: CPU średnio około 7–13% całej VM, GPU aktywne, silny strumień PCIe i wysokie piki RX. Wskazuje to na ścieżkę GPU + transfery ekspertów po PCIe; CPU nie wygląda na główny limit PP. Same te dane nie rozdzielają jednoznacznie czasu jąder GPU od transferów/pipeline i nie dowodzą wyłącznego bottlenecku PCIe.

Decode: duża zajętość CPU (około 58–67% VM) współwystępuje z małym udziałem czasu CPU ekspertów w logach. W reprezentatywnym 128K verify wynosi 19.52 ms/window, GPU-reach wait 8.18 ms, per-layer host 0.58 ms, stage 1.75 ms; przy 256K: verify 21.20 ms, GPU-reach wait 9.01 ms, per-layer host 0.57 ms, stage 1.87 ms. To przemawia za dominacją ścieżki verify GPU i synchronizacji/host staging, nie matematyki CPU ekspertów. Wysokie CPU% może obejmować polling i oczekiwanie; nie należy utożsamiać go z kosztem obliczeń ekspertów. Bez profilu Nsight/ablation brak podstaw do bardziej precyzyjnego rozdzielenia. Nie wykonywano dodatkowego strojenia ani ablation poza kampanią.

Decode trwa tylko około 2 s przy 256 output tokens: zwykle 2–3 próbki na request. Uśrednione utilization/power decode są orientacyjne; normalne liczniki runtime i czasy silnika są silniejszą podstawą niż pojedyncza próbka GPU.

## Storage i RAM

Wszystkie 12 requestów IQ3_S raportuje `file_blobs=0`, `file_mb=0`: brak odczytów ekspertów z plików w decode. IQ3_S używa pełnego przypiętego expert arena około 46.84 GiB; `ram_blobs=0` w tym trybie nie oznacza braku RAM, ponieważ ten licznik dotyczy odrębnego mapped resident source. PLE pozostaje w domyślnym trybie direct i może czytać małe wiersze z plików; zerowe odczyty ekspertów nie oznaczają zerowego całkowitego I/O.

`/srv/ai` jest virtiofs. Guest disk/read_bytes nie pozwala dowieść braku fizycznych odczytów SSD hosta. Nie ma danych o odczytach Q4 w generation, ponieważ start jest odrzucony przed READY. Nie można potwierdzić pełnego resident zestawu Q4 ani odpowiedzieć empirycznie, czy jego misses trafiałyby do SSD w działającym runtime.

Najniższe MemAvailable w całej mierzonej kampanii: ponad 101 GiB; guard 12 GiB nie został aktywowany. Median peak RAM used: około 58.3–59.2 GiB. VRAM peak około 23.30 / 23.42 GiB. Brak OOM.

## Zmienność i PP >1000

IQ3_S przekroczył 1000 PP token/s w każdym mierzonym runie 128K i 256K (najniższe odpowiednio 4024.4 i 4556.8). Mediany 5827.3 i 5841.0. TG mediany 114.9 i 109.4 token/s. TTFT mediany 22.05 i 44.92 s.

Pierwszy request nowej długości bywał wolniejszy w PP mimo reuse=0: 64K 3258.9/5438.7/5439.0; 128K 4024.4/5827.3/5833.2; 256K 4556.8/5841.0/5842.3. Runtime zachowuje wybrane bufory, grafy i cache ekspertów między requestami, zgodnie z normalną metodą Strata. Nie resetowano procesu przed każdą komórką. Mediany opisują ten protokół z jednym warmup dla modelu; nie są cold-prefill ani dowodem identycznej szybkości pierwszego requestu dowolnej długości. Unikalny nonce i reuse=0 eliminują ponowne wykorzystanie KV promptu, ale nie cache sprzętowych/grafów/ekspertów.

## Q4 i używalność

Brak realnego porównania spowolnienia Q4/IQ3_S: wymagany resident-budget + layer split jest odrzucony przez upstream 0.1.31. Q4 nie jest dostępny dla wymaganego workload na obu GPU w tym przypiętym runtime. Nie wyciągamy z tego wniosków o jakości ani o wydajności Q4 na działającym backendzie. Quality sanity jest osobno w `quality/`; bez rankingu automatycznego.
