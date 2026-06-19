import streamlit as st
import os
import tempfile
from pathlib import Path

from utils.downloader import download_audio
from utils.gemini_client import transcribe_audio, generate_summaries
from utils.helpers import format_duration, chunk_audio_file

st.set_page_config(
    page_title="VidMind · AI Video Summarizer",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #0B746C !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
.stApp { color: #FFFEAC !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    max-width: 760px !important;
    background: transparent !important;
}

/* ── Hero ── */
.hero { text-align: center; padding: 3.5rem 1rem 2rem; }
.badge {
    display: inline-flex; align-items: center; gap: 7px;
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.18em;
    text-transform: uppercase; color: #FFFEAC;
    background: rgba(255,254,172,0.08); border: 1px solid rgba(255,254,172,0.2);
    border-radius: 100px; padding: 5px 16px; margin-bottom: 1.8rem;
}
.badge-dot {
    width: 6px; height: 6px; background: #FFFEAC;
    border-radius: 50%; animation: blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.25;} }
.hero-title {
    font-size: clamp(2.4rem, 6vw, 3.8rem);
    font-weight: 700; line-height: 1.08;
    letter-spacing: -0.02em; color: #FFFEAC; margin-bottom: 1.1rem;
}
.hero-sub {
    font-size: 1rem; font-weight: 400;
    color: rgba(255,254,172,0.6); max-width: 440px;
    margin: 0 auto; line-height: 1.7; text-align: center;
}

/* ── Input card ── */
.input-card {
    background: rgba(0,0,0,0.2);
    border: 1px solid rgba(255,254,172,0.15);
    border-radius: 20px;
    padding: 1.6rem 1.6rem 1.3rem;
    margin: 2rem 0 1rem;
}
.input-lbl {
    font-size: 0.68rem; font-weight: 700;
    letter-spacing: 0.16em; text-transform: uppercase;
    color: rgba(255,254,172,0.4); margin-bottom: 0.6rem;
}

/* ── Streamlit input — hide label, style only the input ── */
[data-testid="stTextInput"] label { display: none !important; }
[data-testid="stTextInput"] > div > div {
    background: transparent !important;
}
[data-testid="stTextInput"] input {
    background: rgba(0,0,0,0.25) !important;
    border: 1.5px solid rgba(255,254,172,0.18) !important;
    border-radius: 12px !important;
    color: #FFFEAC !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.95rem !important; font-weight: 400 !important;
    padding: 0.85rem 1.1rem !important;
    caret-color: #FFFEAC !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: rgba(255,254,172,0.55) !important;
    box-shadow: 0 0 0 3px rgba(255,254,172,0.08) !important;
    outline: none !important;
}
[data-testid="stTextInput"] input::placeholder { color: rgba(255,254,172,0.2) !important; }

/* ── Buttons ── */
.stButton > button {
    border-radius: 12px !important; font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important; font-size: 0.92rem !important;
    letter-spacing: 0.03em !important; padding: 0.75rem 1.5rem !important;
    transition: all 0.18s !important; width: 100% !important; cursor: pointer !important;
}
div[data-testid="column"]:first-child .stButton > button {
    background: #FFFEAC !important; color: #0B746C !important;
    border: none !important; font-weight: 700 !important;
    box-shadow: 0 4px 20px rgba(255,254,172,0.2) !important;
}
div[data-testid="column"]:first-child .stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 28px rgba(255,254,172,0.3) !important;
}
div[data-testid="column"]:last-child .stButton > button {
    background: transparent !important; color: rgba(255,254,172,0.4) !important;
    border: 1px solid rgba(255,254,172,0.14) !important;
}
div[data-testid="column"]:last-child .stButton > button:hover {
    color: rgba(255,254,172,0.7) !important; border-color: rgba(255,254,172,0.3) !important;
}

