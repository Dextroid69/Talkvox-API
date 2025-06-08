
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel
from openai import OpenAI
import os
import shutil
import uuid

app = FastAPI()
model = WhisperModel("base", device="cpu", compute_type="int8")

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/ping")
async def ping():
    return {"message": "pong"}

@app.get("/")
async def root():
    return {"message": "API Talkvox en línea 🚀"}

@app.post("/transcribe")
async def transcribe_audio(request: Request, file: UploadFile = File(None)):
    try:
        temp_filename = f"{uuid.uuid4()}.wav"
        temp_path = os.path.join(UPLOAD_DIR, temp_filename)

        if file:
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            print("Archivo recibido como multipart/form-data")
        else:
            body = await request.body()
            with open(temp_path, "wb") as f:
                f.write(body)
            print("Archivo recibido como audio/wav crudo")

        segments, _ = model.transcribe(temp_path, beam_size=7)
        transcription = ' '.join(segment.text for segment in segments)

        # Generar resumen usando modelo gratuito de OpenRouter
        summary = get_chat_response(transcription)

        os.remove(temp_path)

        return {
            "transcription": transcription,
            "summary": summary
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

def get_chat_response(query, model="deepseek/deepseek-r1:free"):
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un experto en resumir. Resume la siguiente transcripción.:"},
                {"role": "user", "content": query}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
