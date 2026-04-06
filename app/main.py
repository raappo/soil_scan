from fastapi import FastAPI, UploadFile, File
import os

app = FastAPI()

# This tells the app where to find our folders
UPLOAD_DIR = "static/uploads"
RESULT_DIR = "static/results"

@app.get("/")
def read_root():
    return {
        "project": "soil_scan",
        "status": "online",
        "phase": 1,
        "message": "Ready for UV image analysis"
    }

@app.post("/test-upload")
async def test_upload(file: UploadFile = File(...)):
    # This is a temporary function to make sure our upload folder works
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}