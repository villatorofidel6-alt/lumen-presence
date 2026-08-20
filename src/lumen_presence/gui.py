"""A local Tkinter editor for Discord Rich Presence profiles."""

from __future__ import annotations

import threading
from tkinter import BooleanVar, StringVar, Tk, messagebox, ttk

from lumen_presence.discord_client import DiscordPresenceClient
from lumen_presence.models import PresenceButton, PresenceProfile
from lumen_presence.storage import ProfileStore


class LumenPresenceApp:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title("Lumen Presence")
        self.root.geometry("900x720")
        self.root.minsize(720, 600)
        self.store = ProfileStore()
        self.client = DiscordPresenceClient()
        self.status = StringVar(value="Ready. Discord desktop must be running before applying a presence.")
        self.profile_name = StringVar(value="My presence")
        self.application_id = StringVar()
        self.details = StringVar()
        self.state = StringVar()
        self.large_image = StringVar()
        self.large_text = StringVar()
        self.small_image = StringVar()
        self.small_text = StringVar()
        self.button_one_label = StringVar()
        self.button_one_url = StringVar()
        self.button_two_label = StringVar()
        self.button_two_url = StringVar()
        self.timer_enabled = BooleanVar(value=True)
        self.saved_profiles = StringVar()
        self._style()
        self._build()
        self._refresh_profiles()
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        self.root.configure(bg="#101522")
        style.configure("TFrame", background="#101522")
        style.configure("Panel.TFrame", background="#172238")
        style.configure("TLabel", background="#101522", foreground="#e4edf8")
        style.configure("Panel.TLabel", background="#172238", foreground="#e4edf8")
        style.configure("Title.TLabel", background="#101522", foreground="#b8a7ff", font=("TkDefaultFont", 19, "bold"))
        style.configure("TButton", background="#6256b8", foreground="#ffffff", padding=(10, 7))
        style.map("TButton", background=[("active", "#796be3")])
        style.configure("TEntry", fieldbackground="#0d1523", foreground="#e4edf8")
        style.configure("TCheckbutton", background="#172238", foreground="#e4edf8")
        style.configure("TCombobox", fieldbackground="#0d1523", foreground="#e4edf8")

    def _build(self) -> None:
        frame = ttk.Frame(self.root, padding=22)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Lumen Presence", style="Title.TLabel").pack(anchor="w")
        ttk.Label(frame, text="Local Discord Rich Presence editor · No tokens, passwords, or browser required", foreground="#9fb3cc").pack(anchor="w", pady=(3, 15))

        profile_panel = ttk.Frame(frame, style="Panel.TFrame", padding=14)
        profile_panel.pack(fill="x", pady=(0, 14))
        ttk.Label(profile_panel, text="Saved profile", style="Panel.TLabel").grid(row=0, column=0, sticky="w")
        self.profile_selector = ttk.Combobox(profile_panel, textvariable=self.saved_profiles, state="readonly", width=31)
        self.profile_selector.grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(profile_panel, text="Load", command=self._load_selected).grid(row=0, column=2, padx=(0, 6))
        ttk.Label(profile_panel, text="Profile name", style="Panel.TLabel").grid(row=0, column=3, sticky="w", padx=(12, 0))
        ttk.Entry(profile_panel, textvariable=self.profile_name, width=23).grid(row=0, column=4, sticky="ew", padx=8)
        ttk.Button(profile_panel, text="Save", command=self._save).grid(row=0, column=5)
        profile_panel.columnconfigure(1, weight=1)
        profile_panel.columnconfigure(4, weight=1)

        fields = ttk.Frame(frame, style="Panel.TFrame", padding=16)
        fields.pack(fill="both", expand=True)
        self._entry(fields, 0, "Discord Application ID", self.application_id, "Create your own application in the Discord Developer Portal")
        self._entry(fields, 1, "Details", self.details, "What you are doing, shown below the activity name")
        self._entry(fields, 2, "State", self.state, "Optional secondary line")
        ttk.Checkbutton(fields, text="Show elapsed timer", variable=self.timer_enabled).grid(row=3, column=1, sticky="w", pady=6)
        ttk.Label(fields, text="Activity assets (use asset keys uploaded to your Discord application)", style="Panel.TLabel", font=("TkDefaultFont", 10, "bold")).grid(row=4, column=0, columnspan=3, sticky="w", pady=(14, 4))
        self._entry(fields, 5, "Large image key", self.large_image, "Example: main-art")
        self._entry(fields, 6, "Large image tooltip", self.large_text, "Optional text shown when hovering")
        self._entry(fields, 7, "Small image key", self.small_image, "Example: badge")
        self._entry(fields, 8, "Small image tooltip", self.small_text, "Optional text shown when hovering")
        ttk.Label(fields, text="Buttons (Discord permits up to two)", style="Panel.TLabel", font=("TkDefaultFont", 10, "bold")).grid(row=9, column=0, columnspan=3, sticky="w", pady=(14, 4))
        self._entry(fields, 10, "Button 1 label", self.button_one_label, "Example: Visit Lumen AI")
        self._entry(fields, 11, "Button 1 URL", self.button_one_url, "https://…")
        self._entry(fields, 12, "Button 2 label", self.button_two_label, "Optional")
        self._entry(fields, 13, "Button 2 URL", self.button_two_url, "https://…")
        fields.columnconfigure(1, weight=1)

        footer = ttk.Frame(frame, padding=(0, 14, 0, 0))
        footer.pack(fill="x")
        ttk.Label(footer, textvariable=self.status, foreground="#9fb3cc", wraplength=550).pack(side="left", fill="x", expand=True)
        ttk.Button(footer, text="Clear activity", command=self._clear).pack(side="right", padx=(8, 0))
        ttk.Button(footer, text="Apply to Discord", command=self._apply).pack(side="right")

    def _entry(self, frame: ttk.Frame, row: int, label: str, variable: StringVar, hint: str) -> None:
        ttk.Label(frame, text=label, style="Panel.TLabel").grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(frame, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        ttk.Label(frame, text=hint, style="Panel.TLabel", foreground="#96a9c1").grid(row=row, column=2, sticky="w", pady=5)

    def _profile(self) -> PresenceProfile:
        buttons = (
            PresenceButton(self.button_one_label.get(), self.button_one_url.get()),
            PresenceButton(self.button_two_label.get(), self.button_two_url.get()),
        )
        return PresenceProfile(
            application_id=self.application_id.get(), details=self.details.get(), state=self.state.get(),
            large_image=self.large_image.get(), large_text=self.large_text.get(), small_image=self.small_image.get(), small_text=self.small_text.get(),
            buttons=buttons, timer_enabled=self.timer_enabled.get(),
        ).validate()

    def _apply(self) -> None:
        try:
            profile = self._profile()
        except ValueError as exc:
            messagebox.showerror("Lumen Presence", str(exc))
            return
        self.status.set("Applying Rich Presence through local Discord IPC…")
        threading.Thread(target=self._apply_worker, args=(profile,), daemon=True).start()

    def _apply_worker(self, profile: PresenceProfile) -> None:
        try:
            self.client.apply(profile)
            self.root.after(0, lambda: self.status.set("Presence applied. Discord may take a moment to refresh the profile card."))
        except Exception as exc:
            self.root.after(0, lambda: messagebox.showerror("Discord IPC", str(exc)))
            self.root.after(0, lambda: self.status.set("Could not reach Discord. Confirm the desktop client and Application ID."))

    def _clear(self) -> None:
        try:
            self.client.clear(self.application_id.get().strip())
            self.status.set("Rich Presence cleared from the local Discord session.")
        except Exception as exc:
            messagebox.showerror("Discord IPC", str(exc))

    def _save(self) -> None:
        try:
            self.store.save(self.profile_name.get(), self._profile())
            self._refresh_profiles()
            self.status.set("Profile saved locally. It contains no Discord credentials.")
        except (ValueError, OSError) as exc:
            messagebox.showerror("Lumen Presence", str(exc))

    def _refresh_profiles(self) -> None:
        names = sorted(self.store.load_all())
        self.profile_selector["values"] = names
        if names and self.saved_profiles.get() not in names:
            self.saved_profiles.set(names[0])

    def _load_selected(self) -> None:
        try:
            profile = self.store.load_all()[self.saved_profiles.get()]
        except (KeyError, OSError, ValueError) as exc:
            messagebox.showerror("Lumen Presence", f"Could not load profile: {exc}")
            return
        self.application_id.set(profile.application_id)
        self.details.set(profile.details)
        self.state.set(profile.state)
        self.large_image.set(profile.large_image)
        self.large_text.set(profile.large_text)
        self.small_image.set(profile.small_image)
        self.small_text.set(profile.small_text)
        self.timer_enabled.set(profile.timer_enabled)
        buttons = list(profile.buttons) + [PresenceButton("", ""), PresenceButton("", "")]
        self.button_one_label.set(buttons[0].label)
        self.button_one_url.set(buttons[0].url)
        self.button_two_label.set(buttons[1].label)
        self.button_two_url.set(buttons[1].url)
        self.status.set("Profile loaded locally. Apply it when Discord desktop is running.")

    def _close(self) -> None:
        self.client.disconnect()
        self.root.destroy()


def launch() -> None:
    root = Tk()
    LumenPresenceApp(root)
    root.mainloop()
