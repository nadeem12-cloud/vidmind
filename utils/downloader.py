"""
downloader.py — Download audio from YouTube using yt-dlp.
Returns (audio_path, video_title, duration_seconds).
No ffmpeg required: yt-dlp extracts m4a/webm natively.
"""

import os
import glob
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    raise ImportError("yt-dlp not installed. Run: pip install yt-dlp")


def download_audio(url: str, output_dir: str, cookies_path: str = None) -> tuple[str, str, float]:
    """
    Download the best available audio track from a YouTube URL.

    Returns
    -------
    audio_path : str   — path to the downloaded audio file
    title      : str   — video title
    duration   : float — video duration in seconds
    """
    output_dir = str(output_dir)

    # Probe metadata first (fast, no download)
    meta_opts = {"quiet": False, "verbose": True, "no_warnings": False, "skip_download": True}
    if cookies_path:
        meta_opts["cookiefile"] = cookies_path

    with yt_dlp.YoutubeDL(meta_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get("title", "Unknown Video")
        duration = info.get("duration", 0) or 0

    # Guard: skip videos longer than 3 hours (Gemini free tier sanity)
    if duration > 10_800:
        raise ValueError(
            f"Video is {duration/3600:.1f} h long. "
            "For free-tier Gemini, please use videos under 3 hours."
        )

    # Download audio — prefer m4a (AAC) so no re-encoding is needed.
    # yt-dlp can extract it from the muxed stream without ffmpeg.
    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best",
        "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s"),
        "quiet": False,
        "verbose": True,
        "no_warnings": False,
        "noplaylist": True,
        # Do NOT post-process — avoids any ffmpeg dependency
        "postprocessors": [],
    }
    if cookies_path:
        ydl_opts["cookiefile"] = cookies_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Find the downloaded file
    candidates = glob.glob(os.path.join(output_dir, "*.*"))
    # Filter out non-audio metadata files
    audio_exts = {".m4a", ".webm", ".mp4", ".ogg", ".opus", ".aac", ".mp3"}
    audio_files = [f for f in candidates if Path(f).suffix.lower() in audio_exts]

    if not audio_files:
        raise FileNotFoundError(
            "Audio download succeeded but no audio file was found. "
            "This usually means yt-dlp couldn't extract a compatible format."
        )

    # Pick the largest file if multiple exist
    audio_path = max(audio_files, key=os.path.getsize)
    return audio_path, title, float(duration)
