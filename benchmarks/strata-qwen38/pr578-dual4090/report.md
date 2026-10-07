# IQ3_S: PR #578 na 2× RTX 4090

## Wynik i zakres

**Rekomendacja: KEEP_LAYER_SPLIT.** Layer split wygrywa porównanie z oryginalnym PR zarówno w decode, jak i prefill. Oryginalny optimized helper z PR #578 nie odtwarza przewagi opisanej przez autora. Osobna lokalna poprawka kolejności dispatchu pomaga helperowi; jej wyniki są oznaczone `H-PRIORITY` i nie są przypisywane oryginalnemu PR.

Każdy headline TG oznacza decode tok/s po warmupie, z MTP, bez suffix lookup. Jedna inferencja naraz. Wszystkie stare wyniki i niepoprawne próby zachowano. Ten raport nie ocenia jakości quantów.

## Źródła, build i środowisko

- Zamrożony upstream/main: `99f3dbd0b21d1401b3769e0c0d963913607f380b`.
- Head otwartego PR #578: `b28121ff6ef117bec2558b3ece7e188dd33a2b7e`; GitHub mergeable/clean w zapisanym snapshotcie.
- Lokalny zwykły merge: `de25a51fe570cd6b7f60aad1fc50557a2c4a1e06`. **Brak konfliktów i ręcznych rozwiązań.**
- Osobny lokalny fix: `ec511d128247ccf25a1ec94168481bd053d35dfd`; [diff](git/helper-priority.diff). Oryginalny PR zamrożono wcześniej w [checkpointcie](ORIGINAL-PR578-CHECKPOINT.json).
- Najnowszy release przy rozpoczęciu: v0.1.38. Świeże checkouty CONTROL/PR/helper-priority; starsze środowiska pozostawiono bez zmian.
- 2× RTX 4090 24 GiB, Ryzen 9 7950X3D, 16 vCPU, około 161 GiB RAM, bez swap; PHB, bez NVLink.
- GCC 15.2, CUDA 13.4, driver 615.71.09; Release, CUDA sm_89, te same opcje CMake. Domyślne kernele, bez dodatkowego fast-math.
- Polecenia, wersje, topologia, status Git i SHA256 binarek: [environment.json](environment.json), [git/](git/). Wspólny pinned ggml został użyty tylko do odczytu, z osobnymi buildami.

IQ3_S: `ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF`, revision `ed59f92082b1e93c0e96d60a8b11aab089b52f09`. Pack `/srv/ai/models/strata/packs/iq3_s`; shardy w `/srv/ai/models/strata/models/IQ3_S/`. Profile: `/srv/ai/strata/data/expert-profile.bin`, MTP: `/srv/ai/models/strata/mtp/rt`. Rozmiary, manifesty i niezmienione mtime: [model-provenance.json](model-provenance.json), [audyt](independent-final-audit.json). Niczego nie pobierano ponownie i nie zmieniano wag.

## Testy i correctness

CONTROL, PR i lokalny fix: **56 testów CTest PASS, 2 SKIP, 4 FAIL środowiskowe** na wariant. Brak fixture Q2_0 dla PLE, brak legacy `experts.bin` dla expert_parity/pool_test oraz test mlock 256 MiB przy hard limit 8 MiB. Nie przedstawiam tego jako kompletu zielonych testów. Nie stwierdzono rzeczywistego failure obliczeń. Python serve CONTROL i PR: 197 testów, 9 skipped, OK. Szczegóły: [test-status.json](test-status.json), logi CTest/Python w [logs/](logs/).

10 identycznych krótkich greedy promptów: math, code, prose i JSON. Zapisano input/output IDs, tekst, SHA256, pierwszy token rozbieżny i finish reason. Brak zaobserwowanych NaN/Inf oraz ewidentnego corruption; oba testy JSON poprawne. Analogiczną baterię przeszedł lokalny fix. Sumowanie FP w innej kolejności daje rozbieżności autoregresyjne i nie oznacza bitwise parity. Positional agreement po rozbieżności nie jest teacher-forced top-1 agreement.

