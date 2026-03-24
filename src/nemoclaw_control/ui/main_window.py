from __future__ import annotations

import webbrowser

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from nemoclaw_control.integrations.twitch import TwitchConfig
from nemoclaw_control.orchestrator.actions import Actions
from nemoclaw_control.orchestrator.recovery import recommended_actions


class WorkerSignals(QObject):
    finished = Signal(object)
    failed = Signal(str)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception as exc:  # visible UI failure instead of silent crash
            self.signals.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self, detector, action_executor, twitch_integration, logger):
        super().__init__()
        self.detector = detector
        self.action_executor = action_executor
        self.twitch_integration = twitch_integration
        self.logger = logger
        self.thread_pool = QThreadPool.globalInstance()

        self.setWindowTitle("NemoClaw Control")
        self.resize(980, 680)

        root = QWidget(self)
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        self.status_label = QLabel("Starting detection…")
        layout.addWidget(self.status_label)

        top_buttons = QHBoxLayout()
        refresh_btn = QPushButton("Refresh Health")
        refresh_btn.clicked.connect(self.refresh_health)
        top_buttons.addWidget(refresh_btn)

        dashboard_btn = QPushButton("Open Dashboard")
        dashboard_btn.clicked.connect(lambda: webbrowser.open("http://127.0.0.1:18789/"))
        top_buttons.addWidget(dashboard_btn)
        top_buttons.addStretch()
        layout.addLayout(top_buttons)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.overview = QPlainTextEdit()
        self.overview.setReadOnly(True)
        self.tabs.addTab(self.overview, "Overview")

        self.actions_panel = QWidget()
        self.tabs.addTab(self.actions_panel, "Recovery")
        self._build_actions_panel()

        self.integrations_panel = QWidget()
        self.tabs.addTab(self.integrations_panel, "Integrations")
        self._build_integrations_panel()

        self.logs = QPlainTextEdit()
        self.logs.setReadOnly(True)
        self.tabs.addTab(self.logs, "Logs")

        self.refresh_health()

    def _build_actions_panel(self):
        layout = QVBoxLayout(self.actions_panel)
        actions = [
            Actions.START_DOCKER,
            Actions.RESTART_DOCKER,
            Actions.START_OLLAMA,
            Actions.RESTART_OLLAMA,
            Actions.NEMOCLAW_ONBOARD,
            Actions.CONNECT_GOAT,
            Actions.PULL_DEFAULT_MODEL,
        ]
        for action in actions:
            btn = QPushButton(action.label)
            btn.clicked.connect(lambda _=False, key=action.key: self.run_action(key))
            layout.addWidget(btn)
        layout.addStretch()

    def _build_integrations_panel(self):
        layout = QVBoxLayout(self.integrations_panel)

        twitch_box = QGroupBox("Twitch")
        form = QFormLayout(twitch_box)
        self.twitch_client_id = QLineEdit()
        self.twitch_access_token = QLineEdit()
        self.twitch_access_token.setEchoMode(QLineEdit.Password)
        self.twitch_channel = QLineEdit()

        form.addRow("Client ID", self.twitch_client_id)
        form.addRow("Access Token", self.twitch_access_token)
        form.addRow("Channel", self.twitch_channel)

        save_btn = QPushButton("Save Twitch Credentials")
        save_btn.clicked.connect(self.save_twitch)
        test_btn = QPushButton("Validate Twitch")
        test_btn.clicked.connect(self.validate_twitch)
        form.addRow(save_btn, test_btn)

        self.twitch_status = QLabel("Unknown")
        form.addRow("Status", self.twitch_status)

        layout.addWidget(twitch_box)
        layout.addStretch()
        self.load_twitch_state()

    def log(self, message: str) -> None:
        self.logger.info(message)
        self.logs.appendPlainText(message)

    def _run_in_thread(self, fn, on_done):
        worker = Worker(fn)
        worker.signals.finished.connect(on_done)
        worker.signals.failed.connect(self.on_error)
        self.thread_pool.start(worker)

    def refresh_health(self):
        self.status_label.setText("Checking system health…")
        self._run_in_thread(self.detector.detect, self.on_health_ready)

    def on_health_ready(self, state):
        self.status_label.setText(f"Overall health: {state.overall().value}")
        lines = [
            f"OS: {state.os_version}",
            f"GPU detected: {state.gpu_present}",
            f"Docker: installed={state.docker.installed.value}, running={state.docker.running.value}",
            f"Ollama: installed={state.ollama.installed.value}, running={state.ollama.running.value}",
            f"Ollama bind(11434): {state.ollama_bind_ok.value}",
            f"Models: {', '.join(state.models_available) if state.models_available else 'none'}",
            f"OpenShell: {state.openshell_path or 'missing'} {state.openshell_version}",
            f"NemoClaw: {state.nemoclaw_path or 'missing'} {state.nemoclaw_version}",
            f"Sandbox goat: exists={state.sandbox_exists.value}, health={state.sandbox_health.value}",
            f"Gateway nemoclaw: {state.gateway_state.value}",
            f"Dashboard: {state.dashboard_reachable.value}",
            "",
            "Recommended actions:",
        ]
        for action_key in recommended_actions(state):
            lines.append(f"- {action_key}")
        self.overview.setPlainText("\n".join(lines))
        self.log("Health refresh complete")

    def run_action(self, action_key: str):
        self.log(f"Running action: {action_key}")
        self._run_in_thread(lambda: self.action_executor.execute(action_key), self.on_action_done)

    def on_action_done(self, result):
        self.log(f"Action finished rc={result.returncode}: {' '.join(result.cmd)}")
        if result.stdout:
            self.log(f"stdout: {result.stdout}")
        if result.stderr:
            self.log(f"stderr: {result.stderr}")
        self.refresh_health()

    def load_twitch_state(self):
        st = self.twitch_integration.load_state()
        self.twitch_status.setText(f"configured={st.configured.value}, tested={st.tested.value}; {st.details}")

    def save_twitch(self):
        cfg = TwitchConfig(
            client_id=self.twitch_client_id.text().strip(),
            access_token=self.twitch_access_token.text().strip(),
            channel=self.twitch_channel.text().strip(),
        )
        if not cfg.client_id or not cfg.access_token or not cfg.channel:
            self.on_error("All Twitch fields are required")
            return
        self.twitch_integration.save(cfg)
        self.load_twitch_state()
        self.log("Twitch credentials saved")

    def validate_twitch(self):
        self._run_in_thread(self.twitch_integration.validate, self.on_twitch_validated)

    def on_twitch_validated(self, state):
        self.twitch_status.setText(f"configured={state.configured.value}, tested={state.tested.value}; {state.details}")
        self.log(f"Twitch validation: {state.details}")

    def on_error(self, message: str):
        self.log(f"ERROR: {message}")
        QMessageBox.critical(self, "NemoClaw Control Error", message)
