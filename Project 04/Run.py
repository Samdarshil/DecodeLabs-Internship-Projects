#!/usr/bin/env python3
"""
project4_decodelabs.py
=======================
DecodeLabs Project 4 — Image / Text Recognition (Basic)

Path selected: PATH 1 — OCR (pytesseract + OpenCV)

This script implements a full Optical Character Recognition pipeline:
  1. Load an image (local file OR public URL)
  2. Preprocess it (grayscale -> Gaussian blur -> deskew -> adaptive threshold)
  3. Run Tesseract OCR with PSM 6 -> PSM 3 fallback
  4. Filter results using an 80% confidence threshold
  5. Print a structured report and save the preprocessed binary image

Usage:
    python project4_decodelabs.py --input image.jpg
    python project4_decodelabs.py --input https://example.com/image.jpg

Author: DecodeLabs Internship Program — Project 4
"""

from __future__ import annotations

import sys
import time
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union
from colorama import Fore, Style, init


# ─────────────────────────────────────────────────────────────────────────────
# VALIDATION 1 — LIBRARY INTEGRATION
# Every optional dependency is imported defensively. If anything is missing,
# we print exact install commands (and OS-specific Tesseract instructions)
# and exit cleanly — never with a raw ImportError traceback.
# ─────────────────────────────────────────────────────────────────────────────

init(autoreset=True)
_MISSING: List[Tuple[str, str]] = []

try:
    import numpy as np
except ImportError:
    _MISSING.append(("numpy", "pip install numpy"))

try:
    import cv2
except ImportError:
    _MISSING.append(("opencv-python", "pip install opencv-python"))

try:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    
except ImportError:
    _MISSING.append(("pytesseract", "pip install pytesseract"))

try:
    from PIL import Image  # noqa: F401  (kept for completeness / future use)
except ImportError:
    _MISSING.append(("Pillow", "pip install Pillow"))

try:
    import requests
except ImportError:
    _MISSING.append(("requests", "pip install requests"))


def _print_tesseract_install_guide() -> None:
    """Print OS-specific instructions for installing the Tesseract OCR engine."""
    print()
    print("Tesseract OCR engine (separate from the 'pytesseract' Python package):")
    print("  Windows : Download installer from")
    print("            https://github.com/UB-Mannheim/tesseract/wiki")
    print("            or, with Chocolatey:  choco install tesseract")
    print("  macOS   : brew install tesseract")
    print("  Linux   : sudo apt-get update && sudo apt-get install -y tesseract-ocr")


if _MISSING:
    print("[ERROR] Missing required Python dependencies:")
    for name, cmd in _MISSING:
        print(f"  - {name:<15} -> {cmd}")
    _print_tesseract_install_guide()
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# DATA MODEL
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Prediction:
    """
    A single OCR (or detection) prediction.

    Attributes:
        label: The recognised word (or object class label).
        confidence: Model confidence in the range [0.0, 1.0].
        bbox: Bounding box as (x, y, w, h) in pixel coordinates, or None.
        text: Recognised text for this prediction (OCR path), or None.
    """
    label: str
    confidence: float
    bbox: Optional[Tuple[int, int, int, int]]
    text: Optional[str]


# ─────────────────────────────────────────────────────────────────────────────
# SOFTMAX & CONFIDENCE EXPLANATION
# ─────────────────────────────────────────────────────────────────────────────
"""
AI MODELS DO NOT "UNDERSTAND" OBJECTS OR TEXT.
================================================
- Predictions are statistical estimates from a Softmax-like probability
  distribution over possible characters/words.
- Confidence = probability the model assigns to its top prediction.
- Higher confidence != guaranteed correctness.
- The 80% threshold reduces low-quality predictions.
- Confidence filtering helps reduce hallucinations and false positives.
- If no prediction reaches 80%, the model is uncertain -> respect that.
- Never display low-confidence outputs to end users.

Source: DecodeLabs Project 4 - The 80% Threshold Rule
"""


