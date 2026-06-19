"""
groq_client.py (kept as gemini_client.py for drop-in compatibility)
Transcription : Groq Whisper Large v3 Turbo — FREE
Summarization : Groq LLaMA 3.3 70B — FREE
Single API key, single service, no OpenRouter needed.
"""

import json
import requests
from pathlib import Path

GROQ_BASE         = "https://api.groq.com/openai/v1"
TRANSCRIBE_MODEL  = "whisper-large-v3-turbo"
SUMMARIZE_MODELS  = [
    "llama-3.3-70b-versatile",   # best quality, generous free limits
    "llama3-70b-8192",           # fallback
    "llama3-8b-8192",            # last resort — always available
]

SUPPORTED_EXTS = {".m4a", ".mp3", ".mp4", ".webm", ".wav", ".ogg", ".flac"}


def _headers(api_key: str) -> dict:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def transcribe_audio(audio_path: str, api_key: str) -> str:
    """
    Transcribe audio using Groq Whisper.
    Free limit: 7,200 audio seconds/day (~2 hours).
    """
    ext = Path(audio_path).suffix.lower()
    if ext not in SUPPORTED_EXTS:
        ext = ".m4a"

    with open(audio_path, "rb") as f:
        resp = requests.post(
            f"{GROQ_BASE}/audio/transcriptions",
            headers={"Authorization": f"Bearer {api_key}"},
            files={"file": (Path(audio_path).name, f, f"audio/{ext.lstrip('.')}")},
            data={
                "model": TRANSCRIBE_MODEL,
                "response_format": "text",
                "temperature": "0",
            },
            timeout=300,
        )

    if resp.status_code != 200:
        raise RuntimeError(f"Transcription API error {resp.status_code}: {resp.text}")

    transcript = resp.text.strip()
    if not transcript:
        raise RuntimeError("Empty transcript returned from Groq.")
    return transcript


def generate_summaries(transcript: str, title: str, api_key: str) -> dict:
    """
    Generate summaries using Groq LLaMA — completely free.
    Tries models in order until one succeeds.
    Groq free limits: 14,400 tokens/min, 500,000 tokens/day on LLaMA 3.3 70B.
    """
    # Groq context window is 32k tokens — trim transcript to be safe
    MAX_CHARS = 80_000  # ~20k tokens, leaves plenty of room for response
    if len(transcript) > MAX_CHARS:
        transcript = transcript[:MAX_CHARS] + "\n\n[Transcript truncated for length]"

    prompt = f"""You are an expert content analyst. Analyze the transcript of a video titled "{title}".

Return ONLY a valid JSON object with these exact keys — no markdown fences, no extra text:

{{
  "short": "3-5 sentence overview of the video",
  "detailed": "A thorough 2-3 paragraph summary covering main ideas, arguments, and conclusions",
  "bullets": ["Key point 1", "Key point 2", "Key point 3", "up to 10 key points"]
}}

TRANSCRIPT:
{transcript}
"""

    last_error = ""
    for model_id in SUMMARIZE_MODELS:
        resp = requests.post(
            f"{GROQ_BASE}/chat/completions",
            headers=_headers(api_key),
            json={
                "model": model_id,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 4096,
            },
            timeout=120,
        )
        if resp.status_code == 200:
            break
        last_error = f"{resp.status_code}: {resp.text}"
    else:
        raise RuntimeError(f"All Groq models failed. Last error: {last_error}")

    raw = resp.json()["choices"][0]["message"]["content"].strip()

    # Strip accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        fallback = raw or "Summary not available."
        data = {"short": fallback, "detailed": fallback, "bullets": [fallback]}

    if isinstance(data.get("bullets"), str):
        data["bullets"] = [
            line.strip("•- ").strip()
            for line in data["bullets"].splitlines()
            if line.strip()
        ]

    return {
        "short":    str(data.get("short", "")),
        "detailed": str(data.get("detailed", "")),
        "bullets":  list(data.get("bullets", [])),
    }