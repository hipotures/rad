"""Generate the final bounded-bootstrap research report from preserved analysis and frozen target metadata."""
import json
from pathlib import Path

from . import pd2_bench as B
from .bootstrap_prepare import TOPIC


def main():
    run=TOPIC/'runs/20261103T-phaseD-bootstrap-execution'
    d=json.loads((run/'results/final_analysis.json').read_text())
    root=TOPIC/'work/phaseD-bootstrap/execution'
    final=json.loads((root/'final-complete.json').read_text())
    search=json.loads((root/'supervisor.json').read_text())
    plan=json.loads((root/'final-plan.json').read_text())
    parents=list(d['lineages'])
    test=d['splits']['test'];transfer=d['splits']['transfer']
    lines=['# Phase D — Parent-to-Editor Bootstrap: completed bounded study','',
    '**Result: no parent-created candidate showed a confirmed improvement in neural-network editing ability.**',
    'Four independent gpt-6.1-sol / medium sessions produced four distinct direct-weight variants of Qwen3.5-0.8B. '
    'None improved the frozen primary endpoint on the independent test split; every paired 95% confidence interval includes zero. '
    'The bootstrap gate did not pass. This is a negative result for this bounded study, not proof that all direct-weight bootstrapping is impossible.','',
    '## Primary result','',
    'The unchanged Phase D v2 primary endpoint uses 15 frozen family/tier cells on 200 independent test instances '
    '(3,104 paired instance × tier × sample outputs per candidate). Confidence intervals use the frozen '
    '2,000-resample instance-cluster bootstrap; Holm correction includes all four parents. The frozen implementation '
    'averages paired differences within instances before averaging across instances. Gold primary recovery is '
    f"{test['editors']['E0']['primary']['mean_recovery']:.6f}.",'',
    '| Parent | Sealed patch | Test Δ vs Gold | 95% CI | Holm p |','|---|---|---:|---|---:|']
    for sid in parents:
        v=test['primary_endpoint'][sid]
        lines.append(f"| {sid[-2:]} | {d['lineages'][sid]['patch_id']} | {v['mean_diff']:+.6f} | [{v['ci95'][0]:+.6f}, {v['ci95'][1]:+.6f}] | {v['p_holm']:.3f} |")
    lines += ['', 'No candidate was select-confirmed either. Select deltas were '
              + ', '.join(f"{sid[-2:]}: {d['splits']['select']['primary_endpoint'][sid]['mean_diff']:+.6f}" for sid in parents)
              + '; all Holm p-values exceed 0.05. Test evaluated the fixed sealed population, including select-negative '
                'candidates, under the execution plan recorded before parents started. No candidate was replaced or '
                'repaired after select, and no select/test/transfer output reached a parent.','',
    '## Useful repairs and regressions','',
    'Slightly less negative aggregate recovery is not evidence of a newly created repair capability. '
    'The table below uses all test T2/T2P cells, including the secondary F4/T2 cell excluded from the primary endpoint. '
    'An effective repair means frozen recovery ≥ 0.5; invalid edits are no-ops. Overall validity and regression rates '
    'include all four tiers, so T0 choice performance must not be mistaken for free-form editing ability.','',
    '| Editor | Effective T2/T2P repairs / 1,600 | Overall valid rate | Overall regression rate |',
    '|---|---:|---:|---:|']
    for eid in ['E0']+parents:
        stats=test['editors'][eid];opened=[c for k,c in stats['cells'].items() if k.endswith(('/T2','/T2P'))]
        count=sum(round(c['effective_rate']*c['n']) for c in opened)
        lines.append(f"| {eid} | {count} | {stats['all']['valid_rate']:.4f} | {stats['all']['regression_rate']:.4f} |")
    metas=[json.loads(p.read_text()) for p in (B.bench_dir()/'test').glob('*.json')]
    baseline={k:sum(m['baselines'][k] for m in metas)/len(metas) for k in ('heuristic_simple','heuristic_improved','oracle')}
    lines += ['', 'The target-level no-op baseline has recovery 0. The frozen simple heuristic averages '
              f"{baseline['heuristic_simple']:.3f}, the improved heuristic {baseline['heuristic_improved']:.3f}, and the oracle "
              f"{baseline['oracle']:.3f} on these test instances. These are references, not matched-compute claims: the "
              'improved heuristic uses multiple probe evaluations whereas T2P permits one per trial. '
              'Complete per-family/tier validity, effective/full-repair rates, regression rates, valid-only means and '
              'jointly valid paired contrasts are retained in results/final_analysis.json.','',
    '## Random controls and transfer','',
    'Each final candidate has one predetermined-seed random editor control that permutes its Gold-relative deltas '
    'onto live positions in the same tensors. Candidate positions are excluded where capacity permits. BF16 rounding '
    'can change the actual control count/norm slightly; exact mismatches are recorded in results/final_plan.json. '
    'No parent beats its own matched random editor on test: all four paired confidence intervals include zero. '
    'p50c and five fixed random editor controls were also evaluated. Target-level matched-random, no-op and heuristic '
    'baselines remain those of the frozen benchmark.','',
    'Transfer uses 92 secret-seed instances: 44 held-out F1–F4 subtype instances plus 48 instances of the unseen '
    'algorithmic-transformer family F5. F5 is secondary and is never added to the frozen primary cells.','',
    '| Parent | Transfer core Δ vs Gold | Core Holm p | F5 Δ vs Gold | F5 95% CI | F5 Holm p |',
    '|---|---:|---:|---:|---|---:|']
    for sid in parents:
        core=transfer['primary_endpoint'][sid];f5=transfer['F5_secondary'][sid]
        lines.append(f"| {sid[-2:]} | {core['mean_diff']:+.6f} | {core['p_holm']:.3f} | {f5['mean_diff']:+.6f} | [{f5['ci95'][0]:+.6f}, {f5['ci95'][1]:+.6f}] | {f5['p_holm_across_four_parents']:.3f} |")
    lines += ['', 'No parent has confirmed positive transfer against Gold. A secondary parent-03 versus its matched '
              'random control contrast on core transfer is positive before correction (p = 0.020), but does not survive '
              'correction across four parents (p = 0.080). It also does not establish improvement over Gold. '
              'No specialization, new general capability, or recursive improvement is demonstrated.','',
    '## What actually ran','',
    'The initial laboratory goal was complete. A new execution goal, configuration and session tools were committed '
    'and pushed before parent execution (commit ebe8ab98e). Subsequent user steering explicitly withdrew the earlier '
    'agent-proposed monetary/token approval wait and authorized existing Codex access. Parents used the existing '
    'ChatGPT login through Codex CLI 0.166.0, with no new service credential or separately configured billed service. '
    'No independent claim about account billing is made.','',
    'Each parent received a fresh conversation, separate scratch space, the common task brief with a different '
    'initial search approach, permitted Gold tensor views and dev-only per-cell feedback. Specializations were not '
    'assigned. Local maxima were 30 full dev passes, 200 numerical sandbox calls and four hours per parent. '
    'Parents chose different dev aggregations and stopped after diminishing returns; the final endpoint was common. '
    'Exact Gold/no-patch requests were refused by the initial broker, so parents used explicitly disclosed near-Gold '
    'controls; final operator evaluation always uses actual Gold.','',
    '| Parent | Dev passes | Sandbox calls | Final changed entries | Direct intervention |',
    '|---|---:|---:|---:|---|']
    descriptions={parents[0]:'Attenuate 36 selected layer-11 MLP output columns by 0.9',
                  parents[1]:'Multiply layer-11 query-norm coordinate 52 by 1.5',
                  parents[2]:'Subtract 1.0 from selected decay biases in six layers',
                  parents[3]:'Subtract 0.125 from selected decay biases in six other layers'}
    for sid in parents:
        count=d['tool_counts'][sid]
        lines.append(f"| {sid[-2:]} | {count['dev_evaluation_passes']} | {count['sandbox_runs']} | {d['lineages'][sid]['changed_entries_in_last_patch']:,} | {descriptions[sid]} |")
    lines += ['', f"The parent search completed 53 full dev passes and 85 sandbox calls in {search['wall_s']:.2f} s wall time. "
              'It produced 46 distinct accepted patches. All four parent processes and both dev workers exited zero. '
              f"Final independent evaluation completed {final['jobs']} jobs in {final['wall_s']:.2f} s: 16 fixed evaluator "
              'entries on select, test and transfer, plus one select-only Gold technical repeat. '
              'There were four distinct final candidate tensor states, not duplicate submissions.','',
    'All candidate updates are direct numerical edits of the pinned immutable Gold checkpoint. Final recipes and '
    'parent interpretations are in parent_reports/; exact tool code, calls, responses and failures are archived. '
    'No candidate training, LoRA, SFT, autograd or optimizer updates were used. The targets are separate frozen '
    'networks; ordinary language-model answers were not used as a substitute for editing quality.','',
    'Parent thread IDs and raw CLI token usage, editor generation/probe/scoring/transition times, token-normalized '
    'and GPU-second-normalized recovery, and peak allocated/reserved memory are in results/final_analysis.json. '
    'CLI input counts include repeatedly cached conversation context and must not be interpreted as unique input '
    'data or a monetary estimate. Resource ratios for negative recovery are descriptive, not evidence of useful efficiency.','',
    '## Integrity and the observed repeat anomaly','',
    'All 595 original benchmark payload pairs and all five manifest commitments were checked, as were Gold and the '
    'original secret-salt commitment. The frozen benchmark/evaluator source lock still matches after execution. '
    'No instances, accepted cells, decoding settings, samples, metric definitions or primary statistical functions '
    'were modified. The original held-out files and salt remain private and owner-restricted.','',
    'Parent tools ran through a session-bound local broker with transactionally enforced evaluation counters, '
    'candidate ownership and irreversible sealing. Numerical Python ran in the existing no-network numpy sandbox; '
    'Gold was read-only. An outer filesystem namespace hid the topic from remaining Codex builtin tools; the '
    'privileged broker communicated over one session-specific socket. Dev workers refuse held-out splits. Final '
    'evaluation is an operator-only adapter around the unchanged persistent evaluator and registry.','',
    'Two cross-GPU dev repeats differed: 58/1,664 output texts for one near-Gold state and 7/1,664 for another '
    'state, with mean-recovery differences −0.002453 and −0.001085. Other observed repeats agreed. Transition '
    'fingerprints passed; the cause is unresolved, so global bit reproducibility across concurrent workers is not '
    'claimed. The diagnostic is preserved in results/dev_repeat_audit.json.','',
    'Before held-out scoring, Gold, all four parents and their matched controls were assigned to one discovered '
    'GPU. The second GPU ran the legacy controls and its own Gold reference. Both persistent engines stayed alive '
    'across splits; all select work completed before test, and all test work before transfer. A same-GPU Gold '
    'select repeat matched all 1,664 responses and scores exactly before test was opened. It contributes no extra '
    'primary samples. All four dev/final worker Gold audits passed. Both GPUs were idle with 1 MiB used after shutdown.','',
    'The synthetic five-job two-GPU smoke and 22 infrastructure/frozen-benchmark tests passed. A separate BF16 '
    'two-generation archive test passed, including corruption rejection. A fresh registry reconstructed all 46 '
    'archived parent patches with matching content IDs and tensor hashes, without changing production Gold. '
    'A representative p50c export also reconstructed its original ID.','',
    '## Persistence, limitations and next step','',
    '- [Compact complete analysis](results/final_analysis.json), [fixed final plan](results/final_plan.json), '
    '[sealed candidates](results/sealed_candidates.json), [recovery check](results/recovery_check.json).',
    '- [Parent provenance and all 46 lossless patch exports](../../evidence/20261103T-phaseD-bootstrap-parent-provenance/), '
    '[full dev rows](../../evidence/20261103T-phaseD-bootstrap-dev/), '
    '[full final rows and control patches](../../evidence/20261103T-phaseD-bootstrap-final/).',
    '- [Goal](../../GOAL.md), [configuration](../../configs/phaseD_bootstrap/), '
    '[ordered reproduction and recovery](../../reproduce.md#12-authorized-existing-codex-four-parent-execution), '
    '[artifact manifest](../../artifact-manifest.json).','',
    'Confidence is high that none of these four candidates passed the frozen primary criterion. It is limited to '
    'one configured frontier model/effort, this small Gold model, these task families and 53 dev passes. The intervals '
    'do not prove exact equivalence or exclude every small gain. No ordinary-task regression campaign or broader '
    'tentative gate threshold was validated; no broader gate success is claimed.','',
    'The provider exposes a model ID, not an immutable parent-model build revision. Exact parent re-execution is '
    'therefore not promised; accepted weight edits themselves are recoverable byte-for-byte from the archives and '
    'public pinned Gold. The private persistent backup location for the original held-out salt remains unknown. '
    'Its loss would break regeneration of these secret split identities; this pre-existing recovery gap is '
    'disclosed rather than described as solved. Private CLI login homes/account databases are excluded from evidence.','',
    'Recommended next step: diagnose the cross-GPU dev repeat differences, then preregister a qualitatively different '
    'bounded parent interface or mechanism (for example controlled activation inspection) before increasing search '
    'or population size. The present evidence does not justify recursive or population-scale improvement claims.','',
    'Configuration guidance consulted and exercised locally: '
    '[official Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference), '
    'accessed 2026-11-03. The first transport probes failed closed on code-mode-host and tool-approval settings; '
    'the corrected probe succeeded. Their complete diagnostic logs are archived separately.','']
    (run/'report.md').write_text('\n'.join(lines))
    print('Wrote',str((run/'report.md').relative_to(TOPIC)))


if __name__=='__main__':main()
