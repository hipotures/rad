# Independent review of the release-aware singleton formation bound

Status: **ANALYTICAL AND SOURCE REVIEW OF A SCOPED OBSTRUCTION**.
I accept the lower bound of 24 excess ranks per weight-five source cube
under the stated pure carried-helper and monotone literal-root model.
This review imports no producer and reruns no producer controls. It does
not verify Gaussian address matrices or native tape execution.

Reviewed source:
[singleton_fanout_release_probe.py](../../code/synthesis/singleton_fanout_release_probe.py),
SHA256 fec8292dd3fad1c1e008b543bfefc448d51648068ebdb32ea123959a27ff5746.
The [producer proof](../synthesis/pure-source-singleton-fanout-release-bound.md)
states the complete premises and its finite controls.

The full paired weight-five cube spans a six-dimensional binary space.
Each of its ten singleton buckets is a different five-dimensional
hyperplane, with sixteen odd labels. In a proper rank-at-most-four
subspace, either the parity functional vanishes and there are no odd
labels, or its odd fiber has at most eight elements. Any nine distinct
bucket labels therefore span that whole bucket. This argument does not
require sampled source orders.

An unreleased pure source helper retains its original source label in its
intersection with the fixed full diagonal Lagrangian D. When it writes
into a canonical bucket root at the same actual frame, that root contains
the label. Monotone root growth retains all earlier unreleased labels.
If r_b released sources belong to bucket b, at least max(8-r_b,0)
unreleased writes must meet its full bucket frame. With l releases and
each source belonging to five buckets, the total compulsory visits obey

    F >= sum_b max(8-r_b,0) >= 80-5l.

Two distinct full bucket frames have distance two. An unreleased helper
visiting r distinct compulsory buckets consequently pays at least
h-1+2(r-1) after its source injection, before its full endpoint. Summing
over no more than 32-l unreleased helpers leaves at least
2max(F-(32-l),0) additional ranks.

The general helper-Lagrangian release argument is also valid. For
E(A)=A intersect D and E(B)=B intersect D, the space
E(A)+E(B)+(A intersect B) is isotropic. Furthermore

    (E(A)+E(B)) intersect (A intersect B) = E(A) intersect E(B).

For the reverse inclusion, write v=a+b with a in E(A), b in E(B) and
v in A intersect B. Then b=v-a belongs to A intersect D as well as E(B),
and a=v-b similarly belongs to E(B). Thus both belong to E(A) intersect
E(B). The dimension bound gives

    d(A,B) >= dim E(A)+dim E(B)-2 dim(E(A) intersect E(B)).

A helper that loses its source line incurs at least h+1 rank from that
line through the losing frame to full, compared with the h-1 geodesic.
Combining released and unreleased contributions proves

    extra >= 2l + 2max(48-4l,0) >= 24.

The elementary minimum occurs at l=12. It is a lower bound, not an
attained chronology. Three cores add at least 3*(24/32)v=2.25v. Genuine
additional formation helpers add their baseline m-rank and W stock
together; that cancels their baseline contribution to the first-moment
deficit, but cannot remove this excess. The unchanged center/data master
has deficit at most 2v, so this formation model already fails the rank
first moment before evaluating a saving.

The producer's all-release scalar word correctly demonstrates why the
stronger no-release bound of 96 is not universal within its allowed
released class. It subtracts each helper's old value at identity, injects
the source at its actual line, returns the helper to identity for unit
root writes, then finishes the helpers and sources at full before source
subtraction. A helper pays 0->line->0->full, h+2 rather than h; all 32
helpers pay 64 excess ranks. The early subtraction retains each root's
own seed and removes only helper responses. Every scalar gate's declared
common-frame check and the complete matrix/inverse source assertions are
consistent with that algebra. This is source inspection, not my own
physical-matrix replay.

Pure source coefficients, direct unit additions, literal monotone bucket
roots and the retained frame metric are indispensable premises. Helper
mixing, cancellation-built coordinates, cuts/new births, copied readers,
non-Clifford operators, cross-column encodings or changed endpoints can
escape them. A shared helper with additional uses may have larger costs;
its useful scalar capacity is not ruled out by this named lower bound.
The review was developed with AI assistance.
