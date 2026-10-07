"""Within-policy reproducibility from completed applications, no inference."""
from campaign import C, load, save
from analyze_live import extent

rows = []
for task in ('code-4', 'structured-4'):
    for variant in ('control', 'conditional'):
        rr = [load(C/'independent'/task/variant/f'rep{i}/results.json')['runs'][0]
              for i in (1, 2, 3)]
        rows.append({
            'task': task, 'variant': variant,
            'output_hashes': [r['actual_output_ids_sha256'] for r in rr],
            'all_same_output': len({r['actual_output_ids_sha256'] for r in rr}) == 1,
            'all_same_MTP': len({tuple(r[k] for k in
                ['mtp_proposed', 'mtp_accepted', 'verify_windows']) for r in rr}) == 1,
            'all_same_routing': len({tuple(r[k] for k in
                ['local_vram_entries', 'cpu_fallback_entries', 'nonlocal_gpu_entries'])
                for r in rr}) == 1,
            'TG': extent([r['TG'] for r in rr]),
            'interpretation': 'Timing variation at unchanged output/MTP/routing indicates environmental or scheduling variation; its precise physical cause is unavailable.'
        })
save(C/'analysis/independent-within-policy-stability.json', rows)
print('INDEPENDENT_STABILITY', rows, flush=True)
