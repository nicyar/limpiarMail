import imaplib
import email
from email.header import decode_header
import re
import html
import os
import json
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()


def cargar_blacklist():
    """
    Carga la lista de CUITs bloqueados desde blacklist.json (no se sube a git,
    igual que .env). En GitHub Actions, ese archivo se genera en el momento
    a partir de un secret, así que nunca queda expuesto en el repositorio.
    """
    ruta = os.getenv("BLACKLIST_PATH", "blacklist.json")

    if not os.path.exists(ruta):
        raise FileNotFoundError(
            f"No se encontró '{ruta}'. Copiá blacklist.example.json a blacklist.json "
            "y completá ahí tus CUITs reales (ese archivo nunca se sube a git)."
        )

    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


cuit_blacklist = cargar_blacklist()


def esta_en_lista_negra(cuit):
    """Devuelve True si el CUIT está en la lista negra, False si no."""
    return any(item["cuit"] == cuit for item in cuit_blacklist)


# PASO 1 — Conectarse al servidor con SSL
servidor = os.getenv("EMAIL_SERVIDOR")
puerto = int(os.getenv("EMAIL_PUERTO", 993))
email_usuario = os.getenv("EMAIL_USUARIO")
email_password = os.getenv("EMAIL_PASSWORD")

# Validar que todas las credenciales estén presentes
if not all([servidor, email_usuario, email_password]):
    raise ValueError("Faltan credenciales en el archivo .env")

conn = imaplib.IMAP4_SSL(servidor, puerto)

# PASO 2 — Autenticarse
conn.login(email_usuario, email_password)

# PASO 3 — Seleccionar la carpeta
conn.select("INBOX")

print("Conexión exitosa!")

# PASO 4 — Buscar mails NO LEÍDOS
_, ids = conn.search(None, "UNSEEN")
lista_ids = ids[0].split()

print(f"Total de mails NO LEÍDOS: {len(lista_ids)}")

# PASO 5 — Iterar sobre todos los mails NO LEÍDOS
asunto_objetivo = "Notificación pago segunda anualidad"

for mail_id in lista_ids:
    # Descargar el mail completo
    _, datos = conn.fetch(mail_id, "(RFC822)")
    raw_mail = datos[0][1]

    # Parsear el mail crudo a un objeto legible
    msg = email.message_from_bytes(raw_mail)

    # Extraer el asunto
    asunto_raw, encoding = decode_header(msg["Subject"])[0]
    asunto = asunto_raw.decode(encoding or "utf-8") if isinstance(asunto_raw, bytes) else asunto_raw

    # Verificar si el asunto es el que buscamos
    if asunto != asunto_objetivo:
        continue

    # Extraer el cuerpo HTML
    cuerpo_html = ""
    for parte in msg.walk():
        if parte.get_content_type() == "text/html":
            payload = parte.get_payload(decode=True)
            if payload:
                cuerpo_html = payload.decode("utf-8", errors="ignore")
                break

    # Limpiar HTML para obtener solo texto
    if cuerpo_html:
        cuerpo = html.unescape(cuerpo_html)
        cuerpo = re.sub(r'<[^>]+>', ' ', cuerpo)
        cuerpo = re.sub(r'\s+', ' ', cuerpo)
        cuerpo = cuerpo.strip()
    else:
        continue

    # Extraer CUIT
    try:
        cuit = cuerpo.split("CUIT :")[1].split("Nombre")[0].strip()
    except (IndexError, AttributeError):
        continue

    # Verificar si está en lista negra y eliminar
    if esta_en_lista_negra(cuit):
        print(f"Eliminando correo con CUIT: {cuit}")
        conn.store(mail_id, "+FLAGS", "\\Deleted")
    else:
        conn.store(mail_id, "-FLAGS", "\\Seen")

# Eliminar permanentemente los correos marcados
conn.expunge()

# Cerrar la sesión
conn.close()
conn.logout()