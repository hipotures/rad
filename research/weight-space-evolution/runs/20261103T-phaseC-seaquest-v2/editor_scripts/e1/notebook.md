# Editor notebook (phaseC-seaquest-v2-e1)
- Pass1 gold-only 1000: 50.86 (len 1365; no episode >3083 steps: surfacing-driven difficulty wall). Sub never moves l/r, faces left, x=5.
- Pass2 p-38e02409d21a (h1[24] O2 gauge cell (9,2)->(9,1): surface at O2<40): +1.48 +-1.90; len +10%, kills/step -7%.
- Pass3 p-cb8f55807c70 (cand1 + strong left-enemy row attraction): -3.22 +-1.97.
- Pass4 p-9848544c5c15 (gate row-3 up drift behind ascent feature): -2.83 +-1.44.
- Pass5 p-38e02409d21a replicate: +0.40 +-1.80. Pooled ~ +0.94 +-1.3.
- Pass6 p-457ce4798f60 (turn-to-shoot module, 264 entries): 8.08 vs 54.10 (-46). Bug: target term T is true when the sub is outside S rows 3-8 (rows 0-2), so FIRE_R/T-suppressed TRIG_L lock the displaced sub at x7 firing; it never ascends -> oxygen deaths.
- Submit p-38e02409d21a.
