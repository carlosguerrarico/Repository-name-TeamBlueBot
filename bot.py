import re
import os
from datetime import timedelta

from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
from telegram.constants import ChatPermissions

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
    "platotipico",
]

NOMBRES_PROHIBIDOS = [
    "sheila",
    "beba",
    "valentino",
    "eidevin",
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

    texto = re.sub(r'[^a-záéíóúñ]', '', texto)

    return texto


async def advertir(update, usuario_id, nombre):
    if usuario_id not in advertencias:
        advertencias[usuario_id] = 0

    advertencias[usuario_id] += 1

    cantidad = advertencias[usuario_id]

    if cantidad < 3:
        await update.effective_chat.send_message(
            f"⚠️ {nombre}, advertencia {cantidad}/3 por incumplir las reglas."
        )
    else:
        await update.effective_chat.restrict_member(
            usuario_id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=timedelta(minutes=10)
        )

        advertencias[usuario_id] = 0

        await update.effective_chat.send_message(
            f"⛔ {nombre} ha sido silenciado durante 10 minutos por acumular 3 advertencias."
        )


async def moderar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    texto = normalizar(update.message.text)

    usuario = update.effective_user
    usuario_id = usuario.id
    nombre = usuario.first_name

    # Ignorar administradores
    miembro = await update.effective_chat.get_member(usuario_id)

    if miembro.status in ["administrator", "creator"]:
        return

    # Revisar malas palabras
    for palabra in PALABRAS_PROHIBIDAS:
        if palabra in texto:
            await update.message.delete()
            await advertir(update, usuario_id, nombre)
            return

    # Revisar nombres protegidos
    for nombre_prohibido in NOMBRES_PROHIBIDOS:
        if nombre_prohibido in texto:
            await update.message.delete()

            await update.effective_chat.send_message(
                "⚠️ No está permitido mencionar nombres protegidos."
            )

            return


app = Application.builder().token(TOKEN).build()

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, moderar)
)

print("Team Blue Security iniciado...")
app.run_polling()