/* ── Chips ── */
.chips { display:flex; gap:0.5rem; flex-wrap:wrap; margin:1.4rem 0 0.8rem; }
.chip {
    display:inline-flex; align-items:center; gap:5px;
    font-size:0.74rem; font-weight:500; padding:4px 12px; border-radius:100px;
    font-family:'Space Grotesk',sans-serif;
}
.chip-done   { background:rgba(255,254,172,0.12); color:#FFFEAC; border:1px solid rgba(255,254,172,0.25); }
.chip-active { background:rgba(255,254,172,0.07); color:rgba(255,254,172,0.6); border:1px solid rgba(255,254,172,0.15); }
.chip-idle   { background:rgba(0,0,0,0.15); color:rgba(255,254,172,0.2); border:1px solid rgba(255,254,172,0.07); }

/* ── Alerts ── */
.stAlert { border-radius: 14px !important; }
hr { border-color: rgba(255,254,172,0.1) !important; margin: 2rem 0 !important; }
.results-label {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.16em;
    text-transform: uppercase; color: rgba(255,254,172,0.35); margin-bottom: 1rem;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(0,0,0,0.2) !important;
    border: 1px solid rgba(255,254,172,0.1) !important;
    border-radius: 14px !important; padding: 4px !important; gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: rgba(255,254,172,0.35) !important;
    border-radius: 10px !important; font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.86rem !important; font-weight: 500 !important;
    padding: 0.45rem 1rem !important; border: none !important;
}
.stTabs [aria-selected="true"] { background: rgba(255,254,172,0.12) !important; color: #FFFEAC !important; }

/* ── Output card ── */
.out-card {
    background: rgba(0,0,0,0.18); border: 1px solid rgba(255,254,172,0.1);
    border-radius: 14px; padding: 1.4rem 1.6rem; margin: 1rem 0 0.5rem;
    line-height: 1.8; color: rgba(255,254,172,0.85);
    font-size: 0.94rem; font-weight: 400; font-family: 'Space Grotesk', sans-serif;
}
.out-card ul { padding-left: 1.3rem; margin: 0; }
.out-card li { margin-bottom: 0.55rem; }

/* ── Copy btn ── */
.copy-btn {
    display: inline-flex; align-items: center; gap: 5px;
    background: transparent; border: 1px solid rgba(255,254,172,0.14);
    border-radius: 8px; color: rgba(255,254,172,0.35);
    font-size: 0.76rem; font-weight: 500; font-family: 'Space Grotesk', sans-serif;
    padding: 5px 12px; cursor: pointer; transition: all 0.15s; margin-top: 0.5rem;
}
.copy-btn:hover { background: rgba(255,254,172,0.08); color: #FFFEAC; border-color: rgba(255,254,172,0.3); }

.stSpinner > div { border-top-color: #FFFEAC !important; }
.stCaption, small { color: rgba(255,254,172,0.4) !important; }
.footer {
    text-align: center; padding: 3rem 0 1rem; font-size: 0.74rem;
    color: rgba(255,254,172,0.2); letter-spacing: 0.06em; font-family: 'Space Grotesk', sans-serif;
}
</style>
""", unsafe_allow_html=True)

# ── API Key ───────────────────────────────────────────────────────────────────
def get_groq_key():
    try:
        return st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="badge"><span class="badge-dot"></span>Groq Whisper · LLaMA 3.3 · 100% Free</div>
  <h1 class="hero-title">Turn any video into<br>instant clarity</h1>
  <p class="hero-sub"><center>Paste a YouTube URL — get a structured summary, key points, and full transcript in seconds.</center></p>
</div>
""", unsafe_allow_html=True)

# ── Key guard ─────────────────────────────────────────────────────────────────
groq_key = get_groq_key()
if not groq_key:
    st.error("⚠️ Missing GROQ_API_KEY — add it to .streamlit/secrets.toml")
    st.code('GROQ_API_KEY = "gsk_..."', language="toml")
    st.stop()

st.markdown('<div class="input-card"><div class="input-lbl">🔗 YouTube URL</div>', unsafe_allow_html=True)
url = st.text_input("url_field", placeholder="https://www.youtube.com/watch?v=...", label_visibility="collapsed")

# Expander for bypass tools
with st.expander("🔧 Cloud deployment? Avoid YouTube blocks (403 errors)"):
    st.markdown("""
    When running in the cloud (like Streamlit Community Cloud), YouTube often blocks the server's IP address and returns a **403 Forbidden** error.
    
    **How to bypass this:**
    1. Install a browser extension like **Get cookies.txt LOCALLY** (Chrome/Edge) or **cookies.txt** (Firefox).
    2. Go to YouTube, log in, and export cookies as a text file.
    3. Upload the exported `cookies.txt` file below.
    """)
    cookie_file = st.file_uploader("Upload cookies.txt file", type=["txt"], key="cookie_file", label_visibility="collapsed")

col1, col2 = st.columns([4, 1])
with col1:
    analyze_btn = st.button("▶  Analyze Video", use_container_width=True)
with col2:
    if st.button("Clear", use_container_width=True):
        st.session_state.clear()
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ── Processing ────────────────────────────────────────────────────────────────
if analyze_btn and url:
    if "youtube.com" not in url and "youtu.be" not in url:
        st.error("Please enter a valid YouTube URL.")
        st.stop()

    steps = {
        "download":   "⬇ Downloading audio",
        "transcribe": "📝 Transcribing",
        "summarize":  "✦ Generating summaries",
    }
    progress_ph = st.empty()
    done = []

    def render_chips(active=None):
        html = '<div class="chips">'
        for k, label in steps.items():
            if k in done:
                html += f'<span class="chip chip-done">✓ {label}</span>'
            elif k == active:
                html += f'<span class="chip chip-active">⟳ {label}</span>'
            else:
                html += f'<span class="chip chip-idle">{label}</span>'
        html += '</div>'
        progress_ph.markdown(html, unsafe_allow_html=True)

    with tempfile.TemporaryDirectory() as tmpdir:

        render_chips("download")
        try:
            cookies_path = None
            if cookie_file is not None:
                # Save the uploaded file temporarily so yt-dlp can access it via path
                temp_cookie = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
                temp_cookie.write(cookie_file.getvalue())
                temp_cookie.close()
                cookies_path = temp_cookie.name

            try:
                with st.spinner("Fetching audio from YouTube..."):
                    audio_path, video_title, duration = download_audio(url, tmpdir, cookies_path=cookies_path)
            finally:
                # Always clean up the temporary cookie file if created
                if cookies_path and os.path.exists(cookies_path):
                    try:
                        os.remove(cookies_path)
                    except Exception:
                        pass

            done.append("download")
            render_chips("transcribe")
            st.success(f"✓  **{video_title}** · {format_duration(duration)}")
        except Exception as e:
            st.error(f"**Download failed:** {e}")
            st.stop()

        try:
            with st.spinner("Transcribing via Groq Whisper..."):
                chunks = chunk_audio_file(audio_path, tmpdir)
                parts = []
                for i, chunk in enumerate(chunks):
                    if len(chunks) > 1:
                        st.caption(f"Chunk {i+1}/{len(chunks)}...")
                    parts.append(transcribe_audio(chunk, groq_key))
                transcript = "\n\n".join(parts)
            done.append("transcribe")
            render_chips("summarize")
        except Exception as e:
            st.error(f"**Transcription failed:** {e}")
            if "limit" in str(e).lower() or "quota" in str(e).lower():
                st.info("💡 Groq free limit hit — wait a minute and retry.")
            st.stop()

        try:
            with st.spinner("Generating summaries with LLaMA 3.3..."):
                results = generate_summaries(transcript, video_title, groq_key)
            done.append("summarize")
            render_chips(None)
        except Exception as e:
            st.error(f"**Summarization failed:** {e}")
            st.stop()

    # ── Results ───────────────────────────────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="results-label">📋 Results</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["⚡ Quick Summary", "📖 Detailed", "🎯 Key Points", "📄 Transcript"])

    def copy_btn(text):
        escaped = text.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
        st.markdown(f"""<button class="copy-btn" onclick="navigator.clipboard.writeText(`{escaped}`).then(()=>{{
            this.textContent='✓ Copied!';setTimeout(()=>this.textContent='⎘ Copy',1600);
        }})">⎘ Copy</button>""", unsafe_allow_html=True)

    with tab1:
        st.markdown(f'<div class="out-card">{results["short"]}</div>', unsafe_allow_html=True)
        copy_btn(results["short"])

    with tab2:
        st.markdown(f'<div class="out-card">{results["detailed"]}</div>', unsafe_allow_html=True)
        copy_btn(results["detailed"])

    with tab3:
        bullets_html = "<ul>" + "".join(f"<li>{b}</li>" for b in results["bullets"]) + "</ul>"
        st.markdown(f'<div class="out-card">{bullets_html}</div>', unsafe_allow_html=True)
        copy_btn("\n".join(f"• {b}" for b in results["bullets"]))

    with tab4:
        st.markdown(
            f'<div class="out-card" style="max-height:420px;overflow-y:auto;'
            f'font-family:\'Space Mono\',monospace;font-size:0.8rem;">'
            f'{transcript.replace(chr(10), "<br>")}</div>',
            unsafe_allow_html=True
        )
        copy_btn(transcript)

elif analyze_btn and not url:
    st.warning("Paste a YouTube URL first.")

st.markdown('<div class="footer">VidMind · Groq Whisper + LLaMA 3.3 · Built with Streamlit</div>', unsafe_allow_html=True)