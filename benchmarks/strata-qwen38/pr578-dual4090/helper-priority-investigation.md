# Helper ownership / primary PCIe planner

Original PR is still being benchmarked; proposed diff is saved only, not applied.

In expert_pool_dispatch_multi, distinct primary misses exclude PeerExperts ownership, but do not exclude RemoteExperts ownership. The planner assigns its --pcie-frac share before RemoteExperts::begin. begin ignores any row whose kind is not -1. Thus kind1 PCIe rows bypass a helper that already caches their expert.

With complementary caches, these experts cannot migrate into the primary cache. Repeated primary reads of their weights from host RAM over PCIe can persist, even with a resident helper copy. The old helper allowed primary adaptation to duplicate hot helper residents, avoiding many of these PCIe reads at the cost of cache overlap.

Steady original PR observed GPU0 RX ~7548MB/s and ~3PCIe expert groups per layer/window, vs layer split ~333MB/s and0.01PCIe groups. These are observations, not a hardware proof. No expert SSD read is implied: mapped host RAM traffic is distinct from SSD traffic.

Proposed minimal fix, optimized-mode only: exclude cached helper residents from the primary PCIe miss quota; leave their kind=-1 until the existing helper begin claims them. Neither helper reduction nor native kernels/weights change. Remaining CPU misses still use the existing PCIe quota. Original helper and layer split keep their ownership decisions.

After all original benchmark outputs/checkpoint are preserved, test this in a third checkout and separate local commit. Same initial numeric cache budgets; same build flags; existing tests and10prompt correctness before speed. Keep fixed variant results separate and never attribute its gains to the unmodified PR.
