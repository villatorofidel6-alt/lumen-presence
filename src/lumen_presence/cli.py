from __future__ import annotations

import argparse
import json
from pathlib import Path

from lumen_presence.discord_client import DiscordPresenceClient
from lumen_presence.gui import launch
from lumen_presence.models import PresenceProfile
from lumen_presence.storage import ProfileStore


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lumen-presence", description="Local editor for Discord Rich Presence profiles")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("gui", help="Open the local desktop editor")
    apply_parser = sub.add_parser("apply", help="Apply a local saved profile to Discord")
    apply_parser.add_argument("name")
    clear_parser = sub.add_parser("clear", help="Clear Lumen Presence activity from the local Discord client")
    clear_parser.add_argument("--application-id", required=True, help="Your Discord Application ID")
    sub.add_parser("profiles", help="List locally saved profiles")
    args = parser.parse_args(argv)
    if args.command == "gui":
        launch()
        return 0
    store = ProfileStore()
    if args.command == "profiles":
        print(json.dumps(sorted(store.load_all()), indent=2, ensure_ascii=False))
        return 0
    client = DiscordPresenceClient()
    try:
        if args.command == "apply":
            profile = store.load_all()[args.name]
            client.apply(profile)
            print("Rich Presence applied through local Discord IPC.")
        else:
            client.clear(args.application_id)
            print("Rich Presence cleared.")
        return 0
    except KeyError:
        print(f"No saved profile named {args.name!r}.")
        return 2
    except Exception as exc:
        print(f"Lumen Presence: {exc}")
        return 2
    finally:
        client.disconnect()
