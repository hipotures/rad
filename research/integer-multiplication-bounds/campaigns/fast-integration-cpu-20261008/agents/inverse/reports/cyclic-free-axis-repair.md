# Cyclic free-axis repair by transient overlapping principal windows

This interface fills a specific gap in sparse tensor repair: a free axis is
an entire cyclic prime period, whereas the physical band-LU lemma accepts
shorter-than-half-period lifted principal line windows. Treating the entire
cyclic matrix as an ordinary banded matrix would discard its border.

Let the current repaired packet have its free axis of period `s` complete.
Let `R=R_exception` be a radius satisfying the global locality lemma's
principal-core precision bound, with `3R<s/2`. Partition `[0,s)` into
successive cores of length `H=R`, except for the last shorter core. For each
core take a lifted integer interval consisting of that core and `R` extra
positions at BOTH ends. Copy the periodic RHS values into this interval,
solve its actual principal matrix, and emit only the core solution values.
Restore the full canonical cyclic line order before the next tensor axis.

This is required on every FREE axis of ALL inverse repair packet types,
including regular bad-grid pair packets. Such packets' free axes still span
the phase-exception rows. A regular-phase Laurent kernel cannot be substituted
on an entire free period. Their constrained regular face axes may instead
retain `R_I`-radius principal windows and the regular-phase error bound;
expanding those narrow face coordinates by `R_exception` would invalidate
the original sparse-volume calculation.

The exact global-principal resolvent lemma gives core error at most

`32 exp(-3u theta R^2) ||rhs||_infinity`.

The window length is at most `3R`, hence it contains each physical residue
at most once and is shorter than half a period. The first/last windows may
cross the original physical cut; they are unfolded using periodic phase
data. Do not erase period aliases from the exact principal definition.
Replacing it with the lifted wrap-free band matrix adds the separately
charged remote-image perturbation bounded by

`4 exp(-pi*u*(s-m)*(s-m-1))`, `m<=3R`.

This is negligible against the requested `2^-Q` guard beyond the common
eventual threshold. Band truncation, fixed-grid factor and solve errors are
also separately charged by the physical band-LU report. The RHS may have
grown through earlier axes; include `log2 max(1,||rhs||)` and the `O(d)`
loose tensor norm guard in working precision `P=O(Q)`.

## Paid copies and no tensor halo product

There are `ceil(s/H)` windows and their total length is exactly

`s+2R ceil(s/H) <= 3s+2R <= 4s`.

Thus current-axis copies have constant TOTAL volume, even when the last
core is short. They are acquired by the already charged ordinary fixed-
tape source-packet sorting/scanning schedule. Every copy has its packet,
line and window coordinates; setup is paid on EACH copied window.
Physical band LU costs `O(m w^2 M(P))` setup and `O(m w M(P))` online work
per line window. Summing by the actual window lengths gives the stated
constant-volume per-axis charge, with `w^2=O(Q/u)=O(d)`.

Only one axis is expanded at a time. After solving it, the emitted cores
partition the original full period and the copied halos are discarded.
The resulting packet again has that free axis complete at its original
volume. Other free axes and unprocessed constrained-axis closure fields
are copied unchanged. Processing the next axis therefore expands the
CURRENT packet by at most four, rather than retaining previous halo
copies. A product such as `4^d` does not describe this schedule.

For a constrained axis, the packet's source-closure schedule must still
retain every source needed by subsequent unprocessed axes. This interface
does not justify premature cropping there. It only supplies the entire
cyclic free-axis operation used between those documented closure stages.

At rare source-volume fraction `rho=O(d^-3)`, the aggregate `d` axis
factor/setup charge is `O(rho*n*d*w^2)` times the scalar normalized
arithmetic factor, hence `O(n/d)` times that factor. Full payload keys,
window replication and their ordinary fixed-tape sorts are included in
the root's `O(rho*n*d*log n)` movement accounting.

More precisely, phase packets have `rho=O(d^-3)` and yield normalized
factor/setup charge `O(d^-1)`. Regular bad-grid pair packets have
`rho=O(d^-4)`; their complete free axes use the SAME global band solver,
giving normalized charge `O(d^-2)`. Their constrained regular axes keep
the smaller original source halos. Both charges include the one-axis
constant transient window replication and precede scalar logarithmic
arithmetic factors. No free complete axis is treated as uniformly regular.

This is a written conditional composition of the independently reviewed
global locality and physical band-LU lemmas. It is not a new cyclic solver
implementation or an independently promoted multiplication exponent.
