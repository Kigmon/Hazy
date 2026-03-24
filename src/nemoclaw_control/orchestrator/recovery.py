from __future__ import annotations

from nemoclaw_control.orchestrator.actions import Actions
from nemoclaw_control.state.models import HealthState, Status


def recommended_actions(state: HealthState) -> list[str]:
    actions: list[str] = []
    if state.docker.running != Status.RUNNING:
        actions.append(Actions.START_DOCKER.key)
    if state.ollama.running != Status.RUNNING:
        actions.append(Actions.START_OLLAMA.key)
    if "nemotron-3-nano:30b" not in state.models_available:
        actions.append(Actions.PULL_DEFAULT_MODEL.key)

    # NemoClaw-first recovery if sandbox exists but gateway unhealthy.
    if state.sandbox_exists in {Status.CONFIGURED, Status.PARTIAL, Status.HEALTHY} and state.gateway_state in {Status.BROKEN, Status.MISSING, Status.PARTIAL}:
        actions.append(Actions.NEMOCLAW_ONBOARD.key)
        actions.append(Actions.CONNECT_GOAT.key)

    return actions
