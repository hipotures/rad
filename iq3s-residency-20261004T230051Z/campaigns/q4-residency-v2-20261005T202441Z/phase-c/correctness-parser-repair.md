# Correctness parser repair

The initial analysis failed because it matched `non-finite` even in healthy prompt-state summaries reporting `0 non-finite`. The original frozen control was falsely rejected. All seven completed batches and failure logs remain unchanged. The corrected parser accepts only known prompt-end summaries with every observed non-finite count equal to zero; head/layer reports or unrecognized non-finite lines still fail. No request is repeated and no runtime/binary/config changes.
