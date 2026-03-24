from __future__ import annotations

from dataclasses import dataclass

from nemoclaw_control.orchestrator.runner import CmdResult, CommandRunner


@dataclass(frozen=True)
class Action:
    key: str
    label: str


class Actions:
    START_DOCKER = Action("start_docker", "Start Docker")
    RESTART_DOCKER = Action("restart_docker", "Restart Docker")
    START_OLLAMA = Action("start_ollama", "Start Ollama")
    RESTART_OLLAMA = Action("restart_ollama", "Restart Ollama")
    NEMOCLAW_ONBOARD = Action("nemoclaw_onboard", "Run NemoClaw Onboard")
    CONNECT_GOAT = Action("connect_goat", "Connect goat Sandbox")
    PULL_DEFAULT_MODEL = Action("pull_model", "Pull nemotron-3-nano:30b")


class ActionExecutor:
    def __init__(self, runner: CommandRunner):
        self.runner = runner

    def execute(self, action_key: str) -> CmdResult:
        mapping: dict[str, list[str]] = {
            Actions.START_DOCKER.key: ["pkexec", "systemctl", "start", "docker"],
            Actions.RESTART_DOCKER.key: ["pkexec", "systemctl", "restart", "docker"],
            Actions.START_OLLAMA.key: ["pkexec", "systemctl", "start", "ollama"],
            Actions.RESTART_OLLAMA.key: ["pkexec", "systemctl", "restart", "ollama"],
            Actions.NEMOCLAW_ONBOARD.key: ["nemoclaw", "onboard"],
            Actions.CONNECT_GOAT.key: ["nemoclaw", "goat", "connect"],
            Actions.PULL_DEFAULT_MODEL.key: ["ollama", "pull", "nemotron-3-nano:30b"],
        }
        cmd = mapping[action_key]
        timeout = 1800 if action_key == Actions.PULL_DEFAULT_MODEL.key else 300
        return self.runner.run(cmd, timeout=timeout)
