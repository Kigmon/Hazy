from __future__ import annotations

from dataclasses import dataclass

import requests

from nemoclaw_control.integrations.credentials import CredentialStore
from nemoclaw_control.state.models import IntegrationState, Status


@dataclass
class TwitchConfig:
    client_id: str
    access_token: str
    channel: str


class TwitchIntegration:
    def __init__(self, store: CredentialStore):
        self.store = store

    def load_state(self) -> IntegrationState:
        token = self.store.get_secret("twitch_access_token")
        client_id = self.store.get_secret("twitch_client_id")
        channel = self.store.get_secret("twitch_channel")
        if token and client_id and channel:
            return IntegrationState(configured=Status.CONFIGURED, tested=Status.UNKNOWN, details=f"Channel: {channel}")
        return IntegrationState(configured=Status.MISSING, tested=Status.UNKNOWN, details="Not configured")

    def save(self, config: TwitchConfig) -> None:
        self.store.set_secret("twitch_client_id", config.client_id)
        self.store.set_secret("twitch_access_token", config.access_token)
        self.store.set_secret("twitch_channel", config.channel)

    def validate(self) -> IntegrationState:
        client_id = self.store.get_secret("twitch_client_id")
        token = self.store.get_secret("twitch_access_token")
        if not client_id or not token:
            return IntegrationState(configured=Status.MISSING, tested=Status.BROKEN, details="Missing credentials")

        headers = {
            "Authorization": f"Bearer {token}",
            "Client-Id": client_id,
        }
        try:
            resp = requests.get("https://id.twitch.tv/oauth2/validate", headers=headers, timeout=8)
        except requests.RequestException as exc:
            return IntegrationState(configured=Status.PARTIAL, tested=Status.BROKEN, details=f"Network error: {exc}")

        if resp.status_code == 200:
            return IntegrationState(configured=Status.CONFIGURED, tested=Status.HEALTHY, details="Token valid")
        return IntegrationState(configured=Status.PARTIAL, tested=Status.BROKEN, details=f"Token invalid ({resp.status_code})")
