# Bounded residual tensor verifier

The verifier checks both literal tensor words at f=1 and f=2, complete source/sink/dirty columns, all paired corruption controls, full Pauli projections and exact small-factor Gram checks. It deliberately exchanges the inverse conditional scales and requires complete-column rejection.

See [check.json](results/check.json) for effective hashes and scope. Run `python3 -B research/integer-mult-breakthrough/code/synthesis/verify_tensor_chronologies.py`. The effective closure is this verifier, `compressed_tensor_chronology.py` and `pauli_tensor_discriminator.py`. No native tape/precision or multiplication exponent is certified. Original receipt is unchanged in ignored `work/synthesis/20261008T231415Z-tensor-ci/check.json`.
