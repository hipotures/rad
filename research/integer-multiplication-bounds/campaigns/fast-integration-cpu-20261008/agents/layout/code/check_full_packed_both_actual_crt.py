#!/usr/bin/env python3
"""Attach actual physical CRT input/output programs to the packed-both pipeline.

This driver keeps the packed arithmetic wrapper and its independent integer
oracle intact. Two-prime trees contain ordinary top maps; actual F_u execution
on longer trees is evidenced separately, never inferred from this driver.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


parser=argparse.ArgumentParser()
for name in ['packed-wrapper','crt-api','config','output']:parser.add_argument('--'+name,required=True)
args,rest=parser.parse_known_args()
config=json.loads(Path(args.config).read_text());out=Path(args.output)
sys.path.insert(0,str(Path(args.crt_api).parent))
api=load('frozen_actual_crt_api',args.crt_api)
wrapper=load('frozen_packed_both_wrapper',args.packed_wrapper)
original_load=wrapper.load;state={'input_programs':[],'conversions':[],'input_digits':[],'recovered':[]}


def install(producer):
    reference=producer.crt_checked_source;original_run=producer.run_case

    def actual_input(digits,primes,q,digit_bits):
        coefficients=list(digits)+[0]*(math.prod(primes)-len(digits));state['input_digits'].append(list(digits))
        receipt=api.transform_payload(primes,coefficients,reverse_check=False,emit_stdout=False)
        binary=receipt.pop('output');caps=[1<<(s-1).bit_length() for s in primes];result=[]
        for key in producer.addresses(primes):
            index=0;stride=1
            for coordinate,capacity in zip(key,caps):index+=coordinate*stride;stride*=capacity
            result.append((binary[index]<<(q-digit_bits-2),0))
        assert result==reference(digits,primes,q,digit_bits)
        state['input_programs'].append(receipt)
        state['conversions'].append({'operation':'paid known-axis-field reversal and padding filter',
                                    'payload_reads':len(binary),'payload_writes':len(result)})
        (out/f'actual-crt-input-{len(state["input_programs"])}.json').write_text(json.dumps(receipt,indent=2)+'\n')
        return result

    def actual_run(parameters):
        transform=producer.source_transform
        def capture(*positional,**keywords):
            result=transform(*positional,**keywords)
            if keywords.get('opposite'):state['recovered'][:]=result
            return result
        producer.source_transform=capture
        result=original_run(parameters)
        primes,q=parameters['source'],parameters['q'];S=math.prod(primes)
        caps=[1<<(s-1).bit_length() for s in primes];binary=[0]*math.prod(caps)
        scale=S*S*(1<<(2*parameters['digit_bits']+4))
        for key,value in zip(producer.addresses(primes),state['recovered']):
            index=0;stride=1
            for coordinate,capacity in zip(key,caps):index+=coordinate*stride;stride*=capacity
            binary[index]=producer.nearest_signed_integer(value[0]*scale,1<<q)
        receipt=api.inverse_payload(primes,binary,emit_stdout=False)
        scalar=receipt.pop('coefficients');padded=receipt.pop('output')
        oracle=producer.direct_integer_convolution(*state['input_digits'],S)
        assert scalar==oracle and padded[:S]==oracle and not any(padded[S:])
        receipt['coefficient_sha256']=hashlib.sha256(json.dumps(scalar).encode()).hexdigest()
        state['final_inverse']=receipt
        state['conversions'].append({'operation':'paid known-axis-field reversal and zero embedding before actual inverse',
                                    'payload_reads':S,'payload_writes':len(binary)})
        (out/'actual-crt-final-inverse.json').write_text(json.dumps(receipt,indent=2)+'\n')
        return result
    producer.crt_checked_source=actual_input;producer.run_case=actual_run


def patched_load(name,path):
    value=original_load(name,path)
    if name=='full_arithmetic':install(value)
    return value


wrapper.load=patched_load
sys.argv=[args.packed_wrapper,'--config',args.config,'--output',args.output,*rest]
wrapper.main()
p=out/'certificate.json';result=json.loads(p.read_text())
result['status']='complete genuine packed Gaussian pipeline and actual CRT input/output programs passed'
result['actual_crt_input_programs']=state['input_programs'];result['actual_final_crt_inverse']=state['final_inverse']
result['paid_crt_layout_conversions']=state['conversions']
result['crt_source_hashes']={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in
    [('API',Path(args.crt_api)),('compiler',Path(args.crt_api).parent/'compiled_crt_pipeline_bankleaf.py'),
     ('guards',Path(args.crt_api).parent/'crt_guard_controls.py'),('driver',Path(__file__))]}
result['limitations'].append('A two-prime tree uses ordinary top maps; actual multi-target F_u execution is not claimed by this two-axis run.')
p.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'compiled_batches':[len(r['compiled_batches']) for r in state['input_programs']]}))
