"""Local Discord IPC wrapper. No Discord password, user token, bot token, or client secret is used."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from pypresence import Presence

from lumen_presence.models import PresenceProfile


class RpcConnection(Protocol):
    def connect(self) -> Any: ...
    def update(self, **kwargs: Any) -> Any: ...
    def clear(self) -> Any: ...
    def close(self) -> Any: ...


class DiscordUnavailableError(RuntimeError):
    pass


@dataclass
class DiscordPresenceClient:
    connection: RpcConnection | None = None
    application_id: str | None = None

    def connect(self, application_id: str) -> None:
        if self.connection is not None and self.application_id == application_id:
            return
        self.disconnect()
        try:
            connection = Presence(application_id)
            connection.connect()
        except Exception as exc:
            raise DiscordUnavailableError("Discord desktop is not reachable through local IPC. Start Discord, sign in, and confirm the Application ID.") from exc
        self.connection = connection
        self.application_id = application_id

    def apply(self, profile: PresenceProfile) -> None:
        validated = profile.validate()
        self.connect(validated.application_id)
        if self.connection is None:
            raise DiscordUnavailableError("Discord connection was not established")
        try:
            self.connection.update(**validated.rpc_payload())
        except Exception as exc:
            raise DiscordUnavailableError("Discord rejected the Rich Presence update. Check your Application ID and uploaded asset keys.") from exc

    def clear(self, application_id: str | None = None) -> None:
        if self.connection is None:
            if not application_id:
                raise DiscordUnavailableError("An Application ID is required to connect and clear a Rich Presence activity")
            self.connect(application_id)
        try:
            if self.connection is None:
                raise DiscordUnavailableError("Discord connection was not established")
            self.connection.clear()
        except Exception as exc:
            raise DiscordUnavailableError("Discord did not accept the request to clear Rich Presence") from exc

    def disconnect(self) -> None:
        if self.connection is not None:
            try:
                self.connection.close()
            except Exception:
                pass
        self.connection = None
        self.application_id = None
