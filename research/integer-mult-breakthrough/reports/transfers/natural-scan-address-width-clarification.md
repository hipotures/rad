# Clarification of native address width and component orientation

This dated receipt qualifies the optional-header paragraph in the frozen
[natural scan report](natural-selected-fiber-scan-tapes.md). Its literal
headerless consumer, carry proof and finite evidence are unchanged.
No frozen source, config, run or report bytes were edited.

The relations d=Theta(p^epsilon), K=floor(d^c), c>0 and epsilon<1 alone
give dK=Theta(p^[epsilon(1+c)]). They do not imply dK=O(p). The optional
header comparison needs the actual original parameter and address contract,
or explicitly epsilon(1+c)<=1 together with bounds on the other address
fields. This missing displayed condition was identified independently by
the coordinator during review.

The pinned `05-layers.tex` at openai/math revision
adc7f1241b42e322a6451854ab7e4b4c146bf78a, SHA256
20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594,
states the final restrictions

    tau=sigma=1-2^-50, beta=1/2, C1=20,
    tau(1+c/beta)<lambda<1,
    epsilon*C1<1.

In particular c<beta(1/tau-1)=1/[2(2^50-1)]<1 and epsilon<1/20.
Thus epsilon(1+c)<1/10<1, which suffices for dK=o(p). More directly,
the final proposition requires

    M=P*S*2^(KD), D<=d,
    log2(2M)<=C_M*p,
    descriptor_length<=C_desc*p.

Those pointwise assumptions give an O(p) complete address and descriptor
length for its admitted arrays. They must be retained when consuming the
optional-header O(MA) bill. A changed supplier or broader parameter family
cannot infer them only from epsilon<1. Without such assumptions, keep the
actual A and its preparation cost. The headerless standalone scan operates
on implicit record positions and does not need A=O(p) to prove its own
linear counter/table traversal; its supplied n-bit mask is still charged.

The original component record is a signed w-bit numerator written most
significant bit first. The literal research scan consumes least-significant
bit first words for its ripple arithmetic. This is an explicit format
conversion, not a free normalization. One complete component can be copied
to an ordinary marked buffer and read backward, with all copy, reverse,
rewind and erase work O(w). Doing so over r complex coefficients in every
record costs O(Mrw), a constant full-volume pass. Returning to the original
orientation costs another such pass. A fixed number of additional ordinary
buffer/stream tapes suffices, independent of r,n and recursion depth; these
conversion tapes are outside the literal seven-tape core's measured count.
The component width and any duplicate full stream are charged. The research
code does not claim to compile the original binary descriptor syntax or
to execute this orientation conversion. It supplies the exact core in the
declared framed little-endian format and an elementary all-size conversion
bill under the primary ordinary-scratch stream model.

The earlier magnitude comparison remains conditional on w=Theta(p):
reserving f+O(1) more integer/sign bits with f<=d=o(p) leaves each long
record Theta(rp). Widths of only K numeric bits still pay 1+f/K. Neither
the address restrictions nor the orientation conversion establish a whole
nonunit-network precision theorem, faster zeta supplier or kappa.
