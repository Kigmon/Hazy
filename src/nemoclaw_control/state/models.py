from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Status(str, Enum):
    INSTALLED = "installed"
    RUNNING = "running"
    HEALTHY = "healthy"
    REACHABLE = "reachable"
    CONFIGURED = "configured"
    PARTIAL = "partial"
    BROKEN = "broken"
    MISSING = "missing"
    UNKNOWN = "unknown"


@dataclass
class ServiceState:
    name: str
    installed: Status = Status.UNKNOWN
    running: Status = Status.UNKNOWN
    details: str = ""


@dataclass
class IntegrationState:
    configured: Status = Status.UNKNOWN
    tested: Status = Status.UNKNOWN
    details: str = ""


@dataclass
class HealthState:
    os_version: str = "unknown"
    gpu_present: bool = False
    docker: ServiceState = field(default_factory=lambda: ServiceState(name="docker"))
    ollama: ServiceState = field(default_factory=lambda: ServiceState(name="ollama"))
    openshell_path: str = ""
    openshell_version: str = ""
    nemoclaw_path: str = ""
    nemoclaw_version: str = ""
    ollama_bind_ok: Status = Status.UNKNOWN
    models_available: list[str] = field(default_factory=list)
    gateway_state: Status = Status.UNKNOWN
    sandbox_exists: Status = Status.UNKNOWN
    sandbox_health: Status = Status.UNKNOWN
    dashboard_reachable: Status = Status.UNKNOWN
    twitch: IntegrationState = field(default_factory=IntegrationState)
    telegram: IntegrationState = field(default_factory=IntegrationState)

    def overall(self) -> Status:
        critical = [
            self.docker.running,
            self.ollama.running,
            self.gateway_state,
            self.sandbox_health,
        ]
        if any(s in {Status.BROKEN, Status.MISSING} for s in critical):
            return Status.BROKEN
        if all(s in {Status.HEALTHY, Status.RUNNING, Status.REACHABLE, Status.CONFIGURED} for s in critical):
            return Status.HEALTHY
        if any(s == Status.UNKNOWN for s in critical):
            return Status.UNKNOWN
        return Status.PARTIAL