# ─────────────────────────────────────────────────────────────────────────────
# STEP-BY-STEP REQUIRED FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def load_image(source: Union[str, Path]) -> np.ndarray:
    """
    Load an image from a local file path or a public HTTP(S) URL.

    Args:
        source: Local filesystem path, or an http:// / https:// URL.

    Returns:
        Loaded image as a BGR NumPy array (OpenCV convention).

    Raises:
        SystemExit: If the source is invalid, the download fails, the file
            is missing, or the image data cannot be decoded.
    """
    source_str = str(source)

    # ── URL input ────────────────────────────────────────────────────────────
    if source_str.startswith("http://") or source_str.startswith("https://"):
        print(f"[INFO] Loading image from URL: {source_str}")

        try:
            response = requests.get(source_str, timeout=15)
        except requests.exceptions.ConnectionError:
            print(f"[ERROR] Failed to download: {source_str}")
            print("[ERROR] Connection error — no internet access or host unreachable.")
            print("        Please download the image manually and run:")
            print("        python project4_decodelabs.py --input <local_image_path>")
            sys.exit(1)
        except requests.exceptions.Timeout:
            print(f"[ERROR] Failed to download: {source_str}")
            print("[ERROR] Request timed out after 15 seconds.")
            sys.exit(1)
        except requests.exceptions.RequestException as exc:
            print(f"[ERROR] Failed to download: {source_str}")
            print(f"[ERROR] {exc}")
            sys.exit(1)

        # Verify download success (status code 200)
        if response.status_code != 200:
            print(f"[ERROR] Failed to download: {source_str}")
            print(f"[ERROR] HTTP status code: {response.status_code}")
            print("        Please check the URL or download the image manually.")
            sys.exit(1)

        content = response.content

        # Verify file size > 0 bytes
        if len(content) == 0:
            print(f"[ERROR] Failed to download: {source_str}")
            print("[ERROR] Downloaded file is empty (0 bytes).")
            sys.exit(1)

        print(f"[INFO] Downloaded {len(content)} bytes (HTTP {response.status_code})")

        # Decode bytes -> NumPy array -> image
        file_bytes = np.frombuffer(content, dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if image is None:
            print("[ERROR] Cannot decode image")
            print(f"        {len(content)} bytes were downloaded from the URL, "
                  f"but OpenCV could not decode them as an image.")
            sys.exit(1)

        return image

    # ── Local file input ────────────────────────────────────────────────────
    path = Path(source_str)

    if not path.exists():
        print(f"[ERROR] File not found: {source_str}")
        sys.exit(1)

    if not path.is_file():
        print(f"[ERROR] File not found: {source_str}")
        print("        (Path exists but is not a regular file.)")
        sys.exit(1)

    print(f"[INFO] Loading image: {source_str}")

    image = cv2.imread(str(path), cv2.IMREAD_COLOR)

    if image is None:
        print("[ERROR] Cannot decode image")
        print(f"        The file exists but could not be read as an image: {source_str}")
        print("        Supported formats include JPG, PNG, BMP, TIFF.")
        sys.exit(1)

    return image


def deskew_image(image: np.ndarray) -> np.ndarray:
    """
    Detect and correct rotational skew in a single-channel image.

    The skew angle is estimated from the minimum-area bounding rectangle
    (`cv2.minAreaRect`) of all foreground (text) pixels after Otsu
    thresholding. If the detected angle is smaller than 0.5 degrees,
    rotation is skipped (the image is considered already aligned).

    Args:
        image: Single-channel (grayscale) image as a NumPy array.

    Returns:
        The deskewed image, or the original image if rotation was skipped
        or angle detection failed.
    """
    try:
        # Binarize purely for angle detection (Otsu finds a global threshold).
        _, otsu = cv2.threshold(
            image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
        )

        coords = np.column_stack(np.where(otsu > 0))

        if coords.size == 0:
            print("[INFO] Deskewing skipped: no foreground pixels detected")
            return image

        angle = cv2.minAreaRect(coords)[-1]

        # cv2.minAreaRect returns angles in [-90, 0); normalise to a
        # human-readable rotation angle in [-45, 45].
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # Skip negligible rotations
        if abs(angle) < 0.5:
            print("[INFO] Deskewing skipped: angle negligible")
            return image

        # Apply rotation correction
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image,
            rotation_matrix,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )

        print(f"[INFO] Step 3: Deskewing (angle: {angle:.1f} deg) -> applying correction")
        return rotated

    except cv2.error as exc:
        print(f"[WARNING] Deskewing failed ({exc}); using original orientation.")
        return image