Istniejący `--dump-logits` nie daje łatwego porównywalnego dumpu dla wymagającego serve optimized-helper; nie raportujemy zmyślonego KL. Odpowiedzi i porównania: [correctness/](correctness/), [summary](correctness/summary.json), [fix summary](correctness/helper-priority-summary.json).

## Kontrola konfiguracji i cache

INT8 KV, `--kv-resident 32768`, max context 262144, MTP `--spec 4 --spec-min-p 0.5`, 15 pool workers, `--prefill auto` (wybrany chunk 8192). Greedy/temperature 0, brak tools, zero reuse. `--suffix-draft 0` rzeczywiście wyłącza suffix lookup; secondary używa 3. Nie zmieniano draft modelu ani samplingu pomiędzy wariantami. Pełne komendy są w każdym raw i [configs/](configs/).

**Fairness helperów przed warmupem:** 8586 fizycznych primary slots + 11796 helper slots = 20382 resident experts, initial overlap 0. Diagnostyka potwierdziła identyczne początkowe ID ekspertów na obu GPU. Numeric `--expert-cache 6567` odpowiada fizycznym 8586 slots: liczba CLI jest budżetem największego blobu, a auto uwzględnia zmienne rozmiary warstw. Wpisanie 8586 jako CLI powiększyłoby cache i zepsuło A/B. [fairness-audit.json](fairness-audit.json).

Layer split auto wybrał **K=25**, około 10112 slots na GPU0 i 8376–8377 na GPU1 (konkretne startup logi zachowane). GPU0/GPU1 mają inne role i pojemności niż w trybie helper; nie należy porównywać topologii jako samej zmiany algorytmu. LS-B zmienia wyłącznie PCIe fraction na historyczne 0.28 zamiast auto około 0.37.

Każda konfiguracja dostała świeży serwer, warmup i trzy kolejne payloady, dzięki czemu widać progresję adaptive cache. Warmup jest poza statystyką. W podstawowym sześciowariantowym screeningu stary warmup miał limit 256, ale zoptymalizowany helper czasem kończył go wcześniej. **Nie przypisujemy różnicy H-OLD/H-OPT wyłącznie PR przy różnej ilości pracy warmupu.** Osobne próby FAIR64 ograniczają warmup do tych samych 64 tokenów; ich negatywne wyniki pokazano poniżej.

## Główna tabela 32K — actual 31 400, suffix OFF

| Config | PP median | TG median | TG min/max | TTFT s | MTP accepted/window | Suffix accepted | CPU fallback¹ | Helper entries | Cache overlap² | CPU % | GPU0 % | GPU1 % | PCIe RX0/RX1 MB/s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LS-A | 4585.5 | 140.8 | 131.7 / 164.3 | 6.933 | 1.846 | 0 | 1616 | — | patrz DIAG | 59.5 | 66.0 | 57.5 | 76/241 |
| LS-B | 4603.0 | 139.6 | 134.3 / 144.3 | 6.904 | 1.815 | 0 | 961 | — | patrz DIAG | 59.5 | 38.5 | 49.5 | 35/37 |
| PR-LS | 4533.4 | 133.9 | 101.6 / 164.8 | 7.082 | 1.846 | 0 | 1616 | — | patrz DIAG | 95.8 | 38.0 | 55.0 | 131/308 |
| H-OLD | 2397.6 | 98.9 | 98.1 / 103.4 | 13.181 | 1.793 | 0 | 5034 | 7704 | patrz DIAG | 95.0 | 94.0 | 9.0 | 3257/42 |
| H-OPT | 2388.9 | 95.7 | 94.3 / 101.1 | 13.227 | 1.667 | 0 | 369 | 19014 | patrz DIAG | 66.3 | 88.0 | 5.0 | 3502/87 |
| H-OPT-FIXED | 2399.0 | 93.0 | 92.3 / 103.3 | 13.176 | 1.667 | 0 | 369 | 19014 | patrz DIAG | 66.0 | 87.5 | 5.7 | 3784/54 |
| H-PRIORITY | 2386.6 | 119.2 | 112.8 / 136.1 | 13.307 | 1.596 | 0 | 855 | 25143 | patrz DIAG | 73.8 | 86.0 | 7.5 | 88/34 |

