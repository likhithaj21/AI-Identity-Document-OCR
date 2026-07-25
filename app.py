"""
app.py
-------
AI-Powered Identity Document Verification System
Main Gradio web application.

Run with:
    python app.py

Then open the local URL printed in your terminal
(usually http://127.0.0.1:7860) in your browser.

Pipeline for every uploaded image:
    1. Convert the uploaded image to OpenCV format
    2. Preprocess it with OpenCV (grayscale, blur, threshold, denoise)
    3. Run EasyOCR on the preprocessed image to extract text
    4. Detect the document type (PAN / Aadhaar / Passport / Driving Licence)
    5. Extract key fields (Document Number, Name, Date of Birth)
    6. Run a document quality check based on OCR confidence
    7. Draw green bounding boxes on the original image
    8. Show everything in a clean Gradio UI + let the user download
       the extracted text as a .txt file
"""

import os
import time
import tempfile

import gradio as gr
from PIL import Image

from utils import (
    pil_to_cv2,
    cv2_to_pil,
    preprocess_image,
    draw_bounding_boxes,
    save_text_to_file,
)
from ocr import extract_text
from fields import (
    detect_document_type,
    extract_document_number,
    extract_dob,
    extract_name,
    check_quality,
    build_summary,
)


def process_document(uploaded_image: Image.Image):
    """
    Full document-intelligence pipeline triggered when the user clicks
    "Extract Text".

    Args:
        uploaded_image (PIL.Image): the image uploaded by the user

    Returns:
        tuple of 9 values matching the Gradio outputs list:
            original image, preprocessed image, boxed image,
            document type, document quality, summary text,
            confidence string, time string, txt file path
    """
    # Guard clause: no image uploaded yet
    if uploaded_image is None:
        return (
            None,
            None,
            None,
            "⚠️ No document uploaded",
            "N/A",
            "Please upload a document image first.",
            "N/A",
            "N/A",
            None,
        )

    start_time = time.time()

    # Step 1: Convert PIL image -> OpenCV image (BGR)
    cv2_image = pil_to_cv2(uploaded_image)

    # Step 2: Preprocess with OpenCV
    processed_gray, processed_display = preprocess_image(cv2_image)

    # Step 3: Run EasyOCR on the cleaned-up (preprocessed) image
    ocr_results, full_text, avg_confidence = extract_text(processed_gray)

    # Step 4: Draw bounding boxes on a copy of the ORIGINAL image
    #         (easier to read than drawing on the black & white version)
    boxed_image = draw_bounding_boxes(cv2_image, ocr_results)

    # ---------------- Detect Document Type ----------------
    document_type = detect_document_type(full_text)

    # ---------------- Extract Important Fields ----------------
    document_number = extract_document_number(document_type, full_text)
    name = extract_name(full_text)
    dob = extract_dob(full_text)

    # ---------------- Quality Check ----------------
    quality = check_quality(avg_confidence)

    # ---------------- Build the final summary text ----------------
    summary = build_summary(
        document_type, document_number, name, dob, avg_confidence, quality, full_text
    )

    processing_time = time.time() - start_time

    # Step 5: Convert OpenCV images back to PIL so Gradio can display them
    processed_pil = cv2_to_pil(processed_display)
    boxed_pil = cv2_to_pil(boxed_image)

    # Save the full summary (not just raw text) to a .txt file for download
    temp_dir = tempfile.mkdtemp()
    txt_path = os.path.join(temp_dir, "extracted_text.txt")
    save_text_to_file(summary, txt_path)

    confidence_str = f"{avg_confidence * 100:.2f} %"
    time_str = f"{processing_time:.2f} seconds"

    return (
        uploaded_image,
        processed_pil,
        boxed_pil,
        document_type,
        quality,
        summary,
        confidence_str,
        time_str,
        txt_path,
    )


def clear_all():
    """Reset every component in the UI back to its empty/default state."""
    # Order must match the `outputs` list on clear_btn.click() below:
    # input_image, original, processed, boxed, document, quality,
    # text, confidence, time, download  -> 10 values total
    return None, None, None, None, "", "", "", "N/A", "N/A", None


# ---------------------------------------------------------------------------
# Build the Gradio UI
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
#title { text-align: center; }
#subtitle { text-align: center; color: #666666; }
.gr-button-primary { background: linear-gradient(90deg, #4facfe, #00f2fe) !important; }
"""

with gr.Blocks(
    title="AI-Powered Identity Document Verification System",
    css=CUSTOM_CSS,
    theme=gr.themes.Soft(),
) as demo:

    gr.Markdown(
        """
# 🪪 AI-Powered Identity Document Verification System

### Intelligent OCR, Document Classification & Information Extraction
""",
        elem_id="title",
    )

    gr.Markdown(
        """
Upload an Aadhaar Card, PAN Card, Passport or Driving Licence.

The system automatically:

✅ Detects document type

✅ Extracts important information

✅ Performs OCR

✅ Calculates confidence

✅ Downloads extracted text

Built using OpenCV + EasyOCR + Gradio.
""",
        elem_id="subtitle",
    )

    with gr.Row():
        # ---------------- Left column: controls & metrics ----------------
        with gr.Column(scale=1):
            input_image = gr.Image(type="pil", label="📤 Upload Document Image")

            with gr.Row():
                submit_btn = gr.Button("🚀 Extract Text", variant="primary")
                clear_btn = gr.Button("🗑️ Clear")

            document_output = gr.Textbox(
                label="🪪 Detected Document", interactive=False
            )
            quality_output = gr.Textbox(
                label="📸 Document Quality", interactive=False
            )
            confidence_output = gr.Textbox(
                label="📊 Average OCR Confidence", interactive=False
            )
            time_output = gr.Textbox(
                label="⏱️ Processing Time", interactive=False
            )
            download_output = gr.File(
                label="⬇️ Download Extracted Text (.txt)"
            )

        # ---------------- Right column: images & text ----------------
        with gr.Column(scale=2):
            with gr.Row():
                original_output = gr.Image(label="🖼️ Original Image")
                processed_output = gr.Image(label="⚙️ Preprocessed Image")

            boxed_output = gr.Image(label="✅ Detected Text (Bounding Boxes)")
            text_output = gr.Textbox(
                label="📝 Extracted Fields & Full OCR Text", lines=14, interactive=False
            )

    # Wire up the buttons to their functions
    submit_btn.click(
        fn=process_document,
        inputs=[input_image],
        outputs=[
            original_output,
            processed_output,
            boxed_output,
            document_output,
            quality_output,
            text_output,
            confidence_output,
            time_output,
            download_output,
        ],
    )

    clear_btn.click(
        fn=clear_all,
        inputs=[],
        outputs=[
            input_image,
            original_output,
            processed_output,
            boxed_output,
            document_output,
            quality_output,
            text_output,
            confidence_output,
            time_output,
            download_output,
        ],
    )

    gr.Markdown(
        """
---
### 🚀 Future Improvements

- Transformer-based OCR (TrOCR)
- LayoutLMv3 Document Understanding
- Face Verification
- Signature Verification
- QR Code Validation
- Fraud Detection
- Multi-language OCR

Built for AI-powered Identity Verification.
"""
    )


if __name__ == "__main__":
    demo.launch()
