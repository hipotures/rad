# Finite-field address routing and a restricted bootstrap obstruction

## Result and status

An exact reduction of dyadic Gaussian circuits modulo five implements a controlled address XOR on arbitrary complete F5 payloads. The first four-worker run checked target widths 1 through 4, including every target/control basis column, dirty guard and companion coordinates, four payload fields, and the literal inverse. This is an algebraic interface with constant-width coefficients. It does not implement a native tape router or recover arbitrary Gaussian outputs.

A separate exact obstruction excludes one tempting bootstrap: replace each mixed weight-five source-line adapter by a single-bank word of coordinate C children and invertible diagonal gates. That word needs at least six coordinate ranks to implement the one-rank mixed-line phase. In the unchanged three-core, fixed-stock center ledger, these replacements alone consume more rank than the available deficit. General routers, helper banks, interference between banks, and changed recurrences remain open.

## Exact coefficient reduction

Let R = Z[i, 1/2]. The assignments i -> 2 and 1/2 -> 3 define a ring homomorphism R -> F5: 2 squared is -1 modulo five, and 2 times 3 is 1. For alpha = (1+i)/2 and beta = (1-i)/2,

```
C       -> [[4, 2], [2, 4]],
C^-1    -> [[2, 4], [4, 2]],
S       -> diag(1, 2),
S^-1    -> diag(1, 3).
```

The literal Gaussian identity Htilde = S C S = alpha H reduces to Htilde = 4 H and Htilde^-1 = 2 H. For f target bits a, immutable control bits c, and any computed mask G(c), put D_G(a,c) = (-1)^(a dot G(c)). The chronological word Htilde^-1, D_G, Htilde is exactly the address permutation

```
(a, c) -> (a XOR G(c), c).
```

The proof is the Walsh character identity: H D_G H = 2^f X_G; the inverse and forward scalar factors multiply to 2^-f. It holds over F5 because two is invertible. The executable retains all input/output chirps and their inverses rather than replacing them by an unpaid normalization.

The tested nonlinear mask is `G(c) = c XOR ((c & 1) * (c >> 1))`, restricted to f bits. It reads no target, guard, or companion coordinate. Two complete spectator guard bits and one complete companion bit carry arbitrary payload fields throughout. They are not used as free clean ancillas. Every matrix entry of each complete target/control block is checked; the full spectator cube is separately replayed on dense F5 and Boolean payloads.

Every exact matrix identity with coefficients in R survives this reduction. This statement does not cover numerical rounding, input-dependent exceptional-record logic, or a circuit containing an inverse of five. The newly retained total-root decoder is dyadic and can be reduced; the older pair-only decoder's odd-divisor interface cannot be silently reused at this prime.

The reduction is nonfaithful: 2-i maps to zero. Consequently it does not recover an arbitrary Gaussian coefficient. For Boolean transport the required endpoint is an exact 0/1 permutation matrix, so reduction returns the correct Boolean bits and preserves arbitrary F5 payloads. Gaussian numerical computation requires a separate reconstruction or representation theorem.

## What remains paid

The word has two complete C_f endpoint calls. The reference code evaluates their coordinate factors directly; it does not supply a faster native C_f implementation. The immutable-control diagonal, chirps, coefficient-field encoding, all long-record moves, metadata computation, and every companion/guard allocation require their own native bill.

Four F5 scalar payload fields are not the original four complex Gaussian fields with long fixed-precision records. A native modular module may pack many field elements in a complete long record, but initialization, lane layout, selected axes, padding, row stock, whole-record arithmetic, and restoration must be proved. Constant-size residues do not turn the Python array operations into a tape implementation. A routing call inside a self-recursive supplier must be included in its child moment and complete volume accounting; it is not an external constant prefactor.

## Coordinate-only rank floor

