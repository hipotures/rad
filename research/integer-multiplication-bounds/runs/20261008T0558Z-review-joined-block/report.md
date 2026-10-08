# Preserved admission-only failure

The finite successor dispatcher was already running, but its first
checkpoint was not yet materialized. This wrapper attempted to read the
expected checkpoint too early and exited with FileNotFoundError. No
scientific child process ran. The one owned reservation was released
in finally. The protocol and command/source hashes are unchanged.

The next fresh attempt waits for checkpoint creation before admission;
the mathematical checker source is unchanged.
