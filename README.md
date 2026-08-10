# limpiarMail

Script en Python que revisa automáticamente una casilla de correo, identifica notificaciones de pago provenientes de CUITs en una lista negra, y las elimina. Corre solo, sin intervención manual, tres veces por semana vía GitHub Actions.

## Qué resuelve

Ciertos remitentes generan notificaciones repetidas de un asunto específico que no aportan valor y solo ensucian la bandeja de entrada. En vez de borrarlas a mano, el script se conecta por IMAP, filtra por asunto, extrae el CUIT del cuerpo del mail, y decide automáticamente si eliminarlo o marcarlo como leído.

## Cómo funciona

1. Se conecta a la casilla vía `imaplib` (IMAP sobre SSL).
2. Busca todos los correos no leídos.
3. Filtra por el asunto exacto que interesa monitorear.
4. Extrae el cuerpo en HTML del correo y lo limpia con regex para quedarse solo con el texto.
5. Parsea el CUIT del texto.
6. Si el CUIT está en la lista negra, elimina el correo. Si no, lo marca como leído sin borrarlo.

## Automatización

El workflow de GitHub Actions (`.github/workflows/limpiar-correos.yml`) corre el script automáticamente lunes, miércoles y viernes, usando **GitHub Secrets** para las credenciales de email — nunca quedan expuestas en el código ni en los logs de ejecución. También se puede disparar manualmente desde la pestaña "Actions" del repositorio (`workflow_dispatch`).

## Stack

- Python 3.10
- `imaplib` / `email` (librería estándar) para el protocolo IMAP y el parseo de correos
- `python-dotenv` para variables de entorno en desarrollo local
- GitHub Actions para la ejecución programada

## Cómo correrlo localmente

1. Instalar dependencias:
   ```
   pip install python-dotenv
   ```

2. Crear un archivo `.env` en la raíz (no se sube a git) con:
   ```
   EMAIL_SERVIDOR=imap.tuproveedor.com
   EMAIL_PUERTO=993
   EMAIL_USUARIO=tu-email@dominio.com
   EMAIL_PASSWORD=tu-contraseña-o-app-password
   ```

3. Crear `blacklist.json` (No subir a Github) a partir de la plantilla:
   ```
   cp blacklist.example.json blacklist.json
   ```
   y completar ahí los CUITs reales a bloquear, con este formato:
   ```json
   [
     { "cuit": "20111111112", "nombre": "Empresa de Ejemplo SA" }
   ]
   ```

4. Correr:
   ```
   python app.py
   ```

## Configurar la automatización en GitHub

En **Settings → Secrets and variables → Actions** del repositorio, cargar:

- `EMAIL_SERVIDOR`
- `EMAIL_USUARIO`
- `EMAIL_PASSWORD`
- `CUIT_BLACKLIST_JSON` — el contenido completo de tu `blacklist.json`, pegado como un secret de tipo texto (el workflow lo escribe a un archivo en el momento de correr, así nunca queda en el repositorio)

## Nota sobre privacidad

Los CUITs y nombres reales bloqueados **no están en este repositorio** — viven en `blacklist.json`, que está en `.gitignore`, y en producción se inyectan vía GitHub Secrets. Solo `blacklist.example.json` (con datos ficticios) queda público, como referencia de formato.

## Bugs

Al corrrer el archivo manualmente, puede fallar en marcar los mails como no leidos

<img width="600" height="313" alt="Image" src="https://github.com/user-attachments/assets/52ee4b7c-3609-4aae-b437-c6e0c0ded117" />


