"""Derive E010 metrics with the same code used for E006, then add its own interpretation."""
import pathlib
from lab import ROOT
original=(ROOT/'scripts/compare_frequency.py').read_text()
s=original.replace("EXP=ROOT/'experiments/E006-frequency'","EXP=ROOT/'experiments/E010-compatible-runtime'")
s=s.replace("('frequency',EXP/'v1'/profile)","('compatible',EXP/'v1'/profile)")
s=s.replace("=='frequency'","=='compatible'")
s=s.replace("'Existing --adapt-decay 0.7 ->1.0; source base/toolchain/common inference settings and physical cache capacities fixed.'",
            "'Causal same-owner compatible-slot EMA matching vs original same-layer EMA; frozen source base, toolchain, heat thresholds/cadence and total per-GPU slot-class bytes. No additional GPU allocation.'")
s=s.replace('Ten saved same-input-ID cases complete, four identical visible outputs; all six textual differences preserved.',
            'Ten saved same-input-ID cases complete, five identical visible outputs; all five textual differences preserved.')
s=s.replace('The six differing short answers','The five differing short answers')
s=s.replace('Predictor GPU/host allocation added by the supported decay option is zero.',
            'Additional GPU allocation is zero; host immutable slot metadata is about150kB and selector scratch/cost must be charged. Native bridge median selector cost0.786ms/call is preserved in selector-tests.')
s=s.replace('Fixed-trace replay starts from observed control post-prefill state; live frequency also changes causal warmup/prefill adaptation history.',
            'Fixed-trace replay starts from observed control post-prefill state; live compatible-slot policy changes causal warmup/prefill adaptation history.')
s=s.replace('Frequency policy live comparison','Compatible-slot live comparison')
s=s.replace('Preserve the slower candidate and its executable launchers.',
            'Preserve the candidate and its executable launchers, including any slower profile.')
s=s.replace('variants/frequency-v1-ready/reproduce.sh','variants/compatible-v1/reproduce.sh')
s=s.replace('Next: bounded diagnostic frequency trace at both profiles if needed to explain the loss; actual boundary/router availability study, and compatible-slot placement replay.',
            'Next: scoped GPU wait diagnostics and same-input first-head comparison; a policy-versus-trajectory explanation is required before selecting the apparent128k gain. Native selector overhead remains a separate repair opportunity.')
exec(compile(s,str(__file__),'exec'))
