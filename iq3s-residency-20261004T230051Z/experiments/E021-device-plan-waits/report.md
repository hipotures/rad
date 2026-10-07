# E021: same-binary scoped coordination waits

All recorded outputs, router decisions, MTP, paths, resident sets, heat and first-head bits match. This is diagnostic timing only.

| Profile | Layer | Phase | Category | N | OFF median us | ON median us | Paired delta us |
|---|---:|---:|---|---:|---:|---:|---:|
| 32k | 2 | 0 | all-local | 827 | 8.192 | 4.096 | -4.096 |
| 32k | 2 | 0 | CPU | 414 | 8.192 | 8.192 | 0.000 |
| 32k | 2 | 0 | mapped | 33 | 8.192 | 8.192 | 0.000 |
| 32k | 2 | 1 | all-local | 827 | 77.824 | 78.848 | 0.000 |
| 32k | 2 | 1 | CPU | 414 | 79.872 | 79.872 | 0.000 |
| 32k | 2 | 1 | mapped | 33 | 72.704 | 73.728 | 0.000 |
| 32k | 2 | 2 | all-local | 827 | 9.216 | 7.168 | -1.024 |
| 32k | 2 | 2 | CPU | 414 | 9.216 | 9.216 | 0.000 |
| 32k | 2 | 2 | mapped | 33 | 168.960 | 168.960 | 0.000 |
| 32k | 2 | 3 | all-local | 827 | 5.120 | 5.120 | 0.000 |
| 32k | 2 | 3 | CPU | 414 | 6.144 | 6.144 | 0.000 |
| 32k | 2 | 3 | mapped | 33 | 5.120 | 6.144 | 1.024 |
| 32k | 2 | 4 | all-local | 827 | 9.216 | 10.240 | 1.024 |
| 32k | 2 | 4 | CPU | 414 | 12.288 | 12.288 | 0.000 |
| 32k | 2 | 4 | mapped | 33 | 12.288 | 12.288 | 0.000 |
| 32k | 24 | 0 | all-local | 809 | 8.192 | 4.096 | -4.096 |
| 32k | 24 | 0 | CPU | 432 | 8.192 | 8.192 | 0.000 |
| 32k | 24 | 0 | mapped | 25 | 8.192 | 8.192 | 0.000 |
| 32k | 24 | 1 | all-local | 809 | 69.632 | 69.632 | 0.000 |
| 32k | 24 | 1 | CPU | 432 | 75.776 | 75.776 | 0.000 |
| 32k | 24 | 1 | mapped | 25 | 73.728 | 73.728 | 0.000 |
| 32k | 24 | 2 | all-local | 809 | 9.216 | 7.168 | -1.024 |
| 32k | 24 | 2 | CPU | 432 | 9.216 | 9.216 | 0.000 |
| 32k | 24 | 2 | mapped | 25 | 165.888 | 167.936 | 1.024 |
| 32k | 24 | 3 | all-local | 809 | 4.096 | 3.072 | -1.024 |
| 32k | 24 | 3 | CPU | 432 | 4.096 | 5.120 | 0.000 |
| 32k | 24 | 3 | mapped | 25 | 5.120 | 5.120 | 0.000 |
| 32k | 24 | 4 | all-local | 809 | 7.168 | 10.240 | 2.048 |
| 32k | 24 | 4 | CPU | 432 | 11.264 | 12.288 | 2.048 |
| 32k | 24 | 4 | mapped | 25 | 11.264 | 15.360 | 4.096 |
| 32k | 40 | 0 | all-local | 837 | 8.192 | 4.096 | -4.096 |
| 32k | 40 | 0 | CPU | 404 | 8.192 | 9.216 | 1.024 |
| 32k | 40 | 0 | mapped | 6 | 7.168 | 8.192 | 1.024 |
| 32k | 40 | 1 | all-local | 837 | 69.632 | 69.632 | 0.000 |
| 32k | 40 | 1 | CPU | 404 | 79.872 | 78.848 | 0.000 |
| 32k | 40 | 1 | mapped | 6 | 87.552 | 87.040 | 0.000 |
| 32k | 40 | 2 | all-local | 837 | 9.216 | 7.168 | -1.024 |
| 32k | 40 | 2 | CPU | 404 | 9.216 | 9.216 | 0.000 |
| 32k | 40 | 2 | mapped | 6 | 193.536 | 195.584 | 1.536 |
| 32k | 40 | 3 | all-local | 837 | 4.096 | 3.072 | -1.024 |
| 32k | 40 | 3 | CPU | 404 | 4.096 | 5.120 | 0.000 |
| 32k | 40 | 3 | mapped | 6 | 5.120 | 5.120 | 0.512 |
| 32k | 40 | 4 | all-local | 837 | 9.216 | 10.240 | 1.024 |
| 32k | 40 | 4 | CPU | 404 | 12.288 | 12.288 | 0.000 |
| 32k | 40 | 4 | mapped | 6 | 12.800 | 12.288 | -0.512 |
| 128k | 2 | 0 | all-local | 833 | 8.192 | 4.096 | -4.096 |
| 128k | 2 | 0 | CPU | 616 | 8.192 | 8.192 | 0.000 |
| 128k | 2 | 0 | mapped | 40 | 8.192 | 8.192 | 0.000 |
| 128k | 2 | 1 | all-local | 833 | 70.656 | 70.656 | 0.000 |
| 128k | 2 | 1 | CPU | 616 | 74.752 | 74.752 | 0.000 |
| 128k | 2 | 1 | mapped | 40 | 73.216 | 73.728 | 0.000 |
| 128k | 2 | 2 | all-local | 833 | 9.216 | 7.168 | -1.024 |
| 128k | 2 | 2 | CPU | 616 | 9.216 | 9.216 | 0.000 |
| 128k | 2 | 2 | mapped | 40 | 167.936 | 168.960 | 0.512 |
| 128k | 2 | 3 | all-local | 833 | 5.120 | 5.120 | -1.024 |
| 128k | 2 | 3 | CPU | 616 | 6.144 | 6.144 | 0.000 |
| 128k | 2 | 3 | mapped | 40 | 6.144 | 6.144 | 0.000 |
| 128k | 2 | 4 | all-local | 833 | 8.192 | 10.240 | 2.048 |
| 128k | 2 | 4 | CPU | 616 | 11.264 | 13.312 | 2.048 |
| 128k | 2 | 4 | mapped | 40 | 11.264 | 13.312 | 1.536 |
| 128k | 24 | 0 | all-local | 960 | 8.192 | 4.096 | -4.096 |
| 128k | 24 | 0 | CPU | 489 | 8.192 | 8.192 | 1.024 |
| 128k | 24 | 0 | mapped | 35 | 8.192 | 8.192 | 1.024 |
| 128k | 24 | 1 | all-local | 960 | 63.488 | 63.488 | 0.000 |
| 128k | 24 | 1 | CPU | 489 | 68.608 | 69.632 | 0.000 |
| 128k | 24 | 1 | mapped | 35 | 73.728 | 73.728 | 0.000 |
| 128k | 24 | 2 | all-local | 960 | 9.216 | 7.168 | -1.024 |
| 128k | 24 | 2 | CPU | 489 | 9.216 | 9.216 | 1.024 |
| 128k | 24 | 2 | mapped | 35 | 167.936 | 168.960 | 1.024 |
| 128k | 24 | 3 | all-local | 960 | 4.096 | 3.072 | -1.024 |
| 128k | 24 | 3 | CPU | 489 | 4.096 | 4.096 | 0.000 |
| 128k | 24 | 3 | mapped | 35 | 5.120 | 5.120 | 0.000 |
| 128k | 24 | 4 | all-local | 960 | 10.240 | 10.240 | 1.024 |
| 128k | 24 | 4 | CPU | 489 | 13.312 | 16.384 | 3.072 |
| 128k | 24 | 4 | mapped | 35 | 13.312 | 16.384 | 3.072 |
| 128k | 40 | 0 | all-local | 963 | 8.192 | 4.096 | -4.096 |
| 128k | 40 | 0 | CPU | 486 | 8.192 | 8.192 | 0.000 |
| 128k | 40 | 0 | mapped | 16 | 8.192 | 8.192 | 0.000 |
| 128k | 40 | 1 | all-local | 963 | 61.440 | 61.440 | 0.000 |
| 128k | 40 | 1 | CPU | 486 | 74.752 | 75.776 | 0.000 |
| 128k | 40 | 1 | mapped | 16 | 75.776 | 76.800 | 1.024 |
| 128k | 40 | 2 | all-local | 963 | 9.216 | 8.192 | -1.024 |
| 128k | 40 | 2 | CPU | 486 | 9.216 | 10.240 | 1.024 |
| 128k | 40 | 2 | mapped | 16 | 195.584 | 195.584 | 0.512 |
| 128k | 40 | 3 | all-local | 963 | 4.096 | 3.072 | -1.024 |
| 128k | 40 | 3 | CPU | 486 | 4.096 | 5.120 | 0.000 |
| 128k | 40 | 3 | mapped | 16 | 4.096 | 5.120 | 1.024 |
| 128k | 40 | 4 | all-local | 963 | 10.240 | 11.264 | 1.024 |
| 128k | 40 | 4 | CPU | 486 | 13.312 | 14.336 | 2.048 |
| 128k | 40 | 4 | mapped | 16 | 13.312 | 13.312 | 0.000 |

Phase0: plan wait and copy;1: resident expert compute;2: mapped wait/compute;3: CPU completion wait;4: device planning and demand doorbell. Host dispatch distributions are preserved separately in summary.json. CPU-zero is not always all-local; mapped work is explicitly separate.

These selected-layer phases do not establish total exposed request cost. Kernel/event floors, cross-stream overlap and VM variation remain. No multiplication by48 or sum of medians is a measured speedup. The next source-supported experiment removes the final redundant GPU row-zero/copy/add operations with exact CPU/GPU row ownership; those operations were not included in these five phases.