Oryginalny PR H-OPT vs LS-A: **-32.03% TG**. Lokalny fix vs oryginalny H-OPT: **24.56%**; fix vs LS-A: **-15.34%**. Warunki warmupu FAIR64 podano osobno; nie traktujemy tej tabeli jako dowodu czystej przewagi PR nad starym helperem.

¹ CPU fallback jest przybliżeniem z zaokrąglonej średniej logu per layer-window × 48 × verify windows. Helper entries są obliczeniami routed entries, nie liczbą unikalnych resident experts. ² Cache overlap zmierzono osobno; instrumentation wyłączona we wszystkich headline speed runs. 1 Hz telemetry przy decode około 2 s jest skąpa; solidniejszą ocenę CPU/GPU/PCIe daje 2048 output. System CPU 100% oznacza wszystkie 16 vCPU, process CPU 100% oznacza jeden vCPU.

PP min/median/max i TG min/median/max, per-run progresja oraz pełne MTP/telemetry: [summary.csv](summary.csv), [summary.json](summary.json), [raw/](raw/). Pierwszy długi prefill po 4K warmupie bywa wolniejszy; nie usuwano go z mediany.

## Warmup, invalid runs i niezależne fresh-server potwierdzenia

| Config | Ważne runy | TG median (tylko 3 ważne) | TG zakres ważnych |
|---|---:|---:|---:|
| H-OLD-FAIR64 | 3 | 101.1 | 90.3 / 104.8 |
| H-OPT-FAIR64 | 2 | brak mediany 3 runów | 94.6 / 97.2 |
| H-OLD-FAIR64-RETRY1 | 3 | 103.7 | 87.8 / 104.0 |
| H-OPT-FAIR64-RETRY1 | 2 | brak mediany 3 runów | 79.3 / 94.1 |
| LS-A-FRESH1 | 1 | 135.7 | 135.7 / 135.7 |
| LS-A-FRESH2 | 1 | 120.9 | 120.9 / 120.9 |
| LS-A-FRESH3 | 1 | 135.4 | 135.4 / 135.4 |
| LS-B-FRESH1 | 1 | 138.6 | 138.6 / 138.6 |
| LS-B-FRESH2 | 1 | 131.9 | 131.9 / 131.9 |
| LS-B-FRESH3 | 1 | 135.7 | 135.7 / 135.7 |

W H-OPT-FAIR64 run 2 oraz jego jednej powtórce model zakończył się po **63 tokenach z tool_calls**. Wyniki zachowano jako INVALID; nie są liczone jako ważny 256-tokenowy decode. Dwa ważne runy nie stanowią żądanej mediany z trzech. Nie zmieniono starych payloadów ani nie dobierano kolejnych retry do pożądanego wyniku.

LS-A i LS-B różniły się poniżej 5%, dlatego wykonano po trzy niezależne starty serwera (TG mediana replicates: 135.4 vs 135.7). Nie potwierdzono przewagi historycznego 0.28; zostaje auto. PR-LS (PR obecny, opt wyłączony) nie wskazuje jednoznacznej dużej regresji: duża zmienność krótkiego decode i innych trajektorii FP wymaga ostrożności.

## MTP i dispatch — metryki uzupełniające 32K

