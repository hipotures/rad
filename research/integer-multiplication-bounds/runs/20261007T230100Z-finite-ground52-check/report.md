# Failed evidence write after ground-size checks

The `h=52`, globally paired, base-threshold-2 circuit computation completed
the map/frame code path, but the command failed while writing its JSON result
because the output directory did not exist. No result was persisted, so this
attempt is not used as evidence that the candidate passed.

The generator was repaired to create the output parent directory. A fresh
attempt is recorded separately under `20261007T230300Z-finite-ground52-recheck`.
The mathematical checker and candidate parameters were unchanged.

Failure: `FileNotFoundError` from `Path(args.output).write_text(encoded)`.
