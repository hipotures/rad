#!/usr/bin/env python3
"""Bound paid joint XOR words and verify the retained phase/row constants."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path


def record(path):
    data = path.read_bytes()
    return {'path':str(path),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    assert args.snapshot.name == 'pr62-ad0f25ff7b23cff7f08ad237c2254e6ecf74257e'
    source = args.snapshot/'research/pair-assembly/balanced_assembly.py'
    spec = importlib.util.spec_from_file_location('pinned_scalar_arithmetic',source)
    arithmetic = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(arithmetic)
    certificate_path = args.snapshot/'research/pair-assembly/frame/frame-certificate.json'
    certificate = json.loads(certificate_path.read_text())
    bridge = certificate['finite_bridge']
    validated = arithmetic.validate_bridge(bridge)
    compiler_path = args.snapshot/'research/pair-assembly/frame/frame-compiler.json'
    compiler = json.loads(compiler_path.read_text())
    N = 4073300
    axes = []
    for h in (23,25):
        path = args.snapshot/f'research/pair-assembly/frame/frame-word-{h}.json.gz'
        packed = path.read_bytes();raw = gzip.decompress(packed);word = json.loads(raw)
        saved = compiler['axes'][str(h)]
        assert hashlib.sha256(packed).hexdigest() == saved['gzip_sha256']
        assert hashlib.sha256(raw).hexdigest() == saved['word_sha256']
        assert word['h'] == h and word['v'] == len(word['sources'])
        v = word['v'];assert N%v == 0
        count = 4*len(word['ops'])+2*len(word['scatter'])+2*v
        assert count == saved['replay']['word_length']
        axes.append({'h':h,'v':v,'invocations':N//v,'roles':word['R'],
                     'mixer_xors':len(word['ops']),'scatter_xors':len(word['scatter']),
                     'source_xors':v,'full_local_XOR_word':count,
                     'weighted_full_local_XOR_word':count*(N//v),
                     'additional_copied_center_groups':2*h*(N//v),
                     'word':record(path),'raw_word_sha256':hashlib.sha256(raw).hexdigest()})
    paid_xors = sum(x['weighted_full_local_XOR_word'] for x in axes)
    centers = sum(x['additional_copied_center_groups'] for x in axes)
    # A whole DATA bank exchange can be treated as one grouped permutation.
    # Three XORs per exchanged pair give an even more conservative bound.
    bit_scalar_bound = paid_xors+3*N+centers
    phase_scalar_bound = validated['complex']['scalar_group_upper']
    assert paid_xors == 2941290600 and centers == 194350
    assert bit_scalar_bound == 2953704850 < phase_scalar_bound == 4793351472
    for key in ('W','m','maxchild'):
        assert validated['bit'][key] <= validated['complex'][key]
    bit_mass = certificate['bit']['total_rank']
    assert bit_mass <= validated['complex']['s']
    bit_literal_bound = (2*bit_scalar_bound*validated['bit']['W']**2
                         +8*bit_mass+4*validated['bit']['W']+4+32*validated['bit']['m'])
    assert bit_literal_bound < validated['semantic']['literal_charge'] < validated['semantic']['E']
    row_coefficient = sum(validated[k]['wire_bits']*validated[k]['halving_degree'] for k in ('bit','complex'))
    assert row_coefficient == bridge['rows']['coefficient'] == 852
    assert bridge['rows']['degree'] == 2000
    assert F(bridge['rows']['degree'])-F(51,25)*row_coefficient == F(6548,25)>0
    sources = [certificate_path,compiler_path,source,
               args.snapshot/'scripts/copied_centers_network.py',
               args.snapshot/'notes/batched-bit-rows.tex',
               args.snapshot/'references/semantic-bulk/pr23/semantic-bulk-17-note.tex']
    result = {'created_utc':datetime.now(timezone.utc).isoformat(),
              'status':'PASS PAID JOINT BIT SCALAR OVERHEAD AND RETAINED PRODUCT STOCK',
              'scope':'Exact pinned PR62 joint words; counts and source hashes are bound. All-role semantic recovery remains the separately verified compiler contract. This does not certify a different word without recounting it.',
              'source':record(Path(__file__)),'consumed_sources':[record(p) for p in sources],
              'axes':axes,'N':N,'paid_local_XOR_steps':paid_xors,
              'additional_center_groups':centers,'global_bank_exchange_XOR_bound':3*N,
              'conservative_bit_scalar_upper':bit_scalar_bound,
              'retained_phase_scalar_upper':phase_scalar_bound,
              'scalar_domination_gap':phase_scalar_bound-bit_scalar_bound,
              'bit_rank_mass':bit_mass,'bit_literal_upper':bit_literal_bound,
              'retained_phase_literal_charge':validated['semantic']['literal_charge'],
              'retained_E':validated['semantic']['E'],
              'literal_domination_gap':validated['semantic']['literal_charge']-bit_literal_bound,
              'row_stock':bridge['rows'],
              'interpretation':'The original PR23 Gaussian literal/precision guard is a complex-phase guard. The bit moment recurrence separately pays its entire fixed finite scalar schedule in additive constant C. If a common conservative scalar bound is desired, max(G_phase,G_bit)=G_phase and W_bit<=W_phase, m_bit<=m_phase, s_bit<=s_phase imply the retained literal/E constants dominate both schedules. No XOR is free. Product row stock uses only the two role volumes and halving depths and is independent of scalar gate count.',
              'remaining_scope':'Changing the scalar word, designated copied-center interface, or physical role count requires recounting the affected quantities. Coherent coordinate relabeling of this identical word preserves its count.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','paid_local_XOR_steps','conservative_bit_scalar_upper','retained_phase_scalar_upper','scalar_domination_gap')}))


if __name__ == '__main__':
    main()
