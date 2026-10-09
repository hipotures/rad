#!/usr/bin/env python3
"""Create a new minimal arithmetic package from the frozen integrated identity.

Copies exact selected finite fixture bytes; does not run any optimizer or
publish to an upstream repository. Apache-2.0; OpenAI GPT-6.1 Sol assistance.
"""
from hashlib import sha256
from pathlib import Path
import argparse
import json
import shutil
import sys

if hasattr(sys,'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sprint',type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--receipt',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Package must be new')
    config=json.loads(args.config.read_bytes());receipt=json.loads(args.receipt.read_bytes())
    if receipt['config_sha256']!=sha256(args.config.read_bytes()).hexdigest():
        raise ValueError('Receipt and source identity differ')
    args.output.mkdir(parents=True)
    records={}
    for key,name in [('bit','bit-profile.json'),('physical','complex-profile.json'),
                     ('scalar','complex-scalar-inventory.json'),('bit_frames','bit-frames.json'),
                     ('complex_frames','complex-frames.json'),('complex_pairs','complex-pairs.json')]:
        item=config['inputs'][key];raw=(args.sprint/item['path']).read_bytes()
        if sha256(raw).hexdigest()!=item['sha256']:raise ValueError('Changed frozen input')
        sub='fixtures' if 'frames' in key or 'pairs' in key else 'inputs'
        destination=args.output/sub/name;destination.parent.mkdir(exist_ok=True)
        destination.write_bytes(raw)
        records[key]=dict(path=str(destination.relative_to(args.output)),bytes=len(raw),sha256=item['sha256'])
    math=(args.sprint/'agents/transfer/code/check_balanced_composition.py').read_text().split('\ndef read_pinned(')[0]
    math=math.replace('Independent exact balanced composition on source-bound supplier profiles.',
        'Exact arithmetic for the distinct balanced lifetime/fused168-170 identity.')
    (args.output/'transfer_math.py').write_text(math+'\n')
    verifier=(args.sprint/'agents/transfer/code/verify_lifetime_fused_portable.py').read_bytes()
    (args.output/'verify_transfer.py').write_bytes(verifier)
    for name in ('transfer_math.py','verify_transfer.py'):
        raw=(args.output/name).read_bytes()
        records[name]=dict(path=name,bytes=len(raw),sha256=sha256(raw).hexdigest())
    upstream_snapshots = {
        'pr163-15c702a': ('chafreaky/integer-mult-bounds','15c702a929b7d640107a95e196186ad74e876c82'),
        'pr165-7518fed': ('chafreaky/integer-mult-bounds','7518fed2688baf25c7c32bae32674f3334b517da'),
        'pr168-98c115b': ('eumemic/integer-mult-bounds','98c115b53742b6613ad630de4d493f37b0119da7'),
        'pr169-4895ba1': ('GamingPuzzled/integer-mult-bounds','4895ba1104cedc7908b6d6ba64fdd6290e0ed7ae'),
        'pr170-29892e2': ('huxint/integer-mult-bounds','29892e2fe8a90714ef61bd8cbfb1a74bec6f8fd4'),
        'pr171-89d0c75': ('jon314159/integer-mult-bounds','89d0c75f8bf97131db21bc610e7546b699afcb9a'),
    }
    def public_record(key,item,section):
        result={name:item[name] for name in ('bytes','sha256')}
        path=item['path']
        if path.startswith('work/frontier/'):
            pieces=path.split('/')
            repository,commit=upstream_snapshots[pieces[2]]
            result.update(repository=repository,commit=commit,source_file='/'.join(pieces[5:]))
        else:
            component='binary' if '/bit/' in path else ('independent' if '/baseline/' in path else 'complex')
            if section=='inputs' and key.startswith('bit'):component='binary'
            result.update(component=component,name=key,filename=Path(path).name,
                recovery='Frozen component fixtures and the source-closed RaD scientific record indexed by the original author configuration SHA256.')
        return result
    public_bindings={key:value for key,value in config.items()
        if key not in ('inputs','sources','closure_requirements')}
    public_bindings['inputs']={key:public_record(key,item,'inputs') for key,item in config['inputs'].items()}
    public_bindings['sources']={key:public_record(key,item,'sources') for key,item in config['sources'].items()}
    public_bindings['source_record_count']=len(config['sources'])
    public_bindings['input_record_count']=len(config['inputs'])
    public_bindings['author_config_sha256']=sha256(args.config.read_bytes()).hexdigest()
    public_bindings['metadata_scope']='Public provenance normalized to upstream immutable refs and component identities; original RaD path-bearing configuration is preserved separately by its SHA256.'
    data=dict(candidate_id=config['candidate_id'],files=records,
        parameters={key:config[key] for key in ('coarse','atom','complex_saving','phase_stop','backoff','strict_weakening','kappa',
            'bit_next_grid_step','complex_next_grid_step','comparison_public_head','comparison_public_kappa','required_publication_ratio')},
        expected_bit_inventory=config['expected_bit_inventory'],expected_bit_roles=config['expected_bit_roles'],
        expected_complex_inventory=config['expected_complex_inventory'],
        scientific_source_bindings=public_bindings,
        author_receipt_sha256=sha256(args.receipt.read_bytes()).hexdigest(),
        finite_prerequisites=config['finite_prerequisites'],inherited_hypotheses=config['inherited_hypotheses'],
        runtime='Python standard library; tested Python3.14.4. This is arithmetic-only; full finite replay is separate.',
        scope='New identity, complete paid moment/transfer arithmetic, exact selected-plan byte binding. This package does not infer word, projector or reflected geometry correctness from saved flags.')
    (args.output/'transfer-inputs.json').write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
    shutil.copyfile(args.sprint/'agents/transfer/publication/joint-balanced-frames/LICENSE',args.output/'LICENSE')
    print('Prepared distinct arithmetic package '+str(args.output))


if __name__=='__main__':main()
