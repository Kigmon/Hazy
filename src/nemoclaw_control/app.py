from __future__ import annotations

import sys
import traceback

from PySide6.QtWidgets import QApplication, QLabel, QMessageBox, QSplashScreen

from nemoclaw_control.integrations.credentials import CredentialStore
from nemoclaw_control.integrations.twitch import TwitchIntegration
from nemoclaw_control.logging.setup import configure_logging
from nemoclaw_control.orchestrator.actions import ActionExecutor
from nemoclaw_control.orchestrator.detector import Detector
from nemoclaw_control.orchestrator.runner import CommandRunner
from nemoclaw_control.ui.main_window import MainWindow


def main() -> int:
    logger = configure_logging()
    app = QApplication(sys.argv)

    splash = QSplashScreen()
    splash.showMessage("Launching NemoClaw Control…", alignment=0x84)
    splash.show()
    app.processEvents()

    try:
        runner = CommandRunner()
        detector = Detector(runner)
        action_executor = ActionExecutor(runner)
        twitch = TwitchIntegration(CredentialStore())

        window = MainWindow(detector, action_executor, twitch, logger)
        window.show()
        splash.finish(window)
        return app.exec()
    except Exception as exc:
        logger.exception("Fatal startup error")
        QMessageBox.critical(
            None,
            "Startup Failure",
            f"NemoClaw Control failed to launch:\n{exc}\n\n{traceback.format_exc()}",
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
