from __future__ import annotations

from pathlib import Path

import pytest

from lumen_presence.discord_client import DiscordPresenceClient
from lumen_presence.models import PresenceButton, PresenceProfile, PresenceValidationError
from lumen_presence.storage import ProfileStore


APPLICATION_ID = "123456789012345678"


class FakeConnection:
    def __init__(self) -> None:
        self.updates: list[dict] = []
        self.cleared = False
        self.closed = False

    def connect(self) -> None:
        return None

    def update(self, **kwargs) -> None:
        self.updates.append(kwargs)

    def clear(self) -> None:
        self.cleared = True

    def close(self) -> None:
        self.closed = True


def test_profile_payload_validates_buttons_and_timer() -> None:
    profile = PresenceProfile(
        application_id=APPLICATION_ID,
        details="Reviewing a local project",
        state="Focused",
        large_image="workspace",
        buttons=(PresenceButton("Project", "https://example.org"),),
        timer_enabled=True,
        timer_started_at=1_700_000_000,
    )
    payload = profile.rpc_payload()
    assert payload["details"] == "Reviewing a local project"
    assert payload["buttons"] == [{"label": "Project", "url": "https://example.org"}]
    assert payload["start"] == 1_700_000_000


def test_profile_rejects_invalid_url_and_application_id() -> None:
    with pytest.raises(PresenceValidationError):
        PresenceProfile(application_id="bad", details="Hello").validate()
    with pytest.raises(PresenceValidationError):
        PresenceProfile(application_id=APPLICATION_ID, details="Hello", buttons=(PresenceButton("Site", "file:///etc/passwd"),)).validate()


def test_client_uses_local_connection_and_can_clear() -> None:
    fake = FakeConnection()
    client = DiscordPresenceClient(connection=fake, application_id=APPLICATION_ID)
    client.apply(PresenceProfile(application_id=APPLICATION_ID, details="Safe fixture", timer_enabled=False))
    client.clear()
    client.disconnect()
    assert fake.updates[0]["details"] == "Safe fixture"
    assert fake.cleared is True
    assert fake.closed is True


def test_store_round_trip_contains_only_profile_configuration(tmp_path: Path) -> None:
    store = ProfileStore(tmp_path / "profiles.json")
    profile = PresenceProfile(application_id=APPLICATION_ID, details="Saved fixture", timer_enabled=False)
    store.save("fixture", profile)
    loaded = store.load_all()["fixture"]
    assert loaded.application_id == APPLICATION_ID
    assert loaded.details == "Saved fixture"
    assert "token" not in store.path.read_text(encoding="utf-8").lower()
