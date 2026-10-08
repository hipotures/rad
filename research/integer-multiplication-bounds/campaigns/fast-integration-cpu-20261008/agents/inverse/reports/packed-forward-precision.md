# Packed forward Gaussian cells: analytic and precision interface

Status: positive analytic and local packing interface. Global source-cell
acquisition, shifted-grid repair and the complete multiplication cost rows
remain separate obligations. This report does not promote a full exponent.

## Exact scalar factorization and separate forward scale

Use `rho=t/s=1+theta`, `u=alpha^2`, and the normalized forward map

```
(S' x)_k=(2alpha)^-1 sum_j exp[-pi*g*(rho*j-k)^2] x_j,
g=(rho*alpha)^-2=1/(rho^2*u).
```

This definition and the following exact factorization are adopted from the
public fast Gaussian note at CrocSwap PR38, head
`cc794077f6c103e24ec0939be765cd1521239aab`,
[notes/fast-gaussian-resampling.tex](https://github.com/CrocSwap/integer-mult-bounds/blob/cc794077f6c103e24ec0939be765cd1521239aab/notes/fast-gaussian-resampling.tex).
The chirped-correlation mechanism is prior work, not a new claim here.

Let input origin be `j0`, output origin `k0`, and put
`a=j-j0`, `b=k-k0`, `y=rho*j0-k0`. Then

```
exp[-pi*g*(rho*a+y-b)^2]
 =exp(pi*g*theta*b^2)
  *exp[-pi*g*rho*theta*(a+y/rho)^2]
  *exp[-pi*g*rho*(a-b+y/rho)^2].
```

The last two factors are at most one. The first is the output diagonal.
The identity holds for all rational origins, including negative local halo
indices. It is a correlation kernel in `a-b`, with no phase-cell jump in its
algebra. A per-axis source core for output `[k0,k0+L)` starts at
`j0=floor(k0/rho)`; then `y` is bounded in magnitude by `rho`.
Its source core has length about `L/rho` and can be padded at the end.

The forward radius is
`R_F=O(alpha*sqrt(Q))=O(sqrt(u*Q))`, **not** the inverse radius.
At `u=Theta(Q/d)` it is `Theta(Q/sqrt(d))`. The forward core must therefore
use a different scale from the regular inverse core. Set

```
L_F=Theta(d^3*R_F).
```

For `theta=Theta(d^-16)`, missing source slots from the near-one size change
occupy `O(theta*L_F)=o(R_F)`. An output farther than a conservative constant
multiple of `R_F` from both core faces has all its required source indices in
the supplied monotone source core. Face outputs require other grids or repair.

## The full tensor chirp reserve remains linear in Q

For `d` axes, the total natural-log output reserve is

```
B_total <= pi * sum_i theta_i*L_(F,i)^2/u_i
        = O(d^7*theta*Q).
```

At `theta=Theta(d^-16)` this is `O(Q/d^9)`. Rounding each axis's reserve
up to a whole bit adds at most `d` bits, also `o(Q)`. This is a **full-tensor**
bound; it does not concatenate `d` separate reserves of order `Q`.

The number of coefficient records in a box is `M=L_F^d`, with
`log M=O(d log d)` in the candidate regime `Q=Theta(d^18)`.
This is much smaller than `Q`. Thus the logarithm of the unnormalized
correlation's row sum and its integer accumulation guard remain `O(Q)`.

## Tensor setup must round contracting products

Forming a product of `d` exact `P`-fractional-bit factors and retaining all
denominators would produce `dP` fractional bits. That would invalidate the
linear-precision interface. Instead, all setup factors in the input diagonal,
the normalized output diagonal and the Gaussian kernel are at most one.
Round each newly formed product back to the `P` grid. After `d` factors,
the coefficient error is at most `d*2^-P` by induction.

Generate each tensor product recursively. At level `i`, append the next
one-dimensional vector to every retained prefix product. The total count is
bounded by the geometric sum of partial volumes, `O(M)`, rather than `dM`
independent products. Large zero gaps in the packed kernel can be emitted by
ordered stream scans. The tensor diagonal page for fixed shapes and axis
parameters can be generated constructively once and reused across boxes.

The source coefficient stream and kernel coefficients are now dyadics on the
same `P` grid. Use a constant number of signed nonnegative packings with slot
width

```
2P+ceil(log2 M)+O(1).
```

The univariate integer products then give exact accumulated grid numerators.
If `G` is the total output reserve in whole bits, the input/setup/rounding
error after rescaling is bounded conservatively by
`C*d*M*2^(G-P)`. A sufficient work precision is

```
P >= Q+G+ceil(log2 M)+ceil(log2 d)+C0 = O(Q).
```

The normalization `(2alpha)^-d` contracts; its rounded setup adds the same
kind of error. The exact normalized forward maps are contractions under the
inherited Gaussian interface, so completed numerical maps can retain its disk
margin once the final error allowance is chosen consistently.

## Halo-free interior Kronecker packing

For simplicity let every local side be the same power of two `L`, and let a
kernel have coordinate offsets `h_i in [-R,R]`, `2R+1<L`. Encode an input
coordinate `a` by `index(a)=sum_i a_i L^i`. Encode the kernel coefficient
for displacement `h` at `sum_i(h_i+R)L^i`.

The output at `b` is read at

```
index(b)+R*sum_i L^i.
```

If every `R<=b_i<L-R`, no coordinate carry can enter a convolution term at
that location. To prove this, start from the least significant coordinate.
A carry into it is impossible. A carry out would require a digit sum larger
than `L-1`, but a false representation of the desired digit plus `L` is
possible only when `b_i<R`, because input digits are at most `L-1` and kernel
digits at most `2R`. Hence there is no carry; induct on the next coordinate.
The desired output digits themselves remain below `L` because `b_i<L-R`.

The packed convolution is therefore exactly the Cartesian convolution on all
interior outputs. The kernel operand length is
`1+2R*sum_i L^i`, and product length is below a fixed multiple of `L^d`.
There is no `2^d` padding of the input tensor. Face outputs may contain carry
collisions and are deliberately not accepted by this local interface.

The independent checker `../code/packed_tensor_controls.py` passed 3,844 exact
interior outputs against separately nested Cartesian sums, using asymmetric
kernels and signed inputs in dimensions two, three and four. It also found
4,412 wrong face outputs, retaining explicit negative examples. Its signed
nonnegative packing guard is defined before examining outputs.

## Conditional recurrence consequence and its boundary

Each packed multiplication has child bit length
`S=O(Q*L_F^d)`, so `log S=O(d log d)=O(b^epsilon log b)` for
`d=Theta(b^epsilon)`, `b=log n`, `epsilon<1`. In a conditional multiplication
recurrence, applying an inductive `S*(log S)^(1-kappa)` bound to the packed
products gives a Gaussian row

```
O(n * b^(epsilon*(1-kappa)) * polylog(b)).
```

Its strict absorption against `n*b^(1-kappa)` requires only `epsilon<1`
for `kappa<1`. This removes the old analytic `d`-pass arithmetic row **if**
the full source packets, grids and repair streams are produced at the paid
cost. The calculation is not permission to use an uncharged nonlinear sort,
duplicate all boxes or omit boundary rows.

Ordinary per-axis halo construction still costs `O(nd)` and would keep the
old limiting row. The campaign layout branch owns a possible one-pass product
embedding and true global shifted-grid acquisition. Sparse repair must include
its input patches and sorting/movement, not only its output count. These
interfaces and every transform/CRT/prefix/row-stock/setup condition remain
necessary before claiming a new complete exponent.
