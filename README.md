# 🎬 VidMind — Generative AI Video Summarizer

> Paste a YouTube URL → get a structured summary, key points, and full transcript powered by **Gemini 1.5 Flash**.

---

## ✦ Features

| Feature | Details |
|---|---|
| **YouTube audio download** | yt-dlp — no ffmpeg required |
| **AI Transcription** | Gemini 1.5 Flash (audio sent natively) |
| **3 summary types** | Quick (3-5 lines), Detailed (paragraphs), Key Points (bullets) |
| **Full transcript** | Searchable, copyable |
| **Copy to clipboard** | One-click copy for each output |
| **Chunked processing** | Long videos split into <19 MB pieces for free-tier compatibility |
| **Error handling** | Quota exceeded, private videos, unsupported formats |

---

## 📁 Project Structure

```
video_summarizer/
├── app.py                   # Main Streamlit UI
├── requirements.txt
├── .gitignore
├── .streamlit/
│   ├── config.toml          # Theme settings
│   └── secrets.toml         # ← API key (NOT committed to Git)
└── utils/
    ├── __init__.py
    ├── downloader.py        # yt-dlp audio download
    ├── gemini_client.py     # Gemini transcribe + summarize
    └── helpers.py           # Duration format, audio chunking
```

---

## 🚀 Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/video-summarizer.git
cd video-summarizer
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **No ffmpeg needed.** yt-dlp downloads m4a/webm audio directly without any post-processing.

### 4. Get a Gemini API key

1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Create a free API key
3. Copy it

### 5. Add your API key

Edit `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-api-key-here"
```

### 6. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## ☁️ Deploy to Streamlit Cloud

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/video-summarizer.git
git push -u origin main
```

> Make sure `.streamlit/secrets.toml` is in your `.gitignore` (it already is).

### Step 2 — Connect to Streamlit Cloud

1. Go to [https://share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Select your GitHub repo and branch
4. Set **Main file path** to `app.py`
5. Click **"Advanced settings"** → paste your secret:

```toml
GEMINI_API_KEY = "your-api-key-here"
```

6. Click **"Deploy"**

That's it — your app will be live at `https://YOUR_APP.streamlit.app`.

---

## ⚠️ Free Tier Notes

| Limit | Detail |
|---|---|
| **Gemini free RPM** | 15 requests/min (Flash) |
| **File size per upload** | 20 MB — app auto-chunks longer audio |
| **Max video length** | App enforces a 3-hour cap |
| **Quota reset** | Daily — wait 24 h if you hit limits |

If you see a `quota exceeded` error, wait a minute and retry with a shorter video.

---

## 🛠️ Troubleshooting

**"No audio file found"** — The video may be age-restricted, members-only, or region-blocked. Try another URL.

**"File processing failed"** — Gemini couldn't parse the audio format. This is rare with m4a; retry once.

**"Transcription timed out"** — The file is very large. The app chunks at 19 MB, but Gemini processing itself can take up to 5 minutes for long audio.

**Streamlit Cloud crash on startup** — Check that `GEMINI_API_KEY` is set in the Secrets manager (not just locally).

---

## 🧱 Tech Stack

- **Frontend:** Streamlit (custom CSS dark theme)
- **Download:** yt-dlp
- **AI:** Google Gemini 1.5 Flash via `google-generativeai` SDK
- **Deployment:** Streamlit Cloud

---

## 📄 License

MIT — free to use, modify, and deploy.
