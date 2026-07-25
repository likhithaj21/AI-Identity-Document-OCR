"""
utils.py
---------
Utility / helper functions for the AI Identity Document OCR project.

This file contains:
    - Image format conversion helpers (PIL <-> OpenCV)
    - Image preprocessing pipeline (grayscale, blur, threshold, denoise)
    - Bounding box drawing for detected text
    - Saving extracted text to a .txt file

Keeping these functions in a separate file keeps app.py (the UI) and
ocr.py (the OCR engine) clean and easy to read.
"""

import cv2
import numpy as np
from PIL import Image


def pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
    """
    Convert a PIL Image (used by Gradio) into an OpenCV image.

    PIL uses RGB color order, OpenCV uses BGR color order,
    so we must convert between them.
    """
    rgb_array = np.array(pil_image.convert("RGB"))
    bgr_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
    return bgr_array


def cv2_to_pil(cv2_image: np.ndarray) -> Image.Image:
    """Convert an OpenCV image (BGR) back into a PIL Image (RGB) for display."""
    rgb_array = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb_array)


def preprocess_image(cv2_image: np.ndarray):
    """
    Preprocess a document image to make text easier for the OCR engine
    to read accurately.

    Pipeline:
        1. Convert to Grayscale   -> removes color, keeps intensity info
        2. Gaussian Blur          -> reduces high-frequency noise/grain
        3. Adaptive Threshold     -> converts image to black & white,
                                      adapting to uneven lighting across
                                      the document (very common in phone
                                      photos of ID cards)
        4. Noise Removal          -> morphological "opening" to remove
                                      small white speckles left after
                                      thresholding

    Args:
        cv2_image (np.ndarray): original image in OpenCV BGR format

    Returns:
        denoised (np.ndarray): final single-channel preprocessed image
                                (this is what we feed into EasyOCR)
        processed_bgr (np.ndarray): 3-channel version of the same image,
                                     used only for displaying in the UI
    """
    # 1. Grayscale conversion
    gray = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2GRAY)

    # 2. Gaussian Blur to smooth out noise before thresholding
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 3. Adaptive Threshold - great for scanned/photographed documents
    #    where lighting is not uniform across the page.
    thresh = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=31,   # size of the local neighborhood used to threshold
        C=15,           # constant subtracted from the mean
    )

    # 4. Noise removal using morphological opening
    #    (erosion followed by dilation) to clean small dots/speckles
    kernel = np.ones((2, 2), np.uint8)
    denoised = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # Convert back to 3-channel BGR just so it displays nicely in Gradio
    processed_bgr = cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)

    return denoised, processed_bgr


def draw_bounding_boxes(cv2_image: np.ndarray, ocr_results: list) -> np.ndarray:
    """
    Draw a green bounding box + confidence label around every piece of
    text detected by EasyOCR.

    Args:
        cv2_image (np.ndarray): the image to draw on (a copy is made,
                                 original is never modified)
        ocr_results (list): list of (bbox, text, confidence) tuples,
                             exactly as returned by EasyOCR's readtext()

    Returns:
        image_with_boxes (np.ndarray): new image with boxes + labels drawn
    """
    image_with_boxes = cv2_image.copy()

    for (bbox, text, confidence) in ocr_results:
        # bbox = 4 points: [top-left, top-right, bottom-right, bottom-left]
        points = np.array(bbox, dtype=np.int32)

        # Draw the green rectangle (polygon) around the detected word/line
        cv2.polylines(
            image_with_boxes,
            [points],
            isClosed=True,
            color=(0, 255, 0),   # Green in BGR format
            thickness=2,
        )

        # Label each box with its confidence percentage
        top_left = tuple(points[0])
        label = f"{confidence * 100:.0f}%"
        label_y = max(top_left[1] - 6, 10)
        cv2.putText(
            image_with_boxes,
            label,
            (top_left[0], label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1,
            cv2.LINE_AA,
        )

    return image_with_boxes


def save_text_to_file(text: str, file_path: str) -> str:
    """
    Save the extracted text to a .txt file so the user can download it.

    Args:
        text (str): the full extracted text
        file_path (str): where to save the file

    Returns:
        file_path (str): same path, returned for convenience
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    return file_path
