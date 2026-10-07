# Replay launchers

These commands perform forced-work experimental replay, not ordinary chat. Each explicit run verifies source/binary/model/tape, detects GPU/port conflicts, creates a NEW sibling reproduction directory, has finite timeout/progress and stops only its owned server/collector. Existing normal Q4 launchers remain ../q4-live-oracle-20261006T040656Z/launchers/control/ unchanged.

Example: `./replay/64F-128k.sh --check` validates only. Without `--check`, a new explicit finite manual reproduction runs. Commands are available for all six retained budgets at32K/128K/256K; measured coverage is documented separately in report.md. No auto-build.
