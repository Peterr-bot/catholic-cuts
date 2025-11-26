"""Audio transcription utilities for Catholic Cuts.

Cloud-safe version for Streamlit Community Cloud deployment.
Handles video file transcription using OpenAI's Whisper API without ffmpeg.
"""

import tempfile
import os
from typing import Optional
from openai import OpenAI
from src import config

# Streamlit Cloud supported formats (Whisper-native only)
SUPPORTED_STREAMLIT_FORMATS = ["mp4", "mp3", "wav", "webm"]


def transcribe_video_to_text(uploaded_file):
    """
    Cloud-safe transcription for Streamlit Community Cloud.
    Only accepts Whisper-native formats: mp4/mp3/wav/webm.
    No ffmpeg, no format conversion.
    """
    from openai import OpenAI
    import tempfile

    if not uploaded_file:
        raise RuntimeError("No file provided for transcription")

    # Check file size (OpenAI Whisper has 25MB limit)
    max_size_mb = 25
    file_size_mb = uploaded_file.size / (1024 * 1024)

    if file_size_mb > max_size_mb:
        raise RuntimeError(f"Video file too large: {file_size_mb:.1f}MB. Maximum allowed: {max_size_mb}MB")

    client = OpenAI()

    # Extract file extension and validate
    suffix = "." + uploaded_file.name.split(".")[-1].lower()
    if suffix.lstrip(".") not in SUPPORTED_STREAMLIT_FORMATS:
        raise ValueError(
            f"Unsupported format in cloud: {suffix}. "
            f"Allowed: {', '.join(SUPPORTED_STREAMLIT_FORMATS)}"
        )

    # Create temporary file with correct extension
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        # Transcribe using Whisper
        with open(tmp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text",
            )

        return transcript.strip()

    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def get_supported_video_formats() -> list:
    """Get list of supported video formats for Streamlit Cloud display.

    Returns:
        List of supported file extensions (cloud-safe formats only)
    """
    return [f".{fmt}" for fmt in SUPPORTED_STREAMLIT_FORMATS]


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted size string (e.g., "15.2 MB")
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    size = float(size_bytes)

    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1

    return f"{size:.1f} {size_names[i]}"