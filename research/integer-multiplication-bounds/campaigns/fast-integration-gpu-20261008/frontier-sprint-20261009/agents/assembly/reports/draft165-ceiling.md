# Exact negative ceiling for the supplied stronger profiles

The paid optimized atom and balanced transfer cannot lift the identified
profile pair above the coordinator's observed draft PR165 claim
`297136180212477/500000000000000000`. This is an exact negative result
conditional on the supplied finite distributions. It is not finite
acceptance of new frames and is not an upper bound on further searches.

The binary input is
`work/bit/batch2-20261009T075800Z-singletons/profile.json`, SHA-256
`94b81652d07b9795188999bfee9e609c081311ee15d0dd23c5d59849f8d4ac1f`;
its frame plan is `eeb54883858786e7244052633461c1cc119e51a8c5ba2bf1ff1d3b1b9102aa8b`.
The complex input is
`work/placement/live161-unequal-op-pairs-polished/physical-profile.json`,
SHA-256 `b06874076cc51b018e5e5d93549ae1b099be0898935497506cd68411f29ada0f`;
its frames are `306f19150268852876fbeb88b541fca6c5ceff1ac1be44b55b05146fa0fe69f8`.
The full complex histogram is reconstructed from component counts; all
binary and complex normalized moments are recomputed using the independent
80-term atanh, degree-14 exponential and `2^224` rational intervals.

For the full binary worst-case fallback envelope,
`a0=59503737587021/10^17` is accepted and `a0+1/10^18` is rejected.
The polished complex saving is strictly between `594608516/10^12` and
`594608517/10^12`. Strict monotonicity of each complete characteristic
justifies these profile-conditional upper endpoints.

For an atom exponent theta, the ordinary saving is
`A(theta)=a0-theta*(a0-a_old)`. Paying the lower adapter toll requires
`theta>A(theta)`, hence `theta>a0/(1+a0-a_old)` and
`A<a0/(1+a0-a_old)`. The boundary increases with a0, so a rejected coarse
endpoint also bounds every supported ordinary saving from this envelope.
The stronger binary supplier leaves ample headroom, and the complex
endpoint binds. Even allowing positive stopping/backoff parameters to
approach zero, the balanced minimum obeys

```
kappa < g = (1-eta)*q/(1+q) < a/(1+a)
      <= min(A_upper,b_upper)/(1+min(A_upper,b_upper))
      = 594608517/1000594608517.
```

The exact shortfall below draft PR165 is
`8601415940185693866609/500297304258500000000000000000`, approximately
`1.72e-8`. This is a structural supplier limit for the identified paid
composition; finer atom or assembly grids cannot overcome it.

The optimistic supplier requirement for that observed target rho is
`rho/(1-rho)=297136180212477/499702863819787523`. With retained
`beta=10^-9`, `eta=10^-8`, and weakening `10^-10`, the exact requirements are

```
a > rho/[(1-2*eta)*(1-eta-rho)]
  = 4952269670207950000000/8328380813762172443404159,
b > (a_required+10^-10)/(1-10^-9)
  = 49522705030460313762172443404159/83283808054337916296419865565958410.
```

A sufficient complex 12-digit grid point is `594625849/10^12`. The binary
ordinary interface must separately exceed the a requirement. Any new
candidate crossing these targets needs fresh full moments, full bills,
47+7, independent finite bit/local-ring and complex reflected-word reviews,
and a refreshed public comparison.

[The standalone assessor](../code/assess_balanced_ceiling.py) and
[reproduction commands](../reproduce.md) preserve the calculation. The
receipt is `work/assembly/20261009T-draft165-ceiling/assessment.json`, with
an intact gzip archive in this lane's evidence. The original first unified
arithmetic result remains immutable and below the later observed claim.
