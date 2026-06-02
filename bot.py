import re
import os
from datetime import datetime, timedelta

from telegram import Update, ChatPermissions
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

PALABRAS_PROHIBIDAS = [
    "hp",
    "hpta",
    "gonorrea",
    "mk",
    "moza",
    "perra",
    "perro",
    "infiel",
    "amante",
    "platotipico",
]

NOMBRES_PROHIBIDOS = [
    "sheila",
    "beba",
    "bba",
    "valentino",
    "eidevin",
    "sofia",
    "zorro",
    "zorroviejo",
    "melissa",
    "melissagate",
    "meli",
    "alexa",
    "alexatorrex",
    "morada",
    "yuli",
    "yuliruiz",
    "nicolas",
    "nicolasarrieta",
    "marilyn",
    "marilynpatino",
]

advertencias = {}


def normalizar(texto):
    texto = texto.lower()

    reemplazos = {
        "0": "o",
        "1": "i",
        "3": "e",
        "4": "a",
        "5": "s",
        "7": "t",
        "@": "a",
        "$": "s",
    }

    for viejo, nuevo in reemplazos.items():
        texto = texto.replace(viejo, nuevo)

    texto = re.sub(r"[^a-záéíóúñ]", "", texto)

    return texto


async def registrar_infraccion(update, usuario_id, nombre):
    if usuario_id not in advertencias:
        advertencias[usuario_id] = 0

    advertencias[usuario_id] += 1

    if advertencias[usuario_id] >= 5:
        try:
            await update.effective_chat.restrict_member(
                usuario_id,
                permissions=ChatPermissions(
                    can_send_messages=False
                ),
                until_date=datetime.utcnow() + timedelta(minutes=10)
            )

            await update.effective_chat.send_message(
                f"⛔️ {nombre}, has incumplido las reglas del grupo."
            )

        except Exception as e:
            print("Error al silenciar:", e)

        advertencias[usuario_id] = 0


async def moderar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:	
        return

    usuario = update.effective_user
    usuario_id = usuario.id
    nombre = usuario.first_name

    miembro = await update.effective_chat.get_member(usuario_id)

    # Ignorar administradores
    if miembro.status in ["administrator", "creator"]:
        return

    contenido = update.message.text or update.message.caption

    if not contenido:
        return

    texto = normalizar(contenido)

    # Revisar malas palabras
    for palabra in PALABRAS_PROHIBIDAS:
        if palabra in texto:
            await update.message.delete()
            await registrar_infraccion(update, usuario_id, nombre)
            return

    # Revisar nombres protegidos
    for nombre_prohibido in NOMBRES_PROHIBIDOS:
        if nombre_prohibido in texto:
            await update.message.delete()
            return


app = Application.builder().token(TOKEN).build()

app.add_handler(
    MessageHandler(~filters.COMMAND, moderar)
)

print("Team Blue Security iniciado...")
app.run_polling()