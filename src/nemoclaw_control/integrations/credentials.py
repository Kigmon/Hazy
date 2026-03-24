from __future__ import annotations

import json
import os
from pathlib import Path

import keyring

SERVICE_NAME = "nemoclaw-control"


class CredentialStore:
    def __init__(self):
        self.fallback_file = Path.home() / ".config" / SERVICE_NAME / "credentials.json"
        self.fallback_file.parent.mkdir(parents=True, exist_ok=True)

    def set_secret(self, key: str, value: str) -> None:
        try:
            keyring.set_password(SERVICE_NAME, key, value)
        except Exception:
            data = self._read_fallback()
            data[key] = value
            self.fallback_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
            os.chmod(self.fallback_file, 0o600)

    def get_secret(self, key: str) -> str | None:
        try:
            val = keyring.get_password(SERVICE_NAME, key)
            if val:
                return val
        except Exception:
            pass
        return self._read_fallback().get(key)

    def _read_fallback(self) -> dict[str, str]:
        if not self.fallback_file.exists():
            return {}
        try:
            raw = json.loads(self.fallback_file.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                return {str(k): str(v) for k, v in raw.items()}
        except Exception:
            return {}
        return {}
