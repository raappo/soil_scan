from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.detection import detect_microplastics
from app.database import init_db, save_scan, get_all_scans

app = FastAPI()

# 1. ALLOW THE FRONTEND TO TALK TO THE BACKEND (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, we would limit this to our domain
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. SERVE THE STATIC IMAGES
# This allows the browser to see images at http://127.0.0.1:8000/static/...
app.mount("/static", StaticFiles(directory="static"), name="static")

init_db()

UPLOAD_DIR = "static/uploads"
RESULT_DIR = "static/results"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"project": "soil_scan", "status": "Frontend Ready"}

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...), weight_g: float = Form(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    result_path, count, particles = detect_microplastics(file_path, RESULT_DIR)
    concentration = round((count / weight_g) * 1000, 2)
    risk = "High" if concentration > 50 else "Medium" if concentration > 10 else "Low"

    save_scan(file.filename, count, weight_g, concentration, risk)

    return {
        "summary": {
            "total_particles": count,
            "concentration_p_kg": concentration,
            "risk_level": risk
        },
        # We return the URL path instead of the local system path
        "processed_image_url": f"http://127.0.0.1:8000/{result_path}"
    }

@app.get("/history")
def view_history():
    data = get_all_scans()
    history = []
    for row in data:
        history.append({
            "id": row[0],
            "date": row[1],
            "file": row[2],
            "count": row[3],
            "concentration": row[5],
            "risk": row[6],
            "image_url": f"http://127.0.0.1:8000/static/results/final_detection_{row[2]}"
        })
    return {"history": history}