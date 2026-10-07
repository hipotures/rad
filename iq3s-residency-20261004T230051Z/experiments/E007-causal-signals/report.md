# Causal Markov and token-history signals

Bounded causal policies at the frozen capacities; not a universal rejection of prediction.

Status: COMPLETE_NEGATIVE for the declared finite candidates; this does not exhaust the family.

| Profile | Policy | Nonlocal entries | Promotion GB | Modeled pending wait s | Python selector s |
|---|---|---:|---:|---:|---:|
| 32k | markov-scaled | 52624 | 5.655 | 0.0879 | 0.843 |
| 32k | token-bigram-hybrid | 35703 | 11.886 | 0.2724 | 0.278 |

32k: dictionary conditional top10 precision 45.27%, unconditional next-row recall 20.77%, nonlocal-row recall 6.11%. Dictionary hits 569/1240.
| 128k | markov-scaled | 60116 | 6.828 | 0.1175 | 0.993 |
| 128k | token-bigram-hybrid | 44699 | 15.512 | 0.4159 | 0.327 |

128k: dictionary conditional top10 precision 44.31%, unconditional next-row recall 10.34%, nonlocal-row recall 3.70%. Dictionary hits 338/1448.

Neither candidate is promoted to live execution: normalized Markov increases nonlocals; bigram improvement is small, has more transfer bytes and Python state/update costs. E008 separately measures legitimate router availability.

These are fixed-trace simulations. More/less nonlocal work is not converted into TG. Transfer waits use a 12.6 GB/s aggregate optimistic measured-range reference, with the physical per-GPU slot classes and safe completion publication. Python dictionary payload bytes omit container overhead; deployment feature/selector contention is not measured. All rejected draft rows remain in execution demand, but only committed rows teach the dictionary.

v1 sensitivity driver stopped on floating cancellation in pending publication; v2 uses exact completion endpoint and has a regression test. Failed and partial v1 records retained.
