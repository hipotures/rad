# A scoped endpoint-correction exclusion

Question: can the new copied-center construction remove Paureel's separate
rank-one endpoint correction by changing only the free pointwise scalar
mixing of the two final data streams? Answer: no in this restricted family.
This changes an attempted assembly optimization, not the producer graphs.

The pinned PR29/36 two-stage endpoint is A=Fy, B=Fx+Ey, where F=D_I,
T=D_P and E=TF=D_(I-P). On a nonzero proper projector component P, T
exchanges the two address chunks; on its complement T is the identity.
The desired pair is (Fy,Fx). These are arbitrary source fields, and the
dirty auxiliary contract is unchanged.

Suppose a constant pointwise scalar matrix M=[[a,b],[c,d]] over F2 takes
(A,B) to (Fy,Fx), with no address operation. The coefficient of x in the
first output gives bF=0, hence b=0 and a=1. The second x coefficient gives
c arbitrary and d=1. Its y coefficient is cF+E=0, so E=cF. Multiplying
by F implies T=cI, impossible for a partial address interchange on a
nonzero proper P. This covers all six invertible scalar mixers, any
pointwise XOR word and either scalar output-bank permutation. It also
covers rationally conjugate address projectors; the obstruction is
operator equality, not a coordinate-specific numerical accident.

The paid transform on a copy succeeds because T(A)=TFy=Ey, so
B+T(A)=Fx. Its copy has the inherited role volume V/W and same row index;
the original A is retained. This analysis preserves, rather than removes,
the N separate rank-one corrections in every promoted child list.

[Exact finite control](../runs/endpoint-mixer-negative/certificate.json)
enumerates all six scalar GL2 mixers for address dimensions2..13 and every
nonzero proper coordinate projector rank. Every basis vector of both
source fields is tested; the paid correction succeeds on every probe.
The [checker](../code/endpoint_mixer_discriminator.py) is independently
implemented with integer bit operations. The proof is general in the
declared family; finite probes are its bounded implementation control.

Changing source gauges, obtaining other live streams, allowing target
frames to leave the retained chronology, joint address actions or a new
native compiler lies outside this exclusion. Those possibilities require
new physical endpoints and charges. It is not a lower bound on integer
multiplication or all two-stage constructions. Endpoint identity and copy
credit belong to Aurel Prosz/Paureel, with PR29 Zhihao Chen and PR36
icekylinx supplying the pinned integration; this campaign supplies the
present restricted attempted-removal audit.
