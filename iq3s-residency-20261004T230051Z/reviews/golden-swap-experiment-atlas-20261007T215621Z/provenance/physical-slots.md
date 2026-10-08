# Physical slot semantics

The chart consumes the already normalized `slot` field, keyed by `(device, slot)`. It is the device-local cache destination used by execution, not a proposed victim's logical identity. No physical address or VRAM allocation change is inferred.

The verified Phase 4 derivative (`95fba2541a57fe6be8290faa639f493c7b8e895f`) retains the Phase 2 safe copier. In `include/strata/research/q4_oracle.hpp`, `OracleEvent` defines distinct `slot` and `oldslot` fields (line 17). The issue branch takes `spare[device][class]`, records it in `e.slot`, and assigns it to `w.destination` (line 111). The publication branch reads the victim's current resident slot into `old`, sets the victim resident entry to -1, assigns incoming residency to `w.destination`, and makes `old` the next spare (line 110). `e.oldslot` records the withdrawn victim slot. The source recovery patches and base identity remain in the Phase 4 campaign; the live source was inspected directly during this review.

Consequently the incoming and victim can occupy different physical slot IDs. A compatible spare can move across layers on the same device, so this view joins all matching device/class layer chunks before grouping intervals. It never joins slot IDs across devices.

Native journals withdraw the victim when native copy is issued; the incoming interval begins at publication. Oracle spare transactions withdraw the victim at valid publication. Blank intervals show absence from the retained resident map, including copy staging; a completed unpublished copy is not occupancy. Startup generation 0 is the attested decode boundary after saved warmup/prefill, not process launch.

Colors identify incoming `(layer, expert)` deterministically. Sorting selects slots with most observed admissions in the requested range; the chart states selected and total slot counts. Exact intervals remain in the layer assets. Missing slots, timestamps or publication events remain unknown; no inferred physical address is added.
