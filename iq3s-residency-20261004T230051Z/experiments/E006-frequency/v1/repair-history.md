# Repairs before inference

No runtime algorithm, model or source-base correction was needed.

1. The initial registration rejected an untracked read-only `.venv` symlink. It also created an empty variant directory before validating source state. Preserve `variants/frequency-v1/FAILED.json`; the repaired registration is `frequency-v1-ready`. The shared dependency symlink is excluded in the local checkout's `.git/info/exclude`, and the registrar now validates before creating a directory. Source remains exact frozen base; binary is unchanged.
2. The first repair was invoked with system Python, which has no `psutil`. It did not change source or run a server. Subsequent research commands use the pinned project venv. The premature test-driver command failed because registration had not completed; its log is retained.
3. The first test helper used `unittest discover -s tests`, whereas upstream Python tests live in `serve`. Zero tests ran, with nonzero return code; this is not counted as success. Only Python discovery is rerun in `tests-python-repair`, not the already completed CTest or native parity tests.

CTest: 62 passed, 2 skipped, 4 environmental failures out of 68. Failures match clean control: missing Q2_0 PLE fixture, restricted mlock, and legacy `pack/full/experts.bin` absent for expert/pool fixture tests. No model download or fixture substitution is used. Real native IQ3_S expert parity for layers 0/1/2/12 reports zero failures. Repaired Python suite: 268 tests, 7 skipped, pass.

Preserved-source correctness requests are frozen with the real service tokenizer in `workloads/correctness-manifest.json`. Their messages/sampling are unchanged; the saved 512-token case-5/6 extensions are used equally for control and frequency. These short requests may stop naturally. NaN debug checks are diagnostic-only and cleared for headline launches.

4. The initial diagnostic battery stopped after case 4 because the harness matched the text `0 non-finite` as an error. Raw engine output explicitly reports zero non-finite values. This is a detector false positive, not a runtime correctness failure. Preserve the partial v1 battery; corrected parsing checks the reported numeric counts. The full battery is rerun under separate `correctness-r2` attempt paths, with both variants using the same requests and diagnostic policy. No headline request has been run or repeated during these repairs.
