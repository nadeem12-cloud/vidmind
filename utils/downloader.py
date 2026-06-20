"""
downloader.py — Download audio from YouTube using yt-dlp.
Returns (audio_path, video_title, duration_seconds).

IMPORTANT (2026): YouTube blocks datacenter/cloud IPs (Streamlit Cloud, AWS,
etc.) from the standard player API — returns "only images available" or
403 Forbidden on download. The reliable fix is to pass YouTube cookies
(exported from a logged-in browser session) so requests look like they're
coming from a real authenticated user, not a bot.

cookies_path is optional — if not provided, falls back to multi-client
emulation (works for some videos, not all, on cloud IPs).
"""

import os
import glob
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    raise ImportError("yt-dlp not installed. Run: pip install yt-dlp")


PLAYER_CLIENTS = ["android_vr", "ios", "android", "tv", "web"]


def _base_opts(output_dir: str, cookies_path: str | None) -> dict:
    opts = {
        "format": "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best",
        "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "postprocessors": [],
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
        },
    }
    if cookies_path and os.path.exists(cookies_path):
        opts["cookiefile"] = cookies_path
    return opts


def _try_download(url: str, output_dir: str, client: str, cookies_path: str | None):
    opts = _base_opts(output_dir, cookies_path)
    opts["extractor_args"] = {"youtube": {"player_client": [client]}}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.extract_info(url, download=True)
        return True
    except Exception:
        return False


def download_audio(
    url: str,
    output_dir: str,
    cookies_path: str | None = None,
) -> tuple[str, str, float]:
    """
    Download the best available audio track from a YouTube URL.

    Parameters
    ----------
    url          : YouTube video URL
    output_dir   : where to save the audio file
    cookies_path : optional path to a cookies.txt file (Netscape format).
                   Strongly recommended when running on cloud platforms
                   (Streamlit Cloud, etc.) — bypasses YouTube's IP-based
                   bot detection that otherwise causes 403 / format errors.

    Returns
    -------
    audio_path : str   — path to the downloaded audio file
    title      : str   — video title
    duration   : float — video duration in seconds
    """
    output_dir = str(output_dir)

    # ── Probe metadata ──────────────────────────────────────────────────────
    info = None
    for client in PLAYER_CLIENTS:
        meta_opts = _base_opts(output_dir, cookies_path)
        meta_opts["skip_download"] = True
        meta_opts["extractor_args"] = {"youtube": {"player_client": [client]}}
        try:
            with yt_dlp.YoutubeDL(meta_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            if info:
                break
        except Exception:
            continue

    if not info:
        raise RuntimeError(
            "Could not fetch video info from YouTube. "
            "The video may be private, age-restricted, region-blocked — "
            "or YouTube is blocking this server. Try uploading cookies.txt."
        )

    title = info.get("title", "Unknown Video")
    duration = info.get("duration", 0) or 0

    if duration > 10_800:
        raise ValueError(
            f"Video is {duration/3600:.1f} h long. "
            "For free-tier usage, please use videos under 3 hours."
        )

    # ── Download — try each client until one succeeds ──────────────────────
    audio_exts = {".m4a", ".webm", ".mp4", ".ogg", ".opus", ".aac", ".mp3"}
    for client in PLAYER_CLIENTS:
        if _try_download(url, output_dir, client, cookies_path):
            candidates = glob.glob(os.path.join(output_dir, "*.*"))
            audio_files = [f for f in candidates if Path(f).suffix.lower() in audio_exts]
            if audio_files:
                audio_path = max(audio_files, key=os.path.getsize)
                return audio_path, title, float(duration)

    # ── All clients failed ───────────────────────────────────────────────────
    if cookies_path:
        raise FileNotFoundError(
            "Download failed even with cookies. The cookies may have expired — "
            "export a fresh cookies.txt from your browser and try again."
        )
    raise FileNotFoundError(
        "YouTube is blocking this server's IP (common on cloud platforms). "
        "Upload a cookies.txt file using the panel above to fix this."
    )