from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import whisper
import os
import uuid

app = FastAPI()
model = whisper.load_model("base")  # use "small" or "medium" if better accuracy needed

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    temp_filename = f"{uuid.uuid4()}.m4a"
    with open(temp_filename, "wb") as f:
        f.write(await file.read())

    # Run Whisper transcription
    result = model.transcribe(temp_filename, language="my")
    os.remove(temp_filename)

    return JSONResponse(content={"transcription": result["text"]})
