from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from datetime import datetime
from app.detection import detect_microplastics
from app.database import init_db, save_scan, get_all_scans
from app.reporter import generate_pdf_report 

app = FastAPI()

# Enable CORS for Frontend communication
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Serve images so the dashboard can display them
app.mount("/static", StaticFiles(directory="static"), name="static")

init_db()

UPLOAD_DIR = "static/uploads"
RESULT_DIR = "static/results"
PDF_DIR = "static/reports"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

def get_suggestions(risk):
    if risk == "High":
        return [
            "Implement phytoremediation (Alfalfa/Vetiver).",
            "Audit irrigation for synthetic fiber runoff.",
            "Apply biochar to stabilize soil structure."
        ]
    return ["Maintain routine monitoring.", "Avoid plastic-based mulching."]

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...), weight_g: float = Form(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    res_path, count, particles = detect_microplastics(file_path, RESULT_DIR)
    concentration = round((count / weight_g) * 1000, 2)
    risk = "High" if concentration > 50 else "Medium" if concentration > 10 else "Low"
    
    save_scan(file.filename, count, weight_g, concentration, risk)

    return {
        "summary": {
            "total_particles": count, 
            "concentration_p_kg": concentration, 
            "risk_level": risk,
            "suggestions": get_suggestions(risk)
        },
        "details": particles,
        "processed_image_url": f"http://127.0.0.1:8000/{res_path}",
        "filename": file.filename
    }

@app.get("/download-pdf/{filename}/{weight}/{count}")
async def get_pdf(filename: str, weight: float, count: int):
    concentration = round((count / weight) * 1000, 2)
    risk = "High" if concentration > 50 else "Medium" if concentration > 10 else "Low"
    
    report_data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "weight_g": weight,
        "count": count,
        "concentration": concentration,
        "risk": risk,
        "suggestions": get_suggestions(risk)
    }
    
    image_path = os.path.join(RESULT_DIR, f"final_detection_{filename}")
    pdf_filename = f"Report_{filename.split('.')[0]}.pdf"
    pdf_path = os.path.join(PDF_DIR, pdf_filename)
    
    generate_pdf_report(report_data, image_path, pdf_path)
    
    return FileResponse(pdf_path, media_type='application/pdf', filename=pdf_filename)

@app.get("/history")
def view_history():
    data = get_all_scans()
    return {"history": [{
        "id": r[0], 
        "date": r[1], 
        "file": r[2], 
        "count": r[3], 
        "weight": r[4], 
        "concentration": r[5], 
        "risk": r[6], 
        "image_url": f"http://127.0.0.1:8000/static/results/final_detection_{r[2]}"
    } for r in data]}