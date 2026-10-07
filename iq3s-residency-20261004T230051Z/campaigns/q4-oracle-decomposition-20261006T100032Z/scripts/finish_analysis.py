"""Finite post-run analysis only after all GPU requests have stopped."""
import subprocess
import sys

from owned import C, run


def main():
    jobs = subprocess.check_output(
        ['nvidia-smi', '--query-compute-apps=pid', '--format=csv,noheader'],
        text=True, timeout=10).strip()
    assert not jobs, 'Refuse heavy analysis concurrently with GPU work'
    for label, script, timeout in [
        ('final-primary-analysis', 'analyze.py', 600),
        ('final-independent-analysis', 'independent_analyze.py', 240),
        ('final-mechanism-analysis', 'mechanism_batch.py', 1200),
        ('final-transactional-summary', 'augment_summary.py', 60),
        ('final-future-memory', 'future_memory.py', 120),
    ]:
        run(label, [sys.executable, C / 'scripts' / script], timeout=timeout)
    print('FINAL_ANALYSIS_COMPLETE', flush=True)


if __name__ == '__main__':
    main()
