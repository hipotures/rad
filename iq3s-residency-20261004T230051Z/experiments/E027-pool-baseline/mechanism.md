# Existing pipeline timing evidence

Rounded runtime stage averages, excluding warmup. Overlap prevents summing stage costs into synthetic request latency. GPU-reach includes coordination; it is not a pure GPU kernel timer.

| Family |Profile|Policy|Stage|GPU-reach ms|Pool+plan ms|Host staging ms|
|---|---|---|---:|---:|---:|---:|
|standard|32k|default|0|6.896|1.810|0.765|
|standard|32k|default|1|6.175|1.039|0.000|
|standard|32k|sleep100us|0|5.675|1.983|0.323|
|standard|32k|sleep100us|1|5.134|1.517|0.000|
|standard|128k|default|0|8.042|2.277|1.028|
|standard|128k|default|1|7.239|1.186|0.000|
|standard|128k|sleep100us|0|6.154|2.390|0.367|
|standard|128k|sleep100us|1|5.614|1.838|0.001|
