# IQ3_S 32K: dokładny replay payloadów v0.1.31 na v0.1.38

Odtworzono dokładnie trzy stare requesty32K, bez regenerowania promptów, nonców ani zmian sampling. Zapisany stary warmup4096 wykonano raz i wyłączono ze statystyki. Wszystkie trzy próby:actual31400,256output,reuse0,finish_reason=length,brakOOM/crash/toolcalls. Zweryfikowano równość JSONpayloadów, wyrenderowanego chat template i wszystkich31400tokenIDs. Pełne wyniki pierwszej kampanii pozostały w ../iq3s-v0138-2x4090/.

## Wynik

| Kampania | PP mediana | TG mediana | Acceptance % | Accepted/window | Verify windows |
|---|---:|---:|---:|---:|---:|
| Stare v0.1.31 | 4652.5 | 131.2 | 73.52 | 1.695 | 95 |
| Nowe v0.1.38, nowe prompty | 4597.4 | 101.8 | 74.29 | 1.545 | 101 |
| v0.1.38, dokładny replay starych promptów | 4580.4 | 131.7 | 74.65 | 1.723 | 94 |

| Replay run | PP | TG | Drafted | Accepted | Accept % | Accepted/window | Verify windows |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 4472.8 | 111.7 | 217 | 162 | 74.65 | 1.723 | 94 |
| 2 | 4587.7 | 147.5 | 206 | 199 | 96.60 | 3.431 | 58 |
| 3 | 4580.4 | 131.7 | 224 | 158 | 70.54 | 1.580 | 100 |

Replay TG mediana131,7tok/s wróciła do poziomu starej131,2tok/s (+0.38%). Względem nowej kampanii101,8tok/s wzrost wynosi+29.37%. Nie ma więc dowodu na stały limitv0.1.38 około100tok/s przy tym modelu i konfiguracji. Sam spadek acceptance nie wyjaśnia pierwszej kampanii:mediany73,52%stare,74,29%nowe i74,65%replay są podobne.

## Różnice promptów i konfiguracji

- Pierwsza nowa kampania nie miała identycznych starych payloadów:inne nonce, dodatkowy systemowy offline/no-tools policy oraz zmieniona granica wycinka korpusu, żeby zachować actual31400. Pełne trzy diffy zapisano w evidence/payload-old-new-run*.diff.
- Sampling w starych i nowych requestach jest ten sam:temperature0,max_tokens256,reasoning_effortnone,stream i include_usage.
- Argumenty engine starego configu i pierwszej nowej kampanii są identyczne. Spec4,min-p0.5,INT8KV,kv-resident32768,MTPi expert profile bez zmian. AutoK25,slots10112/8376,workers15+host.
- Rzeczywisty wynik autoPCIe probe różni się:0.1.31pcie-frac0.28,0.1.38pcie-frac0.37, mimo zmierzonego13,4GB/s w obu. Wv0.1.38 formuła skalowania używa gbps/20; nie wymuszano starej wartości podczas replay.
- Suffix lookup domyślnie3, maksymalneT4; adaptive co4roundy,do96swaps,decay0.7 w obu. Poprzednio decay był hardcoded, teraz opcją domyślną. Te same liczby nie oznaczają identycznej implementacji adaptive; nowe release notes opisują zmianę synchronizacji kopii.
- Brak STRATA_SPLIT_OWN,rotatedKV,experimental speed projection ani patchy. Runtimev0.1.38defaultsm89.

## Decode: acceptance to nie wszystko

Stare trzy próby miały95/98/95verifywindows i około19,91–20,74ms/window. Pierwsza nowa kampania101/103/95windows oraz26,37/24,41/19,54ms/window. Run3 już wtedy osiągnął137,9TG. Zmieniła się zarówno liczba tokenów akceptowanych na window,jak i czas samego window.

Replay run1:94windows,24,38ms/window,111,7TG,74,65%accept. Replay run2:58windows,29,92ms/window,147,5TG,96,60%accept,3,431accepted/window. Normalny log suffix draftera wskazuje35windows i173/173accepted suffixdrafts, wobec starych9windows i32/45. Replay run3:100windows,19,44ms/window,131,7TG,70,54%accept.

Drugi replay zyskał dzięki długim przyjętym draftom z suffix lookup, mimo wolniejszego pojedynczego window. Raportowane acceptance pochodzi z normalnych liczników engine; szczegółowe suffixstats zachowano osobno. Greedy odpowiedzi starego runtime i replay różnią się we wszystkichtrzechpróbach — hashe i literaldiffy zapisano, bez oceny jakości ani LLMjudge.

## Ograniczenia i dalsza diagnoza

Klasyfikacja NOT_CONTROLLED_A_B:payloady i tokenIDs są identyczne, ale runtime,autoPCIe default,historia adaptivecache i greedyoutput różnią się. Poprzedni smoke/pilot lifecycle nie został odtworzony; wykonano tylko zapisany4096warmup. Z tego replay nie można przypisać całej różnicy wyłącznie tekstowi promptu albo wyłącznie MTP. Wynik wspiera zależność TG od workloadu,przyjętych draftów i kosztu window; nie potwierdza ogólnej25%regresji decode.

Jeśli kontynuować izolowanie przyczyny, następnym pojedynczym kontrolowanym krokiem byłby ten sam replay z jawnie ustawionympcie-frac0.28, bez zmiany pozostałych ustawień. Tego dodatkowego testu nie wykonywano.

Artefakty:input-config-comparison.json,summary.json,summary.csv,raw/,references/,evidence/*.diff i hashe. Serwer zatrzymany; GPU wolne. Nie uruchamiano nowych sweepów ani benchmarków64K/128K/256K.
