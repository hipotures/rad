# Unchanged Q4 serving control

Frozen original Strata0.1.39 binary, K24/.28, pool100us,15workers, spec4/.5, INT8, kv-resident32768, prefillauto, suffix/reuseOFF. These scripts never enable tape/oracle, rebuild or change models. They print resolved config and live logs. Default bind0.0.0.0 port8080; --host/--port override. --check validates hashes/provenance without starting a server. Foreground lifetime defaults to12hours and may be set with --timeout-s. stop.sh checks ownedPID/create-time and terminates only this campaign manual process group.

Run from this launcher directory, one server at a time:

| Total context | Command |
|---|---|
| 32768 | ./start-32k.sh --host 0.0.0.0 --port 8080 |
| 131072 | ./start-128k.sh --host 0.0.0.0 --port 8080 |
| 262144 | ./start-256k.sh --host 0.0.0.0 --port 8080 |

Use ./stop.sh to stop only a process recorded by these launchers. All three starts passed identity/model/config and shell syntax checks. The frozen original binary was run in the natural development reference; the campaign did not add separate manual-launcher inference repetitions merely to exercise thin aliases.
