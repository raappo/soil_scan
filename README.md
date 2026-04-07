🔬 SOIL_SCAN ULTRAScientific UV Microplastic Characterization & Geospatial Analysis System

SOIL_SCAN Ultra is a professional-grade environmental tool designed to detect, classify, and analyze microplastic concentrations in soil samples using UV fluorescence imaging. The system utilizes computer vision to distinguish between different types of plastic morphology, tracks pollution trends over time, and generates detailed scientific PDF reports with geospatial tagging.

🌟 Key Features
- **Morphological Classification:** Automatically distinguishes between Fibers (textile runoff) and Fragments (degraded plastic waste) using aspect-ratio analysis.
- **Scientific Calibration:** Converts pixel-based detection into real-world units ($mm^2$) for precise physical characterization.
- **Geospatial Tracking:** Integrated with Leaflet.js to map sample locations via GPS coordinates, allowing for regional pollution heatmapping.
- **Advanced Analytics:** Visualizes concentration trends using Recharts and provides a detailed breakdown of particle types.
- **Automated Expert System:** Provides targeted remediation suggestions based on the specific type and severity of detected pollution.
- **Professional Reporting:** Generates multi-page PDF dossiers including UV detection visuals, statistical summaries, and remediation advice.

🛠️ Tech Stack
**Backend**
- Python (FastAPI): High-performance API framework.
- OpenCV: Core image processing and computer vision engine.
- SQLite: Lightweight database for longitudinal data storage.
- FPDF2: Professional PDF document generation.

**Frontend**
- React (Vite): Fast, modern web interface.
- Tailwind CSS 4: Utility-first styling for a professional dashboard.
- Recharts: Interactive data visualization.
- Leaflet.js: Geospatial mapping and site tracking.

📂 Project Directory Structure
```plaintext
soil_scan/
├── app/                  # Backend Logic
│   ├── main.py           # API Endpoints & Coordination
│   ├── detection.py      # Vision Engine & Classification
│   ├── database.py       # SQLite Schema & Persistence
│   ├── reporter.py       # PDF Report Generation
│   └── __init__.py       # Package Initialization
├── frontend/             # React Application
│   ├── src/
│   │   ├── App.jsx       # Main Dashboard UI
│   │   ├── index.css     # Tailwind Imports
│   │   └── main.jsx      # React Entry Point
│   └── vite.config.js    # Build Configuration
├── static/               # File Storage
│   ├── uploads/          # Original UV Scans
│   ├── results/          # AI Processed Images
│   └── reports/          # Generated PDF Dossiers
├── requirements.txt      # Python Dependencies
├── soil_scan.db          # SQLite Database (Auto-generated)
└── .gitignore            # Git exclusion rules
```

🚀 Installation & Setup

**Prerequisites**
- linux or windows 
- Python 3.10+
- Node.js 20+ & npm

1. **Backend Setup**

Navigate to the root directory and set up the Python environment:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn opencv-python numpy fpdf2 python-multipart
```

2. **Frontend Setup**

Navigate to the frontend folder and install dependencies:

```bash
cd frontend
npm install
npm install axios lucide-react recharts react-leaflet leaflet @tailwindcss/vite
```

🏃 Running the Application

**Start the Backend (Terminal 1)**

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

The API will be live at: http://127.0.0.1:8000.  
Interactive API docs: http://127.0.0.1:8000/docs.

**Start the Frontend (Terminal 2)**

```bash
cd frontend
npm run dev
```

The dashboard will be live at the URL provided by Vite (typically http://localhost:5173).

📝 Usage Guide
- **Upload:** Select a high-contrast UV image of a soil sample.
- **Parameters:** Enter the soil weight in grams to calculate concentration ($p/kg$).
- **Analyze:** Click "Run Pro Analysis." The AI will box fibers in Cyan and fragments in Green.
- **Visualize:** Check the "Site Map" tab to see the geospatial distribution of your samples.
- **Export:** Click "Generate Scientific PDF" to download the full dossier.

⚠️ Troubleshooting
- **Database Reset:** If you encounter an IndexError, delete the soil_scan.db file and restart the backend to update the schema.
- **CORS Issues:** Ensure the allow_origins in main.py matches your frontend URL.
- **GPS Access:** Ensure browser location permissions are enabled for mapping features.
