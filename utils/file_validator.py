"""
RentLens AI - File Validator and Sanitizer.
Ensures uploaded files conform to accepted formats, limits, and integrity.
"""

import io
import base64
from typing import Tuple, Optional, Dict, Any
from PIL import Image, UnidentifiedImageError
import pymupdf

MAX_IMAGE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB
MAX_PDF_SIZE_BYTES = 25 * 1024 * 1024    # 25 MB

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_IMAGE_MIMES = {"image/jpeg", "image/png", "image/jpg"}


def validate_image_file(uploaded_file) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Validates uploaded image file for size, format, and corruption.
    Returns: (is_valid, error_message, metadata)
    """
    if uploaded_file is None:
        return False, "No file provided.", None

    filename = uploaded_file.name
    file_bytes = uploaded_file.getvalue()
    file_size = len(file_bytes)

    # 1. Empty file check
    if file_size == 0:
        return False, f"File '{filename}' is empty (0 bytes). Please upload a valid image.", None

    # 2. Maximum size check
    if file_size > MAX_IMAGE_SIZE_BYTES:
        mb_size = file_size / (1024 * 1024)
        return False, f"File '{filename}' exceeds the maximum allowed size of 15MB (current: {mb_size:.1f}MB).", None

    # 3. Extension check
    lower_name = filename.lower()
    has_valid_ext = any(lower_name.endswith(ext) for ext in ALLOWED_IMAGE_EXTENSIONS)
    if not has_valid_ext:
        return False, f"Unsupported file extension for '{filename}'. Allowed formats: JPG, JPEG, PNG.", None

    # 4. Integrity check via PIL
    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify()  # Verifies headers and integrity
        
        # Re-open after verify() (verify exhausts image buffer)
        image = Image.open(io.BytesIO(file_bytes))
        width, height = image.size
        img_format = image.format or "JPEG"

        metadata = {
            "filename": filename,
            "size_bytes": file_size,
            "size_formatted": f"{file_size / 1024:.1f} KB",
            "width": width,
            "height": height,
            "format": img_format,
            "mode": image.mode,
        }
        return True, None, metadata

    except (UnidentifiedImageError, OSError, Exception) as e:
        return False, f"Corrupted or invalid image file '{filename}'. Details: {str(e)}", None


def image_bytes_to_base64(file_bytes: bytes) -> str:
    """Converts image bytes to base64 string for Ollama vision API."""
    return base64.b64encode(file_bytes).decode("utf-8")


def validate_pdf_file(uploaded_file) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Validates uploaded lease PDF file for size, format, and readability.
    Returns: (is_valid, error_message, metadata)
    """
    if uploaded_file is None:
        return False, "No lease document provided.", None

    filename = uploaded_file.name
    file_bytes = uploaded_file.getvalue()
    file_size = len(file_bytes)

    # 1. Empty file check
    if file_size == 0:
        return False, f"Document '{filename}' is empty (0 bytes). Please upload a valid PDF lease.", None

    # 2. Maximum size check
    if file_size > MAX_PDF_SIZE_BYTES:
        mb_size = file_size / (1024 * 1024)
        return False, f"Document '{filename}' exceeds the 25MB limit (current: {mb_size:.1f}MB).", None

    # 3. Extension check
    if not filename.lower().endswith(".pdf"):
        return False, f"'{filename}' is not a PDF file. Please upload a .pdf document.", None

    # 4. Integrity and read check via PyMuPDF
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        page_count = len(doc)
        if page_count == 0:
            doc.close()
            return False, f"PDF '{filename}' contains no readable pages.", None

        # Check if document is password protected / encrypted without access
        if doc.is_encrypted and not doc.authenticate(""):
            doc.close()
            return False, f"PDF '{filename}' is encrypted or password-protected. Please remove password protection.", None

        doc.close()
        metadata = {
            "filename": filename,
            "size_bytes": file_size,
            "size_formatted": f"{file_size / (1024 * 1024):.2f} MB" if file_size > 1024 * 1024 else f"{file_size / 1024:.1f} KB",
            "page_count": page_count,
        }
        return True, None, metadata

    except Exception as e:
        return False, f"Could not read PDF '{filename}'. It may be corrupted or damaged. Details: {str(e)}", None
