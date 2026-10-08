# Independent review of the extended Gaussian inverse domain

Reviewed on 2026-10-08 after 15:00 UTC. This is a general written argument,
independent of the numerical PASS labels in the root's extended-tail family.
It extends the domain of the inverse branch's existing lifted-kernel lemma;
it introduces no worldwide priority claim and does not change the campaign's
chosen small-mismatch parameter family.

## Scope and conclusion

Let `rho=t/s=1+theta`, where `theta>0` and `s,t` are positive integers,
and let `u>=2`. The long-displacement inverse row-tail inequality is valid:

```
L=3*pi*u/4+pi*u*theta-ln(4)>0,
sum_(|h|>R) |B_(j,h)|
 <=6*exp[-L*(R+1)]/(1-exp(-L))
```

for every nonnegative integer `R` with `R+1>1/theta`. The full global
geometric estimate, valid at every nonnegative integer radius, is

```
a=pi*u*(1+theta)-ln(4)>0,
sum_(|h|>R) |B_(j,h)|
 <=6*exp[pi*u/(4*theta)-a*(R+1)]/(1-exp(-a)).
```

Neither assertion requires `theta<=1/4` or `u*theta>=1`. A uniform bound
on the physical inverse norm, needed for a local principal-window solver,
requires an additional argument. The condition `u*theta>=1` is sufficient
throughout the extended domain; it is retained by the root's numerical
family. Without that condition, the old constant `||N^-1||<2` must not be
silently inherited.

## The weighted identity has no small-mismatch restriction

Use the inverse branch's exact definitions

```
q_j=floor(rho*j+1/2), beta_j=rho*j-q_j in [-1/2,1/2),
n=q_(j+h)-q_j, g=n-h=theta*h+beta_j-beta_(j+h).
```

The physical lifted matrix coefficient is
`exp[-pi*u*n*(n+2*beta_(j+h))]`. For
`W_j=exp(pi*u*beta_j^2/theta)`, direct algebra gives

```
n*(n+2*beta_(j+h))
 -(beta_(j+h)^2-beta_j^2)/theta
 =rho*h^2+(rho/theta)*g*(g+2*beta_(j+h)).
```

The last term is nonnegative because `g` is an integer and the phase is
centered. This argument uses only `theta>0`. Thus every nonzero lifted
displacement of `F=W^-1*(N-I)*W` obeys
`|F_(j,h)|<=exp(-pi*u*rho*h^2)`.

For the periodic-coefficient weighted row algebra, take
`a=pi*u*rho-ln(4)`. Then

```
||F||_a <=2*sum_(h>=1)4^-h*exp[-pi*u*rho*h*(h-1)]<2/3.
```

Absolute convergence, the triangle inequality for displacement lengths,
and the Neumann series give `||(I+F)^-1||_a<3`. No translation invariance
is assumed. In particular, its lifted coefficient is bounded by
`3*exp(-a*|h|)`.

## Unweighting and tails

The physical inverse coefficient is
`B_(j,h)=W_j*K_(j,h)/W_(j+h)`. Centered phases always satisfy
`beta_j^2-beta_(j+h)^2<=1/4`. This gives the global geometric estimate
above by summing both signs.

For `|h|>1/theta`, the same phase gain is at most
`theta*|h|/4`. Therefore

```
|B_(j,h)| <=3*exp[-(a-pi*u/4)*|h|]=3*exp(-L*|h|).
```

The long-displacement tail follows immediately. In fact `L>u` for
`u>=2`: use `pi>3` and `ln(4)<3/2` to obtain
`L-u>(5/4)*u-3/2>0`. This also permits the earlier coarse long-tail
constant in the quadratic-radius argument.

For the short regime `theta*|h|<=1`, the inverse branch's exact centered
phase inequality remains valid:
`beta_j^2-beta_(j+h)^2<=theta*|h|-(theta*h)^2`.
With `u*theta>=1`, it gives
`|B_(j,h)|<=3*exp(-pi*u*theta*h^2)`. Consequently the previous quadratic
tail constant `24*exp(-3*u*theta*R^2)` survives for
`1<=R<=1/(2*theta)` with the weaker assumption `u>=2`. Some extended
parameters have no positive integer radius in that range; the linear and
global estimates are then the applicable statements.

## Physical contraction and principal windows

The direct physical exponent `phi=n*(n+2*beta_(j+h))` has the following
two lower bounds for every `theta>0`:

```
|h|=1: phi>=2*theta,
|h|>=2: phi>=|h|*(|h|-1).
```

For the second bound, use
`phi=(rho*h+beta_j)^2-beta_(j+h)^2` and centered phases to obtain
`phi>=rho*|h|*(rho*|h|-1)>=|h|*(|h|-1)`.
For the first, write `theta=k+f`, `k>=0` integer and `0<=f<1`.
At positive displacement the integer increment is `k+1` or `k+2`.
In the first case the destination phase is at least `-1/2+f`, so
`phi>=(k+1)*(k+2*f)>=2*(k+f)`; the last inequality is
`k*(k-1)+2*k*f>=0`. In the second case
`phi>=(k+2)*(k+1)>=2*(k+f)`. The negative-displacement proof reverses
the phase endpoints and is identical. This includes all physical-period
aliases.

For `u>=2` and `u*theta>=1`, therefore

```
||N-I||_infinity
 <=2*exp(-2*pi*u*theta)
   +2*sum_(h>=2)exp[-pi*u*h*(h-1)]
 <1/16.
```

For a fully elementary estimate, use `pi>3`: the first term is below
`2*exp(-6)`, and the remaining sum is at most
`2*exp(-12)/(1-exp(-24))`. Their sum is below `1/16`.
Thus `||N^-1||_infinity<16/15<2`.

For a principal physical set `I`, the lifted restriction has the same
weighted inverse norm below three. Its boundary operator
`(N_I,I)^-1*N_I,Ic` has weighted norm below two. If every retained core
row is more than `R` steps from the complement, its boundary row tail is
bounded by

```
4*exp[-L*(R+1)]/(1-exp(-L))
```

when `R+1>1/theta`. Multiplying by the global physical inverse norm
bound yields local principal-window error at most

```
8*exp[-L*(R+1)]/(1-exp(-L))*||input||_infinity.
```

The corresponding global geometric alternative has the same replacement
of inverse coefficient constant three by boundary constant two. Without
`u*theta>=1`, one may use the conservative independently proved physical
bound `||N^-1||<=3*exp(pi*u/(4*theta))` instead. That guard is potentially
large and is not an improvement of the original fast-solver interface.

## Cyclic folding and numerical controls

Absolute convergence permits folding the lifted inverse and all kernel
products over displacements congruent modulo `s`. The omitted circular
window consists of a subset of the lifted displacements of length greater
than `R`, so triangle inequality preserves these tail upper bounds. If a
radius covers the entire finite circle, the circular tail is zero; such a
test is vacuous. The root's extended family excludes `2R>=s`.

The root's code `../../code/cyclic_extended_tail_family.py` changes the
original numerical control to choose `u=ceil(s/(t-s))+1`, so it retains
both `u>=2` and `u*theta>=1`. It compares applicable quadratic, global,
and long-displacement alternatives at nonvacuous radii. This is useful
coordinate/alias numerical evidence but does not test the separate
small-`u*theta` scope. No control result is used as a substitute for the
general inequalities in this review.
