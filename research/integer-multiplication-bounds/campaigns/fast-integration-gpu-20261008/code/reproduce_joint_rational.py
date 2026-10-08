#!/usr/bin/env python3
"""Rebuild the selected interval words, exact local profiles and composition.

Public snapshots are acquired separately by fetch_interval_joint_sources.py.
The retained complete DATA proof is re-used through its exact basis-interface
binding; its independent full-family generator is documented separately.
"""
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--snapshot',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True)
    args = p.parse_args()
    root = args.snapshot.resolve()
    work = args.work.resolve()
    assert not work.exists()
    work.mkdir(parents=True)
    campaign = Path(__file__).resolve().parents[1]
    def run(command, log):
        with (work/log).open('wb') as f:
            subprocess.run(list(map(str,command)),stdout=f,stderr=subprocess.STDOUT,check=True)
    graph_file = root/'research/pair-assembly/pair_graph.py'
    assert sha256(graph_file.read_bytes()).hexdigest() == '3d47e89d2649c90800a276bdd0480131def50e0bdf92c122a19494b55bf17420'
    spec = importlib.util.spec_from_file_location('fresh_interval_scalar',graph_file)
    graph = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(graph)
    scalar = dict(status='PASS FRESH PINNED INTERVAL SCALAR DAG RECONSTRUCTION',
                  source_revision='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',rows=[])
    expected = {23:'0607a53aa32d9d0e246dd168c7b6dc660e7c485852f3421bc1dc4b98739552cb',
                25:'605e6786ba7af4a89f559b17dfc623471a1d912a477bdb9f2c938d3472ee0bd8'}
    for h in [23,25]:
        row = graph.graph(h).verify()
        assert row['circuit_sha256'] == expected[h]
        assert row['all_partial_outputs_exact'] and row['all_additions_disjoint'] and row['every_node_has_common_point']
        scalar['rows'].append(dict(h=h,scalar=row,exact_original_pinned_statistics=True))
    scalar_path = work/'scalar.json'
    scalar_path.write_text(json.dumps(scalar,indent=2)+'\n')
    run([sys.executable,'-B',campaign/'agents/graph/code/joint_region_search_v3.py',
         '--source',root,'--work',work/'source-only','--output',work/'source-only.json',
         '--dimensions',23,25,'--workers',1,'--policies','baseline','--rank-deltas',1,'--sweeps',1,'--limit',0], 'fresh-compiler.log')
    native = work/'parameter_joint_word_profiles'
    run(['g++','-O3','-std=c++20',campaign/'agents/geometry/code/parameter_joint_word_profiles.cpp','-o',native], 'build.log')
    axes, words = [], []
    for h,basis in [(23,'beta:-1:1'),(25,'beta:1:21')]:
        binary = work/f'h{h}.bin'
        word = root/f'research/pair-assembly/frame/frame-word-{h}.json.gz'
        run([sys.executable,'-B',campaign/'agents/graph/code/joint_word_check_v4.py','--word',word,'--transitions',binary],f'h{h}-independent-word.log')
        words.append(Path(str(binary)+'.review.json'))
        run([sys.executable,'-B',root/'scripts/experiments/binary_frame_profile_prepare.py',word,binary],f'h{h}-prepare.log')
        profile, audit = work/f'h{h}-profile.json', work/f'h{h}-matrix-audit.json'
        run([native,binary,basis,profile,audit],f'h{h}-profile.log')
        def digest(path):
            return sha256(path.read_bytes()).hexdigest()
        axes.append(dict(config=dict(case_id=f'h{h}',h=h,basis=basis,transitions=str(binary)),
            profile=json.loads(profile.read_text()),profile_path=str(profile),profile_sha256=digest(profile),
            transition_audit=str(audit),transition_audit_sha256=digest(audit),input_binary_sha256=digest(binary)))
    axes_path = work/'axes.json'
    axes_path.write_text(json.dumps(axes,indent=2)+'\n')
    stock = work/'scalar-stock.json'
    run([sys.executable,'-B',campaign/'agents/scout/code/audit_joint_scalar_stock.py','--snapshot',root,'--output',stock],'stock.log')
    data = campaign/'agents/scout/gpu-parameter-results/mixed-fixed23-negative25-data-input-audit-20261008T1800.json'
    assembly = root/'references/frame-compiler/pr48/research/copied-fixed/balanced_assembly.py'
    certificate = work/'certificate.json'
    run([sys.executable,'-B',campaign/'code/compose_joint_word_profiles.py','--axes',axes_path,
         '--phase',campaign/'fixtures/phase-pr36.json','--baseline',root/'research/pair-assembly/frame/frame-certificate.json',
         '--assembly',assembly,'--geometry',data,'--output',certificate],'composition.log')
    run([sys.executable,'-B',campaign/'code/bind_joint_word_certificate.py','--axes',axes_path,'--certificate',certificate,
         '--data',data,'--stock',stock,'--scalar',scalar_path,'--assembly',assembly,'--words',*words,
         '--output',work/'independent-binding.json'],'binding.log')
    print(json.dumps(dict(status='PASS FRESH SOURCE/WORD/PROFILE/COMPOSITION REPRODUCTION',
                         certificate=str(certificate),kappa=json.loads(certificate.read_text())['kappa'])))


if __name__ == '__main__':
    main()
