#!/usr/bin/env python3
"""Run an upstream verify.py with one documented deviation: tolerate manifest keys whose files are absent (job 4).

usage: job4_launcher.py --tolerate .gitattributes <verify.py> <verifier args...>

The verifier's source is read unchanged from the pinned worktree. Exactly one statement is replaced in memory:

    assert actual==read(ROOT/'MANIFEST.json'),'Package manifest mismatch'

becomes a check that the package equals the manifest minus the tolerated keys, *and* that every tolerated key is
really absent from the package. Any other difference (a changed, extra or other missing file) still fails with the
verifier's own message. The verifier runs as __main__ with its own __file__ and sys.argv, so its ROOT, OUT and
subprocesses are as in a normal run. The worktree is not modified.
"""
import sys

NEEDLE = "assert actual==read(ROOT/'MANIFEST.json'),'Package manifest mismatch'"
PATCHED = "assert _job4_check(actual,read(ROOT/'MANIFEST.json')),'Package manifest mismatch'"


def make_check(tolerated):
    state = {'reported': False}

    def check(actual, manifest):
        absent = all(k in manifest and k not in actual for k in tolerated)
        rest = {k: v for k, v in manifest.items() if k not in tolerated}
        ok = absent and actual == rest
        if not state['reported']:
            state['reported'] = True
            print(f'# JOB4 DEVIATION tolerated={sorted(tolerated)} absent={absent} '
                  f'manifest_entries={len(manifest)} package_files={len(actual)} remaining_equal={actual == rest}',
                  flush=True)
        return ok
    return check


def main():
    args = sys.argv[1:]
    tolerated = set()
    while args and args[0] == '--tolerate':
        tolerated.add(args[1])
        args = args[2:]
    if not tolerated or not args:
        sys.exit(__doc__)
    path = args[0]
    with open(path, encoding='utf-8') as f:
        src = f.read()
    n = src.count(NEEDLE)
    if n != 1:
        sys.exit(f'job4_launcher: expected exactly one integrity assertion in {path}, found {n}')
    src = src.replace(NEEDLE, PATCHED)
    import os
    sys.argv = [path, *args[1:]]
    sys.path[0] = os.path.dirname(os.path.abspath(path))
    glb = {'__name__': '__main__', '__file__': path, '__builtins__': __builtins__,
           '_job4_check': make_check(tolerated)}
    exec(compile(src, path, 'exec'), glb)


if __name__ == '__main__':
    main()
