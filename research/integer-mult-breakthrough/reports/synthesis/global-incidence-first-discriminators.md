# Global incidence cancellation: exact scalar leverage and a physical barrier

**Status: EXACT CERTIFICATE for auxiliary binary scalar maps and reversible words; REFUTED WITHIN STATED SCOPE for the naive frozen-ledger port collapse. No larger kappa is claimed.**

The first discriminator asks whether dropping cancellation-free and common-region restrictions exposes a circuit large enough to matter, rather than another local compiler improvement. It does: binary incidence gives a much smaller auxiliary circuit. The unresolved cost is its physical realization, and a first exact test rejects an unpaid replacement of the old port geometry.

## Exact identities

Let x_T be independent binary scalar variables indexed by triples of an h-point set. Define point totals t_c = sum_{T contains c} x_T and pair stars s_ab = sum_{T contains a,b} x_T. The ordinary common-point side requested by a target triple T={a,b,c} is

    y_{c;ab} = t_c + s_ca + s_cb + x_T  (over GF(2)).

Pair stars are shared across common-point groups. The sum of all three ordinary sides is particularly simple:

    z_T = y_{a;bc} + y_{b;ac} + y_{c;ab}
        = x_T + t_a + t_b + t_c.

Its coefficient matrix is A_exactly_one = I + B^T B, where B is the point/triple incidence matrix. This is a statement over GF(2). Over characteristic zero the corresponding identities are y_{c;ab}=t_c-s_ca-s_cb+x_T and z_T=sum_{c in T} t_c - 2 sum_{p subset T,|p|=2} s_p + 3 x_T. Thus the binary global collapse cannot be copied directly to a complex phase network.

The initial exact program checks every scalar output coefficient for h=6,7,8,9,10,23,25. Geometry tests deliberately exclude h=9 where the inherited ambient form is degenerate; the scalar identity itself does not depend on that geometry.

## Literal reversible auxiliary words

A deterministic dirty-scratch echo computes scratch ^= Bx, toggles the output by C scratch, uncomputes scratch, and toggles the output by C scratch again. Every unknown dirty coordinate cancels and is restored; inputs remain unchanged and arbitrary output coordinates receive precisely the desired linear map.

For the summed map the paid word contains 13*binomial(h,3) CNOTs and 2*binomial(h,3)+h physical scalar slots. For all three separate ordinary sides it contains 33*binomial(h,3) CNOTs and 4*binomial(h,3)+h+binomial(h,2) slots. These initial auxiliary words omit the h additional center-total outputs of the historical graph. They therefore certify the named ordinary-side maps, not the historical graph in full. The follow-up full-map probe will charge those center sinks explicitly.

All source, output and dirty basis columns are replayed simultaneously for h=6,7,23,25. Omitting a dirty echo and changing a source operand are both rejected. No source/sink or dirty-basis check is replaced by a gate count. Nevertheless, scalar slot capacity is the only capacity certified here: rational address frames, causal payload accessibility, residual calls and boundary integration remain open.

## Exact physical-frame discriminator

In the inherited fixed-I+J coordinate basis, the source triple line has primal vector w_T with entry 4 on T and 3 elsewhere. Its rational projector is

    P_T = w_T z_T^T / (6(h+1)),
    (z_T)_j = 3(h+1)*1_{j in T} - 10.

Here z_T in the projector formula is a covector, unrelated to the binary output variable above. The desired exactly-one-intersection source lines span the hyperplane with projector F_T=I-P_T. The rank is h-1. A point-total envelope H_c, with c in T, also has rank h-1, but rank(P_{H_c}-F_T)=2. The matrices are unequal; an explicit rational basis-column payload witness is retained for each tested case.

A path formed from nested subspaces cannot replace H_c by F_T without at least one unit of downward rank variation. Any zero-to-full carrier path has total paid rank variation h+2D, where D is its downward rank variation. The old paired controller has rank deficit N-L, with N=binomial(23,3)*binomial(25,3)=4,073,300 and L=2,226,400. If one global whole-output carrier per triple on each axis requires this drop, the additional mass is at least 4N=16,293,200, already much larger than N-L=1,846,900. Its total mass exceeds mW by 3N+L=14,446,300 before a positive saving is attempted.

This is a conditional obstruction to that particular carrier implementation **while retaining the old boundary/controller ledger**. A summed port has changed boundary semantics. A different decoder, redistributed global carriers, simultaneous remixes or a new recurrence may change the ledger; this report is not a general lower bound. The previous campaign's separately stored side-carrier obstruction has not been misrepresented as ruling out all cancellation.

## Honest optimistic sensitivity

