# 🔍 DecodeLabs Project 4 – OCR Text Recognition System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-Image%20Processing-green)
![Tesseract](https://img.shields.io/badge/Tesseract-OCR-orange)
![Status](https://img.shields.io/badge/Status-Completed-success)

---

## 📖 Overview

This project implements a complete **Optical Character Recognition (OCR)** pipeline using **OpenCV** and **Tesseract OCR**.

The system accepts an image from a local file or URL, performs multiple preprocessing operations to improve text readability, and extracts text using a pre-trained OCR engine. To improve reliability, only predictions with a confidence score of **80% or higher** are displayed.

---

## ✨ Features

✅ Image loading from local files and URLs

✅ Grayscale conversion

✅ Gaussian blur noise reduction

✅ Automatic deskewing (rotation correction)

✅ Adaptive thresholding

✅ Tesseract OCR integration

✅ Confidence-based filtering (80% threshold)

✅ Detailed logging and error handling

✅ Command-line execution support

✅ Processed image export for verification

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|----------|
| Python 3.8+ | Core Programming Language |
| OpenCV | Image Processing |
| NumPy | Numerical Operations |
| Tesseract OCR | Text Recognition |
| Requests | URL Image Handling |
| Pillow | Image Support |

---

## 📂 Project Structure

```text
Project-4-OCR/
│
├── project4_decodelabs.py
├── sample_document.png
├── sample_document_skewed.png
├── preprocessed_binary.png
├── README.md
└── requirements.txt
```

---

## ⚙️ Installation

### 1️⃣ Install Python Dependencies

```bash
pip install opencv-python numpy pytesseract pillow requests
```

### 2️⃣ Install Tesseract OCR

#### Windows

Download from:

https://github.com/UB-Mannheim/tesseract/wiki

Or install using Chocolatey:

```bash
choco install tesseract
```

#### macOS

```bash
brew install tesseract
```

#### Linux

```bash
sudo apt update
sudo apt install tesseract-ocr
```

---

## 🚀 Usage

### Local Image

```bash
python project4_decodelabs.py --input sample_document.png
```

### Image from URL

```bash
python project4_decodelabs.py --input https://example.com/image.jpg
```

---

## 🔄 OCR Processing Pipeline

The image passes through the following preprocessing stages:

### 1️⃣ Grayscale Conversion
Converts the image into a single-channel format suitable for OCR.

### 2️⃣ Gaussian Blur
Reduces image noise and smooths edges.

### 3️⃣ Deskewing
Automatically detects and corrects rotation for improved text alignment.

### 4️⃣ Adaptive Thresholding
Produces a high-contrast binary image optimized for text extraction.

---

## 🎯 Confidence Filtering

The OCR engine returns confidence scores for each recognized word.

Only words satisfying:

```python
confidence >= 0.80
```

are included in the final output.

Words below the threshold are automatically discarded to reduce OCR errors and false positives.

---

## 📸 Sample Results

### Input Document

- Invoice Number
- Date
- Customer Information
- Total Amount

### Output

```text
Invoice 2026-001
Date 2026-06-12
Bill To Acme Corporation
Total Due 1250.00 USD
```

---

## 📈 Learning Outcomes

Through this project, I gained practical experience in:

- Optical Character Recognition (OCR)
- Image preprocessing techniques
- Confidence-based prediction filtering
- OpenCV image processing workflows
- Tesseract OCR integration
- Building production-ready Python applications
- Error handling and debugging strategies

---

## 🧪 Key Concepts Demonstrated

- Pre-trained AI Model Integration
- Image Enhancement Pipelines
- Confidence Thresholding
- Automated Rotation Correction
- Real-World OCR Processing
- Structured Software Engineering Practices

---

## 👨‍💻 Author

### Darshil

DecodeLabs Internship Program – Project 4

---

> **"AI does not read text the way humans do—it estimates probabilities. The art of OCR lies in transforming noisy pixels into information reliable enough to trust."** 📄✨

---

⭐ If you found this project interesting, feel free to explore the code and experiment with your own documents.