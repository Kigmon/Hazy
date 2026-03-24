import os

from nemoclaw_control.orchestrator.runner import CommandRunner


def test_runner_preserves_environment():
    os.environ["NEMOCLAW_TEST_ENV"] = "kept"
    runner = CommandRunner(extra_env={"NEMOCLAW_EXTRA_ENV": "added"})
    result = runner.run(["python3", "-c", "import os; print(os.getenv('NEMOCLAW_TEST_ENV'), os.getenv('NEMOCLAW_EXTRA_ENV'))"])
    assert result.returncode == 0
    assert "kept added" in result.stdout
