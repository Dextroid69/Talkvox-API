from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel
from openai import OpenAI
from pydub import AudioSegment
import os
import shutil
import uuid
import hashlib
import json

app = FastAPI()
model = WhisperModel("base", device="cpu", compute_type="int8")

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

UPLOAD_DIR = "uploads"
CACHE_FILE = "cache_db.json"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Cargar caché (simplemente como dict en disco)
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        cache = json.load(f)
else:
    cache = {}

def save_cache():
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

@app.get("/ping")
async def ping():
    return {"message": "pong"}

@app.get("/")
async def root():
    return {"message": "API Talkvox en línea 🚀"}

@app.post("/transcribe")
async def transcribe_audio(request: Request, files: list[UploadFile] = File(...)):
    results = []

    for file in files:
        try:
            # Hasheo único por nombre y tamaño
            hash_key = await file_to_hash(file)
            if hash_key in cache:
                print(f"⚡ Audio en caché: {file.filename}")
                results.append(cache[hash_key])
                continue

            # Convertir a WAV si es necesario
            temp_path = convert_to_wav(file)

            # Transcribir
            segments, _ = model.transcribe(temp_path, beam_size=7)
            transcription = ' '.join(segment.text for segment in segments)

            # Resumen
            summary = get_chat_response(transcription)

            # Resultado y caché
            result = {
                "filename": file.filename,
                "transcription": transcription,
                "summary": summary
            }
            results.append(result)
            cache[hash_key] = result
            save_cache()

            os.remove(temp_path)

        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })

    return results

def convert_to_wav(file: UploadFile) -> str:
    extension = file.filename.split(".")[-1].lower()
    raw_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.{extension}")
    wav_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.wav")

    with open(raw_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    sound = AudioSegment.from_file(raw_path)
    sound = sound.set_channels(1).set_frame_rate(16000)
    sound.export(wav_path, format="wav")
    os.remove(raw_path)
    return wav_path

async def file_to_hash(file: UploadFile) -> str:
    file.file.seek(0)
    content = await file.read()
    file.file.seek(0)
    return hashlib.sha256(content).hexdigest()

def get_chat_response(query, model="deepseek/deepseek-r1:free"):
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un experto en resumir. Resume la siguiente transcripción:"},
                {"role": "user", "content": query}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

