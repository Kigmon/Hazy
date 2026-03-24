from nemoclaw_control.orchestrator.actions import Actions
from nemoclaw_control.orchestrator.recovery import recommended_actions
from nemoclaw_control.state.models import HealthState, Status


def test_recovery_prefers_nemoclaw_onboard_when_gateway_broken_but_sandbox_exists():
    st = HealthState()
    st.docker.running = Status.RUNNING
    st.ollama.running = Status.RUNNING
    st.models_available = ["nemotron-3-nano:30b"]
    st.sandbox_exists = Status.CONFIGURED
    st.gateway_state = Status.BROKEN

    actions = recommended_actions(st)
    assert Actions.NEMOCLAW_ONBOARD.key in actions
    assert Actions.CONNECT_GOAT.key in actions


def test_recovery_model_pull_if_missing_default_model():
    st = HealthState()
    st.docker.running = Status.RUNNING
    st.ollama.running = Status.RUNNING
    st.models_available = ["mixtral:latest"]
    st.sandbox_exists = Status.CONFIGURED
    st.gateway_state = Status.REACHABLE

    actions = recommended_actions(st)
    assert Actions.PULL_DEFAULT_MODEL.key in actions
