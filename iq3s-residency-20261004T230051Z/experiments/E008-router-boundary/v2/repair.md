# Captured-event observability repair

The v1 diagnostic server loaded and reached READY, but its fixed64-output warmup failed in `Signals::completed`: elapsed-time observation was unavailable for default-captured event records. The engine exception and invalid raw request remain under v1/32k. No headline binary was involved.

Local CUDA13.4 headers and the [official CUDA Event Management documentation](https://docs.nvidia.com/cuda/cuda-runtime-api/cuda_runtime_api/group__CUDART__EVENT.html) identify `cudaEventRecordExternal` as an external event node during graph capture. A bounded two-device graph reproducer compares default and external records, then the new diagnostic variant uses `cudaEventRecordWithFlags(...,cudaEventRecordExternal)`.

The new variant is isolated; source/binary/build/protocol are preserved separately. External event nodes can add graph overhead, so the variant remains diagnostic-only. Timing observations cannot be used as clean throughput gains. No model/routing/cache behavior changes.