| Config | MTP proposed | MTP accepted | MTP accept % | Verify windows | ms/window | Helper wait ms | Returned MiB |
|---|---:|---:|---:|---:|---:|---:|---:|
| LS-A | 206 | 168 | 80.0 | 91 | 20.0 | — | — |
| LS-B | 220 | 167 | 76.4 | 92 | 19.5 | — | — |
| PR-LS | 206 | 168 | 80.0 | 91 | 21.0 | — | — |
| H-OLD | 216 | 165 | 76.4 | 92 | 28.4 | 119.0 | 75.2 |
| H-OPT | 213 | 160 | 76.1 | 96 | 27.1 | 88.0 | 139.9 |
| H-OPT-FIXED | 213 | 160 | 76.1 | 96 | 27.8 | 123.0 | 139.9 |
| H-PRIORITY | 215 | 158 | 70.1 | 99 | 20.7 | 95.0 | 144.2 |

Dokładne raportowane primary cache hits/lookups/nonhits i upstream hit rate są w summary.json; ten hit rate wyklucza ekspertów obsługiwanych przez PCIe, a helper entries mają osobny licznik. Nie oznacza on, że 99% całego routingu omija PCIe. Primary VRAM hits, primary PCIe entries i CPU entries per layer-window są zapisane w normalnych timing logs oraz per-run summary.json. Zero suffix proposed/accepted w PRIMARY sprawdzono w audycie. Returned bytes/token i bytes/active layer launch są dostępne w per-run summary, z precyzją normalnego logu MiB.

## Cache, adaptation i transport

Osobne boundary snapshots, instrumentation OFF domyślnie:

| Config | Primary slots | Helper slots | Initial residents | Startup overlap | Po warmup | Po run 3 | Overlap/helper % |
|---|---:|---:|---:|---:|---:|---:|---:|
| H-OLD-DIAG | 8586 | 11796 | 20382 | 0 | 571 | 2073 | 17.57 |
| H-OPT-DIAG | 8586 | 11796 | 20382 | 0 | 0 | 0 | 0.00 |

Old helper po run 3: overlap **2073 / 17.57%**; optimized helper: **0** także po warmupie i kolejnych runach. Primary net new IDs: old 2202, opt 0; helper net new IDs: old 0, opt 404. To zmiany netto zbiorów, nie wszystkie przejściowe swaps. Pending admissions są wykluczone z resident snapshotu i nie oznaczają utraty fizycznej pojemności.

Optimized helper usuwa dużo CPU pracy: w dwóch ważnych runach diagnostyki około 646 routed fallback entries wobec około 4406 w old helper, a w długim decode około 3749 wobec około 12574 layer split. Są to przybliżenia z zaokrąglonych logów, nie dokładne liczniki hot path. Liczba CPU activation quantization skips nie jest dostępna.

Weighted reduction zwraca jeden partial vector/token zamiast osobnych expert rows. Jednak łączne returned bytes na request **nie muszą spaść**: old w diagnostyce około 60.9 MiB, optimized około 139.4 MiB, ponieważ helper obsługuje znacznie więcej entries (około 6240 → 18914). Wartości upstream „full rows” nie są old-helper baseline. Rzeczywisty cały PCIe ruch pokazuje tabela steady decode; nie przypisujemy mu automatycznie spadku.

Instrumentation to tylko dodatkowe snapshots na granicach requestów, w osobnych commitach CONTROL/PR. Nie dodano per-token liczników. Próba OFF/ON była zaszumiona i optimized nie miał trzech ważnych krótkich runów, więc nie dowodzi overhead ≤1%. Z tego powodu final speed runs mają instrumentation **OFF**. Cache diagnostyk nie wlicza się do headline TG.

## Długi decode — ten sam prompt, 2048 output, suffix OFF

