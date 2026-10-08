# Signed terminal kernel transfer

The scalar circuit is Avi Eisenberg's cyclic interval construction in PR #62, pinned at `ad0f25ff7b23cff7f08ad237c2254e6ecf74257e`. The literal reversible joint compiler and paid reclamation are eumemic's PR #57, tested at `cd350f76c9bc01489ec83568bded532cb69be938`. This note applies the campaign's earlier rational conjugacy and signed positive-frame methods to those words. It does not attribute the complete interval or joint construction to this campaign, and it does not by itself certify a multiplication exponent. Alejandro Zarzuelo Urdiales's PR #61 (`afb7cb67d1858641315cfbf4ac768ee64a8eff3a`) refines parameters for the preceding physical construction.

Let (J=\mathbf 1\mathbf 1^T), (H_0=I-J/9), and (L_\beta=I-\beta J). For any admissible rational basis, its conjugate is

\[
\beta^*=\frac{1-9\beta}{9(1-h\beta)},\qquad L_{\beta^*}L_\beta=H_0.
\]

For a source triple (T\), the normalized dual has inside and outside coefficients (u=(1+\gamma)/2\) and (v=\gamma/2\), where \(\gamma=(9\beta-1)/(3(1-h\beta))\). Thus \(u-v=1/2\) and

\[
v-\beta(3u+(h-3)v)=-1/6.
\]

Consequently its actual target functional obeys the exact, basis-independent identity

\[
\mu_T L_\beta x=\frac{3\sum_{i\in T}x_i-\sum_i x_i}{6}.
\]

Fix an ordinary output with common coordinate \(c\in T\), and write \(T=\{c,a,b\}\). Its positive hyperplane is

\[
H_c=\{x:\sum_i x_i=3x_c\}.
\]

The original envelope is \(E=\{x\in H_c:x_a=x_b=0\}\), of dimension \(h-3\). The full legal sink kernel within this positive hyperplane is larger:

\[
K_T=H_c\cap\ker(\mu_TL_\beta)
    =\{x\in H_c:x_a+x_b=0\}
    =E\oplus\operatorname{span}(e_a-e_b).
\]

It has dimension \(h-2\). The added direction is orthogonal to \(E\) for \(H_0\), with squared norm 2. On \(H_c\), the form is positive because

\[
x^TH_0x=\sum_{i\ne c}x_i^2,
\]

and this vanishes only at zero. The signed columns used in the literal words have disjoint nonempty supports outside their forced coordinates, which independently proves their linear independence and positive restriction.

For any integer-column basis \(B\) of a positive space \(A\), define the actual rational projector

\[
P_A=L_\beta B(B^TH_0B)^{-1}B^TL_{\beta^*}.
\]

Writing \(d=e_a-e_b\), the direct sum above gives

\[
P_{K_T}=P_E+\frac{L_\beta dd^TL_{\beta^*}}{2}
       =P_E+\frac{dd^T}{2},
\]

because \(Jd=0\). This proves legal terminal enlargement and its actual projector. It does not imply identical ordered northeast ranks for different bases or words; the executed transition matrices and their contiguous child widths must still be recomputed.

The selected signed words have 5,313 ordinary h23 outputs of rank 21 and 6,900 ordinary h25 outputs of rank 23. Their source injection spaces remain rank-one source lines. Their copied-center spaces remain the same rank \(h-1\) hyperplanes in both directions of containment. Ordinary side growth is explicitly recounted as \(h-r\), giving 10,626 and 13,800 singleton side components respectively. The source-only reconstruction and actual transition binaries, not these totals alone, determine the physical certificate.

An initial interface checker incorrectly demanded equality with every original ordinary envelope. It rejected these valid enlarged terminals. The preserved receipt `gpu-parameter-results/signed-interface-envelope-assumption-rejected-20261008T1954.json` records that scoped verifier failure. The repaired independent checker requires original-envelope containment, exact normalized sink annihilation, actual ranks, unchanged copied-center spaces, and the complete paid word. Its passing receipt is `gpu-parameter-results/signed-budget256-Q-old15-21-source-center-data-scalar-stock-20261008T1955.json`.

The finite payload word acts over F2; these rational identities concern its address spaces. The result remains conditional on the inherited all-size analytic, precision, routing, resampling, prime-setup and fixed-tape interfaces. Full dirty restoration, local CRT ranks, all-source DATA geometry, recurrence moments and complete strict assembly are separate acceptance gates.
