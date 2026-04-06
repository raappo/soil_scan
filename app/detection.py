import cv2
import numpy as np
import os

def detect_microplastics(image_path, result_folder):
    image = cv2.imread(image_path)
    if image is None:
        return None, 0, []

    # 1. Standard Denoising
    clean_img = cv2.medianBlur(image, 5)
    hsv = cv2.cvtColor(clean_img, cv2.COLOR_BGR2HSV)
    
    # 2. Optimized Blue Mask (Targeting UV Glow)
    lower_blue = np.array([90, 150, 50]) 
    upper_blue = np.array([135, 255, 255])
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # 3. Brightness Mask (Filtering out dark soil)
    gray = cv2.cvtColor(clean_img, cv2.COLOR_BGR2GRAY)
    _, bright_mask = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
    final_mask = cv2.bitwise_and(blue_mask, bright_mask)

    # 4. Morphological Closing (Grouping fragments)
    kernel = np.ones((10, 10), np.uint8)
    final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_CLOSE, kernel)

    # 5. Find Contours
    contours, _ = cv2.findContours(final_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    particles_data = []
    count = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 15: 
            count += 1
            x, y, w, h = cv2.boundingRect(cnt)
            
            particles_data.append({
                "id": count,
                "area_px": round(area, 2),
                "width_px": w,
                "height_px": h
            })

            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(image, f"P-{count}", (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    filename = os.path.basename(image_path)
    result_path = os.path.join(result_folder, f"final_detection_{filename}")
    cv2.imwrite(result_path, image)

    return result_path, count, particles_data