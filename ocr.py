"""
ocr.py
-------
Handles all text-extraction logic using EasyOCR.

EasyOCR is a deep-learning based OCR library that works well "out of the
box" for identity documents (Aadhaar, PAN, Passport, Driving Licence)
without needing any manual training.
"""

import easyocr

# ---------------------------------------------------------------------------
# Initialize the EasyOCR reader ONCE when this module is first imported.
# Loading the model is slow (downloads + loads weights), so we do it a
# single time and reuse the same `reader` object for every request.
#
# gpu=False -> works on any machine (CPU only), even without a graphics
#              card. Change to gpu=True if you have a CUDA-capable GPU
#              for much faster processing.
# ---------------------------------------------------------------------------
print("Loading EasyOCR model... (this happens once, may take a minute)")
reader = easyocr.Reader(['en'], gpu=False)
print("EasyOCR model loaded successfully!")


def extract_text(cv2_image):
    """
    Run OCR on a preprocessed image and return the results.

    Args:
        cv2_image: a NumPy image array (grayscale or BGR both work fine)

    Returns:
        results (list): raw EasyOCR output -> list of (bbox, text, confidence)
        full_text (str): all detected text lines joined with newlines
        avg_confidence (float): average confidence score across all
                                 detections, in the range 0.0 - 1.0
    """
    # readtext() runs detection (finding text regions) and recognition
    # (reading the characters) in one call, and returns a list of:
    #   [ [ [x1,y1],[x2,y2],[x3,y3],[x4,y4] ], "detected text", confidence ]
    results = reader.readtext(cv2_image)

    # Handle the case where no text was found at all
    if len(results) == 0:
        return [], "No text detected. Please try a clearer image.", 0.0

    # Combine every detected line of text into one readable block
    detected_lines = [text for (_, text, _) in results]
    full_text = "\n".join(detected_lines)

    # Compute the average confidence score across all detected text regions
    confidences = [confidence for (_, _, confidence) in results]
    avg_confidence = sum(confidences) / len(confidences)

    return results, full_text, avg_confidence