def preprocess_image(image: np.ndarray) -> np.ndarray:
    """
    Run the required 4-step preprocessing pipeline, in exact order:

        1. Grayscale conversion
        2. Gaussian blur (kernel 5x5)
        3. Deskewing (rotation correction with angle detection)
        4. Adaptive thresholding

    Args:
        image: Input image as a BGR or grayscale NumPy array.

    Returns:
        A single-channel binary (0/255) image ready for OCR.

    Raises:
        SystemExit: If the input image is empty or has an unsupported shape.
    """
    if image is None or image.size == 0:
        print("[ERROR] Cannot decode image")
        print("        Preprocessing received an empty image array.")
        sys.exit(1)

    # ── Step 1: Grayscale conversion ────────────────────────────────────────
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif len(image.shape) == 2:
        gray = image.copy()
    else:
        print(f"[ERROR] Unsupported image shape: {image.shape}")
        sys.exit(1)
    print("[INFO] Step 1: Grayscale conversion")

    # ── Step 2: Gaussian blur (kernel 5x5) ──────────────────────────────────
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    print("[INFO] Step 2: Gaussian blur (kernel 5x5)")

    # ── Step 3: Deskewing (rotation correction with angle detection) ───────
    deskewed = deskew_image(blurred)

    # ── Step 4: Adaptive thresholding ───────────────────────────────────────
    binary = cv2.adaptiveThreshold(
        deskewed,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2,
    )
    print("[INFO] Step 4: Adaptive thresholding")

    return binary


def _extract_predictions(ocr_data: dict) -> List[Prediction]:
    """
    Convert raw `pytesseract.image_to_data` output into Prediction objects.

    Args:
        ocr_data: Dictionary returned by
            `pytesseract.image_to_data(..., output_type=Output.DICT)`.

    Returns:
        List of Prediction objects, one per non-empty recognised word,
        in original reading order. Confidence is normalised to [0.0, 1.0].
    """
    predictions: List[Prediction] = []
    n_boxes = len(ocr_data.get("text", []))

    for i in range(n_boxes):
        word = ocr_data["text"][i].strip()
        try:
            raw_conf = float(ocr_data["conf"][i])
        except (ValueError, TypeError):
            raw_conf = -1.0

        # Tesseract uses -1 for boxes with no recognised text
        if word == "" or raw_conf < 0:
            continue

        bbox = (
            int(ocr_data["left"][i]),
            int(ocr_data["top"][i]),
            int(ocr_data["width"][i]),
            int(ocr_data["height"][i]),
        )

        predictions.append(
            Prediction(
                label=word,
                confidence=raw_conf / 100.0,
                bbox=bbox,
                text=word,
            )
        )

    return predictions


def run_inference(preprocessed_image: np.ndarray) -> List[Prediction]:
    """
    Run Tesseract OCR on a preprocessed binary image, with PSM fallback.

    Strategy:
        1. Attempt OCR with `--psm 6 --oem 3` (assumes a single uniform
           block of text — ideal for documents/receipts).
        2. If the resulting text is shorter than 10 characters, retry with
           `--psm 3 --oem 3` (fully automatic page segmentation).

    Args:
        preprocessed_image: Single-channel binary image from
            `preprocess_image`.

    Returns:
        List of Prediction objects for every word Tesseract detected
        (including those below the confidence threshold — filtering
        happens separately in `filter_results`).

    Raises:
        SystemExit: If the Tesseract OCR engine binary is not found on PATH.
    """
    start_time = time.perf_counter()

    try:
        data = pytesseract.image_to_data(
            preprocessed_image,
            config="--psm 6 --oem 3",
            output_type=pytesseract.Output.DICT,
        )
    except pytesseract.TesseractNotFoundError:
        print("[ERROR] Tesseract OCR engine not found on PATH.")
        _print_tesseract_install_guide()
        sys.exit(1)

    predictions = _extract_predictions(data)
    combined_text = " ".join(p.text for p in predictions)

    psm_used = 6
    if len(combined_text.strip()) < 10:
        print("[INFO] Falling back to PSM 3")
        data = pytesseract.image_to_data(
            preprocessed_image,
            config="--psm 3 --oem 3",
            output_type=pytesseract.Output.DICT,
        )
        predictions = _extract_predictions(data)
        psm_used = 3
    else:
        print("[INFO] Using PSM mode: 6")

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    print(f"[INFO] Inference time: {elapsed_ms:.1f} ms")

    return predictions


