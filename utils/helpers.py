"""
helpers.py — Utility functions for VidMind.
"""

import os
import math
from pathlib import Path


def format_duration(seconds: float) -> str:
    """Convert seconds to a human-readable duration string."""
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{m}m {s}s"
    h, remainder = divmod(seconds, 3600)
    m, s = divmod(remainder, 60)
    return f"{h}h {m}m"


def chunk_audio_file(audio_path: str, output_dir: str, max_mb: int = 19) -> list[str]:
    """
    Split an audio file into chunks under max_mb megabytes each.

    Gemini Files API limit is 20 MB per file (free tier).
    We use 19 MB to stay safely under.

    For files already under the limit, returns [audio_path] unchanged.
    Chunking is done by raw byte splitting (no re-encoding needed for transcription).

    Returns a list of file paths (in order).
    """
    max_bytes = max_mb * 1024 * 1024
    file_size = os.path.getsize(audio_path)

    if file_size <= max_bytes:
        return [audio_path]

    # Read full file and split into byte chunks
    with open(audio_path, "rb") as f:
        data = f.read()

    total_chunks = math.ceil(len(data) / max_bytes)
    ext = Path(audio_path).suffix
    chunks = []

    for i in range(total_chunks):
        start = i * max_bytes
        end = min(start + max_bytes, len(data))
        chunk_data = data[start:end]

        chunk_path = os.path.join(output_dir, f"chunk_{i:03d}{ext}")
        with open(chunk_path, "wb") as f:
            f.write(chunk_data)
        chunks.append(chunk_path)

    return chunks
