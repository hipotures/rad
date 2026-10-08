#!/usr/bin/env python3
"""Complete coefficient recovery with actual packed forward AND inverse cells.

All unselected inverse outputs use an explicitly charged full matrix repair
reference. This finite prototype does not infer sparse asymptotic density.
"""
import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import sys
from pathlib import Path
from time import perf_counter

import gmpy2
import mpmath as mp


def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result)
    return result


def encode(point,base):
    value=0
    for coordinate in point:value=value*base+coordinate
    return value


def pack(rows,slot_bytes,degree):
    buffer=bytearray((degree+1)*slot_bytes)
    for index,value in rows:
        buffer[index*slot_bytes:(index+1)*slot_bytes]=value.to_bytes(slot_bytes,'little')
    return gmpy2.mpz(int.from_bytes(buffer,'little'))


def compress(data,source,target,matrices,alpha,q,side,radius,producer,laurent,ledger):
    assert len(source)==2 and side%2==0
    started=perf_counter();d=len(source);u=alpha**2
    reference=data;current=target
    for axis in reversed(range(d)):
        reference,current=producer.real_axis_pass(reference,current,axis,matrices[axis][1],q+64,ledger)
    assert current==source
    selectors=[axis[2]['selector'] for axis in matrices]
    selected=[data[producer.encode(tuple(selectors[i][j] for i,j in enumerate(point)),target)]
              for point in producer.addresses(source)]
    length=side+2*radius;low=-side//2-radius;high=low+length-1
    theta=[mp.mpf(t-s)/s for s,t in zip(source,target)]
    reserve=int(mp.ceil(sum(mp.pi*u*th*max(low*low,high*high)/mp.log(2) for th in theta)))
    p=q+reserve+80;scale=1<<p
    # B0 contains this common contraction; the final source transform later
    # multiplies by 2^(2ud). The local N^-1 error target is paid accordingly.
    normalizing_bits=(2*u-1)*d
    inverse_target=max(32,q-normalizing_bits+4)
    base=length+2*radius
    input_degree=encode((length-1,)*d,base)
    kernel_degree=encode((2*radius,)*d,base)
    assert input_degree+kernel_degree<base**d
    slot_bits=8*math.ceil((2*p+math.ceil(math.log2(length**d))+16)/8);slot_bytes=slot_bits//8
    kernel_cache={};partial={};cells=0;products_count=0;reads=0;maximum_operand=0
    eligible_cache={}

    def eligible(axis,origin):
        key=(axis,origin)
        if key in eligible_cache:return eligible_cache[key]
        s,t=source[axis],target[axis]
        if not 0<=origin+low<=origin+high<s:
            eligible_cache[key]=None;return None
        if any(selectors[axis][origin+a]!=selectors[axis][origin]+a for a in range(low,high+1)):
            eligible_cache[key]=None;return None
        beta=mp.mpf(t*origin-s*selectors[axis][origin])/s
        A=mp.pi*u*(mp.mpf(t)/s-2*abs(beta))-mp.log(4)
        if A<=0:
            eligible_cache[key]=None;return None
        tail=3*mp.exp(-A*radius)
        # Necessary coordinate screen, followed by the complete tensor screen.
        if tail*mp.mpf(2)**reserve>=mp.mpf(2)**(-inverse_target):
            eligible_cache[key]=None;return None
        eligible_cache[key]=(beta,tail);return beta,tail

    for shift in (0,side//2):
        axis_origins=[]
        for axis,s in enumerate(source):
            axis_origins.append([j for j in range(side//2+shift,s,side) if eligible(axis,j)])
        for origins in itertools.product(*axis_origins):
            infos=[eligible(i,j) for i,j in enumerate(origins)]
            D_bound=mp.exp(sum(mp.pi*u*max(abs(infos[i][0]+theta[i]*x)
                          for x in (-side//2,side//2-1))**2 for i in range(d)))
            if 4*D_bound*mp.mpf(2)**reserve*sum(value[1] for value in infos)>=mp.mpf(2)**(-inverse_target):continue
            kernels=[]
            for i,origin in enumerate(origins):
                key=(i,origin)
                if key not in kernel_cache:
                    kernel_cache[key]=laurent.regular_inverse_kernel(source[i],target[i],u,origin,radius,
                                          target_bits=inverse_target,reserve_bits=reserve)
                kernels.append(kernel_cache[key])
            norm=math.prod(1/(1-k['unweighted_perturbation_row_bound'])+k['analytic_kernel_row_error'] for k in kernels)
            tail=norm*D_bound*mp.mpf(2)**reserve*sum(k['analytic_kernel_row_error'] for k in kernels)
            assert tail<mp.mpf(2)**(-inverse_target),tail
            input_rows=[[[],[]],[[],[]]]
            for a in itertools.product(range(length),repeat=d):
                local=tuple(x+low for x in a)
                point=tuple(origin+x for origin,x in zip(origins,local))
                value=selected[producer.encode(point,source)]
                diagonal=int(mp.nint(mp.exp(-sum(mp.pi*u*th*x*x for th,x in zip(theta,local)))*scale))
                for component,word in enumerate(value):
                    weighted=producer.tz((word<<(p-q))*diagonal,p)
                    input_rows[component][weighted<0].append((encode(a,base),abs(weighted)))
                reads+=1
            kernel_rows=[[],[]]
            for hp in itertools.product(range(2*radius+1),repeat=d):
                word=scale
                for i,x in enumerate(hp):word=int(mp.nint(mp.mpf(word)*kernels[i]['coefficients'][radius-x]))
                kernel_rows[word<0].append((encode(hp,base),abs(word)))
            kp,km=[pack(rows,slot_bytes,kernel_degree) for rows in kernel_rows]
            packed_components=[]
            for signed_rows in input_rows:
                ip,im=[pack(rows,slot_bytes,input_degree) for rows in signed_rows]
                maximum_operand=max(maximum_operand,ip.bit_length(),im.bit_length(),kp.bit_length(),km.bit_length())
                packed_components.append([int(ip*kp),int(im*km),int(ip*km),int(im*kp)])
                products_count+=4
            mask=(1<<slot_bits)-1
            for output in itertools.product(range(-side//2,side//2),repeat=d):
                point=tuple(origin+x for origin,x in zip(origins,output));record=producer.encode(point,source)
                if record in partial:continue
                index=encode(tuple(x-low+radius for x in output),base)
                betas=[infos[i][0]+theta[i]*x for i,x in enumerate(output)]
                factor=mp.exp(sum(mp.pi*u*(theta[i]*x*x+betas[i]**2) for i,x in enumerate(output)))/mp.mpf(2)**normalizing_bits
                factor_word=int(mp.nint(factor*scale))
                words=[]
                for products in packed_components:
                    pieces=[(value>>(slot_bits*index))&mask for value in products]
                    numerator=pieces[0]+pieces[1]-pieces[2]-pieces[3]
                    words.append(producer.tz(numerator*factor_word,3*p-q))
                partial[record]=tuple(words)
            cells+=1
    assert partial,'no actual regular inverse output in this changed finite regime'
    discrepancy=max(abs(a-b) for j,value in partial.items() for a,b in zip(value,reference[j]))
    assert discrepancy<=16,('packed inverse vs periodic full compression reference',discrepancy)
    merged=[partial.get(j,value) for j,value in enumerate(reference)]
    receipt={'status':'actual packed inverse cells compose with complete source compression',
       'regular_coefficients':len(partial),'repair_coefficients':len(reference)-len(partial),
       'maximum_integer_grid_discrepancy':discrepancy,'cells':cells,'signed_integer_products':products_count,
       'selector_payload_reads':len(selected),'selector_payload_writes':len(selected),
       'retained_cell_payload_reads':reads,'kernel_setups':len(kernel_cache),
       'maximum_integer_operand_bits':maximum_operand,'reserve_bits':reserve,'work_bits':p,
       'inverse_kernel_target_bits':inverse_target,'source_compression_contraction_bits':normalizing_bits,
       'seconds':perf_counter()-started,
       'limitations':['repair oracle computes and charges the whole dense classical output, rather than a sparse algorithm',
                      'both global period cuts and selector phase jumps are excluded from regular cells',
                      'local analytic Laurent tails plus independent periodic full compression comparisons, not interval proof']}
    return merged,receipt


def main():
    parser=argparse.ArgumentParser()
    for name in ['producer','forward-stage','cyclic-api','laurent-api','config','output']:parser.add_argument('--'+name,required=True)
    args=parser.parse_args();assert gmpy2.__version__=='2.3.0'
    out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    producer=load('full_arithmetic',args.producer);stage=load('packed_forward',args.forward_stage)
    cyclic=load('cyclic_gaussian_reference',args.cyclic_api);sys.modules['cyclic_gaussian_reference']=cyclic
    laurent=load('regular_inverse_kernel',args.laurent_api)
    config=json.loads(Path(args.config).read_text());config['row_output']=str(out/'arithmetic-row.json')
    forward_rows=[];inverse_rows=[]

    def source_transform(data,source,target,matrices,q,chirps,suffix_phases,ledger,opposite=False):
        mp.mp.dps=max(mp.mp.dps,config['packed_digits'])
        if opposite:data=[producer.conjugate(x) for x in data]
        counts={k:0 for k in ['reference_payload_reads','reference_payload_writes','reference_axis_passes',
          'period_cut_cells_excluded','source_packet_payload_reads','zero_padded_packet_writes',
          'packed_tensor_cells','signed_integer_multiplications','packed_polynomial_slots','maximum_operand_bits']}
        partial,reserve=stage.packed_forward(data,source,target,config['alpha'],q,config['side'],config['radius'],counts)
        reference=stage.periodic_band_reference(data,source,target,config['alpha'],q,q+64,counts)
        regular=[j for j,value in enumerate(partial) if value is not None];assert regular
        discrepancy=max(abs(a-b) for j in regular for a,b in zip(partial[j],reference[j]));assert discrepancy<=16
        expanded=[reference[j] if value is None else value for j,value in enumerate(partial)]
        chirped=[producer.cmul(producer.conjugate(a),x,q) for a,x in zip(chirps,expanded)]
        transformed=producer.scalar_cyclic_convolution(chirps,chirped,target,q,suffix_phases,ledger)
        transformed=[producer.cmul(producer.conjugate(a),x,q) for a,x in zip(chirps,transformed)]
        data,inverse_receipt=compress(transformed,source,target,matrices,config['alpha'],q,
                             config['inverse_side'],config['inverse_radius'],producer,laurent,ledger)
        gamma=sum(2*axis[2]['alpha']**2 for axis in matrices)
        data=[(a<<gamma,b<<gamma) for a,b in data]
        if opposite:data=[producer.conjugate(x) for x in data]
        ledger['gaussian_source_transforms']+=1
        forward_rows.append({'regular_coefficients':len(regular),'repair_coefficients':len(reference)-len(regular),
                             'maximum_integer_grid_discrepancy':discrepancy,'reserve':reserve,'movement_ledger':counts})
        inverse_rows.append(inverse_receipt)
        (out/f'inverse-stage-{len(inverse_rows)}.json').write_text(json.dumps(inverse_receipt,indent=2)+'\n')
        return data

    producer.source_transform=source_transform
    started=perf_counter();arithmetic=producer.run_case(config)
    result={'status':'complete integer recovery with genuine packed forward and inverse cells passed',
        'arithmetic':arithmetic,'forward_stages':forward_rows,'inverse_stages':inverse_rows,'seconds':perf_counter()-started,
        'source_hashes':{name:hashlib.sha256(Path(path).read_bytes()).hexdigest() for name,path in
            [('producer',args.producer),('forward_stage',args.forward_stage),('cyclic_api',args.cyclic_api),
             ('laurent_api',args.laurent_api),('wrapper',__file__)]},
        'limitations':['finite pipeline with explicitly charged dense repair references, not an asymptotic complexity benchmark',
                       'finite CRT producer is the exact reference map; native guarded CRT stock is established separately',
                       'native known-bit tape routers are modeled and charged rather than reimplemented']}
    (out/'certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'seconds':result['seconds'],'coefficient_error':arithmetic['coefficient_real_error'],
                      'inverse_regular_coefficients':[r['regular_coefficients'] for r in inverse_rows]}))


if __name__=='__main__':main()
