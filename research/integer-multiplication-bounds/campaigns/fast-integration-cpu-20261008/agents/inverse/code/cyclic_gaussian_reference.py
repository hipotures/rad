#!/usr/bin/env python3
"""Sparse bordered reference solve for the physical cyclic Gaussian N.

Numerical discrimination API, not an all-size fixed-tape solver claim.
Requires mpmath (the campaign's pinned task-local dependency). The first w
physical coordinates form a border; its complement is ordinary banded.
All omitted lifted coefficients, including every remote periodic alias,
have an explicit uniform Gaussian tail bound. Residuals use separately
recomputed higher-precision coefficients, not agreement with LU factors.
"""
from __future__ import annotations
import math
import mpmath as mp


def selector(j, s, t):
    return (2*t*j+s)//(2*s)


def lifted_coefficient(row, h, s, t, u):
    column = row+h
    qi = selector(row, s, t)
    qj = selector(column, s, t)
    beta = mp.mpf(t*column-s*qj)/s
    n = qj-qi
    return mp.exp(-mp.pi*u*n*(n+2*beta))


class CyclicGaussianReference:
    """Factor once, then solve arbitrary real/complex RHS vectors.

    solve returns N^-1 rhs. The separate source J'=N^-1/2 and D' factors
    are NOT applied here. The whole cyclic border is retained, never dropped.
    Out-of-theorem finite parameters are allowed only if their generated
    truncated matrix has a positive conservative row gap; residual-derived
    numerical error is reported separately from all-size near-I constants.
    """
    def __init__(self, s, t, alpha, target_bits=256, half_bandwidth=None):
        assert 0<s<t and alpha>0
        self.s, self.t, self.u = int(s), int(t), int(alpha)**2
        self.target_bits = int(target_bits)
        self.precision = self.target_bits+96+max(1,self.s.bit_length())
        with mp.workprec(self.precision):
            if half_bandwidth is None:
                half_bandwidth = math.ceil(math.sqrt(
                    (self.precision+16)*math.log(2)/(math.pi*self.u)))+2
            self.w = int(half_bandwidth)
            assert self.w>=1 and self.s>4*self.w
            self.rows = []
            for i in range(self.s):
                self.rows.append({(i+h)%self.s:
                    lifted_coefficient(i,h,self.s,self.t,self.u)
                    for h in range(-self.w,self.w+1)})
            self.tail = (2*mp.exp(-mp.pi*self.u*self.w*(self.w+1))/
                         (1-mp.exp(-2*mp.pi*self.u*(self.w+1))))
            gap = min(row[i]-sum(abs(value) for j,value in row.items() if j!=i)
                      for i,row in enumerate(self.rows))
            self.gap = gap/2-self.tail
            assert self.gap>0, ('cyclic reference lost strict row dominance',gap)
            self.m = self.s-self.w
            self.lower = [{} for _ in range(self.m)]
            self.upper = [{j-self.w:value for j,value in self.rows[i].items()
                           if j>=self.w}
                          for i in range(self.w,self.s)]
            for k in range(self.m):
                pivot = self.upper[k][k]
                assert pivot>self.gap
                for i in range(k+1,min(self.m,k+self.w+1)):
                    multiplier = self.upper[i].get(k,mp.mpf(0))/pivot
                    self.lower[i][k] = multiplier
                    self.upper[i].pop(k,None)
                    for j in range(k+1,min(self.m,k+self.w+1)):
                        self.upper[i][j] = (self.upper[i].get(j,mp.mpf(0))-
                                            multiplier*self.upper[k].get(j,mp.mpf(0)))
            # C is supported near the two ends; D^-1C is stored as w columns.
            self.coupling = [self._solve_band([
                self.rows[i].get(a,mp.mpf(0)) for i in range(self.w,self.s)])
                for a in range(self.w)]
            self.border_rows = [{j-self.w:value for j,value in self.rows[a].items()
                                 if j>=self.w} for a in range(self.w)]
            self.schur = mp.matrix(self.w,self.w)
            for a in range(self.w):
                for b in range(self.w):
                    self.schur[a,b] = (self.rows[a].get(b,mp.mpf(0))-
                        sum(value*self.coupling[b][j]
                            for j,value in self.border_rows[a].items()))

    def _solve_band(self, rhs):
        y = list(rhs)
        for i in range(self.m):
            y[i] -= sum(value*y[j] for j,value in self.lower[i].items())
        x = y[:]
        for i in range(self.m-1,-1,-1):
            x[i] = (y[i]-sum(value*x[j] for j,value in self.upper[i].items()
                            if j!=i))/self.upper[i][i]
        return x

    def solve(self, rhs):
        assert len(rhs)==self.s
        with mp.workprec(self.precision):
            rhs = [mp.mpc(value) if getattr(value,'imag',0)!=0 else
                   mp.mpf(getattr(value,'real',value)) for value in rhs]
            y = self._solve_band(rhs[self.w:])
            border_rhs = mp.matrix([rhs[a]-sum(value*y[j]
                for j,value in self.border_rows[a].items()) for a in range(self.w)])
            border = list(mp.lu_solve(self.schur,border_rhs))
            interior = [value-sum(self.coupling[a][i]*border[a]
                                  for a in range(self.w))
                        for i,value in enumerate(y)]
            return border+interior

    def residual_certificate(self, rhs, solution):
        assert len(rhs)==self.s and len(solution)==self.s
        with mp.workprec(self.precision+32):
            residual = max(abs(sum(
                lifted_coefficient(i,h,self.s,self.t,self.u)*solution[(i+h)%self.s]
                for h in range(-self.w,self.w+1))-rhs[i]) for i in range(self.s))
            norm = max(abs(value) for value in solution)
            bound = residual+self.tail*norm
            return {'retained_residual':residual,'omitted_alias_and_band_row_bound':self.tail,
                    'global_residual_upper':bound,'conservative_row_gap':self.gap,
                    'solution_error_upper':bound/self.gap,'solution_norm':norm,
                    'target':mp.mpf(2)**(-self.target_bits),
                    'source_period':self.s,'target_period':self.t,'u':self.u,
                    'half_bandwidth':self.w,'work_bits':self.precision,
                    'within_campaign_u_theta_condition':
                    self.u*mp.mpf(self.t-self.s)/self.s>=1,
                    'scope':'High-precision numerical residual plus analytic lifted Gaussian tail; not directed interval certification'}
