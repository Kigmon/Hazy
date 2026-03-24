from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass


@dataclass
class CmdResult:
    cmd: list[str]
    returncode: int
    stdout: str
    stderr: str


class CommandRunner:
    def __init__(self, extra_env: dict[str, str] | None = None):
        self.extra_env = extra_env or {}

    def run(self, cmd: list[str], timeout: int = 60) -> CmdResult:
        env = os.environ.copy()
        env.update(self.extra_env)
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return CmdResult(cmd=cmd, returncode=proc.returncode, stdout=proc.stdout.strip(), stderr=proc.stderr.strip())
