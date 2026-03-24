from __future__ import annotations

import shutil
import socket
from pathlib import Path

from nemoclaw_control.orchestrator.parsers import parse_ollama_models
from nemoclaw_control.orchestrator.runner import CommandRunner
from nemoclaw_control.state.models import HealthState, Status


class Detector:
    def __init__(self, runner: CommandRunner, sandbox_name: str = "goat", gateway_name: str = "nemoclaw"):
        self.runner = runner
        self.sandbox_name = sandbox_name
        self.gateway_name = gateway_name

    def detect(self) -> HealthState:
        st = HealthState()
        st.os_version = self._os_version()
        st.gpu_present = self._gpu_present()
        self._docker(st)
        self._ollama(st)
        self._openshell(st)
        self._nemoclaw(st)
        self._sandbox(st)
        self._gateway(st)
        self._dashboard(st)
        return st

    def _os_version(self) -> str:
        p = Path("/etc/os-release")
        if not p.exists():
            return "unknown"
        data = p.read_text(encoding="utf-8", errors="ignore")
        for line in data.splitlines():
            if line.startswith("PRETTY_NAME="):
                return line.split("=", 1)[1].strip().strip('"')
        return "unknown"

    def _gpu_present(self) -> bool:
        return shutil.which("nvidia-smi") is not None

    def _docker(self, st: HealthState) -> None:
        st.docker.installed = Status.INSTALLED if shutil.which("docker") else Status.MISSING
        if st.docker.installed == Status.MISSING:
            st.docker.running = Status.MISSING
            return
        res = self.runner.run(["systemctl", "is-active", "docker"], timeout=15)
        st.docker.running = Status.RUNNING if res.returncode == 0 and "active" in res.stdout else Status.BROKEN

    def _ollama(self, st: HealthState) -> None:
        st.ollama.installed = Status.INSTALLED if shutil.which("ollama") else Status.MISSING
        if st.ollama.installed == Status.MISSING:
            st.ollama.running = Status.MISSING
            st.ollama_bind_ok = Status.MISSING
            return

        service = self.runner.run(["systemctl", "is-active", "ollama"], timeout=15)
        st.ollama.running = Status.RUNNING if service.returncode == 0 and "active" in service.stdout else Status.BROKEN

        st.ollama_bind_ok = Status.HEALTHY if self._can_connect("127.0.0.1", 11434) else Status.BROKEN
        models = self.runner.run(["ollama", "list"], timeout=30)
        if models.returncode == 0:
            st.models_available = parse_ollama_models(models.stdout)

    def _openshell(self, st: HealthState) -> None:
        path = shutil.which("openshell")
        st.openshell_path = path or ""
        if not path:
            return
        res = self.runner.run(["openshell", "--version"], timeout=10)
        if res.returncode == 0:
            st.openshell_version = res.stdout.splitlines()[0] if res.stdout else "unknown"

    def _nemoclaw(self, st: HealthState) -> None:
        path = shutil.which("nemoclaw")
        st.nemoclaw_path = path or ""
        if not path:
            return
        res = self.runner.run(["nemoclaw", "--version"], timeout=10)
        if res.returncode == 0:
            st.nemoclaw_version = res.stdout.splitlines()[0] if res.stdout else "unknown"

    def _sandbox(self, st: HealthState) -> None:
        creds = Path.home() / ".nemoclaw" / "credentials.json"
        res = self.runner.run(["nemoclaw", "status"], timeout=25) if st.nemoclaw_path else None
        signals = [
            creds.exists(),
            bool(res and self.sandbox_name in (res.stdout + res.stderr)),
            bool(res and res.returncode == 0),
        ]
        st.sandbox_exists = Status.CONFIGURED if any(signals) else Status.MISSING
        st.sandbox_health = Status.HEALTHY if signals[1] and signals[2] else Status.PARTIAL if any(signals) else Status.BROKEN

    def _gateway(self, st: HealthState) -> None:
        if self._can_connect("127.0.0.1", 8080):
            st.gateway_state = Status.REACHABLE
            return
        if st.nemoclaw_path:
            probe = self.runner.run(["nemoclaw", "status"], timeout=20)
            st.gateway_state = Status.PARTIAL if self.gateway_name in (probe.stdout + probe.stderr) else Status.BROKEN
        else:
            st.gateway_state = Status.MISSING

    def _dashboard(self, st: HealthState) -> None:
        st.dashboard_reachable = Status.REACHABLE if self._can_connect("127.0.0.1", 18789) else Status.BROKEN

    @staticmethod
    def _can_connect(host: str, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1.5)
            return sock.connect_ex((host, port)) == 0
