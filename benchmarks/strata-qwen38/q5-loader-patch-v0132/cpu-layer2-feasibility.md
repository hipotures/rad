# Q5: feasibility CPU-only routed experts na warstwie 2

Wniosek: ścieżka jest technicznie wykonalna z istniejącym kodem obliczeń CPU, bez nowego kernela Q6_K CUDA i bez zmiany wag. Nie jest to mały patch loadera: potrzebna jest integracja mieszanej polityki CPU/GPU w decode, cache, grafie verify/MTP i prefill. Nie wykonano jeszcze takiego patcha ani pełnego model smoke; wydajność pozostaje nieznana.

## Przypięte źródła i model

Checkout `/srv/ai/strata-v0.1.32-q5`, bazowy HEAD `c499bd102e7a4135c0de389dcfe38c399759ccc8`. Pozostaje tylko wcześniejszy patch metadata-only GGUF i jego testy (3 pliki, 88 insertions, 1 deletion). Czysty checkout niezmieniony. Model Unsloth UD-Q5_K_XL, revision `38bb39ee97821de2c9009abb7e93950eec396e66`.

Sprawdzono wszystkie 48 wpisów `native_experts.txt`: tylko layer 2 ma gate/up Q6_K (14), down Q8_0 (8); pozostałe 47 warstw ma Q5_K (13)/Q8_0 (8). Layer 2 ma 512 ekspertów po 4 428 800 B, razem 2 267 545 600 B = 2.112 GiB. Cała arena routed experts Q5: 91.614 GiB. Nie należy utożsamiać tej wartości z całym RAM procesu: Q5 ma też duży tensor PLE Q8_0 (~54.4 GB), KV i bufory. Przyszły smoke musi monitorować MemAvailable i mieć próg abort 12 GiB.

## Potwierdzenie ścieżki CPU

`src/kernels/cpu/native_expert.cpp:32`: `native_fmt` korzysta z ggml-cpu type traits i sprawdza dot products oraz kwantyzatory aktywacji. Q6_K/Q8_0 jest obsługiwane. `native_gu_rows` i `native_down_rows` mają ogólną ścieżkę vec_dot; nie potrzeba nowej implementacji Q6 CPU.

W `feasibility/cpu-q6-probe.cpp` wykonano niezależny od engine test syntetyczny jednego eksperta: H=2560, FF=640, Q6_K gate/up, Q8_0 down, trzy różne aktywacje. `ExpertPool::run_split_multi_native` (2 workerów, bez pinning) porównano z szeregowymi `native_gu_rows` / `native_quant_h` / `native_down_rows`. PASS: 7680 skończonych, niezerowych wyników, max abs diff 0, zgodność bitowa. Pełny wynik: `feasibility/cpu-q6-probe.json`.

To test zgodności puli z szeregową implementacją CPU korzystającą z tych samych prymitywów; nie dowodzi poprawności całego modelu ani zgodności z CUDA/FP16. Nie ładowano modelu, nie wykonano benchmarku, nie modyfikowano GGUF.

## Dlaczego samo usunięcie guarda jest błędne

- `src/program/generate.cpp:1678`: startup odrzuca unsupported GPU pair we wszystkich warstwach. Trzeba dopuścić wyłącznie jawnie oznaczone CPU-only warstwy, po walidacji ich CPU type traits; zachować domyślne odrzucanie unsupported GPU formats.
- `src/core/expert_source.cpp:1579`: multi-token dispatch rozdziela VRAM, PCIe, remote i CPU. Już istnieje CPU job na końcu (`run_split_multi_native`, około 1775). Brak cache hit nie wymusza CPU: PCIe może nadal skierować eksperta do kernela GPU. Maska musi wykluczyć wszystkie trzy ścieżki GPU, single-token dispatch i lookahead/admission.
- `src/core/expert_source.cpp:1823`: dynamiczne cache admission też potrzebuje polityki. Startup profile preload, stage profiles i remote profiles w generate.cpp (~2825–2978), późniejsze refill/adaptive/cache restore muszą respektować tę samą maskę. Pozostałe warstwy zachowują dotychczasową politykę i mogą używać obu GPU.
- `src/core/verify.cpp:753`: graf verify wywołuje `native_expert_layout` i grouped native kernels dla każdej warstwy. Same zerowe liczniki GPU nie wystarczą: dla CPU-only layer nie wolno tworzyć/wywoływać unsupported expert nodes. Trzeba zachować publikację planu, flagi A/B/completion, transfer wyników CPU i combine. Shared expert, routing, attention/dense nadal mogą działać na GPU; CPU-only dotyczy routed experts.
- Negative CTest `native_expert_parity_refuses_q6_K` musi nadal odrzucać bezpośredni GPU expert pair. Fallback nie dodaje obsługi Q6 do GPU API.

