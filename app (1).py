import streamlit as st
from PIL import Image
import io

st.set_page_config(page_title="Image Editor", page_icon=None, layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&display=swap');

/* ── Global ──────────────────────────────────────────── */
html, body, [class*="css"], button, input, textarea {
    font-family: "JetBrains Mono", ui-monospace, SFMono-Regular,
                 Menlo, Monaco, Consolas, monospace !important;
}

/* ── Background ──────────────────────────────────────── */
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
.main {
    background: #0a0a0a !important;
}

[data-testid="stHeader"] {
    background: #0a0a0a !important;
    border-bottom: 1px solid rgba(255,255,255,0.06) !important;
}

/* ── Layout ──────────────────────────────────────────── */
.block-container {
    max-width: 640px !important;
    padding-top: 4rem !important;
    padding-bottom: 5rem !important;
}

/* ── Headings ────────────────────────────────────────── */
h1 {
    font-size: 1.6rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.2rem !important;
    color: #ffffff !important;
    text-transform: uppercase !important;
    margin-bottom: 0.4rem !important;
}
h2, h3 {
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    color: #ffffff !important;
    letter-spacing: 0.25rem !important;
    text-transform: uppercase !important;
    margin-top: 2rem !important;
}

p, label, span {
    color: #8a8a8a !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.05rem !important;
}

/* ── Captions ────────────────────────────────────────── */
[data-testid="stCaptionContainer"] p {
    color: #5a5a5a !important;
    font-size: 0.65rem !important;
    font-weight: 400 !important;
    text-align: center;
    letter-spacing: 0.3rem !important;
    text-transform: uppercase;
}

/* ── File uploader ───────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 0 !important;
    padding: 1.2rem 1rem !important;
    transition: border-color 0.15s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(255,255,255,0.4) !important;
}
[data-testid="stFileUploader"] label {
    font-size: 0.7rem !important;
    font-weight: 500 !important;
    color: #ffffff !important;
    letter-spacing: 0.25rem !important;
    text-transform: uppercase !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small {
    color: #5a5a5a !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.05rem !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    border: 1px dashed rgba(255,255,255,0.10) !important;
    border-radius: 0 !important;
}

/* ── Browse button ───────────────────────────────────── */
[data-testid="stFileUploader"] button {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 0 !important;
    color: #ffffff !important;
    font-size: 0.65rem !important;
    font-weight: 500 !important;
    padding: 0.4rem 1.2rem !important;
    letter-spacing: 0.2rem !important;
    text-transform: uppercase !important;
    transition: all 0.15s ease !important;
}
[data-testid="stFileUploader"] button:hover {
    background: #ffffff !important;
    color: #0a0a0a !important;
    border-color: #ffffff !important;
}

/* ── Download button ─────────────────────────────────── */
[data-testid="stDownloadButton"] button {
    background: transparent !important;
    color: #ffffff !important;
    border: 1px solid #ffffff !important;
    border-radius: 0 !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    padding: 0.85rem 2rem !important;
    width: 100% !important;
    letter-spacing: 0.3rem !important;
    text-transform: uppercase !important;
    transition: all 0.15s ease !important;
    box-shadow: none !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: #ffffff !important;
    color: #0a0a0a !important;
}
[data-testid="stDownloadButton"] button:active {
    background: #d0d0d0 !important;
}

/* ── Spinner ─────────────────────────────────────────── */
[data-testid="stSpinner"] p {
    color: #5a5a5a !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.2rem !important;
    text-transform: uppercase !important;
}

/* ── Divider ─────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.06) !important;
    margin: 2.5rem 0 !important;
}

/* ── Images ──────────────────────────────────────────── */
[data-testid="stImage"] img {
    border-radius: 0 !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    box-shadow: 0 0 30px rgba(0,0,0,0.6) !important;
}

/* ── Hide Streamlit chrome ───────────────────────────── */
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── Cached helpers ─────────────────────────────────────
PROC_SIZE = (1080, 2400)
PREVIEW_MAX = 400


@st.cache_data(show_spinner=False)
def make_preview(file_bytes: bytes) -> Image.Image:
    """Decode once and downscale for fast on-screen preview."""
    img = Image.open(io.BytesIO(file_bytes))
    img.thumbnail((PREVIEW_MAX, PREVIEW_MAX), Image.BILINEAR)
    return img


@st.cache_data(show_spinner=False)
def process_images(base_bytes: bytes, source_bytes: bytes) -> bytes:
    """Run the full crop+paste pipeline and return JPEG bytes. Cached by inputs."""
    base   = Image.open(io.BytesIO(base_bytes)).convert("RGBA").resize(PROC_SIZE, Image.LANCZOS)
    source = Image.open(io.BytesIO(source_bytes)).convert("RGBA").resize(PROC_SIZE, Image.LANCZOS)

    section1 = source.crop((0, 581, 1080, 2400))
    section2 = source.crop((456, 1018, 688, 1082))

    base.paste(section1, (0, 347), section1)
    base.paste(section2, (152, 910), section2)

    buf = io.BytesIO()
    base.convert("RGB").save(buf, format="JPEG", quality=90, optimize=True)
    return buf.getvalue()


# ─── UI ─────────────────────────────────────────────────
st.markdown("<h1>Image Editor</h1>", unsafe_allow_html=True)
st.markdown(
    '<p style="color:#5a5a5a;font-size:0.7rem;margin-top:-0.2rem;'
    'margin-bottom:3rem;letter-spacing:0.2rem;text-transform:uppercase;">'
    '— Upload · Process · Download —</p>',
    unsafe_allow_html=True
)

base_file   = st.file_uploader("Base Image",   type=["png", "jpg", "jpeg", "webp"])
source_file = st.file_uploader("Source Image", type=["png", "jpg", "jpeg", "webp"])

if base_file and source_file:
    base_bytes   = base_file.getvalue()
    source_bytes = source_file.getvalue()

    col1, col2 = st.columns(2)
    with col1:
        st.caption("Base")
        st.image(make_preview(base_bytes), width="stretch")
    with col2:
        st.caption("Source")
        st.image(make_preview(source_bytes), width="stretch")

    st.divider()

    with st.spinner("Processing"):
        result_bytes = process_images(base_bytes, source_bytes)

    st.markdown("<h3>Result</h3>", unsafe_allow_html=True)
    st.image(result_bytes, width="stretch")

    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label="Download",
        data=result_bytes,
        file_name="edited_image.jpg",
        mime="image/jpeg",
        use_container_width=True,
    )

else:
    st.markdown("""
    <div style="
        background: transparent;
        border: 1px dashed rgba(255,255,255,0.12);
        border-radius: 0;
        padding: 3.5rem 2rem;
        text-align: center;
        margin-top: 1rem;
    ">
        <p style="font-size:0.75rem;font-weight:500;color:#ffffff;
                  margin:0 0 0.6rem;letter-spacing:0.3rem;text-transform:uppercase;">
            Awaiting Input
        </p>
        <p style="font-size:0.65rem;color:#5a5a5a;margin:0;
                  letter-spacing:0.25rem;text-transform:uppercase;">
            Base &nbsp;·&nbsp; Source
        </p>
    </div>
    """, unsafe_allow_html=True)
