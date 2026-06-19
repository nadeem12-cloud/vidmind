<div align="center">

# 🎬 VidMind — AI Video Summarizer

**Turn any YouTube video into structured insights — instantly.**

[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Powered%20by-Groq-F55036?style=flat-square)](https://groq.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)

[**Live Demo →**](https://vidmind-10.streamlit.app/) &nbsp;·&nbsp; [Report Bug](https://github.com/nadeem12-cloud/vidmind/issues) &nbsp;·&nbsp; [Request Feature](https://github.com/nadeem12-cloud/vidmind/issues)

![VidMind Screenshot](assets/screenshot.png)

</div>

---

## ✦ What is VidMind?

VidMind is a Generative AI-powered video summarizer that takes any YouTube URL and delivers a clean, structured breakdown in seconds — no manual note-taking, no scrubbing through long videos.

Built as part of a remote AI internship project at **Thinking Tech**, it demonstrates a complete end-to-end AI pipeline: audio extraction → speech-to-text transcription → LLM-powered summarization — all wrapped in a clean Streamlit interface.

---

## ⚡ Features

| Feature | Details |
|---|---|
| 🎵 **Audio Extraction** | yt-dlp — no ffmpeg dependency |
| 📝 **AI Transcription** | Groq Whisper Large v3 Turbo |
| ✦ **Smart Summaries** | 3 formats — Quick, Detailed, Key Points |
| 📄 **Full Transcript** | Scrollable, monospace, copyable |
| ⎘ **Copy to Clipboard** | One-click copy for every output |
| 🔄 **Progress Tracking** | Live status chips for each pipeline stage |
| 🧩 **Audio Chunking** | Handles long videos via automatic splitting |
| 💸 **100% Free** | Groq free tier — no credit card needed |

---

## 🛠️ Tech Stack

```
Frontend      →  Streamlit (custom CSS — teal + cream theme)
Audio         →  yt-dlp (YouTube audio download, no ffmpeg)
Transcription →  Groq API — Whisper Large v3 Turbo
Summarization →  Groq API — LLaMA 3.3 70B Versatile
Deployment    →  Streamlit Cloud
```

---

## 📁 Project Structure

```
vidmind/
├── app.py                    # Main Streamlit UI
├── requirements.txt
├── .gitignore
├── README.md
├── assets/
│   └── screenshot.png        # UI screenshot
├── .streamlit/
│   ├── config.toml           # Theme config
│   └── secrets.toml          # API key (NOT committed)
└── utils/
    ├── __init__.py
    ├── downloader.py         # yt-dlp audio download
    ├── gemini_client.py      # Groq transcription + summarization
    └── helpers.py            # Duration format, audio chunking
```

---

## 🚀 Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/nadeem12-cloud/vidmind.git
cd vidmind
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Get a free Groq API key
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up with Google → **API Keys** → **Create API Key**
3. Copy the key (starts with `gsk_...`)

### 5. Add your API key
Create `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "gsk_..."
```

### 6. Run
```bash
streamlit run app.py
```

App opens at `http://localhost:8501` 🎉

---

## ☁️ Deploy to Streamlit Cloud

1. Push repo to GitHub (make sure `secrets.toml` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your repo → set main file to `app.py`
4. **Advanced settings** → add secret:
```toml
GROQ_API_KEY = "gsk_..."
```
5. Click **Deploy** — live in ~2 minutes ✦

---

## 🔄 How It Works

```
YouTube URL
    │
    ▼
yt-dlp downloads audio (m4a/webm, no ffmpeg)
    │
    ▼
Audio chunked into <25MB pieces (Groq file limit)
    │
    ▼
Groq Whisper Large v3 Turbo → Full transcript
    │
    ▼
Groq LLaMA 3.3 70B → 3 structured outputs
    │
    ├── ⚡ Quick Summary   (3-5 sentences)
    ├── 📖 Detailed        (2-3 paragraphs)
    ├── 🎯 Key Points      (bullet list)
    └── 📄 Full Transcript (scrollable)
```

---

## ⚠️ Free Tier Limits

| Service | Limit |
|---|---|
| Groq Whisper | 7,200 audio seconds/day (~2 hrs) |
| Groq LLaMA 3.3 70B | 500,000 tokens/day |
| Max video length | 3 hours (app enforced) |

---

## 🤝 Acknowledgements

Built during a remote AI internship at **[Thinking Tech](https://thinkingtech.in)**.

- [Groq](https://groq.com) — blazing fast inference
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — YouTube audio extraction
- [Streamlit](https://streamlit.io) — rapid ML app development

---

## 📄 License

MIT — free to use, fork, and build on.

---

<div align="center">
Built with ❤️ by <a href="https://github.com/nadeem12-cloud">Nadeem Memon</a>
</div>