## Prefill: brak gotowego CPU fallback

`src/prefill/prefill.cpp:1580–1650` już grupuje routing na hoście i zna mapowanie sorted expert rows. Dalej uruchamia MMQ albo CUDA dequant + GPU GEMM (`iq_dequant_gu_f16`, około 1747). BF16/FP16 path nie oznacza obliczeń CPU i nadal nie obsłuży Q6_K przez obecny expert dequantizer.

Minimalny rzeczywisty CPU-only branch powinien pobrać FP32 `m.mixed`, użyć istniejącego source RAM blob i native activation quantization, policzyć routed experts przez pulę CPU, przenieść niezważone wyniki do GPU `m.Dm` w porządku `slot/src`, a następnie użyć istniejącego `moe_combine` (około 1811). Wagi routera stosować dokładnie raz. Pula ma `MAXT=8` (`include/strata/kernels/cpu/expert.hpp:131`) oraz ograniczoną liczbę jobs; trzeba dzielić duże grupy prefill na ograniczone batche, bez przepełnienia buforów.

CPU dequant weights -> GPU FP16 GEMM byłoby innym rozwiązaniem: nie realizuje wymagania „ALL routed experts tej warstwy -> CPU”. Nie przyjęto go jako CPU-only fallback.

## Minimalny zakres patcha i testów

1. Centralna jawna maska CPU-only layers, używana przy ładowaniu, planowaniu cache i dispatch. Błąd dla warstw bez poprawnej ścieżki CPU; domyślny tryb upstream zachowuje obecne validation.
2. Wykluczenie layer 2 z obu GPU caches, PCIe kernels, helper GPU i device-only planning; pozostałe warstwy bez zmiany polityki.
3. Decode single-token i verify/MTP: wszystkie routed outputs layer 2 z puli CPU, zero GPU expert groups, działające synchronizacje, combine i layer split.
4. Prefill CPU branch z poprawnym token/expert mapping i bounded jobs; reuse/refill nie może przywrócić layer 2 do GPU.
5. Test supported expert format forced CPU-only na syntetycznych danych: dispatch counts, brak admission, CPU output/weights, nietknięte inne warstwy. Test Q6_K/Q8_0 CPU, prefill względem CPU referencji, repeated graph replay, MTP off/on, dwie GPU i prefix reuse. Zachować istniejące negative GPU Q6 tests.
6. Dopiero po testach: load/health + 64-token smoke na 2×4090, K=24, INT8 KV, spec 4/min-p .5; RAM guard. Na następny blocker STOP. Bez benchmarku na tym etapie.

## Ocena kosztu i decyzja

Nie trzeba najpierw pisać CUDA Q6_K. Proponowane rozwiązanie wymaga kilku punktów integracji runtime, szczególnie nowej ścieżki prefill; nie można nazwać go kilkulinijkową poprawką. Koszt CPU-only jednej warstwy nie musi wynosić 1/48 czasu: wszystkie wybrane routed experts tej warstwy oraz synchronizacja znajdują się w ścieżce zależności, a duży prefill może zdominować czas całego requestu. Wydajność ustalimy dopiero po działającym smoke i późniejszym osobno zleconym teście.

CPU i GPU mogą liczyć inaczej numerycznie mimo niezmienionych wag. Test syntetyczny potwierdził zgodność CPU pool vs serial CPU, nie parity tekstu modelu. Eksperyment Q5 pozostaje otwarty; następny konkretny krok to osobny opt-in patch polityki per-layer CPU-only wraz z decode/verify/prefill i testami, bez nowych CUDA kernels.
