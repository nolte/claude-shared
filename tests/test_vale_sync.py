"""scripts/vale_sync.py serialises concurrent `vale sync` runs (#770)."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
WRAPPER = REPO / "scripts" / "vale_sync.py"

# A fake `vale` that records overlapping runs: each run first marks itself as
# running, holds for a moment, then counts the markers present; more than its own
# means another run was inside `vale sync` at the same time.
FAKE_VALE = """#!/bin/sh
touch "$VALE_FAKE_DIR/running.$$"
sleep 0.3
n=$(ls "$VALE_FAKE_DIR"/running.* | wc -l)
if [ "$n" -gt 1 ]; then echo overlap >> "$VALE_FAKE_DIR/overlaps"; fi
rm -f "$VALE_FAKE_DIR/running.$$"
echo "$1" >> "$VALE_FAKE_DIR/calls"
"""


def test_concurrent_syncs_never_overlap(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "vale"
    fake.write_text(FAKE_VALE)
    fake.chmod(0o755)
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", "VALE_FAKE_DIR": str(tmp_path)}
    procs = [subprocess.Popen([sys.executable, str(WRAPPER)], env=env) for _ in range(3)]
    assert [p.wait(timeout=30) for p in procs] == [0, 0, 0]
    assert (tmp_path / "calls").read_text().split() == ["sync", "sync", "sync"]
    assert not (tmp_path / "overlaps").exists()


def test_exit_status_of_vale_sync_is_passed_through(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "vale"
    fake.write_text("#!/bin/sh\nexit 3\n")
    fake.chmod(0o755)
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"}
    assert subprocess.run([sys.executable, str(WRAPPER)], env=env, check=False).returncode == 3
