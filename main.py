from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydub import AudioSegment
import speech_recognition as sr
import os
import uuid

app = FastAPI()

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    temp_id = str(uuid.uuid4())
    temp_filename = f"{temp_id}.m4a"
    with open(temp_filename, "wb") as f:
        f.write(await file.read())

    # Convert to wav
    audio = AudioSegment.from_file(temp_filename, format="m4a")
    os.remove(temp_filename)  # remove m4a after conversion

    chunk_length_ms = 60000  # 60 seconds
    chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

    recognizer = sr.Recognizer()
    transcript = ""

    for i, chunk in enumerate(chunks):
        chunk_filename = f"{temp_id}_chunk{i}.wav"
        chunk.export(chunk_filename, format="wav")

        with sr.AudioFile(chunk_filename) as source:
            audio_data = recognizer.record(source)

            try:
                text = recognizer.recognize_google(audio_data, language="my-MM")
            except sr.UnknownValueError:
                text = "[မသိသာတဲ့အသံ]"
            except sr.RequestError as e:
                text = f"[API error: {e}]"
                break

            transcript += text + " "

        os.remove(chunk_filename)

    return JSONResponse(content={"transcription": transcript.strip()})
