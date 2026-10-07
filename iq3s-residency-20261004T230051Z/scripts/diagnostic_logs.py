"""Parse actual numerical failure counts from upstream NaN diagnostic logs."""
import re
def has_nonfinite_failure(log):
    counts=[int(v) for v in re.findall(r'(\d+)\s+non-finite',log)]
    counts += [int(v) for v in re.findall(r': (\d+) of \d+ logits non-finite',log)]
    for values in re.findall(r'non-finite GU (\d+) H (-?\d+) Dm (\d+) bo (\d+)',log):counts.extend(map(int,values))
    return any(v>0 for v in counts) or bool(re.search(r'max \|x\| (?:nan|inf)\b',log,re.I))