| Config | Runy | PP | TG | TG min/max | ms/window | CPU fallback¹ | CPU % | GPU0 % | GPU1 % | RX0 MB/s | RX1 MB/s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LS-A-STEADY2048 | 3 | 4673.9 | 158.8 | 153.3 / 161.0 | 18.9 | 12574 | 94.4 | 45.4 | 54.6 | 333 | 144 |
| H-OLD-STEADY2048 | 3 | 2427.1 | 76.0 | 73.9 / 80.5 | 37.5 | 75125 | 99.4 | 95.0 | 11.2 | 4804 | 44 |
| H-OPT-STEADY2048 | 3 | 2436.0 | 75.3 | 74.6 / 78.4 | 36.8 | 3749 | 77.9 | 96.9 | 5.3 | 7548 | 177 |
| H-PRIORITY-STEADY2048 | 3 | 2432.9 | 135.4 | 125.5 / 150.9 | 23.0 | 6307 | 94.0 | 92.9 | 11.9 | 185 | 105 |

Ten workload to osobny deterministyczny code-maintenance payload; nie historyczne A/B z 256 output. `--prompt-cache 0` zapewnia zero reuse przy kolejnych identycznych requestach. Payload i jego token IDs: [steady2048-request.json](references/steady2048-request.json), token-ids/.

Oryginalny PR kieruje część helper-owned ekspertów do primary mapped-RAM PCIe przed `RemoteExperts::begin()`. Primary planner wyklucza PeerExperts, lecz nie RemoteExperts z quota PCIe. Lokalny fix wyklucza wyłącznie ekspertów aktualnie posiadanych przez optimized helper z tego quota, pozostawiając je do istniejącego dispatchu helpera. Nie zmienia kerneli, wag, pojemności cache, old-helper ani layer-split ownership. Ta hipoteza ma potwierdzenie w danych PCIe/wykorzystaniu i osobnym A/B fixu, a nie tylko w samym wykorzystaniu GPU. W fixed steady median MTP accepted/window zmieniło się z 1.885 do 2.119, więc całego wzrostu TG nie można utożsamić z samym skróceniem czasu identycznej ścieżki obliczeń.

Kontrolowane helper A/B w steady decode: identyczny 64-tokenowy warmup, ten sam input i 2048 output oraz initial capacity 8586/11796. Original helper 76.0 vs PR optimized 75.3 TG: -0.92%. Lokalny fix 135.4 TG: +79.81% względem oryginalnego PR, ale -14.74% względem layer split. Nie potwierdzono headline przewagi oryginalnego PR nad original helper na tym workloadzie.

## Finalna macierz rzeczywistych kontekstów

| Config | Actual input | Runy | PP | TG | TTFT s | CPU fallback¹ | Helper entries | Overlap² | CPU % | GPU0 % | GPU1 % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LS-A-FINAL | 31400 | 3 | 4595.1 | 135.1 | 6.913 | 998 | — | — | 59.4 | 41.0 | 63.5 |
| LS-A-FINAL | 63400 | 3 | 5361.4 | 126.9 | 11.965 | 1067 | — | — | 51.7 | 38.7 | 64.7 |
| LS-A-FINAL | 127000 | 3 | 5668.8 | 119.2 | 22.667 | 840 | — | — | 68.2 | 41.5 | 50.0 |
| LS-A-FINAL | 259500 | 3 | 5684.4 | 114.3 | 46.160 | 931 | — | — | 83.2 | 43.0 | 50.0 |
| H-OPT-FINAL | 31400 | 3 | 2400.7 | 95.4 | 13.161 | 485 | 18784 | 0 w DIAG | 77.7 | 89.5 | 6.0 |
| H-OPT-FINAL | 63400 | 3 | 2408.6 | 84.1 | 26.461 | 294 | 27724 | 0 w DIAG | 53.7 | 93.3 | 5.3 |
| H-OPT-FINAL | 127000 | 3 | 2358.2 | 82.4 | 54.106 | 485 | 22147 | 0 w DIAG | 77.2 | 91.0 | 6.7 |
| H-OPT-FINAL | 259500 | 3 | 2281.9 | 76.2 | 114.213 | 369 | 25567 | 0 w DIAG | 64.8 | 95.0 | 5.0 |
| H-PRIORITY-FINAL | 31400 | 3 | 2381.7 | 117.5 | 13.334 | 714 | 24822 | — | 74.6 | 88.5 | 7.0 |
| H-PRIORITY-FINAL | 63400 | 3 | 2388.0 | 100.8 | 26.821 | 639 | 35502 | — | 61.6 | 92.5 | 7.0 |
| H-PRIORITY-FINAL | 127000 | 3 | 2355.7 | 125.1 | 54.176 | 672 | 28448 | — | 77.7 | 90.5 | 8.0 |
| H-PRIORITY-FINAL | 259500 | 3 | 2282.7 | 117.7 | 114.169 | 587 | 34321 | — | 76.4 | 91.5 | 8.0 |

