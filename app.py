import html
import json
from io import BytesIO

import streamlit as st
import streamlit.components.v1 as components
from gtts import gTTS

from translator import get_languages, translate_text

MAX_CHARS = 500

st.set_page_config(
    page_title="Language Translation Tool",
    page_icon="🌍",
    layout="centered",
)

# ---------- Custom styling ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 820px; }

    .hero {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 55%, #06B6D4 100%);
        border-radius: 20px;
        padding: 2.2rem 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 12px 30px rgba(79, 70, 229, 0.28);
        margin-bottom: 1.6rem;
    }
    .hero h1 { margin: 0; font-size: 2.1rem; font-weight: 700; color: white; }
    .hero p { margin: .5rem 0 0 0; font-size: 1.02rem; opacity: .92; color: white; }

    .section-label {
        font-size: .78rem; font-weight: 600; letter-spacing: .06em;
        text-transform: uppercase; color: #6B7280; margin-bottom: .2rem;
    }

    div[data-testid="stTextArea"] textarea {
        border-radius: 14px; border: 1.5px solid #E5E7EB;
        padding: 1rem; font-size: 1.05rem; background: #FFFFFF;
    }
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #4F46E5; box-shadow: 0 0 0 3px rgba(79, 70, 229, .15);
    }
    div[data-baseweb="select"] > div { border-radius: 12px; }

    .stButton > button {
        border-radius: 12px; font-weight: 600; padding: .65rem 1rem;
        border: 1.5px solid #E5E7EB; transition: all .15s ease;
    }
    .stButton > button:hover { border-color: #4F46E5; color: #4F46E5; transform: translateY(-1px); }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4F46E5, #7C3AED);
        color: white; border: none; box-shadow: 0 6px 16px rgba(79, 70, 229, .3);
    }
    .stButton > button[kind="primary"]:hover { color: white; box-shadow: 0 8px 22px rgba(79, 70, 229, .4); }

    .result-card {
        background: #FFFFFF; border: 1.5px solid #E0E7FF; border-left: 5px solid #4F46E5;
        border-radius: 14px; padding: 1.1rem 1.3rem; margin-top: 1rem;
        box-shadow: 0 6px 18px rgba(17, 24, 39, .06);
    }
    .result-label {
        font-size: .75rem; font-weight: 600; letter-spacing: .06em;
        text-transform: uppercase; color: #4F46E5; margin-bottom: .4rem;
    }
    .result-text { font-size: 1.15rem; line-height: 1.6; color: #111827; word-wrap: break-word; }

    .footer { text-align: center; color: #9CA3AF; font-size: .82rem; margin-top: 2.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Helpers ----------
@st.cache_data
def load_languages():
    """Return {'French': 'fr', ...} with display-friendly names."""
    return {name.title(): code for name, code in get_languages().items()}


def swap_languages():
    st.session_state.src, st.session_state.tgt = (
        st.session_state.tgt,
        st.session_state.src,
    )


def text_to_speech(text, lang_code):
    buffer = BytesIO()
    gTTS(text=text, lang=lang_code).write_to_fp(buffer)
    return buffer.getvalue()


def copy_button(text):
    """A styled 'Copy' button that puts the text in the clipboard."""
    payload = json.dumps(text).replace("</", "<\\/")
    components.html(
        f"""
        <button id="copy-btn" style="
            width:100%; padding:11px 16px; border-radius:12px; cursor:pointer;
            border:1.5px solid #E5E7EB; background:#fff; color:#111827;
            font-family:Inter,sans-serif; font-weight:600; font-size:14px;">
            📋 Copy translation
        </button>
        <script>
        const text = {payload};
        const btn = document.getElementById('copy-btn');
        btn.addEventListener('click', async () => {{
            try {{
                await navigator.clipboard.writeText(text);
            }} catch (e) {{
                const area = document.createElement('textarea');
                area.value = text; document.body.appendChild(area);
                area.select(); document.execCommand('copy'); area.remove();
            }}
            btn.textContent = '✅ Copied!';
            setTimeout(() => btn.textContent = '📋 Copy translation', 1800);
        }});
        </script>
        """,
        height=52,
    )


# ---------- State ----------
languages = load_languages()
names = sorted(languages.keys())

if "src" not in st.session_state:
    st.session_state.src = "French"
if "tgt" not in st.session_state:
    st.session_state.tgt = "English"
if "result" not in st.session_state:
    st.session_state.result = None

# ---------- Header ----------
st.markdown(
    f"""
    <div class="hero">
        <h1>🌍 Language Translation Tool</h1>
        <p>Translate text between {len(languages)} languages in one click.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Language selection ----------
col_src, col_swap, col_tgt = st.columns([5, 1.3, 5], vertical_alignment="bottom")
with col_src:
    st.markdown('<div class="section-label">From</div>', unsafe_allow_html=True)
    st.selectbox("Source language", names, key="src", label_visibility="collapsed")
with col_swap:
    st.button("⇄", on_click=swap_languages, help="Swap languages", use_container_width=True)
with col_tgt:
    st.markdown('<div class="section-label">To</div>', unsafe_allow_html=True)
    st.selectbox("Target language", names, key="tgt", label_visibility="collapsed")

# ---------- Input ----------
st.markdown('<div class="section-label" style="margin-top:1rem">Text to translate</div>', unsafe_allow_html=True)
text = st.text_area(
    "Text to translate",
    height=170,
    max_chars=MAX_CHARS,
    placeholder="Type or paste your text here...",
    label_visibility="collapsed",
)

# ---------- Translate ----------
if st.button("Translate", type="primary", use_container_width=True):
    st.session_state.result = None
    if not text.strip():
        st.warning("Please enter some text to translate.")
    elif st.session_state.src == st.session_state.tgt:
        st.warning("The source and target languages are the same. Please choose two different languages.")
    else:
        with st.spinner("Translating..."):
            try:
                result = translate_text(
                    text,
                    languages[st.session_state.src],
                    languages[st.session_state.tgt],
                )
                st.session_state.result = {
                    "text": result,
                    "lang_name": st.session_state.tgt,
                    "lang_code": languages[st.session_state.tgt],
                }
            except Exception as error:
                st.error(f"Translation failed. Please try again in a moment. ({error})")

# ---------- Result ----------
res = st.session_state.result
if res:
    safe_text = html.escape(res["text"]).replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-label">{res['lang_name']}</div>
            <div class="result-text">{safe_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_copy, col_audio = st.columns(2)
    with col_copy:
        copy_button(res["text"])
    with col_audio:
        if st.button("🔊 Listen", use_container_width=True):
            try:
                st.audio(text_to_speech(res["text"], res["lang_code"]), format="audio/mp3")
            except Exception:
                st.warning("Audio is not available for this language right now.")

st.markdown(
    '<div class="footer">Built with Python &amp; Streamlit</div>',
    unsafe_allow_html=True,
)