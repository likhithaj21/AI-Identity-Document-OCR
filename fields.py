"""
fields.py
----------
Document intelligence layer built on top of raw OCR output.

This module takes the plain text returned by EasyOCR and turns it into
structured, useful information — the kind of thing an identity
verification product (like HyperVerge, Onfido, etc.) actually needs:

    - Which document is this? (Aadhaar / PAN / Passport / Driving Licence)
    - What is the document number?
    - What is the date of birth?
    - What is the person's name? (best-effort)
    - Is the scan good enough to trust? (quality check)

Everything here is rule-based (keyword matching + regular expressions),
which keeps the project dependency-free and easy to understand. A
production system would typically replace/augment this with a trained
NER (Named Entity Recognition) model — see the README's
"Future Improvements" section.
"""

import re


def detect_document_type(full_text: str) -> str:
    """
    Guess which type of identity document was scanned, based on
    keywords that reliably appear on each document type in India.

    Args:
        full_text (str): all OCR-detected text, joined together

    Returns:
        str: one of "PAN Card", "Aadhaar Card", "Passport",
             "Driving Licence", or "Unknown Document"
    """
    text_upper = full_text.upper()

    if "INCOME TAX" in text_upper or "PERMANENT ACCOUNT NUMBER" in text_upper:
        return "PAN Card"

    if "UNIQUE IDENTIFICATION AUTHORITY" in text_upper or "AADHAAR" in text_upper:
        return "Aadhaar Card"

    if "PASSPORT" in text_upper:
        return "Passport"

    if "DRIVING LICENCE" in text_upper or "DRIVING LICENSE" in text_upper:
        return "Driving Licence"

    return "Unknown Document"


def extract_document_number(document_type: str, full_text: str) -> str:
    """
    Extract the document's unique ID number using a regex pattern
    tailored to the detected document type. Falls back to a generic
    alphanumeric-ID pattern if the document type is unknown.

    Args:
        document_type (str): output of detect_document_type()
        full_text (str): all OCR-detected text

    Returns:
        str: the matched document number, or "Not Found"
    """
    # Remove extra spaces so patterns like "1234 5678 9012" still match
    # when EasyOCR happens to split digits across separate detections.
    condensed = full_text.upper()

    patterns = {
        # PAN: 5 letters + 4 digits + 1 letter, e.g. ABCDE1234F
        "PAN Card": r"[A-Z]{5}[0-9]{4}[A-Z]",
        # Aadhaar: 12 digits, usually shown in 3 groups of 4 separated by
        # a single space (never a newline). We deliberately use [ ]?
        # instead of \s? so the match can't accidentally span across
        # lines (e.g. bleeding into a DOB printed just above/below it),
        # and the (?<!\d)/(?!\d) guards stop it grabbing a partial
        # number out of a longer digit run.
        "Aadhaar Card": r"(?<!\d)\d{4}[ ]?\d{4}[ ]?\d{4}(?!\d)",
        # Indian Passport: 1 letter followed by 7 digits, e.g. M1234567
        "Passport": r"[A-Z][0-9]{7}",
        # Driving Licence: state code + numbers, varies a lot by state
        # e.g. "TN01 20230001234" or "MH1220110012345"
        "Driving Licence": r"[A-Z]{2}[0-9]{2}\s?[0-9]{10,13}",
    }

    pattern = patterns.get(document_type)

    if pattern:
        match = re.search(pattern, condensed)
        if match:
            return match.group().strip()

    # Fallback: try every known pattern in case the document type
    # detection missed but the number is still present in the text
    for fallback_pattern in patterns.values():
        match = re.search(fallback_pattern, condensed)
        if match:
            return match.group().strip()

    return "Not Found"


def extract_dob(full_text: str) -> str:
    """
    Extract a date of birth in DD/MM/YYYY or DD-MM-YYYY format.

    Args:
        full_text (str): all OCR-detected text

    Returns:
        str: the matched date, or "Not Found"
    """
    match = re.search(r"\d{2}[/-]\d{2}[/-]\d{4}", full_text)
    return match.group() if match else "Not Found"


def extract_name(full_text: str) -> str:
    """
    Best-effort extraction of the document holder's name.

    Strategy: identity documents almost always print a "Name" label
    directly above or beside the actual name. We scan line-by-line and
    grab the text that immediately follows a line containing the word
    "NAME" (case-insensitive). This is a simple heuristic, not a
    guaranteed-correct NER model — see README limitations.

    Args:
        full_text (str): all OCR-detected text

    Returns:
        str: best-guess name, or "Not Found"
    """
    lines = [line.strip() for line in full_text.split("\n") if line.strip()]

    for i, line in enumerate(lines):
        if "NAME" in line.upper() and i + 1 < len(lines):
            candidate = lines[i + 1]
            # Skip if the "next line" is actually another label/number
            # rather than a real name (e.g. all-digit strings).
            if not re.fullmatch(r"[\d\s/-]+", candidate):
                return candidate

    return "Not Found"


def check_quality(avg_confidence: float) -> str:
    """
    Simple pass/fail quality gate based on average OCR confidence.
    A low-confidence scan usually means blur, glare, poor lighting,
    or a low-resolution photo — all things that would make automated
    identity verification unreliable.

    Args:
        avg_confidence (float): average OCR confidence, range 0.0 - 1.0

    Returns:
        str: "🟢 Good" or "🔴 Poor"
    """
    return "🟢 Good" if avg_confidence >= 0.60 else "🔴 Poor"


def build_summary(document_type, document_number, name, dob, avg_confidence, quality, full_text):
    """
    Assemble all extracted fields into one human-readable summary block,
    used for the downloadable .txt file and the "Full OCR" preview.
    """
    summary = f"""📄 Document Type      : {document_type}
🪪 Document Number    : {document_number}
🙍 Name                : {name}
📅 Date of Birth       : {dob}
⭐ OCR Confidence      : {avg_confidence * 100:.2f} %
📸 Document Quality    : {quality}

------------------------------------
FULL OCR TEXT
------------------------------------
{full_text}
"""
    return summary
