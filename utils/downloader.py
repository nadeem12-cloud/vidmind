"""
downloader.py — Download audio from YouTube using yt-dlp.
Returns (audio_path, video_title, duration_seconds).

2026 YouTube blocking notes:
- Cloud/datacenter IPs get throttled to image-only or restricted formats.
- Fix #1: try multiple player clients (android_vr, ios, android, tv, web).
- Fix #2: use cookies.txt from a real logged-in session (strongly recommended).
- Fix #3: loosen format selector — DASH-only videos need 'bv*+ba/b' style
  selectors, not a hardcoded ext list, or every client fails identically.
"""

import os
import glob
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    raise ImportError("yt-dlp not installed. Run: pip install yt-dlp")


PLAYER_CLIENTS = ["android_vr", "ios", "android", "tv", "web"]

# Ordered from most-specific to most-permissive. The final 'best' with no
# filters at all is the ultimate catch-all — if even that fails, the video
# is genuinely inaccessible (private/geo-blocked/age-gated).
FORMAT_SELECTORS = [
    "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio",
    "bestaudio/best",
    "worstaudio/worst",
    "best",
]


def _base_opts(output_dir: str, cookies_path: str | None) -> dict:
    opts = {
        "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "postprocessors": [],
        "ignoreerrors": False,
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


def _try_download(url: str, output_dir: str, client: str, fmt: str, cookies_path: str | None):
    opts = _base_opts(output_dir, cookies_path)
    opts["format"] = fmt
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
    Tries every combination of (player_client × format_selector) until
    one succeeds — this is the most resilient approach against YouTube's
    2026-era cloud-IP blocking and inconsistent format availability.
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

    # ── Download — try every (client, format) combo ────────────────────────
    audio_exts = {".m4a", ".webm", ".mp4", ".ogg", ".opus", ".aac", ".mp3", ".m4b"}
    video_exts = {".mp4", ".webm", ".mkv"}  # fallback: extract audio track from video container

    for fmt in FORMAT_SELECTORS:
        for client in PLAYER_CLIENTS:
            if _try_download(url, output_dir, client, fmt, cookies_path):
                candidates = glob.glob(os.path.join(output_dir, "*.*"))
                media_files = [
                    f for f in candidates
                    if Path(f).suffix.lower() in (audio_exts | video_exts)
                ]
                if media_files:
                    audio_path = max(media_files, key=os.path.getsize)
                    return audio_path, title, float(duration)

    # ── Everything failed ────────────────────────────────────────────────────
    if cookies_path:
        raise FileNotFoundError(
            "Download failed even with cookies, across all formats and clients. "
            "The cookies may have expired — export a fresh cookies.txt and retry. "
            "If that still fails, the video may be DRM-protected or region-locked."
        )
    raise FileNotFoundError(
        "YouTube is blocking this server's IP across all known workarounds. "
        "Upload a cookies.txt file using the panel above — this is required "
        "for most cloud deployments in 2026."
    )