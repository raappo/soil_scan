from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from datetime import datetime
from app.detection import detect_microplastics
from app.database import init_db, save_scan, get_all_scans
from app.reporter import generate_pro_report

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="static"), name="static")

init_db()

UPLOAD_DIR, RESULT_DIR, PDF_DIR = "static/uploads", "static/results", "static/reports"
for d in [UPLOAD_DIR, RESULT_DIR, PDF_DIR]: os.makedirs(d, exist_ok=True)

def get_pro_advice(risk, fibers, fragments):
    advice = []
    if fibers > fragments:
        advice.append("Morphology Alert: Synthetic fibers dominate. Check nearby residential laundry outlets.")
    else:
        advice.append("Morphology Alert: Plastic fragments dominate. Check for degraded agricultural mulching.")
        
    if risk == "High":
        advice.append("Remediation: Implement phytoremediation with Vetiver grass for immediate capture.")
        advice.append("Policy: Restricted agricultural use advised for this specific coordinate.")
    else:
        advice.append("Monitoring: Soil health is stable. Maintain biennial UV screening.")
    return advice

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...), 
    weight_g: float = Form(...),
    lat: float = Form(None),
    lon: float = Form(None),
    px_mm: float = Form(10.0)
):
    path = os.path.join(UPLOAD_DIR, file.filename)
    
    # FIX: Read from the uploaded 'file' object
    file_content = await file.read()
    
    # FIX: Write content to the local 'buffer' handle
    with open(path, "wb") as buffer:
        buffer.write(file_content)

    res_path, count, fibers, fragments, details = detect_microplastics(path, RESULT_DIR, px_mm)
    conc = round((count / weight_g) * 1000, 2)
    risk = "High" if conc > 50 else "Medium" if conc > 10 else "Low"
    
    save_scan(file.filename, count, fibers, fragments, weight_g, conc, risk, lat, lon)

    return {
        "summary": {"total": count, "fibers": fibers, "fragments": fragments, "concentration": conc, "risk": risk},
        "suggestions": get_pro_advice(risk, fibers, fragments),
        "details": details,
        "image_url": f"http://127.0.0.1:8000/{res_path}",
        "filename": file.filename
    }

@app.get("/download-pdf/{filename}/{weight}/{count}/{fibers}/{fragments}/{lat}/{lon}")
async def download(filename: str, weight: float, count: int, fibers: int, fragments: int, lat: str, lon: str):
    conc = round((count / weight) * 1000, 2)
    risk = "High" if conc > 50 else "Medium" if conc > 10 else "Low"
    
    data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "weight_g": weight, "count": count, "fibers": fibers, "fragments": fragments,
        "concentration": conc, "risk": risk, "lat": lat, "lon": lon,
        "suggestions": get_pro_advice(risk, fibers, fragments)
    }
    
    out_path = os.path.join(PDF_DIR, f"Ultra_Report_{filename.split('.')[0]}.pdf")
    generate_pro_report(data, os.path.join(RESULT_DIR, f"pro_detect_{filename}"), out_path)
    return FileResponse(out_path, media_type='application/pdf')

@app.get("/history")
def history():
    # Index 9 and 10 are Latitude and Longitude in the scientific schema
    return {"history": [{
        "id": r[0], "date": r[1], "file": r[2], 
        "conc": r[7], "risk": r[8], "lat": r[9], "lon": r[10]
    } for r in get_all_scans()]}