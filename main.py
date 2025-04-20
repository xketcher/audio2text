from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import base64
import tempfile
import os
from pydub import AudioSegment
import speech_recognition as sr

app = FastAPI()

@app.post("/")
async def transcribe(request: Request):
    try:
        data = await request.json()
        lang = data.get("lang")
        content_base64 = data.get("content")

        if not lang or not content_base64:
            return JSONResponse(content={"error": "Missing 'lang' or 'content'"}, status_code=400)

        # Decode base64 to mp3
        audio_bytes = base64.b64decode(content_base64)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3_file:
            mp3_file.write(audio_bytes)
            mp3_path = mp3_file.name

        # Convert mp3 to wav
        wav_path = mp3_path.replace(".mp3", ".wav")
        sound = AudioSegment.from_mp3(mp3_path)
        sound.export(wav_path, format="wav")

        # Speech recognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio, language=lang)

        # Cleanup
        os.remove(mp3_path)
        os.remove(wav_path)

        return JSONResponse(content={"transcript": text})

    except sr.UnknownValueError:
        return JSONResponse(content={"error": "Speech unintelligible"}, status_code=400)
    except sr.RequestError as e:
        return JSONResponse(content={"error": f"Speech Recognition error: {e}"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
