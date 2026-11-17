#!/usr/bin/env python3
"""Run `vale sync` under an exclusive lock.

`task check` runs `lint` (whose pre-commit prose hook calls `task lint:prose`) and
`test` in parallel, and both sync the Vale style packages into the same
`.github/styles/` tree. Two concurrent syncs can collide while one deletes a
package directory the other is filling (`unlinkat … directory not empty`, #770).
This wrapper serialises them across processes with an advisory file lock, so the
second sync waits and then finds the styles current.

The lock file lives in the system temp directory, keyed by this checkout's path,
so separate worktrees don't block each other. Exits with `vale sync`'s status, or
127 with a one-line message when Vale isn't installed.
"""
from __future__ import annotations

import fcntl
import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def lock_path(repo: Path = REPO) -> Path:
    key = hashlib.sha256(str(repo).encode()).hexdigest()[:16]
    return Path(tempfile.gettempdir()) / f"vale-sync-{key}.lock"


def main() -> int:
    if shutil.which("vale") is None:
        print("vale is not on PATH; install the version pinned in .github/workflows/ci.yml "
              "(VALE_VERSION)", file=sys.stderr)
        return 127
    with open(lock_path(), "w") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)  # released when the file closes
        return subprocess.run(["vale", "sync"], cwd=REPO, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