A hypothetical favorable internal histogram with R_h rank-h calls and h(h-1) singleton losses, retaining all old exterior/data/growth terms, passes the binary target a=1/9999 at the abstract ordinary-side and summed-map role counts. With the old accepted role counts it fails. At a=1/999 none of the tested hypothetical counts passes, including input-only role counts. These results identify potential component leverage and a separate architecture-scale ceiling; they are not implemented physical costs or a multiplication theorem. The unchanged complex certificate separately caps final kappa below 1e-4.

A follow-up will replace this hypothetical sensitivity with a rigorous favorable lower bound, check the complete center-output map and explore cancellation circuits that remain in monotone admissible frames. The continuation criterion is a physically paid mechanism that avoids per-output rank drops or supplies a new boundary ledger with enough deficit. Large sweeps of the rejected same-carrier implementation are unwarranted.

## Provenance and reproduction

- Initial source: [global_incidence.py](../../code/synthesis/global_incidence.py), [run_discriminators.py](../../code/synthesis/run_discriminators.py).
- Results: [initial run](../../runs/20261008T210801Z-synthesis-global-incidence/).
- Geometry origin: chafreaky/integer-mult-bounds commit bc2f7ed4c20dc18898305ab17165c0c995cbb804; PR58/PR48 fixed-I+J formulas; the read-only independent rational formula control is in RaD checkpoint def95e9c12f62a41fc7a50af13d5dcc87ce13d79 at joint-frame/agents/scout/code/cancellation_rank_drop_control.py and integer_crt_profiles_v1.cpp.
- The historical scalar identities follow elementary inclusion-exclusion; this implementation and the new global-hyperplane test were authored with OpenAI Codex. Preserve predecessor credits to icekylinx, Dominik Scholz, Zhihao Chen, Swapnil Jain, Rohan Arun, Chafik Boukhalfa, Aurel Prosz and RaD/hipotures.

From the repository root, using a fresh ignored output directory:

```sh
python3 -B research/integer-mult-breakthrough/code/synthesis/run_discriminators.py \
  --workers 4 --output research/integer-mult-breakthrough/work/synthesis/NEW-RUN/results
```

The run is deterministic, has no seed and uses four single-thread worker processes. No local solver, downloaded source, network, GPU or historical binary is required. This was exercised for all four probes; the longest probe completed in approximately 16 seconds. A general exact CNOT word is not yet independently reviewed as a physical framed network.

## Dimension-uniform hyperplane proof

For h>=6, fix a triple T. Differences between two eligible source lines sharing
the same outside pair give e_a-e_b for a,b in T, spanning the two-dimensional
inside zero-sum space. Differences between two eligible source lines with a
fixed common point and one fixed outside point give e_i-e_j outside T,
spanning dimension h-4. There are at least three outside points, so those
constructions are available. These h-2 independent differences, together with
one eligible line w_U, span h-1 dimensions. Every eligible line is annihilated
by the covector z_T=3(h+1)1_T-10*1; hence this span is exactly ker(z_T).

The point-total hyperplane has annihilator ell_c=3(h+1)e_c-4*1 and complement
kernel q_c=(3h-7)*1+(h-9)e_c. These formulas follow by substituting the high
envelope into the pinned rational projector. For c in T, ell_c and z_T are
independent: compare an outside coordinate with a second target coordinate.
Likewise q_c and w_T are independent, because q_c takes the same nonzero
value at these two coordinates whereas w_T takes values 3 and 4. Thus
P_T-(I-P_Hc) is a difference of rank-one matrices with independent image
vectors and independent row covectors. Its rank is exactly two. This proves
the frame-difference claim uniformly in the stated range, rather than by
extrapolating the finite tests. The historical physical model additionally
excludes h=9 because its ambient form is degenerate; scalar and rational
matrix identities alone do not repair that model boundary.

## Related retained research

The broader read-only library already studied
[final partial-output aggregation](../../../integer-multiplication-bounds/reports/downstream-bit-output-aggregation.md),
including the target-kernel span, and proved that plain cancellation-free
aggregation does not improve its frozen multiuser-flow compiler. The
[pair-star central negative](../../../integer-multiplication-bounds/reports/downstream-pair-star-central-negative.md)
gives a closed symmetric projection-path rank lower bound under full
gather/undo and monotone target kernels. Those historical scopes remain
unchanged. This run does not claim to originate elementary inclusion-exclusion
or whole-output aggregation. Its auxiliary dirty words, explicit global-frame
mismatch tests and frozen two-axis ledger sensitivity are new campaign records;
static or dynamic global signal-basis proposals must address the prior
chronology restrictions rather than merely renaming the old motif.
