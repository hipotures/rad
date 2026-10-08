#!/usr/bin/env python3
"""Construct an actual infinite-Laurent inverse approximation by Neumann sums.

The source phase is computed from integer periods/origin, never a binary64
beta. No dense finite inverse is used as a stand-in for a stationary kernel.
All intermediate convolution support is retained through the last Neumann
power, then the returned kernel is restricted. Its omitted input band,
Neumann remainder and final inverse-kernel tail are charged separately.
Coefficient arithmetic is high-precision mpmath, not interval certification.
"""
import mpmath as mp
from cyclic_gaussian_reference import selector


def regular_inverse_kernel(s, t, u, origin, radius, target_bits=256,
                           reserve_bits=0, half_bandwidth=None):
    assert 0<s<t and int(u)==u and u>=1 and radius>=1
    work_bits=int(target_bits+reserve_bits+128+s.bit_length())
    with mp.workprec(work_bits):
        rho=mp.mpf(t)/s
        beta=mp.mpf(t*origin-s*selector(origin,s,t))/s
        decay=mp.pi*u*(rho-2*abs(beta))
        A=decay-mp.log(4)
        assert A>0, ('phase gap does not support regular Laurent kernel',beta,A)
        row_bound=2/mp.expm1(decay)
        assert row_bound<mp.mpf(2)/3
        if half_bandwidth is None:
            half_bandwidth=int(mp.ceil(mp.sqrt((work_bits+16)*mp.log(2)/(mp.pi*u))))+2
        w=int(half_bandwidth)
        e={h:mp.exp(-mp.pi*u*(rho*h*h+2*beta*h))
           for h in range(-w,w+1) if h}
        omitted_e=(2*mp.exp(-mp.pi*u*w*(w+1))/
                   (1-mp.exp(-2*mp.pi*u*(w+1))))
        iterations=max(1,int(mp.ceil((work_bits*mp.log(2)-mp.log(1-row_bound))/
                                     (-mp.log(row_bound)))))
        power={0:mp.mpf(1)}
        inverse=dict(power)
        multiply_adds=0
        for k in range(1,iterations+1):
            nxt={}
            for a,value in power.items():
                for h,coefficient in e.items():
                    nxt[a+h]=nxt.get(a+h,mp.mpf(0))-value*coefficient
                    multiply_adds+=1
            power=nxt
            for h,value in power.items():
                inverse[h]=inverse.get(h,mp.mpf(0))+value
        coefficients={h:inverse.get(h,mp.mpf(0)) for h in range(-radius,radius+1)}
        neumann=row_bound**(iterations+1)/(1-row_bound)
        inverse_band_error=omitted_e/(1-row_bound)**2
        kernel_tail=3*mp.exp(-A*radius)
        return {'coefficients':coefficients,'beta':beta,'rho':rho,'spatial_weight':A,
                'unweighted_perturbation_row_bound':row_bound,
                'input_band_tail':omitted_e,'inverse_band_error':inverse_band_error,
                'neumann_remainder':neumann,'final_kernel_tail':kernel_tail,
                'analytic_kernel_row_error':inverse_band_error+neumann+kernel_tail,
                'radius':radius,'half_bandwidth':w,'iterations':iterations,
                'generated_halfspan':iterations*w,'work_bits':work_bits,
                'multiply_adds':multiply_adds,'source_period':s,'target_period':t,
                'u':u,'origin':origin,'reserve_bits':reserve_bits,
                'orientation':'b_h acts from input column i+h to output row i; polynomial convolution uses b_-h',
                'scope':'Finite high-precision kernel generation with exact analytic tail formulas; numerical coefficient rounding is separate'}
