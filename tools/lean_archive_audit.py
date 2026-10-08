#!/usr/bin/env python3
"""Narrow publication-policy extension for the formal proof package and CI."""
from pathlib import Path

PREFIX = ("research", "integer-mult-breakthrough", "formal")


def main() -> None:
    import archive_workspace as archive
    original = archive.reason

    def reason(path, data=None):
        relative = path.relative_to(archive.ROOT)
        workflow = (len(relative.parts) == 3 and relative.parts[:2] == (".github", "workflows")
                    and relative.suffix in {".yml", ".yaml"})
        formal = (relative.parts[:3] == PREFIX and
                  (relative.suffix == ".lean" or relative.parts == PREFIX + ("lean-toolchain",)))
        if not workflow and not formal:
            return original(path, data=data)
        if path.is_symlink():
            return "local-symlink"
        if ".lake" in relative.parts or "lake-packages" in relative.parts:
            return "local-directory:lean-build"
        content = path.read_bytes() if data is None else data
        surrogate = (archive.ROOT / "tools" / path.name if workflow
                     else path.with_suffix(".txt"))
        return original(surrogate, data=content)

    archive.reason = reason
    archive.main()


if __name__ == "__main__":
    main()
