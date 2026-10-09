# Independent review of contiguous streaming boundaries

Status: **SOURCE AND MATHEMATICAL REVIEW** of the stated conditional scan bill and finite operator/precision scope. I inspected the frozen producer, arithmetic closure, integer audit and report without importing or executing their programs. Producer PASS counts cited below remain producer evidence, not independent reruns. No fast postprocessor or exponent is accepted.

Reviewed source closure:

- [streaming_scan_boundary_preflight.py](../../code/synthesis/streaming_scan_boundary_preflight.py), SHA256 `835fbd189c6ea0c8ab50e99aca8ee17e02bc66f408bc854c2c313b186480637c`.
- [audit_streaming_scan_precision.py](../../code/synthesis/audit_streaming_scan_precision.py), SHA256 `ba4e3de3df2f680101043df46b53dedd053dd291f63e1c93463650c0946a5bfe`.
- [nonunit_address_amplitude_preflight.py](../../code/synthesis/nonunit_address_amplitude_preflight.py), SHA256 `b1ddb07507be5b093ae88bc16364c3284f8db14366f57fa9916e96b17ed5a50a`.

The [producer report](../synthesis/streaming-scan-boundary-preflight.md) separates complete finite matrices, finite physical register controls and the conditional standalone scan cost. The [operator run](../../runs/20261009T035303Z-synthesis-streaming-scan-preflight/) and [repaired integer run](../../runs/20261009T040121Z-synthesis-streaming-scan-precision-repair/) retain their own protocols. The earlier annotation-only failure is preserved under its original source and recovery patch. I made no changes to these files.

## Full-record scan bill

For a contiguous stream of complete guarded records, a prefix computes `y_a=x_a+y_(a-1)`; its inverse computes `x_a=y_a-y_(a-1)` using the original previous input, not an already differenced value. The source's forward scan and saved-original difference have the correct chronology. Right matrix multiplication uses the reversed column-update chronology, which is essential for the stated pre/post equation.

Two complete record buffers suffice on a fixed number of tapes. Read the current record into B2. For a prefix, replace its coefficient fields by B2+B1, output B2, and copy it to B1. For a difference, replace B1's coefficient fields by B2-B1, output those fields with the current metadata, and copy the unchanged current B2 to B1. These operations explicitly retain the previous sum or previous ORIGINAL record as appropriate. They do not require clean logical Gaussian banks.

MSB-first signed fields can be added by walking the guarded buffers from their least significant ends, updating one buffer, then returning to emit forward-order output. Every arithmetic traversal, head return, complete-buffer copy, metadata copy and final buffer erase costs O(R+A), where R is the payload width and A the complete metadata width. The record count M therefore gives `O(M(R+A))` standalone traffic. When complete-record volume includes the headers, or the retained long-record regime has A=O(R), this is O(V). Descriptor initialization and any higher polynomial control computation remain separate until their paid long-record hypotheses apply.

The finite simulator tracks Gaussian records and logical reads/writes rather than literal tape-head motion. My argument accepts the conditional traffic order, not a claim that the Python simulation compiled it. Ordinary blank machine workspace may be written and erased with its cost; this is different from erasing an arbitrary dirty scalar bank. The two buffers need their complete numerical guards, and the end erases must scan their full visited widths.

On a D-record fiber, a prefix needs at most log2(D) additional magnitude bits; a difference needs one. Integer shears and routes introduce no fractional bits. The one amplitude layer multiplies a coordinate by two or one-half and needs its actual one-bit guard. The finite preword's matrix-prefix L1 bounds are uniform bounds for that named finite linear map. Observed integer-register peaks in the audit concern the declared finite fields and literal temporaries; they do not automatically become an all-input, all-size implementation guard for an unknown post word.

## Exact operator and fixed-grid scope

The tested quotient is `P0=diag(I,I,C_f,C_f,C_f,C_f)` with target Q consisting of six C_f tensors. The actual original h4 joint core has distinct missing directions; this quotient cannot be substituted into it without a separate physical audit. Given a preword B, the unique matrix `R=Q*B^-1*P0^-1` trivially specifies the required repair. Exact comparison of `R*P0*B=Q` establishes the complete finite operator identity, not a native factorization of R.

The integer audit starts with one reserved grid that includes the incoming format, preword denominators, actual core C depth and post-coefficient grid. It checks each signed numerator and individual exact division. Its dense coefficient evaluation pays four integer products per nonzero complex coefficient per Gaussian field; it does not use fraction reduction or free output normalization. The retained totals, 156456 integer coefficient products and 1440 final component comparisons, are internally consistent with the four cases' coefficient counts and three fields. They are finite correctness/precision evidence and an explicit expensive implementation control.

The modular cut ranks are legitimate characteristic-zero LOWER certificates: reduction of Gaussian-dyadic coefficients into the field F3[i]/(i^2+1) is a ring homomorphism, and a nonzero minor modulo three cannot come from a zero Gaussian-rational minor. Equality with a full rational rank is not presumed. Independently, C_f's off-diagonal midpoint block is a nonzero scalar times C_(f-1), giving rank D/2; six target banks give 3D and four core banks give 2D.

## Geometry that remains unpaid

A contiguous D=2^f quotient scan is not yet a scan along selected bits in a complete native `(f+1)K`-bit slot. Those selected bits are interleaved with arbitrary guards and spectators. A native program must either gather/reset the selected-bit fibers with all routing work paid, or define a genuinely different scan across the full complete address range and prove its whole target. Neither geometry can silently discard guard values. The magnitude allowance is the logarithm of the ACTUAL range accumulated by the scan, not f merely because f bits were selected in a quotient test.

Similarly, per-bank reversal, large-stride routing, every nonlinear q control, row splitting, full-field format, returned layout and postprocessor must be bound to the complete native shape. They are correctly listed as unpaid in the producer report. Reversal or a nonlinear address route may carry large cut rank cheaply; a fixed-order scan lower bound cannot be transported across that route without recomputing its cut.

The [separate coupled cut-rank deduction](coupled-cut-rank-transfer-boundary.md) gives an all-size obstruction for bounded cross-cut-rank boundary blocks. It does not reject general scans with changed routing order. Prefix scans genuinely escape a row-support bound, while the missing native layout and required post still prevent a whole transfer or larger kappa claim.
