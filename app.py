import imaplib
import email
from email.header import decode_header
import re
import html
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# LISTA NEGRA DE CUITs
cuit_blacklist = [
    
    "30717647501",  # FOVANI SRL
    "30714954217",  # MOBISOND SA
    "30715005413",  # TRIMMER S.A.
    "30714928577",  # SIMPLEX VILI S.A.
    "30636741120",  # CIGLIUTTI GUERINI
    "30575818826",  # CASA ABE SA
    "20937313358",  # PALOMINO VENERO DOMINGO ELEODORO
    "30528956145",  # LA POMME SOCIEDAD ANONIMA GANADERA AGROPECUARIA Y COMERCIAL
    "30714153796",  # CHAD MEDICINE SRL
    "33716533579",  # PENA COMEX SRL
    "30710298684",  # FOOD PATAGONIA S.A.
    "30711724954",  # PAUMA S.R.L.
    "30707611533",  # LIBRESRIO SRL
    "30714190608",  # HRC AIR SA
    "30712482164",  # AMERICAN CRYSTAL SRL
    "30708693479",  # DEMATE SA
    "30708429518",  # ACTIVASALUD S.R.L.
    "30502878936",  # GIACOMINO SA
    "30656171827",  # ANGIOCOR SA
    "30702709101",  # ASOCIACION MUTUAL DE LA ECONOMIA SOLIDARIA
    "30506988264",  # Sindicato Unidos Portuarios Argentinos - Puerto de Capital Federal y Dock Sud
    "30590921862",  # RIOLIBRES SRL
    "30709887374",  # ADMINISTRAR SALUD SA
    "30709302465",  # URUGUAY TRANSPORTE SRL
    "30710448031",  # Haciendo Camino Asociacion Civil
    "30714276367",  # BERPHARMA SA
    "30717324915",  # VERTICE CONSTRUCCIONES SA
    "30715693913",  # CONSBAGO SRL
    "30714453447",  # ITALIA COMUNICACION SRL
    "20084321509",  # FOGAROLLI CARLOS ATILIO
    "20319634755",  # RIQUELME FERNANDO OSCAR
    "30714725358",  # LOVINNE S.A
    "30718085221",  # XAPOR S.A. - LX ARGENTINA S.A. - UNIÓN TRANSITORIA U. T. E
    "30718644344",  # Bran Morrigan SA
    "30708244186",  # PARAKEET CAPITAL SA
    "30717597261",  # AD3 SERVICIOS INTEGRALES SRL
    "33585510489",  # MARLEW SA
    "33718102419",  # Nacarse SA
    "30717570754",  # EPPIX SRL
    "33694503859",  # ORGANIZACION MEDICA S A
    "30717496740",  # FOX ELECTRONICS SRL
    "20084321509",  # FOGAROLLI CARLOS ATILIO
    "30717570754",  # EPPIX SRL
    "33585510489",  # Marlew SA
    "20319634755",  # RIQUELME FERNANDO OSCAR
    "30717693147",  # CONSTRUCTORA PAMPEANA SA
    "30708163658",  # AMBIENT ARGENTINA
    "30716619253",  # INSTITUTO INCORPORADO SH. I. AGNON A672
    "30714434906",  # IMPLANTES BIO - CORP SA
    "30710448031",  # Haciendo Camino Asociacion Civil
    "30699670231",  # OLAZABAL ENRIQUE Y OLAZABAL GUILLERMO SH
    "27060445899",  # MARTINENGO NELIDA ROSA
    "30717042812",  # SIGNA DESARROLLOS SA
    "30711620253",  # CIC LOGISTICA SRL
    "33503716319",  # DELPA SRL
    "30708727519"  # GRAFICA OFFSET SRL

]

def esta_en_lista_negra(cuit):
    """Devuelve True si el CUIT está en la lista negra, False si no"""
    return cuit in cuit_blacklist

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
