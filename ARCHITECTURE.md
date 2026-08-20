# Lumen Presence — Arquitectura y límites

Lumen Presence es una aplicación de escritorio local que se comunica exclusivamente con el cliente de Discord instalado en el mismo equipo mediante **IPC**. El usuario proporciona el **Application ID** de una aplicación que haya creado en el Discord Developer Portal; no se solicita, almacena ni utiliza contraseña, token de usuario, token de bot ni `client_secret`.

| Componente | Responsabilidad | Límite de seguridad |
|---|---|---|
| Modelo de actividad | Detalles, estado, nombres de assets, botones y temporizador | Valida límites y URLs antes de enviarlos. |
| Cliente IPC | Busca el socket local de Discord, realiza `HANDSHAKE` y envía `SET_ACTIVITY` | No abre conexiones de red, no usa WebSocket y no accede a otras cuentas. |
| Interfaz de escritorio | Permite editar, aplicar, limpiar y guardar perfiles locales | No modifica el avatar ni datos permanentes de la cuenta. |
| Persistencia | Guarda perfiles JSON bajo el directorio local de la aplicación | Solo conserva configuración de presencia; nunca credenciales. |

Discord documenta que RPC sobre IPC permite comunicación local entre una aplicación nativa y el cliente de Discord, con `HANDSHAKE` que incluye la versión RPC y el Client ID. En Linux y macOS, la ubicación de IPC se resuelve mediante directorios de entorno y `/tmp` como fallback. [1] `SET_ACTIVITY` actualiza Rich Presence y admite las actividades Playing, Listening, Watching o Competing. [1] Rich Presence puede incluir campos de texto, timestamps, assets cargados, botones y enlaces; Discord indica que se pueden configurar hasta dos botones y que los assets se referencian por clave tras cargarlos en el Developer Portal. [2] [3]

> Discord muestra Rich Presence públicamente. Durante el desarrollo, Discord recomienda usar una cuenta de prueba privada; Lumen Presence muestra este recordatorio y no pretende suplantar identidades ni modificar perfiles. [2]

## Referencias

[1] [Discord Developer Docs: RPC](https://docs.discord.com/developers/topics/rpc)

[2] [Discord Developer Docs: Rich Presence](https://docs.discord.com/developers/platform/rich-presence)

[3] [Discord Developer Docs: Setting Rich Presence](https://docs.discord.com/developers/discord-social-sdk/development-guides/setting-rich-presence)

**Créditos:** Lumen AI · GitHub [@villatorofidel6-alt](https://github.com/villatorofidel6-alt) · Discord `px1j`.
