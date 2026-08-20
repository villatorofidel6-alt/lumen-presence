from __future__ import annotations

from dataclasses import asdict, dataclass, field
from time import time
from typing import Any
from urllib.parse import urlparse


MAX_DETAILS = 128
MAX_STATE = 128
MAX_ASSET_TEXT = 128
MAX_BUTTONS = 2
MAX_BUTTON_LABEL = 32


class PresenceValidationError(ValueError):
    pass


def _required_text(value: str, label: str, limit: int) -> str:
    normalized = value.strip()
    if not normalized:
        raise PresenceValidationError(f"{label} is required")
    if len(normalized) > limit:
        raise PresenceValidationError(f"{label} must be {limit} characters or fewer")
    return normalized


def _optional_text(value: str, label: str, limit: int) -> str | None:
    normalized = value.strip()
    if not normalized:
        return None
    if len(normalized) > limit:
        raise PresenceValidationError(f"{label} must be {limit} characters or fewer")
    return normalized


def _safe_url(value: str) -> str:
    normalized = value.strip()
    parsed = urlparse(normalized)
    if parsed.scheme not in {"https", "http"} or not parsed.netloc:
        raise PresenceValidationError("Button URLs must be absolute http(s) URLs")
    return normalized


@dataclass(frozen=True)
class PresenceButton:
    label: str
    url: str

    def validate(self) -> "PresenceButton":
        return PresenceButton(_required_text(self.label, "Button label", MAX_BUTTON_LABEL), _safe_url(self.url))


@dataclass(frozen=True)
class PresenceProfile:
    application_id: str
    details: str
    state: str = ""
    large_image: str = ""
    large_text: str = ""
    small_image: str = ""
    small_text: str = ""
    buttons: tuple[PresenceButton, ...] = field(default_factory=tuple)
    timer_enabled: bool = True
    timer_started_at: int | None = None

    def validate(self) -> "PresenceProfile":
        application_id = self.application_id.strip()
        if not application_id.isdigit() or not 15 <= len(application_id) <= 22:
            raise PresenceValidationError("Application ID must be a 15–22 digit Discord application ID")
        buttons = tuple(button.validate() for button in self.buttons if button.label.strip() or button.url.strip())
        if len(buttons) > MAX_BUTTONS:
            raise PresenceValidationError("Discord Rich Presence supports at most two buttons")
        return PresenceProfile(
            application_id=application_id,
            details=_required_text(self.details, "Details", MAX_DETAILS),
            state=_optional_text(self.state, "State", MAX_STATE) or "",
            large_image=_optional_text(self.large_image, "Large image key", 256) or "",
            large_text=_optional_text(self.large_text, "Large image tooltip", MAX_ASSET_TEXT) or "",
            small_image=_optional_text(self.small_image, "Small image key", 256) or "",
            small_text=_optional_text(self.small_text, "Small image tooltip", MAX_ASSET_TEXT) or "",
            buttons=buttons,
            timer_enabled=self.timer_enabled,
            timer_started_at=self.timer_started_at or (int(time()) if self.timer_enabled else None),
        )

    def rpc_payload(self) -> dict[str, Any]:
        profile = self.validate()
        payload: dict[str, Any] = {"details": profile.details}
        if profile.state:
            payload["state"] = profile.state
        if profile.large_image:
            payload["large_image"] = profile.large_image
        if profile.large_text:
            payload["large_text"] = profile.large_text
        if profile.small_image:
            payload["small_image"] = profile.small_image
        if profile.small_text:
            payload["small_text"] = profile.small_text
        if profile.buttons:
            payload["buttons"] = [{"label": item.label, "url": item.url} for item in profile.buttons]
        if profile.timer_enabled and profile.timer_started_at:
            payload["start"] = profile.timer_started_at
        return payload

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["buttons"] = [asdict(item) for item in self.buttons]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PresenceProfile":
        buttons = tuple(PresenceButton(**button) for button in data.get("buttons", []))
        return cls(
            application_id=str(data.get("application_id", "")),
            details=str(data.get("details", "")),
            state=str(data.get("state", "")),
            large_image=str(data.get("large_image", "")),
            large_text=str(data.get("large_text", "")),
            small_image=str(data.get("small_image", "")),
            small_text=str(data.get("small_text", "")),
            buttons=buttons,
            timer_enabled=bool(data.get("timer_enabled", True)),
            timer_started_at=data.get("timer_started_at"),
        )
