# Existing pipeline timing evidence

Rounded runtime stage averages, excluding warmup. Overlap prevents summing stage costs into synthetic request latency. GPU-reach includes coordination; it is not a pure GPU kernel timer.

| Family |Profile|Policy|Stage|GPU-reach ms|Pool+plan ms|Host staging ms|
|---|---|---|---:|---:|---:|---:|
|code|32k|default|0|7.601|2.278|1.661|
|code|32k|default|1|6.837|0.536|0.000|
|code|32k|sleep100us|0|5.588|1.545|0.484|
|code|32k|sleep100us|1|5.156|0.846|0.000|
|code|128k|default|0|6.650|1.564|1.072|
|code|128k|default|1|6.073|0.387|0.000|
|code|128k|sleep100us|0|6.134|1.127|0.410|
|code|128k|sleep100us|1|5.679|0.567|0.000|
|math|32k|default|0|7.143|2.435|1.491|
|math|32k|default|1|6.351|0.904|0.000|
|math|32k|sleep100us|0|5.674|2.100|0.359|
|math|32k|sleep100us|1|5.200|1.573|0.000|
|math|128k|default|0|6.746|1.390|0.651|
|math|128k|default|1|6.163|0.658|0.000|
|math|128k|sleep100us|0|6.178|2.112|0.304|
|math|128k|sleep100us|1|5.679|1.554|0.000|
|prose|32k|default|0|8.829|1.982|1.224|
|prose|32k|default|1|7.803|0.645|0.000|
|prose|32k|sleep100us|0|5.645|1.547|0.392|
|prose|32k|sleep100us|1|5.197|0.923|0.000|
|prose|128k|default|0|6.614|1.252|0.763|
|prose|128k|default|1|6.048|0.472|0.000|
|prose|128k|sleep100us|0|6.217|0.985|0.282|
|prose|128k|sleep100us|1|5.740|0.608|0.000|
