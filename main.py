from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydub import AudioSegment
import speech_recognition as sr
import os
import uuid

app = FastAPI()

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    temp_filename = f"{uuid.uuid4()}.m4a"
    with open(temp_filename, "wb") as f:
        f.write(await file.read())

    # Convert to wav
    audio = AudioSegment.from_file(temp_filename, format="m4a")
    wav_filename = temp_filename.replace(".m4a", ".wav")
    audio.export(wav_filename, format="wav")

    recognizer = sr.Recognizer()
    full_transcript = ""

    # Get duration from pydub
    duration_seconds = int(audio.duration_seconds)
    chunk_duration = 60  # seconds
    offset = 0

    with sr.AudioFile(wav_filename) as source:
        while offset < duration_seconds:
            try:
                audio_data = recognizer.record(source, offset=offset, duration=chunk_duration)
                text = recognizer.recognize_google(audio_data, language="my-MM")
            except sr.UnknownValueError:
                text = "[မသိသာတဲ့အသံ]"
            except sr.RequestError as e:
                text = f"[API error: {e}]"
                break

            full_transcript += text + " "
            offset += chunk_duration

    os.remove(temp_filename)
    os.remove(wav_filename)

    return JSONResponse(content={"transcription": full_transcript.strip()})
