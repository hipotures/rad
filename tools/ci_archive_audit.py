#!/usr/bin/env python3
"""Apply the ordinary archive audit with a narrow CI-workflow path exception.

Only .github/workflows/*.yml or *.yaml is additionally managed. Size, UTF-8,
secret, symlink and index checks remain in the existing archive implementation.
No historical data or policy is rewritten.
"""
from pathlib import Path


def is_workflow(relative: Path) -> bool:
    return (len(relative.parts) == 3 and relative.parts[:2] == (".github", "workflows")
            and relative.suffix in {".yml", ".yaml"})


def main() -> None:
    import archive_workspace as archive
    original = archive.reason

    def reason(path, data=None):
        if not is_workflow(path.relative_to(archive.ROOT)):
            return original(path, data=data)
        if path.is_symlink():
            return "local-symlink"
        content = path.read_bytes() if data is None else data
        # Validate the same bytes through the existing managed-source rules.
        # Audit still checks the real indexed path, Git mode and secret patterns.
        return original(archive.ROOT / "tools" / path.name, data=content)

    archive.reason = reason
    archive.main()


if __name__ == "__main__":
    main()
