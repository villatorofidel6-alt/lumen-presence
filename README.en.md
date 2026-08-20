# Lumen Presence

> **A local desktop editor for custom Discord Rich Presence.**

[Documentación en español](README.md) · [Architecture](ARCHITECTURE.md) · [Discord setup guide](docs/CONFIGURAR_DISCORD.md)

Lumen Presence configures a custom activity for the local Discord session: details, state, activity images, tooltips, up to two buttons, and an elapsed timer. It uses local IPC with Discord Desktop; it does not use a browser, upload data, or request a password, user token, bot token, or client secret.

| Element | Configuration |
|---|---|
| Activity name | The name is configured on your own Discord application in the Developer Portal. |
| Details and state | Edited in Lumen Presence. |
| Activity images | Referenced by asset keys uploaded to your Discord application. |
| Buttons | Up to two HTTPS buttons with a label and URL. |
| Real Discord avatar/profile | **Never modified.** The app controls only temporary local-session activity. |

## Quick start

Create your own application in the [Discord Developer Portal](https://discord.com/developers/applications), choose its activity name, copy its **Application ID**, and upload any Rich Presence assets. Then:

```bash
git clone https://github.com/villatorofidel6-alt/lumen-presence.git
cd lumen-presence
python -m venv .venv
# Activate the virtual environment for your OS
python -m pip install -e .
lumen-presence gui
```

Lumen Presence saves only profile configuration locally; it does not retain Discord credentials. Discord Desktop must be running and signed in before applying an activity.

## Credits

**Creator and founder:** Lumen AI  
**GitHub:** [@villatorofidel6-alt](https://github.com/villatorofidel6-alt)  
**Discord:** `px1j`

## References

[1] [Discord: Setting Rich Presence](https://docs.discord.com/developers/discord-social-sdk/development-guides/setting-rich-presence)

[2] [Discord: RPC over IPC](https://docs.discord.com/developers/topics/rpc)
