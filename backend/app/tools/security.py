import os
from pathlib import Path


class UnsafePath(ValueError):
    pass


def safe_workspace_path(workspace: str | Path, requested: str) -> Path:
    root = Path(workspace).resolve()
    candidate = (root / requested).resolve()
    if candidate != root and root not in candidate.parents:
        raise UnsafePath("path escapes workspace")
    if os.path.isabs(requested):
        raise UnsafePath("absolute path is not allowed")
    return candidate


def command_allowed(command: str, allowlist: set[str], denylist: set[str]) -> bool:
    first = command.strip().split(maxsplit=1)[0] if command.strip() else ""
    return first in allowlist and not any(token in command for token in denylist)
