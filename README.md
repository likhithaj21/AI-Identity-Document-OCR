# 🪪 AI-Powered Identity Document Verification System

### Intelligent OCR, Document Classification & Information Extraction

A web application that automatically **classifies** and **extracts
structured information** from Indian identity documents — **Aadhaar
Card, PAN Card, Passport, and Driving Licence** — using classic
computer vision preprocessing (OpenCV), deep learning-based OCR
(EasyOCR), and a rule-based document-intelligence layer, all wrapped in
a clean, interactive **Gradio** UI.

Upload a document image and instantly get:
- ✅ Automatic document type detection (PAN / Aadhaar / Passport / DL)
- ✅ Extracted key fields — Document Number, Name, Date of Birth
- ✅ Document quality check (🟢 Good / 🔴 Poor) based on OCR confidence
- ✅ Average OCR confidence score
- ✅ Bounding boxes highlighting every detected text region
- ✅ Side-by-side original vs. preprocessed image
- ✅ Processing time
- ✅ A downloadable `.txt` file with the full structured summary

---

## 📖 Project Overview

Manual verification of identity documents is slow and error-prone. This
project demonstrates a lightweight, end-to-end **document intelligence
pipeline** — the same shape of pipeline used by real identity-verification
(KYC) products — that can serve as the foundation for an automated
verification system.

The pipeline works in six stages:

1. **Upload** — the user uploads a photo/scan of an ID document.
2. **Preprocess** — OpenCV cleans up the image (grayscale → blur →
   adaptive threshold → noise removal) to make text easier to read.
3. **Extract (OCR)** — EasyOCR (a deep learning OCR engine) detects and
   reads all text regions, returning the text, its location, and a
   confidence score for each detection.
4. **Classify** — keyword-based rules detect which type of document was
   uploaded (PAN / Aadhaar / Passport / Driving Licence).
5. **Extract Fields** — regular expressions and label-based heuristics
   pull out the Document Number, Name, and Date of Birth.
6. **Verify & Export** — a quality score flags poor scans, detected text
   regions are highlighted with green bounding boxes, and the full
   structured summary is displayed and made downloadable.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎨 Beautiful Gradio UI | Clean, modern, responsive interface with emoji icons |
| 📤 Upload Image | Drag-and-drop or click-to-upload any document photo |
| 🧠 Document Type Detection | Automatically classifies PAN / Aadhaar / Passport / Driving Licence |
| 🪪 Field Extraction | Pulls out Document Number, Name, and Date of Birth |
| 📸 Document Quality Check | Flags scans as 🟢 Good or 🔴 Poor based on OCR confidence |
| 🖼️ Image Preview | See your uploaded image immediately |
| ⚙️ Preprocessed Image | View the OpenCV-cleaned version side-by-side |
| ✅ Bounding Boxes | Green boxes highlight every detected text region |
| 📝 Structured Summary | Document type, fields, and full OCR text in one readable panel |
| 📊 Average Confidence | Overall OCR confidence shown as a percentage |
| ⏱️ Processing Time | See exactly how long the pipeline took |
| ⬇️ Download as TXT | One-click download of the full structured summary |
| 🗑️ Clear Button | Reset the entire UI in one click |

---

## 📁 Folder Structure

```
Document-OCR/
│
├── app.py               # Main Gradio application (entry point)
├── ocr.py                # EasyOCR text extraction logic
├── utils.py               # OpenCV preprocessing & helper functions
├── fields.py               # Document classification & field extraction (NEW)
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation (this file)
├── sample_images/         # Put sample ID document images here for testing
├── screenshots/           # App screenshots for documentation
└── .gitignore              # Files/folders excluded from git
```

---

## 🛠️ Tech Stack

