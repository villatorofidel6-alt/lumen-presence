# Configurar tu aplicación de Discord

Lumen Presence no usa aplicaciones compartidas. Crea una aplicación propia para decidir exactamente qué nombre y qué assets mostrará tu Rich Presence.

1. Abre el [Discord Developer Portal](https://discord.com/developers/applications) e inicia sesión en tu cuenta.
2. Selecciona **New Application**, asigna un nombre a la aplicación y guarda. Ese nombre será la línea principal de la actividad en Discord.
3. En **General Information**, copia el **Application ID**. Este identificador público se usa en Lumen Presence; **no copies ni pegues el Client Secret**.
4. Abre **Rich Presence → Art Assets** y carga las imágenes que quieras usar. Discord recomienda assets de 1024 × 1024; conserva las claves de cada asset para introducirlas en Lumen Presence. [1]
5. Abre Discord Desktop, inicia sesión y habilita la compartición de actividad si deseas que sea visible.
6. Abre Lumen Presence, introduce el Application ID, detalles, estado y claves de assets. Guarda el perfil y pulsa **Apply to Discord**.

| Problema | Revisión recomendada |
|---|---|
| No se puede conectar | Confirma que Discord Desktop está abierto, que has iniciado sesión y que el Application ID contiene solo dígitos. |
| No aparece la imagen | Verifica la clave exacta del asset cargado en tu propia aplicación de Discord. |
| Discord rechaza el perfil | Revisa los límites de texto, URLs HTTPS y máximo de dos botones. |
| La actividad no es pública | Verifica la configuración de privacidad y actividad de Discord. |

No compartas tu Client Secret, token de usuario, contraseña, cookies ni códigos de autenticación. Lumen Presence no los necesita ni debe almacenarlos.

## Referencias

[1] [Discord: Setting Rich Presence and Uploading Assets](https://docs.discord.com/developers/discord-social-sdk/development-guides/setting-rich-presence)
