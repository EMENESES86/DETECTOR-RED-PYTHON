
# 🌐 Monitor de Conectividad ISP con Alertas por Telegram

Sistema profesional de monitoreo en **Python** diseñado para la supervisión continua de la estabilidad del servicio de Internet (ISP). Utiliza pruebas híbridas de **HTTP** y **DNS** para clasificar el estado de la red y notificar cambios críticos en tiempo real a través de **Telegram**.

Ideal para entornos académicos, servidores locales o servicios críticos que requieren evidencia técnica de intermitencias del proveedor.

---

## ✨ Características Principales

* **Monitoreo Híbrido:** Validación mediante resolución DNS y peticiones HTTP a servicios de alta disponibilidad (Google, Cloudflare, etc.).
* **Detección de Latencia:** Identifica estados de servicio "Degradado" basándose en tiempos de respuesta.
* **Notificaciones Inteligentes:** Sistema anti-spam que solo envía alertas cuando ocurre un cambio de estado.
* **Seguridad:** Gestión de credenciales mediante variables de entorno (`.env`).
* **Diagnóstico Técnico:** Reporta latencia promedio y éxito de paquetes en cada ciclo.

---

## 🛠️ Requisitos del Sistema

* **Python:** v3.9 o superior.
* **Librerías:** `requests`, `python-dotenv`.
* **Token de Bot:** Obtenido a través de [@BotFather](https://t.me/botfather).

---

## 📂 Estructura del Proyecto

```text
DETECTOR_RED_PYTHON/
├── monitor_isp_telegram.py   # Lógica principal del monitor
├── get_chat_id.py            # Herramienta para extraer el ID de Telegram
├── .env                      # Variables de configuración (Privado)
├── .gitignore                # Exclusión de archivos sensibles
├── requirements.txt          # Dependencias del proyecto
└── README.md                 # Documentación técnica

```

---

## 🚀 Configuración e Instalación

### 1. Clonar e instalar dependencias

```bash
# Instalar las librerías necesarias
pip install requests python-dotenv

```

### 2. Configuración de Telegram (Bot)

1. Habla con **@BotFather** en Telegram y crea un nuevo bot con `/newbot`.
2. Guarda el **API Token** generado.
3. Crea un archivo `.env` en la raíz del proyecto:
```env
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_CHAT_ID=0

```



### 3. Obtener el CHAT_ID numérico

> **Nota:** Telegram requiere el ID numérico interno, no el nombre de usuario.

1. Busca tu bot en Telegram y envíale un mensaje inicial (ej. "Hola").
2. Ejecuta el script de utilidad:
```bash
python get_chat_id.py

```


3. Copia el ID numérico resultante y actualiza tu `.env`:
```env
TELEGRAM_CHAT_ID=123456789

```



---

## 📊 Estados del Monitoreo

| Estado | Indicador | Condición |
| --- | --- | --- |
| **UP** | ✅ Operativo | Latencia baja y resolución DNS exitosa. |
| **DEGRADED** | ⚠️ Degradado | Conectividad parcial o latencia mayor a 500ms. |
| **DOWN** | ❌ Caído | Pérdida total de paquetes o falla en resolución DNS. |

---

## 💻 Uso

Para iniciar el monitoreo en tiempo real, ejecuta:

```bash
python monitor_isp_telegram.py

```

### Ejemplo de salida en consola:

```text
🚀 Iniciando monitoreo ISP con Telegram
[2026-02-03 10:55] DNS=OK 15ms | HTTP 3/3 | avg=42ms -> ESTADO: UP
[2026-02-03 10:58] DNS=FAIL | HTTP 0/3 | avg=0ms -> ESTADO: DOWN
📨 Alerta de Telegram enviada con éxito.

```

---

## 🛡️ Notas de Seguridad

* **Archivo .gitignore:** Asegúrate de que el archivo `.env` nunca se suba a repositorios públicos para proteger tu Token de bot.
* **Firewalls:** En redes corporativas (como universidades), asegúrate de que el tráfico hacia la API de Telegram (`api.telegram.org`) esté permitido.

---

## 📝 Licencia

Desarrollado para uso académico y profesional. Libre de modificación para fines de mejora operativa.