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

    with sr.AudioFile(wav_filename) as source:
        audio_length = int(source.DURATION)
        chunk_duration = 60  # seconds
        offset = 0

        while offset < audio_length:
            try:
                audio_data = recognizer.record(source, duration=chunk_duration)
                text = recognizer.recognize_google(audio_data, language="my-MM")
            except sr.UnknownValueError:
                text = "[Unrecognized]"
            except sr.RequestError as e:
                text = f"[API Error: {e}]"
                break  # Stop if there's a serious error

            full_transcript += text + " "
            offset += chunk_duration

    # Clean up
    os.remove(temp_filename)
    os.remove(wav_filename)

    return JSONResponse(content={"transcription": full_transcript.strip()})