def filter_results(
    predictions: List[Prediction], threshold: float = 0.80
) -> List[Prediction]:
    """
    Filter predictions, keeping only those with confidence >= threshold.

    Every rejected prediction is logged with a `[DROPPED]` message and is
    never included in the returned list or in any displayed output.

    Args:
        predictions: List of raw Prediction objects.
        threshold: Minimum confidence (0.0-1.0) required to keep a
            prediction. Defaults to 0.80 (the DecodeLabs 80% rule).

    Returns:
        List of accepted Prediction objects (confidence >= threshold),
        preserving original order.
    """
    accepted: List[Prediction] = []

    for pred in predictions:
        if pred.confidence >= threshold:
            accepted.append(pred)
        else:
            print(f"[DROPPED] Word '{pred.label}' confidence {pred.confidence * 100:.1f}%")

    return accepted


def save_outputs(
    image: np.ndarray, predictions: List[Prediction], output_path: str
) -> None:
    """
    Save the preprocessed binary image to disk for visual confirmation.

    Args:
        image: The preprocessed (binary) image to save.
        predictions: Accepted predictions (currently unused for the OCR
            path's image output, but kept for signature consistency with
            the Object Detection path and future annotation features).
        output_path: Destination file path, e.g. "preprocessed_binary.png".

    Returns:
        None. Logs success or failure to the console.
    """
    del predictions  # Not drawn onto the OCR output image — see docstring.

    try:
        success = cv2.imwrite(output_path, image)
    except cv2.error as exc:
        print(f"[ERROR] Failed to save output image: {exc}")
        return

    if not success:
        print(f"[ERROR] Failed to save output image: {output_path}")
        return

    success_message(f"Output saved -> {output_path}")


def print_banner() -> None:
    print(Fore.CYAN + Style.BRIGHT + r"""
═══════════════════════════════════════════════════════════════
                                                                                                                                                                                                                                                                    
      🔍 DECODELABS OCR RECOGNITION SYSTEM 🔍                                                                                                                                                                                          
                                                                                                                                                                                                                                                                        
         Project 4 — Image & Text Recognition                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                         
                    👨‍💻 Author: Darshil                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                         
     "Turning pixels into meaningful information."                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                         
════════════════════════════════════════════════════════════════
""")


def section(title: str) -> None:
    print("\n" + Fore.YELLOW + Style.BRIGHT + "═" * 70)
    print(Fore.YELLOW + Style.BRIGHT + f"  {title}")
    print(Fore.YELLOW + Style.BRIGHT + "═" * 70)


def success_message(msg: str) -> None:
    print(Fore.GREEN + f"✅ {msg}")


def info_message(msg: str) -> None:
    print(Fore.CYAN + f"ℹ️ {msg}")
# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """
    Entry point: parse CLI arguments and run the full OCR pipeline.

    Pipeline stages:
        1. Load image (local path or URL)
        2. Preprocess (grayscale -> blur -> deskew -> threshold)
        3. Run OCR inference (PSM 6 -> PSM 3 fallback)
        4. Log first 3 raw predictions as [DEBUG]
        5. Filter by 80% confidence threshold
        6. Print results summary and extracted text
        7. Save preprocessed_binary.png

    Returns:
        None. Exits with status 1 on any unrecoverable error.
    """
    parser = argparse.ArgumentParser(
        description="DecodeLabs Project 4 — OCR Text Recognition (pytesseract + OpenCV)"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a local image file (JPG/PNG) or an http(s):// image URL",
    )
    parser.add_argument(
        "--output",
        default="preprocessed_binary.png",
        help="Output path for the preprocessed binary image (default: preprocessed_binary.png)",
    )
    args = parser.parse_args()

    print_banner()

    section("OCR PIPELINE INITIALIZATION")

    info_message(f"Input Source : {args.input}")

    # — Step 1-2: Load image —
    image = load_image(args.input)

    section("PREPROCESSING PIPELINE")

    # ── Step 3: Preprocess (grayscale -> blur -> deskew -> threshold) ──────
    try:
        preprocessed = preprocess_image(image)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 — convert to clean [ERROR] message
        print(f"[ERROR] Preprocessing failed: {exc}")
        sys.exit(1)

    # ── Step 4-5: Run inference, extract raw confidence values ─────────────
    try:
        section("OCR ENGINE")
        raw_predictions = run_inference(preprocessed)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] OCR inference failed: {exc}")
        sys.exit(1)

    # ── No text detected at all ─────────────────────────────────────────────
    if not raw_predictions:
        print("[WARNING] No text detected")
        print("          Suggestions: increase image contrast, verify the")
        print("          image resolution (300 DPI recommended for scans),")
        print("          or try a different PSM mode.")
        save_outputs(preprocessed, [], args.output)
        print("=======================================")
        return

    # ── Step 6: Log first 3 raw predictions with [DEBUG] tag ────────────────
    for i, pred in enumerate(raw_predictions[:3], start=1):
        pct = pred.confidence * 100.0
        suffix = " -> dropped" if pred.confidence < 0.80 else ""
        print(f"[DEBUG] Raw prediction {i}: '{pred.label}' ({pct:.0f}%){suffix}")

    # ── Step 7: Filter results (>= 80% confidence) ──────────────────────────
    accepted = filter_results(raw_predictions, threshold=0.80)
    rejected_count = len(raw_predictions) - len(accepted)

    # ── No predictions met the threshold ────────────────────────────────────
    if not accepted:
        print("[WARNING] No predictions met the confidence threshold (>=80%)")
        top_raw = sorted(raw_predictions, key=lambda p: p.confidence, reverse=True)[:3]
        for pred in top_raw:
            print(f"[DEBUG] Top raw score: '{pred.label}' ({pred.confidence * 100:.1f}%)")
        save_outputs(preprocessed, accepted, args.output)
        print("=======================================")
        return

    # ── Step 9: Generate final output ───────────────────────────────────────
    confidences = [p.confidence for p in accepted]
    avg_confidence = sum(confidences) / len(confidences) * 100.0
    max_confidence = max(confidences) * 100.0
    extracted_text = " ".join(p.text for p in accepted if p.text)

    section("RECOGNITION STATISTICS")
    
    print(Fore.GREEN + f"🎯 Average Confidence : {avg_confidence:.1f}%")
    print(Fore.GREEN + f"🏆 Maximum Confidence : {max_confidence:.1f}%")
    print(Fore.GREEN + f"✅ Accepted Words     : {len(accepted)}")
    print(Fore.YELLOW + f"🚫 Rejected Words     : {rejected_count}")

    section("EXTRACTED TEXT")

    print(Fore.WHITE + Style.BRIGHT)
    print(extracted_text)

    save_outputs(preprocessed, accepted, args.output)

    section("EXECUTION SUMMARY")

    success_message("OCR Pipeline Completed Successfully")
    success_message("Confidence Threshold Applied (80%)")
    success_message("Visual Output Generated")

    print(Fore.CYAN + Style.BRIGHT)
    print("🚀 Status : PASS")
    print("📄 DecodeLabs Project 4 Complete")
    print("🔥 Ready for GitHub Submission")





if __name__ == "__main__":
    main()
