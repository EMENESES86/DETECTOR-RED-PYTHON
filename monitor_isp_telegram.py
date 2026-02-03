import time
import socket
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

# 🔹 Cargar variables desde .env
load_dotenv()

# ==========================================================
# 🔐 TELEGRAM – CONFIGURACIÓN QUEMADA
# ==========================================================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise RuntimeError("Faltan variables TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en .env")

CHAT_ID = int(CHAT_ID)  # asegura tipo correcto


# ==========================================================
# 🌐 MONITOREO ISP
# ==========================================================
URLS = [
    "https://www.google.com/generate_204",
    "https://www.cloudflare.com/cdn-cgi/trace",
    "https://github.com",
]

INTERVALO_SEG = 5
TIMEOUT_SEG = 4

# Estado global
FALLOS_CONSEC_GLOBAL = 3           # ISP caído si falla N veces seguidas
LATENCIA_DEGRADACION_MS = 300      # ms promedio para estado DEGRADED
COOLDOWN_ALERTA_SEG = 60           # anti-spam Telegram

# ==========================================================
# UTILIDADES
# ==========================================================
def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg):
    print(f"[{now()}] {msg}")

session = requests.Session()

def telegram_send(msg):
    # 1) prueba rápida de conectividad a Telegram (opcional pero útil)
    try:
        _ = session.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=10)
    except requests.RequestException as e:
        log(f"Telegram precheck FAIL: {type(e).__name__}")
        return False

    # 2) envío real
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "disable_web_page_preview": True
    }
    try:
        r = session.post(url, json=payload, timeout=15)
        if r.status_code != 200:
            log(f"Telegram HTTP {r.status_code}: {r.text[:200]}")
            return False
        return True
    except requests.exceptions.ConnectTimeout:
        log("Telegram error: ConnectTimeout (posible bloqueo/red lenta)")
        return False
    except requests.RequestException as e:
        log(f"Telegram error: {type(e).__name__}")
        return False


def dns_check(host="google.com"):
    t0 = time.perf_counter()
    try:
        socket.gethostbyname(host)
        return True, (time.perf_counter() - t0) * 1000
    except:
        return False, (time.perf_counter() - t0) * 1000

def http_check(url):
    t0 = time.perf_counter()
    try:
        r = requests.get(url, timeout=TIMEOUT_SEG)
        return True, r.status_code, (time.perf_counter() - t0) * 1000
    except:
        return False, None, (time.perf_counter() - t0) * 1000

# ==========================================================
# MAIN
# ==========================================================
def main():
    estado = "UNKNOWN"   # UNKNOWN | UP | DEGRADED | DOWN
    fallos_global = 0
    ultima_alerta = {}

    log("🚀 Iniciando monitoreo ISP con Telegram")
    log(f"URLs={len(URLS)} intervalo={INTERVALO_SEG}s timeout={TIMEOUT_SEG}s")
    log("Ctrl+C para salir\n")

    try:
        while True:
            dns_ok, dns_ms = dns_check()

            ok_count = 0
            latencias = []
            detalles = []

            for u in URLS:
                ok, status, ms = http_check(u)
                if ok:
                    ok_count += 1
                    latencias.append(ms)
                    detalles.append(f"✅ {u} ({ms:.0f}ms)")
                else:
                    detalles.append(f"❌ {u} ({ms:.0f}ms)")

            avg_latency = sum(latencias) / len(latencias) if latencias else None

            # Reglas ISP
            up = ok_count >= 2
            degraded = avg_latency and avg_latency >= LATENCIA_DEGRADACION_MS

            if up:
                fallos_global = 0
            else:
                fallos_global += 1

            nuevo_estado = estado
            if not up and fallos_global >= FALLOS_CONSEC_GLOBAL:
                nuevo_estado = "DOWN"
            elif up and degraded:
                nuevo_estado = "DEGRADED"
            elif up:
                nuevo_estado = "UP"

            log(f"DNS={'OK' if dns_ok else 'FAIL'} {dns_ms:.0f}ms | "
                f"HTTP {ok_count}/{len(URLS)} | "
                f"avg={avg_latency:.0f}ms" if avg_latency else "avg=--")

            # Notificar solo si cambia estado
            if nuevo_estado != estado:
                msg = (
                    f"📡 *MONITOREO ISP*\n"
                    f"Estado: {estado} ➜ {nuevo_estado}\n"
                    f"Hora: {now()}\n"
                    f"DNS: {'OK' if dns_ok else 'FAIL'} ({dns_ms:.0f}ms)\n"
                    f"HTTP OK: {ok_count}/{len(URLS)}\n"
                )
                if avg_latency:
                    msg += f"Latencia promedio: {avg_latency:.0f} ms\n"
                msg += "\n" + "\n".join(detalles)

                key = f"{estado}->{nuevo_estado}"
                last = ultima_alerta.get(key, 0)

                if time.time() - last > COOLDOWN_ALERTA_SEG:
                    if telegram_send(msg):
                        log("📨 Telegram enviado")
                    ultima_alerta[key] = time.time()

                estado = nuevo_estado

            time.sleep(INTERVALO_SEG)

    except KeyboardInterrupt:
        log("🛑 Monitoreo detenido")

if __name__ == "__main__":
    main()
