import cv2
import numpy as np
import re
from typing import List, Dict, Any, Tuple

INDIAN_PLATE_REGEX = re.compile(r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$")

def assess_image_quality(plate_img: np.ndarray) -> Dict[str, Any]:
    """
    Computes an Image Quality Score (0-100) using OpenCV.
    Evaluates: Blur (Laplacian variance), Brightness, Contrast, Resolution.
    """
    if plate_img is None or plate_img.size == 0:
        return {"overall_quality": 0.0, "blur_score": 0.0, "needs_enhancement": True}

    gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY) if len(plate_img.shape) == 3 else plate_img

    # 1. Blur Metric (Variance of Laplacian)
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    blur_score = min(1.0, laplacian_var / 300.0)

    # 2. Brightness & Contrast
    mean_intensity = float(np.mean(gray))
    contrast_std = float(np.std(gray))
    brightness_score = max(0.0, 1.0 - abs(mean_intensity - 128.0) / 128.0)
    contrast_score = min(1.0, contrast_std / 64.0)

    # 3. Geometric Resolution
    h, w = gray.shape[:2]
    res_score = min(1.0, (w * h) / (120.0 * 40.0))

    overall = (0.35 * blur_score + 0.25 * contrast_score + 0.20 * brightness_score + 0.20 * res_score) * 100.0
    return {
        "overall_quality": round(overall, 1),
        "blur_score": round(blur_score, 2),
        "contrast_score": round(contrast_score, 2),
        "brightness_mean": round(mean_intensity, 1),
        "resolution": (w, h),
        "needs_enhancement": overall < 70.0
    }

def enhance_plate_crop(plate_img: np.ndarray, quality_info: Dict[str, Any]) -> np.ndarray:
    """
    Conditionally applies enhancement (CLAHE for low-light/contrast, sharpening for blur).
    """
    if plate_img is None or plate_img.size == 0:
        return plate_img

    gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY) if len(plate_img.shape) == 3 else plate_img

    # If low contrast or dark, apply CLAHE
    if quality_info.get("brightness_mean", 128) < 80 or quality_info.get("contrast_score", 1.0) < 0.4:
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

    # If blurred, apply unsharp masking kernel
    if quality_info.get("blur_score", 1.0) < 0.35:
        gaussian = cv2.GaussianBlur(gray, (0, 0), 2.0)
        gray = cv2.addWeighted(gray, 1.5, gaussian, -0.5, 0)

    return gray

def fuse_multiframe_reads(readings: List[Tuple[str, float, float]]) -> Tuple[str, float, str]:
    """
    Fuses plate character readings across multiple consecutive video frames.
    Input: List of (plate_text, confidence, quality_score)
    Output: (fused_plate_text, composite_confidence, observation_status)
    """
    if not readings:
        return "", 0.0, "UNREADABLE"

    # Filter out empty or unreadable
    valid = [r for r in readings if r[0] and r[0] != "UNKNOWN"]
    if not valid:
        return "", 0.0, "UNREADABLE"

    # Weight character frequencies across positions
    max_len = max(len(r[0]) for r in valid)
    fused_chars = []
    total_weights = []

    for pos in range(max_len):
        char_votes: Dict[str, float] = {}
        for text, conf, q in valid:
            if pos < len(text):
                c = text[pos].upper()
                weight = conf * (q / 100.0)
                char_votes[c] = char_votes.get(c, 0.0) + weight

        if char_votes:
            best_char = max(char_votes.items(), key=lambda x: x[1])
            fused_chars.append(best_char[0])
            total_weights.append(min(1.0, best_char[1]))
        else:
            fused_chars.append("?")
            total_weights.append(0.2)

    fused_text = "".join(fused_chars)
    avg_conf = sum(total_weights) / len(total_weights) if total_weights else 0.0

    # Format check
    clean_text = fused_text.replace("?", "")
    if avg_conf >= 0.85 and "?" not in fused_text:
        status = "CONFIRMED"
    elif avg_conf >= 0.50 or len(clean_text) >= 6:
        status = "PROBABLE"
    else:
        status = "UNREADABLE"

    return fused_text, round(avg_conf, 2), status
