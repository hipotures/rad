# Numeric trace schema v1

Little-endian x86 records; sizes asserted in C++ and NumPy. Timestamps are CPU `steady_clock` nanoseconds. Clock domains are not mixed with GPU events. Files per request are prefixed`runtime-requestN`:

- entries:8bytes `(expert:i16, global_verify_branch:i8, path:i8, slot:i32)`. Path0localVRAM,1mapped/stagedPCIe,2remote/peer,minus1CPU. The branch ordinal includes the second verify group offset.
- layers:64bytes `(window,t0,t1,t2,t3,t4,entry_offset:u64; layer:u32; token_count,k:u16)`. Time sections match existing begin/plan/actq/jobs/run brackets; t3–t4 includes existing CPU jobs and remote wait where present, not an additive latency saving.
- windows:104bytes: window,position,begin,verify_end,end,pending_begin,pending_end:u64;T,accepted,cumulative_emitted,reserved:u32;input_token_ids[8]:i32. Accepted counts include committed drafts; requested output truncation may cap emitted count in the final window. All computed rejected branches remain in demand.
- promotions:48bytes:window,issue,observed_ready,bytes:u64;layer,incoming,outgoing,slot:i32. Issue is observed just after the existing async copy call;ready is observed after the existing event wait/query and before publication. This is a completion observation bracket, not actual GPU copy duration. Unpublished end-of-request copies remain marked with ready0.
- reach:40bytes:window,begin,reached,released:u64;layer,reserved:i32. Existing host wait for the GPU doorbell, followed by pool/plan/PLE/release. Same-layer wait generally precedes that layer's expert work; lagged association is required when studying mapped-expert delays.
- initial/final residency:i32[layer,expert], initial/final usage:f32[layer,expert], expert blob sizes:u64[layer], physical slot-byte classes:u64[slot] perGPU, emitted output IDs:i32[output].

No token identities, cache access, promotions or absent counters are manufactured. `trace_reader.py` validates totals, grouped branch indices, physical slot capacity and replay of actual issue/publication events before speculative policy projections. Buffered record flushing happens after engine decode timing; client wall time includes that diagnostic overhead. Diagnostic timing does not become a headline speed result.
