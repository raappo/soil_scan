import cv2
import numpy as np
import os

def detect_microplastics(image_path, result_folder, px_per_mm=10):
    image = cv2.imread(image_path)
    if image is None:
        return None, 0, 0, 0, []

    # 1. Image Enhancement
    clean_img = cv2.medianBlur(image, 5)
    hsv = cv2.cvtColor(clean_img, cv2.COLOR_BGR2HSV)
    
    # 2. Dual-Mask Logic (Color + Brightness)
    lower_blue = np.array([90, 150, 50]) 
    upper_blue = np.array([135, 255, 255])
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    gray = cv2.cvtColor(clean_img, cv2.COLOR_BGR2GRAY)
    _, bright_mask = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY)
    final_mask = cv2.bitwise_and(blue_mask, bright_mask)

    # 3. Shape Consolidation
    kernel = np.ones((7, 7), np.uint8)
    final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_CLOSE, kernel)

    # 4. Analysis & Classification
    contours, _ = cv2.findContours(final_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    particles_data = []
    fiber_count = 0
    fragment_count = 0
    
    for cnt in contours:
        area_px = cv2.contourArea(cnt)
        if area_px > 15:
            x, y, w, h = cv2.boundingRect(cnt)
            
            # Classification Logic: Aspect Ratio
            aspect_ratio = max(w, h) / min(w, h)
            p_type = "Fiber" if aspect_ratio > 3.5 else "Fragment"
            
            if p_type == "Fiber": fiber_count += 1
            else: fragment_count += 1

            # Real-world sizing: Area in mm^2
            # Area_mm2 = Area_px / (px_per_mm^2)
            area_mm2 = round(area_px / (px_per_mm ** 2), 4)

            particles_data.append({
                "type": p_type,
                "area_mm2": area_mm2,
                "dimensions": f"{round(w/px_per_mm, 2)}x{round(h/px_per_mm, 2)}mm"
            })

            # Color coding: Fibers (Cyan), Fragments (Green)
            color = (255, 255, 0) if p_type == "Fiber" else (0, 255, 0)
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
            cv2.putText(image, p_type[0], (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    filename = os.path.basename(image_path)
    result_path = os.path.join(result_folder, f"pro_detect_{filename}")
    cv2.imwrite(result_path, image)

    return result_path, len(particles_data), fiber_count, fragment_count, particles_data