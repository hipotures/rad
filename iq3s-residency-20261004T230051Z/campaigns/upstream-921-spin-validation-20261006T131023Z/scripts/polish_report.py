from pathlib import Path
p=Path('scripts/render_report.py');s=p.read_text()
for a,b in {'GGML pin`':'GGML pin `','roughly47%':'roughly 47%','0.28,15':'0.28, 15','balanced2/2':'balanced 2/2','AggregateCPU':'Aggregate CPU','andTTFT':'and TTFT','Seed92110020261006':'Seed 92110020261006','First10':'First 10','2AB/2BA':'2 AB/2 BA','2 AB/2BA':'2 AB/2 BA','Limitations:10–12pairs':'Limitations: 12 pairs','Limitations: 10–12 pairs':'Limitations: 12 pairs'}.items():s=s.replace(a,b)
s=s.replace('Thanks for specifying','Thanks, Niko, for specifying')
s=s.replace('Request means, clocks, temperatures, power, VRAM, throttling flags, PCIe widths/generations, RSS/RAM/swap and PSI are retained in raw telemetry and `requests.csv`.', 'Request means, clocks, temperatures, power, VRAM, PCIe widths/generations and RSS/RAM/swap are in `requests.csv`; full raw samples, event flags and PSI remain in telemetry.')
s=s.replace('Guest-visible negotiated PCIe and clocks are in inventory and per-phase telemetry.', 'Guest-visible PCIe is x8 on both GPUs: idle sysfs reports 2.5 GT/s, with maximum 16 GT/s x16 capability; measured decode samples report Gen4 x8. Complete topology, negotiation and clocks are retained in inventory and per-phase telemetry.')
s=s.replace('Built-in aggregate CPU completion timing includes useful computation and coordination and does not isolate wake-up cost.', 'The retained CPU_completion_ms_per_window field is the native CPU dispatch/completion section plus remote/peer finish paths, normalized by verify windows. Its source definitions are preserved in provenance/native-cpu-timing-definition.txt and provenance/native-decode-timing-definition.txt. It does not isolate wake-up cost; overlapping stage timers are not additive.')
s=s.replace("## Required interpretation','']", "## Figures','','[Paired throughput and CPU changes](figures/paired-results.png); [CPU demand relationship](figures/cpu-demand.png). Exportable SVG/PDF versions are in `figures/`.','','## Required interpretation','']")
idx=s.index(" out+=['','MTP/routing parity")
new=""" out+=['','| Cell | Native process CPU median A/B | Native CPU section ms/window A/B | Native host section ms/window A/B | Median paired CPU-section change |','|---|---:|---:|---:|---:|']
 for cell,v in s['cells'].items():
  rs=[r for r in rows if r['cell']==cell];ratios=[float(r['CPU_completion_ms_per_window_B'])/float(r['CPU_completion_ms_per_window_A']) for r in rs]
  process='/'.join(f\"{v['arm']['process_CPU'][a]['median']:.2f}%\" for a in ['A','B'])
  cpu='/'.join(f\"{v['routing']['CPU_completion_ms_per_window'][a]['median']:.3f}\" for a in ['A','B'])
  host='/'.join(f\"{v['routing']['pool_plus_plan_ms_per_window'][a]['median']:.3f}\" for a in ['A','B'])
  out.append(f\"| {cell} | {process} | {cpu} | {host} | {pct(statistics.median(ratios))} |\")
 out+=['','Native process CPU uses `/proc/PID/stat` user+system tick differences divided by observed decode wall time and 16 vCPUs. Guest active CPU uses aggregate `/proc/stat` busy/total tick differences, with steal separate. These are separate guest accounting estimates, not quantities to add. The native CPU section is generally longer with 100 µs while total TG improves; this identifies an aggregate coordination/execution tradeoff, without isolating its cause.']
"""
s=s[:idx]+new+s[idx:]
p.write_text(s)
