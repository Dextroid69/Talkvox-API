# 🧠 Talkvox API - Transcripción y Resumen con IA

API gratuita que permite la transcripción de audios y generación de resúmenes usando **FasterWhisper** y **OpenRouter AI**.

---

## ⚙️ Tecnologías Usadas

- [FastAPI](https://fastapi.tiangolo.com/)
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper)
- [OpenRouter (DeepSeek)](https://openrouter.ai/)
- [pydub + ffmpeg] para soportar múltiples formatos (.mp3, .wav, .ogg, etc.)

---

## 🚀 Cómo desplegar en [Render](https://render.com)

1. Crea una cuenta gratuita en [Render.com](https://render.com)
2. Crea un nuevo **Web Service**
3. Conecta tu repositorio de GitHub
4. Elige:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
5. En "Advanced", marca `PYTHON_VERSION = 3.10` y agrega la variable de entorno:
   - `OPENROUTER_API_KEY = TU_API_KEY_DE_OPENROUTER`

---

## 📦 Estructura del Proyecto

```
.
├── main.py                 # Código principal de la API
├── requirements.txt        # Dependencias de Python
├── cache_db.json           # Almacenamiento de resultados para evitar reprocesos
├── uploads/                # Carpeta temporal para audios
```

---

## 📡 Endpoints Disponibles

| Método | Ruta         | Descripción                           |
|--------|--------------|----------------------------------------|
| GET    | `/ping`      | Verifica si el servicio está activo    |
| GET    | `/`          | Mensaje de bienvenida                  |
| POST   | `/transcribe`| Transcribe uno o varios archivos audio |

---

## 📤 Ejemplo de uso (con `curl`)

```bash
curl -X POST http://localhost:8000/transcribe \
  -F "files=@audio1.mp3" \
  -F "files=@audio2.ogg"
```

---

## 📌 Notas

- Asegúrate de tener `ffmpeg` instalado localmente para procesar formatos de audio.
- Soporta `.mp3`, `.ogg`, `.wav`, `.m4a`, entre otros.
- Utiliza caching interno con `SHA256` para evitar transcribir dos veces el mismo archivo.
- Máximo 10 archivos por llamada.

---

## 🧠 Créditos

Desarrollado por [Carlos - Talkvox]