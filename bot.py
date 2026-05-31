import re
import os
import google.generativeai as genai

from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

modelo = genai.GenerativeModel("gemini-1.5-flash")

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

async def mensaje_prohibido_por_ia(texto):
    try:
        prompt = f"""
Analiza este mensaje de Telegram.

Responde únicamente con SI o NO.

SI:
- insultos graves
- amenazas
- acoso
- spam evidente
- lenguaje extremadamente ofensivo

NO:
- conversación normal
- bromas inofensivas
- mensajes cotidianos

Mensaje:
{texto}
"""

        respuesta = modelo.generate_content(prompt)

        resultado = respuesta.text.strip().upper()

        return resultado.startswith("SI")

    except Exception as e:
        print("Error Gemini:", e)
        return False

async def moderar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    texto_original = update.message.text
    texto = normalizar(texto_original)

    for palabra in PALABRAS_PROHIBIDAS:
        if palabra in texto:
            await update.message.delete()
            print("Eliminado por palabra prohibida:", texto_original)
            return

    for nombre in NOMBRES_PROHIBIDOS:
        if nombre in texto:
            await update.message.delete()
            print("Eliminado por nombre prohibido:", texto_original)
            return

    if await mensaje_prohibido_por_ia(texto_original):
        await update.message.delete()
        print("Eliminado por IA:", texto_original)
        return

app = Application.builder().token(TOKEN).build()

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, moderar)
)

print("Team Blue Security IA iniciado...")
app.run_polling()