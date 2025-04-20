from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydub import AudioSegment
import speech_recognition as sr
import os
import uuid

app = FastAPI()

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    # Save uploaded file
    temp_filename = f"{uuid.uuid4()}.m4a"
    with open(temp_filename, "wb") as f:
        f.write(await file.read())

    # Convert m4a to wav using pydub
    audio = AudioSegment.from_file(temp_filename, format="m4a")
    wav_filename = temp_filename.replace(".m4a", ".wav")
    audio.export(wav_filename, format="wav")

    # Recognize speech using SpeechRecognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_filename) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            text = "Could not understand audio"
        except sr.RequestError as e:
            text = f"API Error: {e}"

    # Clean up
    os.remove(temp_filename)
    os.remove(wav_filename)

    return JSONResponse(content={"transcription": text})
