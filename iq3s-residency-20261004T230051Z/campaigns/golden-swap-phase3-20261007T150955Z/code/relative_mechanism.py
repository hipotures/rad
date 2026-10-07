"""Paired percentages supplement absolute timers; no nested interval sums."""
from common import *

if __name__ == '__main__':
    runs = load(C / 'results/live-attempts.json')
    metrics = []
    for pair in load(C / 'results/paired-blocks.json'):
        baseline = next(r for r in runs if r['task'] == pair['task'] and r['block'] == pair['block'] and r['arm'] == 'PLANNER_BASELINE')
        metrics.append({'task':pair['task'],'block':pair['block'],'CPU_removed_pct':100*pair['planner_cpu_removed_ms']/baseline['planner']['host_cpu_ms'],'GPU_plan_wait_removed_pct':100*pair['gpu_plan_wait_removed_ms']/baseline['gpu_plan_wait_ms']})
    save(C / 'results/relative-mechanism.json', metrics)
    print('RELATIVE MECHANISM', len(metrics), flush=True)
