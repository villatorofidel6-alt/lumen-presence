"""Local JSON profile storage. Discord credentials are never stored."""

from __future__ import annotations

import json
from pathlib import Path

from lumen_presence.models import PresenceProfile


class ProfileStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (Path.home() / ".lumen-presence" / "profiles.json")
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> dict[str, PresenceProfile]:
        if not self.path.exists():
            return {}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return {name: PresenceProfile.from_dict(profile) for name, profile in data.get("profiles", {}).items()}

    def save(self, name: str, profile: PresenceProfile) -> None:
        normalized = name.strip()
        if not normalized or len(normalized) > 64:
            raise ValueError("Profile name must contain 1–64 characters")
        profiles = self.load_all()
        profiles[normalized] = profile.validate()
        payload = {"version": 1, "profiles": {key: value.to_dict() for key, value in profiles.items()}}
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def delete(self, name: str) -> None:
        profiles = self.load_all()
        profiles.pop(name, None)
        payload = {"version": 1, "profiles": {key: value.to_dict() for key, value in profiles.items()}}
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
