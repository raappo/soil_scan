from fpdf import FPDF
import os

class ProSoilReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(40, 40, 120)
        self.cell(0, 15, "SOIL_SCAN: SCIENTIFIC ANALYSIS", ln=True, align="C")
        self.set_draw_color(40, 40, 120)
        self.line(10, 28, 200, 28)
        self.ln(10)

def generate_pro_report(data, image_path, output_path):
    pdf = ProSoilReport()
    pdf.add_page()
    
    # Section 1: Site Data
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "1. Sample Metadata", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Date: {data['date']}", ln=True)
    pdf.cell(0, 7, f"Location (GPS): {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}", ln=True)
    pdf.cell(0, 7, f"Soil Weight: {data['weight_g']}g", ln=True)
    pdf.ln(5)

    # Section 2: Characterization
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "2. Morphological Characterization", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Total Particles: {data['count']}", ln=True)
    pdf.cell(0, 7, f"- Fibers detected: {data['fibers']}", ln=True)
    pdf.cell(0, 7, f"- Fragments detected: {data['fragments']}", ln=True)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, f"Final Concentration: {data['concentration']} p/kg", ln=True)
    pdf.ln(5)

    # Risk Assessment
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 10, f"RISK LEVEL: {data['risk'].upper()}", ln=True, fill=True, align="C")
    pdf.ln(10)

    # Detection Visual
    pdf.image(image_path, x=15, w=180)
    
    # Suggestions
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "3. Targeted Remediation Advice", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for advice in data['suggestions']:
        pdf.multi_cell(0, 8, f"> {advice}")
        pdf.ln(2)

    pdf.output(output_path)