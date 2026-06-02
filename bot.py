import re
import os
import json
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

def cargar_json(archivo):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def guardar_json(archivo, datos):
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)


PALABRAS_PROHIBIDAS = cargar_json("palabras.json")
NOMBRES_PROHIBIDOS = cargar_json("nombres.json")

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


async def agregarpalabra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        await update.message.reply_text(
            "Uso: /agregarpalabra palabra"
        )
        return

    palabra = normalizar(" ".join(context.args))

    if palabra in PALABRAS_PROHIBIDAS:
        await update.message.reply_text(
            "⚠️ Esa palabra ya existe."
        )
        return

    PALABRAS_PROHIBIDAS.append(palabra)

    guardar_json(
        "palabras.json",
        PALABRAS_PROHIBIDAS
    )

    await update.message.reply_text(
        f"✅ Palabra agregada: {palabra}"
    )


async def eliminarpalabra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        await update.message.reply_text(
            "Uso: /eliminarpalabra palabra"
        )
        return

    palabra = normalizar(" ".join(context.args))

    if palabra not in PALABRAS_PROHIBIDAS:
        await update.message.reply_text(
            "⚠️ Esa palabra no existe."
        )
        return

    PALABRAS_PROHIBIDAS.remove(palabra)

    guardar_json(
        "palabras.json",
        PALABRAS_PROHIBIDAS
    )

    await update.message.reply_text(
        f"✅ Palabra eliminada: {palabra}"
    )


async def agregarnombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        await update.message.reply_text(
            "Uso: /agregarnombre nombre"
        )
        return

    nombre = normalizar(" ".join(context.args))

    if nombre in NOMBRES_PROHIBIDOS:
        await update.message.reply_text(
            "⚠️ Ese nombre ya existe."
        )
        return

    NOMBRES_PROHIBIDOS.append(nombre)

    guardar_json(
        "nombres.json",
        NOMBRES_PROHIBIDOS
    )

    await update.message.reply_text(
        f"✅ Nombre protegido agregado: {nombre}"
    )


async def eliminarnombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        await update.message.reply_text(
            "Uso: /eliminarnombre nombre"
        )
        return

    nombre = normalizar(" ".join(context.args))

    if nombre not in NOMBRES_PROHIBIDOS:
        await update.message.reply_text(
            "⚠️ Ese nombre no existe."
        )
        return

    NOMBRES_PROHIBIDOS.remove(nombre)

    guardar_json(
        "nombres.json",
        NOMBRES_PROHIBIDOS
    )

    await update.message.reply_text(
        f"✅ Nombre protegido eliminado: {nombre}"
    )


async def verpalabras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not PALABRAS_PROHIBIDAS:
        await update.message.reply_text(
            "No hay palabras registradas."
        )
        return

    texto = "📋 Palabras prohibidas:\n\n"

    for palabra in PALABRAS_PROHIBIDAS:
        texto += f"• {palabra}\n"

    await update.message.reply_text(texto)


async def vernombres(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not NOMBRES_PROHIBIDOS:
        await update.message.reply_text(
            "No hay nombres registrados."
        )
        return

    texto = "📋 Nombres protegidos:\n\n"

    for nombre in NOMBRES_PROHIBIDOS:
        texto += f"• {nombre}\n"

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
    CommandHandler(
        "agregarpalabra",
        agregarpalabra
    )
)

app.add_handler(
    CommandHandler(
        "eliminarpalabra",
        eliminarpalabra
    )
)

app.add_handler(
    CommandHandler(
        "agregarnombre",
        agregarnombre
    )
)

app.add_handler(
    CommandHandler(
        "eliminarnombre",
        eliminarnombre
    )
)

app.add_handler(
    CommandHandler(
        "verpalabras",
        verpalabras
    )
)

app.add_handler(
    CommandHandler(
        "vernombres",
        vernombres
    )
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