# Reproduce the independent finite review

Run from the campaign directory. Keep Python assertions enabled; use a GCC or
Clang supporting C++17 and unsigned 128-bit arithmetic. Each native job has
one thread. Obtain the exact tested source commit from `input-manifest.json`,
validate the acquisition identity, and copy it to a fresh ignored execution
directory. The following relative shell variables are task-specific examples.

```
SCOUT_CODE=joint-frame/agents/scout/code
SCOUT_RUN=work/joint-frame/scout/reproduction
SCOUT_SOURCE=work/joint-frame/scout/reproduction/source
mkdir -p "$SCOUT_RUN/original-profiler"
cp "$SCOUT_CODE/integer_crt_profiles_v1.cpp" "$SCOUT_RUN/original-profiler/integer_crt_profiles.cpp"
cp "$SCOUT_CODE/integer_crt_certificate_v1.py" "$SCOUT_RUN/original-profiler/integer_crt_certificate.py"
g++ -O3 -std=c++17 "$SCOUT_RUN/original-profiler/integer_crt_profiles.cpp" -o "$SCOUT_RUN/original-profiler/profiles"
python3 -B "$SCOUT_CODE/check_pr58_word.py" --word "$SCOUT_SOURCE/certificates/joint-dual-word-23.json.gz" --transitions "$SCOUT_RUN/word23.bin" --output "$SCOUT_RUN/physical23.json"
python3 -B "$SCOUT_CODE/check_pr58_word.py" --word "$SCOUT_SOURCE/certificates/joint-dual-word-25.json.gz" --transitions "$SCOUT_RUN/word25.bin" --output "$SCOUT_RUN/physical25.json"
python3 -B "$SCOUT_RUN/original-profiler/integer_crt_certificate.py" --binary "$SCOUT_RUN/original-profiler/profiles" --transitions "$SCOUT_RUN/word23.bin" --profiles "$SCOUT_RUN/profile23.json" --output "$SCOUT_RUN/crt23.json"
python3 -B "$SCOUT_RUN/original-profiler/integer_crt_certificate.py" --binary "$SCOUT_RUN/original-profiler/profiles" --transitions "$SCOUT_RUN/word25.bin" --profiles "$SCOUT_RUN/profile25.json" --output "$SCOUT_RUN/crt25.json"
python3 -B "$SCOUT_CODE/check_joint_moment.py" --profile23 "$SCOUT_RUN/profile23.json" --profile25 "$SCOUT_RUN/profile25.json" --physical23 "$SCOUT_RUN/physical23.json" --physical25 "$SCOUT_RUN/physical25.json" --inherited-certificate "$SCOUT_SOURCE/certificates/joint-dual-kappa.json" --assembly "$SCOUT_SOURCE/references/frame-compiler/pr48/research/copied-fixed/balanced_assembly.py" --saving 1187740349/25000000000000 --kappa 475073569/10000000000000 --output "$SCOUT_RUN/complete-moment.json"
```

The expected baseline values are R23=30790, R25=40446, W=150593466,
rank mass 86589396050 and paid wrapped XOR count 2206597276. Both orientations
and all role frame paths must pass. Every corner is checked at twelve proved
prime moduli. The resulting block vectors must equal the pinned baseline.

For a changed word, use `check_candidate_job.py`, passing its physical word,
dimension, the independently reviewed partner profile/physical receipt and
the same pinned inherited arithmetic paths. Its saved protocol has every exact
ordered command. It creates new output paths and never overwrites a successful
run. The exact source and input hashes are retained at each step.

For cost-directed joint synthesis, compile the current optional-export C++
profiler, run `prepare_joint_edge_costs.py` separately for h23/h25, then run
`joint_mincost_compile.py` on those certified tables. The tables bind the exact
ordered `(block,use,input_index)` candidate stream. The selected occurrence
stream and changed word are complete execution text artifacts; publication or
deterministic regeneration is required for a selected new witness. The
pre-reclamation additive objective is not treated as the final reclaimed
moment. That moment is regenerated from the complete physical word.

What was exercised: both full pinned dimensions, all source/target/dirty basis
columns in both orientations, exact role-level transition reconstruction,
all twelve-modulus corner profiles, unchanged stored-profile equality and the
complete rational controller/assembly for the two changed high-rank words.
The broader `make verify` historical sweep was intentionally outside scope.
