import re
import os
from datetime import datetime, timedelta

from telegram import Update, ChatPermissions
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 8698288233

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


async def estadisticas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    usuarios = len(advertencias)
    total = sum(advertencias.values())

    await update.message.reply_text(
        f"📊 Team Blue Security\n\n"
        f"Usuarios registrados: {usuarios}\n"
        f"Infracciones activas: {total}"
    )


async def infracciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not advertencias:
        await update.message.reply_text(
            "No hay infracciones registradas."
        )
        return

    texto = "📋 Infracciones actuales\n\n"

    for usuario_id, cantidad in advertencias.items():
        texto += f"ID {usuario_id}: {cantidad}\n"

    await update.message.reply_text(texto)


async def moderar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    mensaje = update.message or update.edited_message

    if not mensaje:
        return

    contenido = mensaje.text or mensaje.caption

    if not contenido:
        return

    usuario = mensaje.from_user
    usuario_id = usuario.id
    nombre = usuario.first_name

    miembro = await update.effective_chat.get_member(usuario_id)

    if miembro.status in ["administrator", "creator"]:
        return

    texto = normalizar(contenido)

    # Palabras prohibidas = cuentan infracción
    for palabra in PALABRAS_PROHIBIDAS:
        if palabra in texto:
            await mensaje.delete()
            await registrar_infraccion(update, usuario_id, nombre)
            return

    # Nombres protegidos = NO cuentan infracción
    for nombre_prohibido in NOMBRES_PROHIBIDOS:
        if nombre_prohibido in texto:
            await mensaje.delete()
            return


app = Application.builder().token(TOKEN).build()

app.add_handler(
    CommandHandler("estadisticas", estadisticas)
)

app.add_handler(
    CommandHandler("infracciones", infracciones)
)

app.add_handler(
    MessageHandler(
        filters.ALL,
        moderar
    )
)

print("Team Blue Security iniciado...")

app.run_polling(
    allowed_updates=[
        "message",
        "edited_message"
    ]
)