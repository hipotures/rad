# Qwen3.8-Flash-Next — raport końcowy (2026-08-29)

## Wynik

Najwyższą praktyczną reprezentacją sprawdzoną na tej maszynie jest aktualny Unsloth **Q8_0**, revision `c8b5954a88c2775c546b92593eda40ea041d3176`. Ma 175.298 GiB, działa na 2×RTX 4090 z częściowym offloadem do RAM przy `-c 131072 -np 1` i ukończył test z 122 897 tokenami promptu: 23.53 tok/s prefill oraz 5.03 tok/s decode.

BF16 (~329.716 GiB samych wag) przekracza łączny budżet GPU+RAM (~203 GiB) przed KV i buforami. Q8 mieści się, choć nie w samym VRAM. Q6/Q5 nie pobrano: po potwierdzeniu Q8 nie mogły poprawić wierności, a pobieranie ich tylko dla kompletności byłoby niecelowe.

EXP-016 (Q4, prompt 122 897) przerwano na polecenie użytkownika przy 41 472 tokenach: 34%, 799.40 s, średnio 51.88 tok/s. Wszystkie wcześniejsze wyniki i logi zachowano. To wynik częściowy, nie podstawa do ogłoszenia długokontekstowego zwycięzcy Q4.

## Sprzęt i runtime

- 2× RTX 4090; brak NVLink/P2P, topologia SYS, PCIe 4.0 ×8
- Ryzen 7950X3D, 16 aktywnych wątków, jeden NUMA
- driver 595.84; CUDA runtime 13.2; nvcc 13.3
- llama.cpp `d0e6d1ae42ea9934676b9a78d323fc75f3b6b2d6`, Release/CUDA sm_89/graphs/FA
- wymagane `LLAMA_ATTN_ROT_DISABLE=1`; NCCL niedostępny

## Granica wierność/wydajność

`n/a` oznacza brak pomiaru, nie estymację.

| Reprezentacja | Klasa | Rozmiar | VRAM 0/1 | RSS hosta | 131072 | Krótki pp | Długi pp | Krótki tg | Długi tg | MTP | Werdykt |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---|
| BF16 | 16-bit | 329.716 GiB | n/a | n/a | nie | n/a | n/a | n/a | n/a | n/a | brak pamięci |
| Unsloth Q8_0 | Q8 | 175.298 GiB | 23146/23072 MiB | 127.17 GiB | **tak, 122897** | 33.24@529; 42.42@8K | **23.53@122897** | 11.01@529; 10.63@8K | **5.03@122897** | n/a | **maks. praktyczna wierność** |
| Unsloth Q6_K | Q6 | 157.548 GiB | n/a | n/a | nie testowano | n/a | n/a | n/a | n/a | n/a | niższa wierność od działającego Q8 |
| Unsloth Q5 | Q5 | 147.416 GiB | n/a | n/a | nie testowano | n/a | n/a | n/a | n/a | n/a | niższa wierność od działającego Q8 |
| UD-Q4_K_XL | dynamic Q4 | 103.688 GiB | 23000/22908 MiB | 70.90 GiB | start/krótkie: tak; 120K przerwane | 46.53@529; 75.11@8K | 51.88@41472, **częściowe** | 12.69@529; 17.95@8K | n/a | 0.28, wadliwe | speed baseline |
| UD-IQ4_XS | IQ4 | 87.249 GiB | n/a | n/a | tylko microbench | n/a | n/a | n/a | n/a | n/a | opcjonalny speed reference |

RSS oraz VRAM są odrębnymi pomiarami mapowania/offloadu, nie należy ich sumować jako unikalnych bajtów. W finalnym Q8 minimum `MemAvailable` wynosiło 150.38 GiB; oba GPU osiągały 100% użycia.

## Q8 przy rosnącym zajęciu kontekstu

Wszystkie testy działały z `-c 131072 -np 1`.

| Prompt | Prefill tok/s | Decode tok/s |
|---:|---:|---:|
| 529 | 33.24 | 11.01 |
| 8 209 | 42.42 | 10.63 |
| 32 785 | 40.97 | 8.76 |
| 65 553 | 32.83 | 6.94 |
| 102 417 | 26.33 | 5.74 |
| 122 897 | 23.53 | 5.03 |

Każdy ukończony wynik przeszedł test deterministycznego markera. Jakość szeregowano według wierności reprezentacji wag, nie kilku subiektywnych odpowiedzi.

## Leaderboard runtime — niezmieniony Q4

To **MICROBENCH**, a nie finalny serwer 128K.

| Runtime | pp512 | pp2048 | pp8192 | tg128 | tg512 |
|---|---:|---:|---:|---:|---:|
| wdrożeniowy `250b614` | 423.75 | 479.05 | 463.16 | 25.39 | 26.11 |
| upstream `cc83d7b` | 405.59 | 502.50 | 475.46 | 24.69 | 30.48 |
| poprawki Qwen3.8 `dfc7932` | **480.73** | **537.38** | 231.73 | **33.20** | **34.66** |

Rzeczywisty serwer Q4 128K: pp 46.53/75.11 i tg 12.69/17.95 przy 529/8209 tokenach. Test 120K jest nieukończony.

## Rewizje i poprawki