W każdym punkcie osobny warmup + 3 measured, dokładnie 256 output, reuse 0. Payloady są literalnie starymi requestami i mają identyczne token IDs między konfiguracjami. Jeden świeży serwer per config; historia adaptation zachowana przy kolejnych kontekstach. Krótkie warmupy mają deterministyczny nonce per context identyczny między wariantami, aby także warmup nie korzystał z prefix reuse.

Pamięć i moc — mediany peak całego requestu / średniej fazy decode; to nie sumy pamięci GPU:

| Config | Context | RAM used GiB | RSS GiB | VRAM0 GiB | VRAM1 GiB | Power0 W | Power1 W |
|---|---:|---:|---:|---:|---:|---:|---:|
| H-OPT-FINAL | 31400 | 58.0 | 53.8 | 23.3 | 23.3 | 217.9 | 79.5 |
| H-OPT-FINAL | 63400 | 58.2 | 54.0 | 23.3 | 23.3 | 208.2 | 67.4 |
| H-OPT-FINAL | 127000 | 58.5 | 54.2 | 23.3 | 23.3 | 210.7 | 70.8 |
| H-OPT-FINAL | 259500 | 58.6 | 54.3 | 23.3 | 23.3 | 203.8 | 71.2 |
| H-PRIORITY-FINAL | 31400 | 58.3 | 53.8 | 23.3 | 23.3 | 230.8 | 80.6 |
| H-PRIORITY-FINAL | 63400 | 58.1 | 54.0 | 23.3 | 23.3 | 219.3 | 64.1 |
| H-PRIORITY-FINAL | 127000 | 58.5 | 54.2 | 23.3 | 23.3 | 256.5 | 68.4 |
| H-PRIORITY-FINAL | 259500 | 58.5 | 54.3 | 23.3 | 23.3 | 239.0 | 72.9 |
| LS-A-FINAL | 31400 | 58.8 | 54.6 | 23.3 | 23.4 | 138.2 | 182.3 |
| LS-A-FINAL | 63400 | 59.0 | 54.8 | 23.3 | 23.4 | 131.5 | 178.9 |
| LS-A-FINAL | 127000 | 59.4 | 55.2 | 23.3 | 23.4 | 144.6 | 172.6 |
| LS-A-FINAL | 259500 | 59.4 | 55.2 | 23.3 | 23.4 | 164.5 | 180.6 |

Brak CUDA/host OOM i crash. Guard abort <12 GiB MemAvailable. Normalny log nie wykazał logical expert file reads podczas decode; mapped-RAM PCIe nie jest SSD streaming. PLE/table reads i SSD keepalive są oddzielną aktywnością, a I/O VM nie dowodzi fizycznych host SSD reads. Nie odczytywano PSS co sekundę; tylko przed/po requestach, poza timerem.

## Zmiana TG względem layer split w finalnej macierzy

| Actual input | Original PR TG delta | PR + local fix TG delta | LS/fix PP ratio |
|---|---:|---:|---:|
| 31400 | -29.39% | -13.03% | 1.93× |
| 63400 | -33.73% | -20.57% | 2.25× |
| 127000 | -30.87% | 4.95% | 2.41× |
| 259500 | -33.33% | 2.97% | 2.49× |