- **Python 3.9+**
- **[EasyOCR](https://github.com/JaidedAI/EasyOCR)** — deep learning OCR engine
- **[OpenCV](https://opencv.org/)** — image preprocessing (grayscale, blur, thresholding, denoising)
- **[Gradio](https://www.gradio.app/)** — interactive web UI framework
- **[NumPy](https://numpy.org/)** — array/image manipulation
- **[Pillow](https://python-pillow.org/)** — image format conversion (PIL ↔ OpenCV)
- **[Matplotlib](https://matplotlib.org/)** — available for further visualization/plotting

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/Document-OCR.git
cd Document-OCR
```

### 2. (Recommended) Create a virtual environment
```bash
python -m venv venv

# Activate it
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> **Note:** The very first run will download the EasyOCR English model
> weights (~65 MB) automatically. This requires an internet connection
> the first time only — after that, the model is cached locally.

---

## ▶️ How to Run

```bash
python app.py
```

Then open the local URL printed in your terminal (usually
`http://127.0.0.1:7860`) in your web browser.

**Using the app:**
1. Click the upload box and select a photo of an Aadhaar, PAN, Passport,
   or Driving Licence (or use a sample image from `sample_images/`).
2. Click **🚀 Extract Text**.
3. View the original image, the preprocessed image, and the image with
   green bounding boxes around detected text.
4. Read the extracted text, check the average confidence and processing
   time, and download the text file if needed.
5. Click **🗑️ Clear** to reset and try another document.

---

## 🖼️ Screenshots

> Add your own screenshots to the `screenshots/` folder and reference
> them here, for example:

```
![App UI](screenshots/app_ui.png)
![Extraction Result](screenshots/extraction_result.png)
```

---

## 🚀 Applications in Identity Verification

- **KYC (Know Your Customer) automation** for banks, fintech, and telecom onboarding
- **Digital form auto-fill** — automatically populate name/DOB/ID number fields
- **Document authenticity checks** — combined with a downstream field-validation layer
- **Bulk digitization** of physical ID archives into searchable text records
- **Access control systems** — quick ID scanning at gates/checkpoints

---

## 🔮 Future Improvements

- **Transformer-based OCR (TrOCR)** for higher accuracy than CNN-based EasyOCR
- **LayoutLMv3 Document Understanding** to extract fields by layout/position instead of regex
- **Face Verification** — extract the photo from the ID and match it against a selfie
- **Signature Verification** — detect and compare signatures
- **QR Code Validation** — read and verify Aadhaar's embedded QR code
- **Fraud / tamper detection** (hologram checks, font consistency, edge analysis)
- **Multi-language OCR** support (Hindi, Tamil, and other regional languages)
- Replace the current CNN-classifier-free keyword rules with a trained **document image classifier**
- Deploy as a **REST API** (FastAPI) in addition to the Gradio UI
- Add **PDF upload support** in addition to images
- Add **automatic image rotation/deskew correction** for tilted photos

---

## ⚠️ Limitations

- OCR accuracy depends heavily on image quality, lighting, and glare
- Handwritten sections (e.g., signatures) are not reliably read
- **Document type detection** is keyword/rule-based, not a trained
  classifier — it can misfire on unusual layouts or heavily cropped images
- **Field extraction** (Name, DOB, Document Number) relies on regex
  patterns and label-adjacency heuristics; it works well on clean,
  well-lit scans but is not guaranteed correct on every layout/state
  variant (this is especially true for Driving Licence numbers, which
  vary a lot by Indian state)
- The **quality check** is a simple confidence threshold, not a true
  fraud/tamper/liveness detector
- This project performs **automated text extraction and classification
  only** — it does **not** perform official identity verification,
  fraud detection, or database matching against government records
- Currently supports **English text only**
- Not intended for production use with real personal data without
  additional security, encryption, and compliance (e.g., data privacy
  laws) measures in place

---


## 🙏 Acknowledgements

- [EasyOCR](https://github.com/JaidedAI/EasyOCR) by JaidedAI
- [Gradio](https://www.gradio.app/) by Hugging Face
- [OpenCV](https://opencv.org/)
