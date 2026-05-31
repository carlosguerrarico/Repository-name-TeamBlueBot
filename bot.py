import re
import os

from telegram import Update
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
    "plato tipico",
]

NOMBRES_PROHIBIDOS = [
    "sheila",
    "beba",
    "valentino",
    "eidevin",
]

def normalizar(texto):
    texto = texto.lower()

    reemplazos = {
        "0": "o",
        "1": "i",
        "3": "e",
        "4": "a",
        "5": "s",
    }

    for viejo, nuevo in reemplazos.items():
        texto = texto.replace(viejo, nuevo)

    return texto

async def moderar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    texto = normalizar(update.message.text)

    for palabra in PALABRAS_PROHIBIDAS:
        if palabra in texto:
            await update.message.delete()
            return

    for nombre in NOMBRES_PROHIBIDOS:
        if nombre in texto:
            await update.message.delete()
            return

app = Application.builder().token(TOKEN).build()

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, moderar)
)

print("Team Blue Security iniciado...")
app.run_polling()