Lokalny fix wygrywa decode przy 128K o około 5% i 256K o około 3%, lecz znacznie wydłuża TTFT/prefill. Nie rekomendujemy na tej podstawie zastąpienia layer split w agentowym workloadzie, który często przetwarza nowe długie wejścia. Dla bardzo długiego decode na już rozgrzanym kontekście potrzebne byłyby osobne testy >2048 przy tych kontekstach, aby potwierdzić trwałość małej przewagi; nie przedstawiamy tego jako wynik oryginalnego PR.

## Secondary: suffix lookup ON

| Config | Runy | PP | TG | Suffix accepted | Fairness |
|---|---:|---:|---:|---:|---:|
| LS-A-LOOKUP-ON | 3 | 4649.5 | 135.6 | 27 | patrz raw warmup/layout |
| H-OLD-FAIR64-LOOKUP-ON | 3 | 2399.1 | 98.8 | 35 | patrz raw warmup/layout |
| H-OPT-LOOKUP-ON | 3 | 2404.3 | 94.5 | 41 | CAPACITY_MISMATCH |
| H-OPT-FIXED-LOOKUP-ON | 3 | 2380.1 | 84.1 | 39 | patrz raw warmup/layout |

Pierwsze auto H-OPT-LOOKUP-ON dobrało 8583/11797 zamiast 8586/11796, więc jest oznaczone **INITIAL_CACHE_CAPACITY_MISMATCH**, nie controlled helper A/B. Zachowano je i wykonano H-OPT-FIXED-LOOKUP-ON z jawnie równymi pojemnościami. Warmup może kończyć się naturalnie wcześniej; liczba tokenów jest zapisana. Nie przypisujemy speedup PR, gdy stan warmupu różni się. Primary wyniki pozostają suffix OFF.

## Odpowiedzi na pytania i ograniczenia

1. Integracja: zwykły merge na wspólnym main, bez konfliktów.
2. Testy: brak rzeczywistej awarii correctness; cztery znane failures środowiskowe na build, jawnie opisane.
3. Helper działa bez OOM/crash i poprawnie odpowiada na małe testy, ale konkretne stare payloady potrafią zakończyć się tool_calls; takie runy są INVALID.
4. TG wszystkich trybów i procenty są w tabelach powyżej. Layer split wygrywa względem oryginalnego PR; osobny lokalny fix może dawać niewielką przewagę decode przy dłuższym kontekście, kosztem dużo wolniejszego prefill.
5. Complementary caches działają: optimized overlap 0 po warmupie/run 3; stary helper 17.57%.
6. CPU fallback maleje, lecz nie gwarantuje wzrostu TG. Oryginalny helper-opt przenosi bottleneck na GPU0/mapped-RAM PCIe i verifier wait, pozostawiając GPU1 słabo wykorzystane. CPU layer split w steady decode nadal jest blisko pełnego obciążenia (~94% wszystkich vCPU); zaobserwowano także próbki 100% system CPU.
7. GPU utilization nie rośnie równomiernie: oryginalny optimized helper około 97% GPU0 i 5% GPU1, layer split około 45%/55% w steady decode. Dokładny efekt lokalnego fixu jest w jego osobnym wierszu.
8. Stripe vs layer: parser wspiera oba, ale przy jednym helperze kod omija multi_remote placement i wybiera tę samą listę. Drugi sweep byłby powtórką tego samego algorytmu.
9. Auto sizing dobiera sensowne pojemności, ale może zmienić je o kilka slots między startami. Fixed reprodukuje fizyczny auto budget; nie stwierdzono przewagi samego ręcznego sizingu. Nie robiono dodatkowego capacity tuningu.
10. Helper wymaga serve/profile/cache/pool; --peer-device wyklucza helper i split. Na dwóch GPU helper i layer split są alternatywami. Kod przewiduje do trzech helperów, lecz tylko dual CUDA zweryfikowano; HIP nieweryfikowany. Pinned-host transport działa bez P2P/NVLink.
11. Prosta dalsza optymalizacja do przedstawienia upstream: helper ownership przed primary PCIe quota, opisana i zmierzona jako osobny lokalny commit. Niczego nie pushowano.
12. Mixed/math vs code: wykonano code-agent replay i steady code workload oraz math correctness, nie osobny mixed/math speed suite. Nie ma podstaw do uniwersalnego zwycięzcy zależnego od gatunku promptu.

