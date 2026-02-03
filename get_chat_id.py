import requests
import os
from dotenv import load_dotenv

# 🔹 Cargar variables desde .env
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN no está definido. Revisa el archivo .env")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

r = requests.get(url, timeout=15)
r.raise_for_status()

data = r.json()
if not data.get("ok"):
    raise SystemExit(f"Telegram API error: {data}")

results = data.get("result", [])
if not results:
    raise SystemExit("No hay updates. Escribe 'hola' al bot en Telegram y vuelve a ejecutar.")

# Tomar el último update con mensaje
for upd in reversed(results):
    msg = upd.get("message") or upd.get("channel_post")
    if msg and "chat" in msg and "id" in msg["chat"]:
        chat = msg["chat"]
        print("CHAT_ID =", chat["id"])
        print("CHAT_TYPE =", chat.get("type"))
        print("CHAT_TITLE/USER =", chat.get("title") or chat.get("username") or chat.get("first_name"))
        break
else:
    raise SystemExit("No encontré un chat_id. Envía un mensaje al bot y reintenta.")
