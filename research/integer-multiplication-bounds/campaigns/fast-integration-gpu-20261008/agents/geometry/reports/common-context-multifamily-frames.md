# Common-context selection among actual signed frame families

The selected finite network retains the scalar DAG, paid roles and literal XOR
word of the intermediate interval-strip joint compiler. It chooses a different
actual containing positive frame family independently for each common point.
This is an exact finite candidate; the assembled conditional construction is
accepted only by the separate source/DATA/stock/moment/assembly binder.

The source construction is Avi Eisenberg's PR #62 at
`ad0f25ff7b23cff7f08ad237c2254e6ecf74257e`, using eumemic's PR #57 joint
compiler. Alejandro Zarzuelo Urdiales contributed PR #61's parameter refinement.
The source partitions, signed positive frames and selected containing region
assignments extend earlier work by Rohan Arun and the prior whole-chain and
source-partition researchers. This result does not attribute the complete
interval-strip or joint-compiler architecture to those later extensions.
AI assistance was used in the research and implementation.

## Why the choices can be combined

`mix_common_frame_families.py` realizes complete assignments, rather than
splicing child-width histograms. Each global family is obtained with the frozen
component constructor and its minimal forward closure. Every changed frame
with a single forced common coordinate has outgoing frame-containment edges
only to that same common coordinate. Frames with two or three forced
coordinates retain exactly their original rational spaces in every selected
family. Consequently choosing one family at each common coordinate preserves
all original-to-selected and selected-to-maximal inclusions and every actual
transition inclusion. The implementation checks these statements on every
frame and literal transition, constructs the resulting physical word, and
replays it independently in both dirty orientations.

The h23 axis uses `unbalanced12` at common coordinates 20, 21 and 22 and
`balanced12` elsewhere. The h25 axis uses `unbalanced12` at 0, 1, 2, 22 and 24,
`core18` at 11, 13, 15 and 17, and `balanced12` elsewhere. The bases are
`beta:1:15` and `beta:7:207`, respectively. Coordinate permutations, parent
hashes and every choice are fixed in
`../configs/selected-common-multifamily-portable.json`.

The roles remain R23=27,719 and R25=36,353. All XORs, reclamation operations,
source injection frames and copied-center spaces are unchanged. Every actual
selected transition is profiled again. Ordered projector rooks and contiguous
recursive child widths are not inferred from dimension or total rank alone.

## Compact evidence

- Fresh public-source construction and byte equality:
  `../../graph/results/joint-common-multifamily-Q-source-only-23.json` and
  `../../graph/results/joint-common-multifamily-Q-source-only-25.json`.
- Selected exact native axes:
  `../results/selected-intermediate-Q-common-multifamily-axis-23.json` and
  `../results/selected-intermediate-Q-common-multifamily-axis-25.json`.
- Ninety-six independent Fraction controls using explicit column matrices and
  the H0 Gram inverse, ordered pivots and integer-minor bounds:
  `../results/joint-common-multifamily-controls-20261008T2115.json`.
- Source, center, full 4,073,300-pair DATA and scalar stock binding:
  `../../scout/gpu-parameter-results/signed-common-multifamily-Q-one15-seven207-source-center-data-scalar-stock-20261008T2117.json`.

The signed transition hashes are
`64b9882983cc352a29df7e3e8ae09dadd3d6e81d6e6b45f2ab6fb7fe6c451d8d` (h23)
and `c212ef3b04dbfaa6041ac37c562d2a8e81b37f313ad4b47a82a8e25134674a75`
(h25). The selected h25 profile is the 7/207 profile; the same word also has a
different 1/21 discovery profile, which must not replace it in assembly.

## Regeneration from public source

The fifteen authored dependencies and their SHA256 identities are fixed in
`../configs/selected-common-multifamily-dependencies.json`. Requirements are
Python 3.10 or newer, a C++17 compiler, Boost multiprecision headers, Git and the
GitHub CLI. Large public snapshots and regenerated words belong outside the
checkout. Fetch the public repository automatically and freeze the pinned
commit before running the following commands from the campaign directory:

```bash
c++ -O3 -std=c++17 agents/geometry/code/signed_joint_word_profiles.cpp -o "$REPRO_WORK/signed_joint_word_profiles"
python3 - "$PUBLIC_SOURCE" "$REPRO_WORK" <<'PY'
import json, pathlib, subprocess, sys
source, work = map(pathlib.Path, sys.argv[1:])
manifest = json.loads(pathlib.Path('agents/geometry/configs/selected-common-multifamily-dependencies.json').read_text())
choices = json.loads(pathlib.Path(manifest['choices_file']).read_text())
controls = []
for axis, config in zip(manifest['selected_axes'], choices):
    h = axis['h']
    axis_work = work / f'h{h}'
    subprocess.run([
        sys.executable, manifest['source_constructor'], '--source', str(source),
        '--work', str(axis_work), '--output', str(work / f'source-{h}.json'),
        '--h', str(h), '--budget', str(3584 if h == 23 else 5120),
        '--order', *map(str, config['parent']['Q']),
        '--choices-file', manifest['choices_file'],
        '--expected-parent-sha256', config['parent']['word_sha256'],
        '--expected-word-sha256', axis['word_sha256']], check=True)
    transition = axis_work / 'signed-transitions.bin'
    import hashlib
    assert hashlib.sha256(transition.read_bytes()).hexdigest() == axis['transition_sha256']
    audit = axis_work / 'transition-audit.json'
    subprocess.run([str(work / 'signed_joint_word_profiles'), str(transition),
                    axis['basis'], str(axis_work / 'profile.json'), str(audit)], check=True)
    controls.append(dict(case_id=f'h{h}-regenerated', binary=str(transition),
                         basis=axis['basis'], audit=str(audit)))
(work / 'fraction-controls.json').write_text(json.dumps(controls, indent=2) + '\n')
PY
python3 agents/geometry/code/review_signed_joint_word_profiles.py --input "$REPRO_WORK/fraction-controls.json" --work "$REPRO_WORK/fraction" --output "$REPRO_WORK/fraction-receipt.json" --samples 48
```

Use a fresh `REPRO_WORK` directory; the source constructors reject reused axis
directories and receipt filenames. `PUBLIC_SOURCE` must name the immutable
public source at the pinned revision, not an older main-line construction.
The two source constructors and the native/independent exact paths were
exercised for the retained receipts above. The convenience command sequence
does not itself re-run the separate all-source-pair, recurrence or assembly
binder.

The physical address conclusion retains the explicit inherited rational gauge,
linear routing and fixed-tape premises. The finite F2 word restores every
arbitrary dirty role component; its extension to address arrays uses the
dimension-independent linear dirty-echo lemma. Neither role-basis counts nor
unchanged scalar outputs by themselves prove a new address projector identity
or eliminate any inherited all-size analytic assumption.