- Oficjalny [Qwen/Qwen3.8-Flash-Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next): sprawdzony HEAD `de4b8e4`; brak późniejszej korekty wag/config/tokenizera.
- [unsloth/Qwen3.8-Flash-Next-GGUF](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF): revision `c8b5954...`.
- Lokalny Q4 ma snapshot `824f539`, lecz wszystkie cztery shardy są bajt-w-bajt identyczne z obecnym HEAD. Nowszy commit dodał imatrix/dokumentację, nie nowe wagi.
- GGUF v3: `qwen4exp`, context 262144, tokenizer `qwen35`, 48 bloków, 512 ekspertów/10 aktywnych, sześć tensorów PLE. Osobny draft head MTP nie jest częścią głównego GGUF.
- Konwerter celowo oddziela MTP. Nie znaleziono błędu nazw/metadanych uzasadniającego pobranie BF16 i świeżą konwersję.

Istotne prace: [PR #27956](https://github.com/ggml-org/llama.cpp/pull/27956), [MTP #27836](https://github.com/ggml-org/llama.cpp/pull/27836), [detached loader](https://github.com/crusaderky/llama.cpp/commit/a82a58a57fc307e5cec0dc68db64d143339be4f2). Poprawki dotyczą runtime (m.in. sparse selection, PLE, cache/rollback, GDN i CUDA RMSNorm), a nie przestarzałej konwersji lokalnego GGUF.

## MTP i dwa GPU

Standardowy loader MTP nie załadował sidecara. Eksperymentalny loader uruchomił 128K, ale dał ~0.28 tok/s, akceptację 12/35=34.3% i niestabilne zakończenie. MTP nie nadaje się teraz do wdrożenia.

Bezpieczny układ to layer split; Q8 obciążał oba GPU do 100%. Tensor split jest wyłączony przez poprawki poprawności dla tej architektury, więc nie ma uczciwego porównania tensor-vs-layer. NCCL nie zbudowano ani nie zmierzono.

## Dokładna rekomendacja

Model (sześć zweryfikowanych shardów z revision `c8b5954...`):

`/srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q8/Q8_0/Qwen3.8-Flash-Next-Q8_0-00001-of-00006.gguf`

```bash
LLAMA_ATTN_ROT_DISABLE=1 \
/srv/ai/benchmarks/qwen38-flash-next-20260829-105917/builds/current-corrected-d0e6d1a/bin/llama-server \
  -m /srv/ai/models/Qwen3.8-Flash-Next-GGUF-20260829-unsloth-Q8/Q8_0/Qwen3.8-Flash-Next-Q8_0-00001-of-00006.gguf \
  -c 131072 -np 1 -dev CUDA0,CUDA1 -sm layer \
  -fit on -fitt 1024,1024 -fitc 131072 \
  -fa on -ctk f16 -ctv f16 -b 512 -ub 128 -t 16 -tb 16 \
  --metrics --host 127.0.0.1 --port 18080
```

Build zawiera jeszcze otwarte poprawki Qwen3.8, więc należy śledzić ich merge/rebase. To jednak dokładnie przetestowany build.

Najlepszy zmierzony kompromis jakości/szybkości to także Q8: Q6/Q5 nie zostały zmierzone. Jeżeli 5 tok/s przy 120K jest za wolne, kolejnym celowym testem jest pojedynczy Q6_K, potem Q5. Q4 pozostaje szybszym baseline, ale nie głównym wdrożeniem przy priorytecie wierności.

## Odpowiedzi końcowe

1. Najwyższa praktyczna wierność: Q8_0. BF16/FP16: nie. FP8/Q8: tak.
2. Pamięć i szybkości każdej poważnej reprezentacji podaje tabela; Q6/Q5 nie mierzono, więc nie wymyślono delt BF16→Q8→Q6→Q5→Q4.
3. Zachowanie przy 32K/64K/100K/120K podaje tabela skalowania.
4. MTP nie zbliżył wysokiej precyzji do Q4; brak rekomendowanej konfiguracji MTP.
5. Optymalny bezpieczny multi-GPU: layer split + fit. Tensor split i NCCL nie mają wyniku.
6. Aktualne poprawki llama.cpp są materialne dla poprawności i Q4 microbench, lecz rozwojowe.
7. Obecny Unsloth Q4 jest aktualny i dobry jako speed baseline, nie jako model maksymalnej wierności.
8. Nie ma nowszych shardów Q4 ani dowodu na lepszą bieżącą konwersję.
9. Świeżej konwersji nie wykonano, bo brak przesłanki, że zmieni model; nie można twierdzić, że przewyższa pobrany GGUF.
10. Najwyższy pełny decode/prefill zależy od kontekstu: Q4 jest szybszy w krótkim screenie; Q8 jest jedynym wysokiej wierności finalistą z ukończonym 120K.
11. Dokładny model i komenda wdrożeniowa są powyżej.

## Zachowane dane

- `results/experiments.jsonl` — ukończone rekordy
- `logs/EXP-*-responses.json` — odpowiedzi
- `logs/EXP-*-gpu-telemetry.jsonl` — telemetria
- `logs/EXP-*-server-stderr.log` — logi, w tym częściowy EXP-016
- `scripts/` — harness