Autor PR podał original helper 88.07/85.15, layer split 126.86/146.95 i optimized helper 143.35/197.58 tok/s (Mixed/Code), z równymi początkowymi cache capacities. Nasze capacity fairness odtworzono. PR zawiera implementację i dokumentację, nie dokładny corpus requestów ani harness autora. Inny workload/config i OS mogą zmieniać koszty; nie oczekujemy tych samych liczb ani nie zgadujemy ich przyczyn bez danych. Źródło: [PR #578](https://github.com/Niko1221/Strata/pull/578), zapis body/diff w git/.

Historyczne raw/report IQ3_S: v0.1.31 PP 4652.5/TG 131.2; v0.1.38 replay PP 4580.4/TG 131.7, poszczególne TG 111.7/147.5/131.7 (173/173 accepted suffix drafts w szybkim runie). **HISTORICAL / NOT_CONTROLLED_A_B**. Dzisiejsze controlled A/B używa jednego main, modelu, token IDs, build flags i frozen settings.

Ograniczenia: nie mierzymy dokładnych transient swaps ani quantization-skip count. Nie ma teacher-forced KL/top1. PCIe telemetry ma 1 Hz i tolerancję fazy ±0.5 s. Krótkie decode są zaszumione; dlatego wykonano także 2048 output i fresh-server replicates. Nie zamieniamy brakujących metryk na zero.

## Końcowy audyt

Zweryfikowano 105 raw measured requests; issues: 0. Zachowano 3 negatywne measured requests (63 output, tool_calls), wykluczone z median. Wszystkie ważne requesty mają wymaganą liczbę output, reuse 0, prawidłowe actual token counts i identyczne zapisane input IDs między wariantami. Model/pack size i mtime nie zmieniły się. Checkouty lokalne mają czysty git status. Nie było push ani otwarcia PR. Wszystkie serwery/driver kampanii zakończone; nvidia-smi compute apps puste, obie GPU 0% utilization i po 1 MiB VRAM. Szczegóły: [independent-final-audit.json](independent-final-audit.json), [STATUS.md](STATUS.md).

## Odtwarzanie i artefakty

- [summary.json](summary.json) zawiera per-run wyniki i mediany; [summary.csv](summary.csv) tabelę komórek wraz z PP/TG min/max.
- [raw/](raw/) zawiera niezmienione payloady, pełne komendy, source/binary SHA, actual token counts, odpowiedzi, czasy i invalid runs.
- [logs/](logs/), [telemetry/](telemetry/), [configs/](configs/), [git/](git/), [correctness/](correctness/) przechowują materiał źródłowy.
- `analyze.py` odtwarza JSON/CSV, `report-final.py` ten raport; `final-audit.py` weryfikuje model provenance, token IDs, parametry i cache fairness.
- Oryginalny PR: [original-pr578-checkpoint/](original-pr578-checkpoint/); lokalny fix: oddzielny checkout, commit i build. Nie nadpisano oryginalnego benchmarku.

## RECOMMENDATION

**KEEP_LAYER_SPLIT**

Pozostać przy layer split auto K=25 dla IQ3_S na tej VM i obu 4090. Oryginalny optimized helper jest wolniejszy w krótkim i długim decode oraz dużo wolniejszy w prefill. Lokalny fix ma 125.1 TG przy 128K wobec 119.2 layer split i 117.7 przy 256K wobec 114.3, ale odpowiednio PP 2355.7/2282.7 wobec 5668.8/5684.4; nie jest to wynik oryginalnego PR. Lokalny helper-priority fix warto przeanalizować upstream, ale nie daje podstaw, aby zastąpić nim bieżący layer split w OpenCode.
