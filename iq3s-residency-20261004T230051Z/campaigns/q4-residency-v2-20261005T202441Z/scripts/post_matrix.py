"""Finite, serial follow-up; never overlap a build or diagnostic with speed runs."""
from campaign import C, R, load, save, guard
import subprocess, time


def main():
    end = min(time.time() + 5400, load(C / 'deadline.json')['experiment_cutoff_epoch'])
    while not (C / 'phase-c/matrix-exit.json').exists():
        guard()
        assert time.time() < end, 'Matrix wait exceeded its finite budget'
        time.sleep(5)
    assert load(C / 'phase-c/matrix-exit.json')['exit_code'] == 0
    steps = [
        ('primary-analysis', ['analyze_live.py'], 240),
        ('independent-application', ['additional_live.py', 'independent'], 2100),
        ('prediction-ablation', ['additional_live.py', 'diagnostics'], 900),
        ('client-cancellation', ['test_cancel_live.py'], 600),
        ('history-transactions', ['run_history_diagnostic.py'], 3000),
        ('additional-analysis', ['analyze_additional.py'], 240),
        ('advertised-launch-smokes', ['smoke_launchers.py'], 1500),
    ]
    py = str(R / 'src/control/.venv/bin/python')
    records = []
    for name, args, timeout in steps:
        guard()
        assert not subprocess.check_output(
            ['nvidia-smi', '--query-compute-apps=pid', '--format=csv,noheader'],
            text=True).strip(), 'Previous owned stage did not release its GPUs'
        log = C / 'logs' / ('post-' + name + '.log')
        print('POST_STAGE_START', name, flush=True)
        started = time.time()
        try:
            with log.open('x') as out:
                result = subprocess.run([py, str(C / 'scripts' / args[0]), *args[1:]],
                                        cwd=C, stdout=out, stderr=subprocess.STDOUT,
                                        timeout=timeout)
            record = {'name': name, 'exit_code': result.returncode,
                      'wall_s': time.time() - started, 'log': str(log)}
        except BaseException as error:
            save(C / 'phase-c/post-failure.json',
                 {'name': name, 'error': repr(error), 'log': str(log),
                  'next': 'Preserve and diagnose this stage before continuing; no automatic retry'})
            raise
        records.append(record)
        save(C / 'phase-c/post-progress.json', records)
        print('POST_STAGE_END', name, result.returncode, flush=True)
        assert result.returncode == 0, 'Inspect retained stage failure; no automatic retry'
    save(C / 'phase-c/post-complete.json', {'stages': records, 'finished_epoch': time.time()})


if __name__ == '__main__':
    main()