Consider a single scalar bank, coordinate C children, and arbitrary invertible diagonal gates. No noncoordinate address permutation or helper-bank interference is allowed. A coordinate factor is a 2 by 2 dense invertible matrix whose four entries remain nonzero after reduction. A grouped coordinate child is charged once for each coordinate factor it contains.

Let U have odd weight ell >= 3. Its mixed-line phase is

```
C_U = alpha I + beta X_U,
```

and each column has exactly two nonzero entries. To create the displacement U, the word must touch every one of its ell coordinates. If its total coordinate rank were ell, each necessary coordinate would occur exactly once and no other coordinate could occur. For any input and final active address there is then exactly one path: each coordinate's required flip or stay choice is determined by the final address. Its coefficient is a product of nonzero coordinate entries and diagonal units. Thus all 2^ell active outputs are nonzero, contradicting the two-entry support of C_U. Total coordinate rank is therefore at least ell+1. The bound is not asserted to be tight.

The executable checks all columns for ell = 3, 5, 7 with varying literal intervening unit diagonals. The all-size argument is the unique-path proof above, not extrapolation from those examples. Coordinate permutations preserving this model can be absorbed into a relabeling; a general invertible linear router can change the displacement weight and is outside the premise.

## Consequence for one unchanged center ledger

For p = 12 paired coordinates, h = 24, v = 32 choose(p,5) = 25344, and q = 2p(p-1)+1 = 265 independently dirty pair/total roots. The optimistic copied-center first-moment deficit is

```
2v - 3qh = 31608.
```

Each source-helper identity-to-weight-five-line adapter is charged rank one. A coordinate-only replacement needs at least six ranks, adding at least five ranks per source per core, or 15v = 380160 over three cores. The resulting deficit is at most -348552. Under the same physical stock and proper-child master, even the first moment cannot contract. For every 0 < exponent <= 1, proper-child power moments are at least this failed first moment.

This conditional exclusion concerns these separately implemented line adapters. It does not exclude a joint implementation of the line/full endpoints, multiple banks, dynamic births, a different source family, nonlinear or general linear native routes, modular arithmetic suppliers, or a changed master. In particular, the direct-full center variant retains the helpers; it is not the earlier proposal to delete them and use the original sources.

## Evidence and reproduction

The first attempt is [20261009T122428Z-transfer-finite-field-router-first](../../runs/20261009T122428Z-transfer-finite-field-router-first/report.md). Its source is [finite_field_router_bootstrap.py](../../code/transfers/finite_field_router_bootstrap.py), SHA256 `21d76df70d3b1eda2b68a94d84469ea95b2da1d5d45c6793e48545b74353fc86`. Python's standard library is the only dependency. The actual process started at 2026-10-09T12:24:28.434785+00:00 and finished in 0.277 seconds.

The full attempt checked 2720 complete records on both dense F5 and Boolean fields, 43520 forward/inverse scalar values, 340 complete target/control columns, and 69904 block matrix entries. The independent coordinate discriminator checked 168 columns and 17472 entries. Omission of an input chirp is rejected. A nonfaithfulness witness is retained as an explicit reconstruction negative.

From the repository root:

```bash
python3 -B research/integer-mult-breakthrough/code/transfers/finite_field_router_bootstrap.py --workers 4 --output /tmp/fresh-f5-router-full.json
python3 -B research/integer-mult-breakthrough/code/transfers/finite_field_router_bootstrap.py --workers 1 --bounded --output /tmp/fresh-f5-router-bounded.json
```

Output paths must be fresh. The bounded command retains target width two, the weight-five obstruction, and the p12 complete conditional rank ledger. It passed in [20261009T123338Z-transfer-finite-field-router-bounded](../../runs/20261009T123338Z-transfer-finite-field-router-bounded/report.md), with actual process start 2026-10-09T12:33:38.077397+00:00 and 0.044 seconds elapsed. All first-attempt originals and source/config pins are immutable. No native supplier, all-size time bound, larger kappa, or formal verification is claimed.
