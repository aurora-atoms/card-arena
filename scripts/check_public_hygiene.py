#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)(api_key|secret|token|password)\s*=\s*['\"][^'\"]+['\"]"),
]

SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache"}


def iter_files(root: Path):
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.stat().st_size < 1_000_000:
            yield path


def main() -> int:
    root = Path.cwd()
    failures: list[str] = []
    for path in iter_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                failures.append(str(path))
                break
    if failures:
        print("potential public hygiene issues:")
        for item in failures:
            print(f"- {item}")
        return 1
    print("public hygiene check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
