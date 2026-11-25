import hashlib
import html
import json
import re
import socket
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import streamlit as st

st.set_page_config(
    page_title="CekIjazah • Validasi Ijazah Blockchain",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# TAMPILAN: tema "Buku Tulis & Kartu Mahasiswa"
# kertas kotak-kotak, garis tebal, bayangan keras, warna ceria
# =========================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=DM+Sans:wght@400;500;600;700&display=swap');

:root{
  --ink:#111322; --paper:#fffdf6; --muted:#4b5073;
  --blue:#3b5bff; --sky:#9bd8ff; --yellow:#ffd93d; --pink:#ff8fc2; --coral:#ff5a4e;
  --bw:3px;               /* tebal garis semua komponen */
  --sh:5px 5px 0 var(--ink); /* bayangan standar */
}

/* ---------- Dasar ---------- */
.stApp, .stApp p, .stApp label, .stApp input, .stApp textarea, .stApp button, .stApp li{font-family:'DM Sans',system-ui,sans-serif;}
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.disp{font-family:'Space Grotesk','DM Sans',sans-serif;}
.stApp{
  background-color:var(--paper);
  background-image:linear-gradient(#e3e7f7 1px,transparent 1px),linear-gradient(90deg,#e3e7f7 1px,transparent 1px);
  background-size:28px 28px; color:var(--ink);
}
.stApp [data-testid="stMarkdownContainer"] p, .stApp [data-testid="stWidgetLabel"] *{color:var(--ink);}
.stApp [data-testid="stWidgetLabel"] p{font-weight:600; font-size:.92rem;}
.stApp [data-testid="stCaptionContainer"], .stApp [data-testid="stCaptionContainer"] *{color:var(--muted) !important;}
#MainMenu, footer, [data-testid="stAppDeployButton"], .stDeployButton{display:none !important;}
header[data-testid="stHeader"]{background:transparent;}
[data-testid="stToolbar"] *, [data-testid="stSidebarCollapsedControl"] *, [data-testid="stExpandSidebarButton"] *,
[data-testid="stSidebarCollapseButton"] *{color:var(--ink) !important; fill:var(--ink) !important;}
[data-testid="stSidebarCollapsedControl"] button, [data-testid="stExpandSidebarButton"]{
  background:var(--yellow) !important; border:var(--bw) solid var(--ink) !important; border-radius:12px !important; box-shadow:3px 3px 0 var(--ink); opacity:1 !important;}
[data-testid="stSidebarCollapseButton"] button{border:2.5px solid var(--ink); border-radius:10px; background:#fff;}
[data-testid="stMain"], section.main{overflow-x:hidden;}
.block-container{max-width:1100px; padding-top:1.4rem; padding-bottom:4rem;}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"]{background:var(--yellow); border-right:var(--bw) solid var(--ink);}
[data-testid="stSidebar"] *{color:var(--ink);}
[data-testid="stSidebar"] code, .cap code{background:#fff !important; color:var(--ink) !important; border:2px solid var(--ink); border-radius:6px; padding:.05rem .35rem; font-size:.74rem;}
.crest{display:flex; align-items:center; gap:.7rem; margin-bottom:.8rem;}
.crest .emb{width:46px; height:46px; border-radius:12px; background:#fff; border:var(--bw) solid var(--ink); box-shadow:3px 3px 0 var(--ink);
  display:flex; align-items:center; justify-content:center; font-size:1.4rem;}
.crest .t{font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.3rem; line-height:1;}
.crest .s{font-size:.78rem; font-weight:600;}
.side-h{font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:.98rem; margin:1.3rem 0 .5rem;}
.cap{font-size:.8rem; font-weight:500; margin:.4rem 0; word-break:break-word; line-height:1.5;}
.status{display:inline-flex; align-items:center; gap:.45rem; padding:.28rem .85rem; border:2.5px solid var(--ink); border-radius:999px;
  font-size:.82rem; font-weight:700; background:#fff;}
.status i{width:9px; height:9px; border-radius:50%; background:var(--blue); display:inline-block; border:2px solid var(--ink);}
.status.bad i{background:var(--coral);}
.addr{font-family:ui-monospace,Menlo,Consolas,monospace; font-size:.72rem; word-break:break-all; background:#fff;
  border:2.5px solid var(--ink); border-radius:12px; padding:.55rem .7rem; margin:.5rem 0;}
.peran{display:inline-block; font-size:.8rem; font-weight:700; padding:.25rem .8rem; border:2.5px solid var(--ink); border-radius:999px; margin-top:.2rem;}
.peran.a{background:var(--pink);} .peran.m{background:var(--sky);}

/* ---------- Hero ---------- */
.hero{display:grid; grid-template-columns:minmax(0,1.25fr) minmax(0,.75fr); gap:2rem; align-items:center; padding:.5rem 0 1rem;}
.sticker{display:inline-block; background:var(--pink); border:var(--bw) solid var(--ink); border-radius:999px; padding:.3rem .95rem;
  font-weight:700; font-size:.85rem; box-shadow:3px 3px 0 var(--ink); transform:rotate(-2deg); margin-bottom:1rem;}
.hero h1{font-size:3.1rem; line-height:1.05; font-weight:700; margin:0 0 .9rem; padding:0; letter-spacing:-.02em; color:var(--ink);}
.hero h1 mark{background:linear-gradient(transparent 55%,var(--yellow) 55%); color:inherit; padding:0 .15em;}
.hero h1 .blue{color:var(--blue);}
.hero p{font-size:1.05rem; line-height:1.6; color:#2d3150; max-width:520px; margin:0;}
.mini-id{position:relative; background:#fff; border:var(--bw) solid var(--ink); border-radius:18px; box-shadow:8px 8px 0 var(--ink); transform:rotate(3deg); overflow:hidden;}
.mini-id .bar{background:var(--blue); color:#fff; font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:.75rem; letter-spacing:.12em;
  padding:.55rem 1rem; border-bottom:var(--bw) solid var(--ink);}
.mini-id .body{display:flex; gap:.9rem; padding:1rem; align-items:center;}
.ph{flex:0 0 72px; width:72px; height:84px; border:var(--bw) solid var(--ink); border-radius:12px; background:var(--yellow);
  display:flex; align-items:center; justify-content:center; font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:2rem;}
.mini-id b{display:block; font-family:'Space Grotesk',sans-serif; font-size:1.05rem;}
.mini-id small{color:var(--muted); font-weight:600;}
.code, .barcode{height:26px; margin-top:.5rem; background:repeating-linear-gradient(90deg,var(--ink) 0 2px,transparent 2px 5px,var(--ink) 5px 6px,transparent 6px 10px);}
.mini-id .stamp{position:absolute; right:12px; bottom:14px; border:var(--bw) solid var(--blue); color:var(--blue); border-radius:8px;
  font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:.85rem; padding:.1rem .5rem; transform:rotate(-12deg); background:rgba(255,255,255,.9);}

/* ---------- Langkah ---------- */
.steps{display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:1.1rem; margin:1.3rem 0 .8rem;}
.note{border:var(--bw) solid var(--ink); border-radius:14px; padding:.9rem 1rem; box-shadow:var(--sh);}
.note:nth-child(1){background:var(--yellow); transform:rotate(-.8deg);}
.note:nth-child(2){background:var(--pink); transform:rotate(.6deg);}
.note:nth-child(3){background:var(--sky); transform:rotate(-.5deg);}
.note:nth-child(4){background:#fff; transform:rotate(.8deg);}
.note .no{font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:.8rem; background:var(--ink); color:#fff; display:inline-block; padding:.05rem .55rem; border-radius:999px; margin-bottom:.4rem;}
.note b{display:block; font-family:'Space Grotesk',sans-serif; font-size:1.1rem; color:var(--ink);}
.note small{font-weight:500; color:#2d3150;}
.live{display:flex; gap:.6rem; flex-wrap:wrap; margin:1rem 0 1.4rem;}
.chip{font-size:.8rem; font-weight:700; background:#fff; border:2.5px solid var(--ink); padding:.25rem .85rem; border-radius:999px; color:var(--ink);}

/* ---------- Tab ---------- */
.stTabs div:has(> [data-baseweb="tab-list"]){overflow:visible !important;}
.stTabs [data-baseweb="tab-list"], .stTabs [role="tablist"]{gap:.7rem !important; flex-wrap:wrap; overflow:visible !important;
  padding:.4rem .4rem 1rem !important; border-bottom:none !important; background:transparent !important;}
.stTabs button[role="tab"], .stTabs [data-baseweb="tab"]{height:48px !important; padding:0 1.25rem !important; margin:0 !important;
  border:var(--bw) solid var(--ink) !important; border-radius:999px !important; background:#fff !important; box-shadow:3px 3px 0 var(--ink);
  transition:transform .1s ease, box-shadow .1s ease;}
.stTabs button[role="tab"] p{font-family:'Space Grotesk',sans-serif !important; font-weight:700 !important; font-size:1rem !important; color:var(--ink) !important; margin:0 !important;}
.stTabs button[role="tab"]:hover{transform:translate(-1px,-1px); box-shadow:4px 4px 0 var(--ink);}
.stTabs button[role="tab"][aria-selected="true"]{background:var(--yellow) !important; box-shadow:5px 5px 0 var(--ink); transform:translate(-1px,-1px);}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"]{display:none !important; height:0 !important; background:transparent !important;}
.stTabs [data-baseweb="tab-panel"]{padding-top:.6rem !important;}

/* ---------- Kartu form ---------- */
[class*="st-key-card"]{background:#fff; border:var(--bw) solid var(--ink); border-radius:18px; padding:1.5rem 1.7rem 1.7rem; box-shadow:7px 7px 0 var(--ink);}
.ct{font-family:'Space Grotesk',sans-serif; font-size:1.45rem; font-weight:700; color:var(--ink);}
.cd{color:#3d4263; font-size:.95rem; margin:.25rem 0 1.1rem; line-height:1.55;}
.role{display:inline-block; font-size:.72rem; font-weight:700; padding:.15rem .7rem; border:2.5px solid var(--ink); border-radius:999px; margin-left:.6rem; vertical-align:middle; color:var(--ink);}
.role.pub{background:var(--sky);} .role.auth{background:var(--pink);} .role.mhs{background:var(--yellow);}

/* ---------- Input (satu garis tebal, tidak dobel) ---------- */
.stApp [data-baseweb="input"], .stApp [data-baseweb="base-input"], .stApp [data-baseweb="textarea"]{background:#fff !important; border-radius:12px !important;}
.stApp [data-baseweb="input"]{border:var(--bw) solid var(--ink) !important; box-shadow:3px 3px 0 var(--ink);}
.stApp [data-baseweb="base-input"]{border:none !important;}
.stApp [data-baseweb="input"]:focus-within{border-color:var(--blue) !important; box-shadow:3px 3px 0 var(--blue);}
.stApp input, .stApp textarea{color:var(--ink) !important; -webkit-text-fill-color:var(--ink) !important; background:#fff !important; font-weight:500;}
.stApp input::placeholder, .stApp textarea::placeholder{color:#8a8fa8 !important; -webkit-text-fill-color:#8a8fa8 !important; opacity:1;}
[data-testid="stNumberInput"] button{background:#fff !important; color:var(--ink) !important; border-left:2px solid var(--ink) !important;}
[data-testid="stNumberInput"] button svg{fill:var(--ink) !important;}

/* ---------- Dropdown ---------- */
[data-baseweb="select"] > div{background:#fff !important; border:var(--bw) solid var(--ink) !important; border-radius:12px !important; min-height:46px; box-shadow:3px 3px 0 var(--ink);}
[data-baseweb="select"] > div *{background-color:transparent !important; color:var(--ink) !important;}
[data-baseweb="select"] svg{fill:var(--ink) !important;}
[data-baseweb="popover"] [data-baseweb="menu"], [data-baseweb="popover"] ul{background:#fff !important; border:var(--bw) solid var(--ink); border-radius:12px;}
[data-baseweb="popover"] li, [data-baseweb="popover"] li *{color:var(--ink) !important; background:transparent;}
[data-baseweb="popover"] li:hover, [data-baseweb="popover"] li[aria-selected="true"]{background:var(--yellow) !important;}

/* ---------- Upload file ---------- */
[data-testid="stFileUploaderDropzone"]{border:var(--bw) dashed var(--ink); background:#f4f6ff; border-radius:14px;}
[data-testid="stFileUploaderDropzone"] *{color:var(--ink);}
[data-testid="stFileUploaderDropzoneInstructions"] *{color:var(--muted) !important;}
[data-testid="stFileUploaderDropzone"] button{background:#fff !important; border:2.5px solid var(--ink) !important; border-radius:10px !important; box-shadow:2px 2px 0 var(--ink);}
[data-testid="stFileUploaderFile"], [data-testid="stFileUploaderFile"] *{color:var(--ink) !important;}

/* ---------- Tombol ---------- */
.stButton button{border-radius:12px; padding:.7rem 1.6rem; border:var(--bw) solid var(--ink); background:#fff;
  box-shadow:var(--sh); transition:transform .1s ease, box-shadow .1s ease;}
.stButton button p{font-family:'Space Grotesk',sans-serif !important; font-weight:700 !important; font-size:1.05rem !important; margin:0 !important; color:var(--ink) !important;}
.stButton button[kind="primary"], .stButton button[data-testid="stBaseButton-primary"]{background:var(--blue) !important;}
.stButton button[kind="primary"] p, .stButton button[data-testid="stBaseButton-primary"] p{color:#fff !important;}
.stButton button:hover{transform:translate(3px,3px); box-shadow:2px 2px 0 var(--ink) !important; border-color:var(--ink) !important;}
.stButton button:focus-visible{outline:3px solid var(--pink); outline-offset:3px;}

/* ---------- Notifikasi ---------- */
[data-testid="stAlert"]{background:#fff4c2 !important; border:var(--bw) solid var(--ink); border-radius:14px; box-shadow:3px 3px 0 var(--ink);}
[data-testid="stAlert"] *{color:var(--ink) !important;}

.hashrow{background:#f4f6ff; border:2.5px dashed var(--ink); border-radius:12px; padding:.65rem .85rem; margin-top:.8rem; display:flex; gap:.7rem; align-items:flex-start;}
.hashrow b{font-size:.78rem; white-space:nowrap; color:var(--ink);}
.hashrow code{font-size:.72rem; word-break:break-all; background:transparent !important; color:var(--ink) !important; border:none !important; padding:0 !important;}

/* ---------- Kartu hasil verifikasi ---------- */
.idcard{position:relative; background:#fff; border:var(--bw) solid var(--ink); border-radius:20px; margin:1.4rem 0; overflow:hidden; box-shadow:8px 8px 0 var(--ink);}
.idcard .bar{display:flex; justify-content:space-between; gap:1rem; background:var(--blue); color:#fff; padding:.7rem 1.3rem;
  border-bottom:var(--bw) solid var(--ink); font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:.82rem; letter-spacing:.1em;}
.idcard.revoked .bar{background:var(--coral);} .idcard.unknown .bar{background:var(--yellow); color:var(--ink);}
.idcard .main{display:flex; gap:1.3rem; padding:1.4rem 1.5rem .8rem; align-items:center; flex-wrap:wrap;}
.idcard .ph{flex:0 0 96px; width:96px; height:112px; font-size:2.6rem;}
.idcard .info{flex:1 1 260px;}
.idcard .st{font-weight:700; font-size:.85rem; color:var(--muted); margin-bottom:.15rem;}
.idcard .nm{font-family:'Space Grotesk',sans-serif; font-size:2rem; font-weight:700; line-height:1.1; margin-bottom:.2rem; color:var(--ink);}
.idcard .nimx{font-weight:700; color:var(--blue);} .idcard.revoked .nimx{color:var(--coral);}
.idcard .ket{color:#3d4263; line-height:1.5;}
.idcard .stamp{flex:0 0 auto; border:5px double var(--blue); color:var(--blue); border-radius:14px; padding:.35rem 1rem;
  font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.7rem; transform:rotate(-9deg); text-align:center; line-height:1.1;}
.idcard .stamp small{display:block; font-size:.62rem; letter-spacing:.14em;}
.idcard.revoked .stamp{border-color:var(--coral); color:var(--coral);}
.idcard.unknown .stamp{border-color:#b58a00; color:#8a6800;}
.idcard .grid{display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:.9rem 1.4rem; padding:1rem 1.5rem; border-top:var(--bw) dashed var(--ink); margin-top:.6rem;}
.idcard .grid span{display:block; font-size:.72rem; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:.06em;}
.idcard .grid div{font-weight:700; word-break:break-word; color:var(--ink);}
.idcard .mono{font-family:ui-monospace,Menlo,Consolas,monospace; font-size:.74rem; font-weight:500;}
.idcard .barcode{margin:0 1.5rem;}
.idcard .foot{padding:.5rem 1.5rem 1.1rem; font-size:.7rem; color:var(--muted); word-break:break-all;}

.slip{background:var(--yellow); border:var(--bw) solid var(--ink); border-radius:14px; padding:1rem 1.2rem; margin-top:1rem; box-shadow:var(--sh);}
.slip b{display:block; font-family:'Space Grotesk',sans-serif; font-size:1.05rem; margin-bottom:.3rem; color:var(--ink);}
.slip code{font-size:.76rem; word-break:break-all; background:#fff !important; color:var(--ink) !important; border:2px solid var(--ink); border-radius:6px; padding:.1rem .35rem;}

.chk{display:flex; gap:.9rem; padding:.85rem 0; border-bottom:var(--bw) dashed #d4d8ee;}
.chk:last-child{border-bottom:none;}
.chk b{color:var(--ink);}
.chk code{background:var(--ink) !important; color:#fff !important; border-radius:6px; padding:.1rem .4rem;}
.chk .n{flex:0 0 36px; height:36px; border-radius:10px; border:var(--bw) solid var(--ink); background:var(--yellow);
  display:flex; align-items:center; justify-content:center; font-family:'Space Grotesk',sans-serif; font-weight:700; color:var(--ink);}
.chk.done .n{background:var(--blue); color:#fff;}

@media (max-width:1280px){ .hero{grid-template-columns:1fr;} .mini-id{max-width:360px; margin:.4rem 0 .8rem 1rem;} }
@media (max-width:760px){ .hero h1{font-size:2.3rem;} .mini-id{display:none;} .idcard .nm{font-size:1.6rem;} .idcard .stamp{font-size:1.3rem;} }
@media (prefers-reduced-motion:reduce){ .stButton button, .stTabs button[role="tab"]{transition:none;} }

/* ---------- Pilihan peran (radio) ---------- */
[data-testid="stSidebar"] [role="radiogroup"]{gap:.55rem !important;}
[data-testid="stSidebar"] [role="radiogroup"] label{background:#fff; border:2.5px solid var(--ink); border-radius:12px; padding:.55rem .85rem; margin:0; width:100%;
  box-shadow:3px 3px 0 var(--ink); cursor:pointer;}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:var(--pink);}
[data-testid="stSidebar"] [role="radiogroup"] label p{font-weight:700; font-size:.92rem; margin:0;}

/* ---------- Perbaikan tab & input (tahan beda versi Streamlit) ---------- */
div:has(> [role="tablist"]){overflow:visible !important;}
[role="tablist"]{gap:.7rem !important; flex-wrap:wrap; overflow:visible !important; padding:.4rem .4rem 1rem !important;
  border-bottom:none !important; background:transparent !important;}
[role="tablist"] > div:empty, [data-baseweb="tab-highlight"], [data-baseweb="tab-border"]{display:none !important; height:0 !important;}
button[role="tab"]{height:48px !important; padding:0 1.25rem !important; margin:0 !important; border:var(--bw) solid var(--ink) !important;
  border-radius:999px !important; background:#fff !important; box-shadow:3px 3px 0 var(--ink); transition:transform .1s ease, box-shadow .1s ease;}
button[role="tab"] p{font-family:'Space Grotesk',sans-serif !important; font-weight:700 !important; font-size:1rem !important; color:var(--ink) !important; margin:0 !important;}
button[role="tab"]:hover{transform:translate(-1px,-1px); box-shadow:4px 4px 0 var(--ink);}
button[role="tab"][aria-selected="true"]{background:var(--yellow) !important; box-shadow:5px 5px 0 var(--ink); transform:translate(-1px,-1px);}
[data-testid="stTextInputRootElement"], [data-testid="stNumberInputContainer"]{border:var(--bw) solid var(--ink) !important; border-radius:12px !important;
  background:#fff !important; box-shadow:3px 3px 0 var(--ink); overflow:hidden;}
[data-testid="stTextInputRootElement"]:focus-within, [data-testid="stNumberInputContainer"]:focus-within{border-color:var(--blue) !important; box-shadow:3px 3px 0 var(--blue);}
[data-testid="stTextInputRootElement"] > div, [data-testid="stTextInputRootElement"] > div > div,
[data-testid="stNumberInputContainer"] > div, [data-testid="stNumberInputContainer"] > div > div{border:none !important; box-shadow:none !important; background:transparent !important;}

/* ---------- Dashboard ---------- */
.stats{display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:1.1rem; margin:1rem 0 1.6rem;}
.stat{border:var(--bw) solid var(--ink); border-radius:16px; padding:1rem 1.2rem; box-shadow:var(--sh);}
.stat:nth-child(1){background:var(--yellow);} .stat:nth-child(2){background:var(--pink);}
.stat:nth-child(3){background:var(--sky);} .stat:nth-child(4){background:#fff;}
.stat .v{font-family:'Space Grotesk',sans-serif; font-size:2.6rem; font-weight:700; line-height:1.1; color:var(--ink);}
.stat .l{font-weight:700; color:var(--ink);} .stat small{color:#2d3150; font-weight:500;}
[data-testid="stDataFrame"]{border:var(--bw) solid var(--ink); border-radius:12px; overflow:hidden;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# Buat .streamlit/config.toml otomatis (tema terang) kalau belum ada
_CFG = Path(".streamlit/config.toml")
if not _CFG.exists():
    try:
        _CFG.parent.mkdir(exist_ok=True)
        _CFG.write_text(
            '[theme]\nbase = "light"\nprimaryColor = "#3b5bff"\nbackgroundColor = "#fffdf6"\n'
            'secondaryBackgroundColor = "#ffffff"\ntextColor = "#111322"\nfont = "sans serif"\n\n'
            '[server]\nheadless = true\n',
            encoding="utf-8",
        )
        st.warning("File tema dibuat otomatis di .streamlit/config.toml. Hentikan Streamlit (Ctrl+C), lalu jalankan lagi `streamlit run app.py` supaya warnanya rapi.")
    except Exception:
        pass


# =========================================================
# HELPER
# =========================================================
def esc(x) -> str:
    return html.escape(str(x))


def hash_file(file) -> bytes:
    return hashlib.sha256(file.getvalue()).digest()


def rapikan_error(e: Exception) -> str:
    pesan = str(e)
    for kunci in ("reverted with reason string", "revert"):
        if kunci in pesan:
            pesan = pesan.split(kunci, 1)[1]
            break
    return pesan.strip(" :'\"")[:300] or "Transaksi ditolak oleh kontrak."


def judul_kartu(judul: str, deskripsi: str, peran_label: str, kelas: str):
    st.markdown(
        f'<div class="ct">{judul}<span class="role {kelas}">{peran_label}</span></div>'
        f'<div class="cd">{deskripsi}</div>',
        unsafe_allow_html=True,
    )


def baris_hash(h: bytes):
    st.markdown(
        f'<div class="hashrow"><b>🔐 Sidik jari SHA-256</b><code>{h.hex()}</code></div>',
        unsafe_allow_html=True,
    )


def baca_deployment() -> str:
    """Ambil alamat kontrak terakhir dari deployment.json (ditulis oleh scripts/deploy.js)."""
    try:
        data = json.loads(Path("deployment.json").read_text(encoding="utf-8"))
        return str(data.get("address", "")).strip()
    except Exception:
        return ""


PERAN_PERUSAHAAN = "🏢 Perusahaan / Umum"
PERAN_MAHASISWA = "🎒 Mahasiswa"
PERAN_KAMPUS = "🏛️ Kampus (Authority)"
PERAN_DASHBOARD = "📊 Dashboard"

INFO_PERAN = {
    PERAN_DASHBOARD: dict(
        sticker="📊 Statistik platform",
        h1='Sudah berapa ijazah <mark>tercatat</mark> <span class="blue">di sini</span>?',
        p="Angka di halaman ini dibaca langsung dari smart contract, jadi bisa dipakai sebagai bukti "
          "berapa banyak ijazah yang pernah didaftarkan lewat aplikasi ini.",
        langkah=[],
    ),
    PERAN_PERUSAHAAN: dict(
        sticker="🏢 Untuk HR &amp; perusahaan",
        h1='Ijazah pelamar <mark>asli</mark>? Pastikan dalam <span class="blue">10 detik</span>.',
        p="Tanpa daftar, tanpa wallet. Unggah PDF ijazah dan masukkan nomor ijazahnya, "
          "hasilnya langsung muncul lengkap dengan bukti verifikasi yang bisa diunduh.",
        langkah=[("Minta berkas", "PDF + nomor ijazah dari pelamar"),
                 ("Unggah", "Di tab Verifikasi"),
                 ("Lihat hasil", "Asli, dicabut, atau tidak cocok"),
                 ("Simpan bukti", "Unduh bukti verifikasi")],
    ),
    PERAN_MAHASISWA: dict(
        sticker="🎒 Untuk mahasiswa &amp; alumni",
        h1='Ijazahmu, <mark>kamu</mark> yang pegang. Buktikan <span class="blue">kapan saja</span>.',
        p="Klaim ijazahmu dengan wallet yang didaftarkan kampus, lalu bagikan tautan atau QR code "
          "ke perusahaan supaya mereka bisa mengecek sendiri.",
        langkah=[("Klaim", "Pakai wallet yang terdaftar"),
                 ("Bagikan", "Tautan atau QR code"),
                 ("Dicek HR", "Perusahaan verifikasi sendiri")],
    ),
    PERAN_KAMPUS: dict(
        sticker="🏛️ Untuk admin kampus",
        h1='Terbitkan ijazah yang <mark>tak bisa</mark> <span class="blue">dipalsukan</span>.',
        p="Daftarkan mahasiswa, terbitkan ijazah dengan sidik jari PDF-nya, "
          "dan cabut kalau ada masalah. Semua tercatat permanen di blockchain.",
        langkah=[("Registrasi", "Daftarkan mahasiswa"),
                 ("Terbitkan", "Hash PDF dicatat on-chain"),
                 ("Cabut", "Kalau ijazah bermasalah")],
    ),
}


def pakai_alamat_deploy():
    st.session_state["alamat_kontrak"] = baca_deployment()


# =========================================================
# KONEKSI
# =========================================================
try:
    from web3 import Web3
except Exception as e:
    st.error(f"Library web3 belum terpasang: {e}")
    st.code('python -m pip install "streamlit>=1.50" "web3>=7.0"')
    st.stop()

RPC_URL = "http://127.0.0.1:8545"
ABI_PATH = Path("artifacts/contracts/ValiditasIjazah.sol/ValiditasIjazah.json")

w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={"timeout": 5}))
try:
    terhubung = w3.is_connected()
except Exception:
    terhubung = False

# nilai awal: peran Perusahaan (pintu masuk publik), alamat kontrak dari deployment.json
alamat_deploy = baca_deployment()
if "peran" not in st.session_state:
    st.session_state["peran"] = PERAN_PERUSAHAAN
if "alamat_kontrak" not in st.session_state:
    st.session_state["alamat_kontrak"] = alamat_deploy

akun_list, pilihan, akun = [], 0, None

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown(
        '<div class="crest"><div class="emb">🎓</div>'
        '<div><div class="t">CekIjazah</div><div class="s">Anti ijazah palsu</div></div></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-h">Masuk sebagai</div>', unsafe_allow_html=True)
    peran = st.radio(
        "Masuk sebagai",
        [PERAN_PERUSAHAAN, PERAN_MAHASISWA, PERAN_KAMPUS, PERAN_DASHBOARD],
        key="peran",
        label_visibility="collapsed",
    )
    butuh_wallet = peran in (PERAN_MAHASISWA, PERAN_KAMPUS)

    st.markdown('<div class="side-h">Jaringan</div>', unsafe_allow_html=True)
    if terhubung:
        st.markdown('<span class="status"><i></i>Terhubung</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="cap">{esc(RPC_URL)}</div>', unsafe_allow_html=True)

        if butuh_wallet:
            st.markdown('<div class="side-h">Akun wallet</div>', unsafe_allow_html=True)
            akun_list = w3.eth.accounts
            if akun_list:
                pilihan = st.selectbox(
                    "Pilih akun",
                    options=list(range(len(akun_list))),
                    format_func=lambda i: f"Account #{i}",
                    label_visibility="collapsed",
                )
                akun = akun_list[pilihan]
                saldo = w3.from_wei(w3.eth.get_balance(akun), "ether")
                st.markdown(f'<div class="addr">{akun}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="cap">Saldo: <b>{float(saldo):,.4f} ETH</b></div>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status bad"><i></i>Belum terhubung</span>', unsafe_allow_html=True)

    st.markdown('<div class="side-h">Smart contract</div>', unsafe_allow_html=True)
    alamat_kontrak = st.text_input(
        "Alamat kontrak hasil deploy",
        key="alamat_kontrak",
        placeholder="0x...",
        label_visibility="collapsed",
    ).strip()
    if alamat_deploy and alamat_kontrak.lower() != alamat_deploy.lower():
        st.button("🔄 Pakai alamat dari deployment.json", on_click=pakai_alamat_deploy)
    elif alamat_deploy:
        st.markdown('<div class="cap">✓ Sama dengan <code>deployment.json</code></div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="cap">Alamat didapat dari <code>npx hardhat run scripts/deploy.js --network localhost</code></div>',
            unsafe_allow_html=True,
        )

# =========================================================
# HERO + LANGKAH (menyesuaikan peran)
# =========================================================
info = INFO_PERAN[peran]
langkah_html = "".join(
    f'<div class="note"><span class="no">{i}</span><b>{esc(j)}</b><small>{esc(k)}</small></div>'
    for i, (j, k) in enumerate(info["langkah"], 1)
)
steps_html = f'<div class="steps">{langkah_html}</div>' if langkah_html else ""
st.markdown(
    f"""
<div class="hero">
  <div>
    <div class="sticker">{info["sticker"]}</div>
    <h1>{info["h1"]}</h1>
    <p>{info["p"]}</p>
  </div>
  <div class="mini-id">
    <div class="bar">KARTU MAHASISWA</div>
    <div class="body"><div class="ph">🎓</div>
      <div><b>NAMA MAHASISWA</b><small>NIM 2021•••••••</small><div class="code"></div></div></div>
    <div class="stamp">VERIFIED</div>
    <div style="height:2.6rem"></div>
  </div>
</div>
{steps_html}
""",
    unsafe_allow_html=True,
)
if terhubung:
    st.markdown(
        f'<div class="live"><span class="chip">Chain ID {w3.eth.chain_id}</span>'
        f'<span class="chip">Block terbaru #{w3.eth.block_number}</span>'
        f'<span class="chip">{esc(RPC_URL)}</span></div>',
        unsafe_allow_html=True,
    )
else:
    st.write("")


# =========================================================
# CEK KESIAPAN
# =========================================================
def panduan(langkah):
    baris = ""
    for i, (selesai, judul, ket) in enumerate(langkah, 1):
        baris += (
            f'<div class="chk {"done" if selesai else ""}"><div class="n">{"✓" if selesai else i}</div>'
            f"<div><b>{judul}</b><br><span style='color:#3d4263'>{ket}</span></div></div>"
        )
    with st.container(key="card_setup"):
        st.markdown(
            '<div class="ct">Siap-siap dulu, bentar aja 🚀</div>'
            '<div class="cd">Selesaikan langkah ini supaya fitur ijazah bisa dipakai.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(baris, unsafe_allow_html=True)
    st.stop()


abi_ada = ABI_PATH.exists()
alamat_valid = bool(alamat_kontrak) and Web3.is_address(alamat_kontrak)
kontrak_ada = False
if terhubung and alamat_valid:
    try:
        kontrak_ada = len(w3.eth.get_code(Web3.to_checksum_address(alamat_kontrak))) > 0
    except Exception:
        kontrak_ada = False

if not (terhubung and abi_ada and alamat_valid and kontrak_ada):
    panduan(
        [
            (terhubung, "Nyalakan blockchain lokal",
             "Jalankan <code>npx hardhat node</code> di terminal lain, lalu refresh halaman ini."),
            (abi_ada, "Compile smart contract",
             "Jalankan <code>npx hardhat compile</code> di folder proyek ini."),
            (alamat_valid and kontrak_ada, "Masukkan alamat kontrak",
             "Setelah <code>hardhat node</code> di-restart, deploy ulang lalu klik tombol "
             "<b>Pakai alamat dari deployment.json</b> di sidebar."),
        ]
    )

abi = json.loads(ABI_PATH.read_text(encoding="utf-8"))["abi"]
alamat_cs = Web3.to_checksum_address(alamat_kontrak)
kontrak = w3.eth.contract(address=alamat_cs, abi=abi)

if butuh_wallet and akun is None:
    st.error("Tidak ada akun dari node Hardhat.")
    st.stop()


def kirim_transaksi(fungsi):
    """Kirim transaksi dari akun terpilih dan tampilkan hasilnya."""
    try:
        with st.spinner("Menunggu transaksi masuk ke block..."):
            tx_hash = fungsi.transact({"from": akun})
            w3.eth.wait_for_transaction_receipt(tx_hash)
        st.toast("Transaksi berhasil", icon="✅")
        st.markdown(
            f'<div class="slip"><b>🎉 Berhasil dicatat di blockchain</b>'
            f"Bukti transaksi:<br><code>{w3.to_hex(tx_hash)}</code></div>",
            unsafe_allow_html=True,
        )
    except Exception as e:
        st.error(f"Transaksi ditolak: {rapikan_error(e)}")


# =========================================================
# DATA DARI SMART CONTRACT + TAUTAN
# =========================================================
def ip_lokal() -> str:
    """Alamat IP laptop di jaringan Wi-Fi (supaya QR bisa discan dari HP)."""
    try:
        sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sk.connect(("8.8.8.8", 80))
        ip = sk.getsockname()[0]
        sk.close()
        return ip
    except Exception:
        return "localhost"


def ambil_log(nama_event: str):
    ev = getattr(kontrak.events, nama_event)()
    try:
        return ev.get_logs(from_block=0)
    except TypeError:
        return ev.get_logs(fromBlock=0)


def ambil_ringkas(cert: str) -> dict:
    nim_d, nama_d, ipk_d, tgl_d = kontrak.functions.lihatDetailIjazah(cert).call()
    _, penerbit, waktu, diklaim, dicabut = kontrak.functions.lihatStatusIjazah(cert).call()
    return dict(cert=cert, nim=nim_d, nama=nama_d, ipk=ipk_d, tgl=tgl_d, penerbit=penerbit,
                waktu=datetime.fromtimestamp(waktu), diklaim=diklaim, dicabut=dicabut)


def ambil_riwayat_ijazah():
    """Semua ijazah yang pernah diterbitkan (ID dari event, detail dari fungsi view kontrak)."""
    hasil = []
    for lg in ambil_log("IjazahDiterbitkan"):
        try:
            x = ambil_ringkas(lg["args"]["certificateId"])
        except Exception:
            continue
        status = "Dicabut" if x["dicabut"] else ("Sudah diklaim" if x["diklaim"] else "Diterbitkan")
        hasil.append({
            "No. Ijazah": x["cert"], "Nama": x["nama"], "NIM": x["nim"], "IPK": x["ipk"],
            "Tanggal Lulus": x["tgl"], "Dicatat": x["waktu"].strftime("%d %b %Y %H:%M"), "Status": status,
        })
    return hasil


def tampilkan_ringkasan(cert: str):
    """Hasil cepat dari catatan blockchain (tanpa PDF). Muncul otomatis saat tautan/QR dibuka."""
    try:
        ada = kontrak.functions.daftarIjazah(cert).call()[9]
        x = ambil_ringkas(cert) if ada else None
    except Exception as e:
        st.error(f"Gagal membaca kontrak: {rapikan_error(e)}")
        return
    if not x:
        st.markdown(
            f"""
<div class="idcard unknown">
  <div class="bar"><span>HASIL PENCARIAN</span><span>⛓ ON-CHAIN</span></div>
  <div class="main">
    <div class="ph">?</div>
    <div class="info"><div class="st">Nomor ijazah {esc(cert)}</div>
      <div class="nm">Tidak ditemukan</div>
      <div class="ket">Cek lagi penulisan nomornya, atau ijazah ini belum pernah diterbitkan.</div></div>
    <div class="stamp">NIHIL<small>NOT FOUND</small></div>
  </div>
  <div class="barcode"></div><div class="foot">&nbsp;</div>
</div>""",
            unsafe_allow_html=True,
        )
        return
    kelas, cap, sub = ("revoked", "DICABUT", "REVOKED") if x["dicabut"] else ("valid", "TERCATAT", "ON-CHAIN")
    ket = ("Ijazah ini sudah dicabut oleh penerbit dan tidak berlaku lagi." if x["dicabut"]
           else "Ijazah ini tercatat resmi di blockchain dan masih berlaku.")
    st.markdown(
        f"""
<div class="idcard {kelas}">
  <div class="bar"><span>HASIL PENCARIAN</span><span>⛓ ON-CHAIN</span></div>
  <div class="main">
    <div class="ph">{esc(str(x["nama"]).strip()[:1].upper() or "?")}</div>
    <div class="info"><div class="st">Nomor ijazah {esc(x["cert"])}</div>
      <div class="nm">{esc(x["nama"])}</div><div class="nimx">NIM {esc(x["nim"])}</div>
      <div class="ket">{ket}</div></div>
    <div class="stamp">{cap}<small>{sub}</small></div>
  </div>
  <div class="grid">
    <div><span>IPK</span>{esc(x["ipk"])}</div>
    <div><span>Tanggal lulus</span>{esc(x["tgl"])}</div>
    <div><span>Dicatat pada</span>{x["waktu"].strftime("%d %b %Y, %H:%M")}</div>
    <div><span>Status klaim</span>{"Sudah diklaim" if x["diklaim"] else "Belum diklaim"}</div>
    <div><span>Alamat penerbit</span><div class="mono">{esc(x["penerbit"])}</div></div>
  </div>
  <div class="barcode"></div><div class="foot">&nbsp;</div>
</div>""",
        unsafe_allow_html=True,
    )
    if not x["dicabut"]:
        st.info("Ini hasil dari catatan blockchain. Untuk memastikan file PDF-nya juga asli, "
                "unggah PDF di atas lalu tekan Cek sekarang.")


def valid_ipk(teks: str) -> bool:
    t = teks.strip().replace(",", ".")
    return bool(re.fullmatch(r"\d(\.\d{1,2})?", t)) and 0 < float(t) <= 4


def valid_tanggal(teks: str) -> bool:
    try:
        datetime.strptime(teks.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False


# =========================================================
# VERIFIKASI: proses, tampilan hasil, dan bukti unduhan
# =========================================================
def tampilan_status(hasil: str):
    """-> (kelas css, cap stempel, sub-cap, judul, keterangan, teks polos untuk bukti)"""
    if hasil == "VALID":
        return ("valid", "ASLI", "VERIFIED", "Ijazah terverifikasi asli ✅",
                "Dokumen cocok dengan data yang tercatat di blockchain.", "ASLI (VALID)")
    if hasil == "DICABUT":
        return ("revoked", "DICABUT", "REVOKED", "Ijazah ini sudah dicabut ⛔",
                "Ijazah dicabut oleh penerbit dan tidak berlaku lagi.", "DICABUT")
    if hasil == "TIDAK DITEMUKAN":
        return ("unknown", "NIHIL", "NOT FOUND", "Nomor ijazah tidak ditemukan ❓",
                "Cek lagi penulisan nomornya, atau ijazah ini belum pernah diterbitkan.", "TIDAK DITEMUKAN")
    return ("revoked", "BEDA", "MISMATCH", "Dokumen tidak sesuai ⚠️",
            "Isi file PDF berbeda dengan yang diterbitkan kampus (kemungkinan dipalsukan atau diedit).",
            "TIDAK COCOK (dokumen berbeda dari yang diterbitkan)")


def proses_verifikasi(cert: str, pdf) -> dict:
    h = hash_file(pdf)
    hasil = kontrak.functions.cekStatusIjazah(cert, h).call()
    d = {
        "cert": cert, "hash": h.hex(), "hasil": hasil, "waktu": datetime.now(),
        "block": w3.eth.block_number, "chain": w3.eth.chain_id, "kontrak": alamat_cs,
        "detail": None, "error_detail": None,
    }
    if hasil != "TIDAK DITEMUKAN":
        try:
            nim_d, nama_d, ipk_d, tgl_d = kontrak.functions.lihatDetailIjazah(cert).call()
            _, penerbit, waktu, diklaim, _dicabut = kontrak.functions.lihatStatusIjazah(cert).call()
            d["detail"] = dict(nim=nim_d, nama=nama_d, ipk=ipk_d, tgl=tgl_d, penerbit=penerbit,
                               waktu=datetime.fromtimestamp(waktu), diklaim=diklaim)
        except Exception as e:
            d["error_detail"] = rapikan_error(e)
    return d


def buat_bukti(d: dict):
    """Bukti verifikasi: PDF kalau fpdf2 terpasang, kalau tidak teks biasa. -> (bytes, nama file, mime)"""
    teks_status = tampilan_status(d["hasil"])[5]
    dt = d["detail"]
    baris = [
        ("Waktu pengecekan", d["waktu"].strftime("%d %b %Y, %H:%M:%S")),
        ("Hasil pemeriksaan", teks_status),
        ("Nomor ijazah", d["cert"]),
    ]
    if dt:
        baris += [
            ("Nama", dt["nama"]), ("NIM", dt["nim"]), ("IPK", dt["ipk"]),
            ("Tanggal lulus", dt["tgl"]),
            ("Dicatat di blockchain", dt["waktu"].strftime("%d %b %Y, %H:%M")),
            ("Alamat penerbit", dt["penerbit"]),
        ]
    baris += [
        ("SHA-256 dokumen yang dicek", d["hash"]),
        ("Alamat smart contract", d["kontrak"]),
        ("Chain ID / block saat dicek", f'{d["chain"]} / #{d["block"]}'),
    ]
    nama_dasar = "bukti-verifikasi-" + "".join(c if c.isalnum() else "_" for c in d["cert"])

    try:
        from fpdf import FPDF

        def aman(x):  # font bawaan PDF hanya mengenal karakter latin
            return str(x).encode("latin-1", "replace").decode("latin-1")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 10, "Bukti Verifikasi Ijazah", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, "Diperiksa lewat blockchain (smart contract ValiditasIjazah)", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        for label, nilai in baris:
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(0, 5, aman(label), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 6, aman(nilai), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
        return bytes(pdf.output()), nama_dasar + ".pdf", "application/pdf"
    except Exception:
        isi = "BUKTI VERIFIKASI IJAZAH\n" + "=" * 40 + "\n"
        isi += "\n".join(f"{label}: {nilai}" for label, nilai in baris)
        return isi.encode("utf-8"), nama_dasar + ".txt", "text/plain"


def tampilkan_hasil(d: dict):
    kelas, cap, sub, judul, ket, _ = tampilan_status(d["hasil"])
    inisial, nama_html, grid_html = "?", f'<div class="ket">{ket}</div>', ""
    dt = d["detail"]
    if dt:
        inisial = esc(str(dt["nama"]).strip()[:1].upper() or "?")
        nama_html = (
            f'<div class="nm">{esc(dt["nama"])}</div>'
            f'<div class="nimx">NIM {esc(dt["nim"])}</div>'
            f'<div class="ket">{ket}</div>'
        )
        grid_html = f"""
<div class="grid">
  <div><span>IPK</span>{esc(dt["ipk"])}</div>
  <div><span>Tanggal lulus</span>{esc(dt["tgl"])}</div>
  <div><span>Dicatat pada</span>{dt["waktu"].strftime("%d %b %Y, %H:%M")}</div>
  <div><span>Status klaim</span>{"Sudah diklaim" if dt["diklaim"] else "Belum diklaim"}</div>
  <div><span>Alamat penerbit</span><div class="mono">{esc(dt["penerbit"])}</div></div>
</div>"""
    elif d["error_detail"]:
        st.warning(f"Detail tidak bisa dibaca: {d['error_detail']}")

    st.markdown(
        f"""
<div class="idcard {kelas}">
  <div class="bar"><span>KARTU HASIL VERIFIKASI</span><span>⛓ ON-CHAIN</span></div>
  <div class="main">
    <div class="ph">{inisial}</div>
    <div class="info"><div class="st">{judul}</div>{nama_html}</div>
    <div class="stamp">{cap}<small>{sub}</small></div>
  </div>
  {grid_html}
  <div class="barcode"></div>
  <div class="foot">SHA-256 dokumen yang dicek: {d["hash"]}</div>
</div>""",
        unsafe_allow_html=True,
    )
    data, nama_file, mime = buat_bukti(d)
    st.download_button("⬇️ Unduh bukti verifikasi", data=data, file_name=nama_file, mime=mime)


# =========================================================
# HALAMAN PER PERAN
# =========================================================
if peran == PERAN_PERUSAHAAN:
    tab_verif, tab_info = st.tabs(["🔎 Verifikasi", "ℹ️ Cara kerja"])

    with tab_verif:
        with st.container(key="card_verif"):
            judul_kartu(
                "Cek keaslian ijazah",
                "Masukkan nomor ijazah dan unggah PDF yang diberikan pelamar. Sidik jari file dibandingkan dengan yang tercatat di blockchain.",
                "Tanpa wallet", "pub",
            )
            a, b = st.columns(2, gap="large")
            with a:
                cert_v = st.text_input(
                    "Nomor ijazah", key="v_cert", value=st.query_params.get("cert", ""),
                    placeholder="Contoh: IJZ-2025-001",
                )
            with b:
                pdf_v = st.file_uploader("PDF ijazah yang mau dicek", type=["pdf"], key="v_pdf")
            if pdf_v:
                baris_hash(hash_file(pdf_v))
            st.write("")
            cek = st.button("Cek sekarang", type="primary", use_container_width=True)

        if cek:
            if not cert_v or not pdf_v:
                st.warning("Isi nomor ijazah dan unggah file PDF dulu.")
            else:
                try:
                    st.session_state["hasil_verif"] = proses_verifikasi(cert_v.strip(), pdf_v)
                except Exception as e:
                    st.session_state.pop("hasil_verif", None)
                    st.error(f"Gagal memeriksa: {rapikan_error(e)}")

        cert_now = cert_v.strip()
        hv = st.session_state.get("hasil_verif")
        if hv and hv["cert"] == cert_now:
            tampilkan_hasil(hv)
        elif cert_now:
            tampilkan_ringkasan(cert_now)

    with tab_info:
        with st.container(key="card_info"):
            judul_kartu("Bagaimana cara kerjanya?", "Singkat saja, tanpa istilah rumit.", "Info", "mhs")
            st.markdown(
                """
1. Saat ijazah diterbitkan, kampus menghitung **sidik jari digital (SHA-256)** dari file PDF-nya, lalu mencatatnya di blockchain.
2. Saat kamu mengecek, aplikasi menghitung sidik jari PDF yang kamu unggah dan **mencocokkannya** dengan catatan itu.
3. Edit satu huruf saja di PDF, sidik jarinya berubah total, jadi hasilnya **tidak cocok**.

**Yang perlu diingat:** file PDF tidak dikirim ke blockchain, hanya sidik jarinya yang dicocokkan.
Hasil "ASLI" berarti file itu sama dengan yang diterbitkan kampus. Tetap cocokkan **nama dan NIM di hasil**
dengan identitas pelamar, karena sistem ini tidak membuktikan siapa yang membawa berkas.
"""
            )

elif peran == PERAN_MAHASISWA:
    tab_klaim, tab_bagi = st.tabs(["🎒 Klaim ijazah", "🔗 Bagikan ke perusahaan"])

    with tab_klaim:
        with st.container(key="card_klaim"):
            judul_kartu(
                "Klaim ijazahmu",
                "Pakai wallet yang didaftarkan saat registrasi (pilih di sidebar), lalu masukkan nomor ijazahmu.",
                "Mahasiswa", "mhs",
            )
            cert_k = st.text_input("Nomor ijazah", key="k_cert", placeholder="Contoh: IJZ-2025-001")
            st.write("")
            if st.button("Klaim ijazah", type="primary"):
                if not cert_k:
                    st.warning("Isi nomor ijazah dulu.")
                else:
                    kirim_transaksi(kontrak.functions.klaimIjazah(cert_k))

    with tab_bagi:
        with st.container(key="card_bagi"):
            judul_kartu(
                "Bagikan ke perusahaan",
                "Perusahaan cukup membuka tautan ini, lalu mengunggah PDF ijazahmu. Nomor ijazah sudah terisi otomatis.",
                "Mahasiswa", "mhs",
            )
            cert_s = st.text_input("Nomor ijazah", key="s_cert", placeholder="Contoh: IJZ-2025-001")
            basis = st.text_input(
                "Alamat aplikasi ini", key="s_basis", value=f"http://{ip_lokal()}:8501",
                help="Pakai alamat IP laptop (bukan localhost) supaya bisa dibuka dari HP di Wi-Fi yang sama.",
            )
            if cert_s.strip():
                tautan = f"{basis.rstrip('/')}/?cert={quote(cert_s.strip())}"
                st.markdown("**Tautan verifikasi**")
                st.code(tautan, language="text")
                st.link_button("Buka halaman verifikasi ini", tautan)
                st.caption("Agar QR bisa discan dari HP: HP dan laptop harus satu Wi-Fi, dan izinkan Python di firewall Windows. "
                           "Kalau mencoba di laptop yang sama, ganti alamat di atas menjadi http://localhost:8501.")
                try:
                    import io

                    import qrcode

                    buf = io.BytesIO()
                    qrcode.make(tautan).save(buf, format="PNG")
                    st.image(buf.getvalue(), caption="Scan untuk verifikasi", width=200)
                except Exception:
                    st.caption('QR code belum aktif. Pasang dengan: python -m pip install "qrcode[pil]"')

elif peran == PERAN_DASHBOARD:
    try:
        riwayat = ambil_riwayat_ijazah()
        n_mhs = len(ambil_log("MahasiswaDiregistrasi"))
        galat_dash = None
    except Exception as e:
        riwayat, n_mhs, galat_dash = [], 0, rapikan_error(e)
    if galat_dash:
        st.warning(f"Data belum bisa dibaca dari kontrak: {galat_dash}")
    total = len(riwayat)
    n_klaim = sum(1 for r in riwayat if r["Status"] == "Sudah diklaim")
    n_cabut = sum(1 for r in riwayat if r["Status"] == "Dicabut")
    st.markdown(
        f"""
<div class="stats">
  <div class="stat"><div class="v">{total}</div><div class="l">Ijazah pernah terdaftar</div><small>{total - n_cabut} masih berlaku</small></div>
  <div class="stat"><div class="v">{n_mhs}</div><div class="l">Mahasiswa teregistrasi</div><small>dibaca dari smart contract</small></div>
  <div class="stat"><div class="v">{n_klaim}</div><div class="l">Sudah diklaim</div><small>oleh pemilik wallet</small></div>
  <div class="stat"><div class="v">{n_cabut}</div><div class="l">Dicabut</div><small>tidak berlaku lagi</small></div>
</div>""",
        unsafe_allow_html=True,
    )
    with st.container(key="card_riwayat"):
        judul_kartu(
            "Riwayat penerbitan",
            "Semua ijazah yang pernah didaftarkan lewat aplikasi ini, dari yang terbaru.",
            "Dari smart contract", "pub",
        )
        if riwayat:
            st.dataframe(riwayat[::-1], use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada ijazah terdaftar. Terbitkan lewat peran Kampus (Authority).")
        st.markdown(f'<div class="cap">Alamat smart contract: <code>{esc(alamat_cs)}</code></div>', unsafe_allow_html=True)

else:  # PERAN_KAMPUS
    adalah_authority = False
    try:
        adalah_authority = kontrak.functions.isAuthority(akun).call()
    except Exception:
        pass

    if not adalah_authority:
        st.error(
            f"Account #{pilihan} bukan authority, jadi tidak bisa mendaftarkan, menerbitkan, atau mencabut ijazah. "
            "Ganti akun di sidebar (akun yang dipakai saat deploy otomatis menjadi authority)."
        )
        st.stop()

    try:
        nama_auth = kontrak.functions.namaAuthority(akun).call()
    except Exception:
        nama_auth = "Authority"
    st.markdown(
        f'<div class="live"><span class="chip">🏛️ Masuk sebagai {esc(nama_auth)}</span></div>',
        unsafe_allow_html=True,
    )

    tab_reg, tab_terbit, tab_cabut = st.tabs(["🧾 Registrasi", "📜 Terbitkan", "🚫 Cabut"])

    with tab_reg:
        with st.container(key="card_reg"):
            judul_kartu(
                "Daftarkan mahasiswa",
                "Simpan data mahasiswa dan hubungkan dengan wallet miliknya.",
                "Authority", "auth",
            )
            a, b = st.columns(2, gap="large")
            nim = a.text_input("NIM", key="reg_nim")
            nama = b.text_input("Nama lengkap", key="reg_nama")
            prodi = a.text_input("Program studi", key="reg_prodi")
            tahun = b.number_input("Tahun masuk", min_value=1900, max_value=2100, value=2021, step=1)
            univ = st.text_input("Universitas", value="UIN Siber Syekh Nurjati Cirebon", key="reg_univ")
            pilih_mhs = st.selectbox(
                "Wallet mahasiswa",
                options=list(range(len(akun_list))),
                index=min(1, len(akun_list) - 1),
                format_func=lambda i: f"Account #{i} — {akun_list[i]}",
                key="reg_wallet",
            )
            st.write("")
            if st.button("Daftarkan mahasiswa", type="primary"):
                if not (nim.strip() and nama.strip() and prodi.strip() and univ.strip()):
                    st.warning("Lengkapi NIM, nama, program studi, dan universitas.")
                elif kontrak.functions.daftarMahasiswa(nim.strip()).call()[7]:
                    st.warning(f"NIM {nim.strip()} sudah terdaftar.")
                else:
                    kirim_transaksi(
                        kontrak.functions.registrasiMahasiswa(
                            nim, nama, prodi, univ, int(tahun), akun_list[pilih_mhs]
                        )
                    )

    with tab_terbit:
        with st.container(key="card_terbit"):
            judul_kartu(
                "Terbitkan ijazah",
                "Unggah PDF ijazah. Hanya sidik jarinya yang dikirim ke blockchain, filenya tetap di komputermu.",
                "Authority", "auth",
            )
            a, b = st.columns(2, gap="large")
            cert_id = a.text_input("Nomor ijazah", key="t_cert", placeholder="Contoh: IJZ-2025-001")
            nim_t = b.text_input("NIM mahasiswa", key="t_nim")
            ipk = a.text_input("IPK", key="t_ipk", placeholder="Contoh: 3.85")
            tgl = b.text_input("Tanggal lulus", key="t_tgl", placeholder="Contoh: 2025-08-20")
            pdf_t = st.file_uploader("File PDF ijazah", type=["pdf"], key="t_pdf")
            if pdf_t:
                baris_hash(hash_file(pdf_t))
            st.write("")
            if st.button("Terbitkan ijazah", type="primary"):
                galat = []
                if not pdf_t:
                    galat.append("Unggah file PDF ijazah dulu.")
                if not (cert_id.strip() and nim_t.strip() and ipk.strip() and tgl.strip()):
                    galat.append("Lengkapi nomor ijazah, NIM, IPK, dan tanggal lulus.")
                else:
                    if not valid_ipk(ipk):
                        galat.append("IPK tidak valid. Gunakan angka 0.01 sampai 4.00, contoh 3.85.")
                    if not valid_tanggal(tgl):
                        galat.append("Tanggal lulus harus berformat YYYY-MM-DD, contoh 2025-08-20.")
                if not galat:
                    try:
                        m = kontrak.functions.daftarMahasiswa(nim_t.strip()).call()
                        if not m[7]:
                            galat.append(f"NIM {nim_t.strip()} belum diregistrasi. Daftarkan dulu di tab Registrasi.")
                        elif m[6] == 1:
                            galat.append(f"Mahasiswa dengan NIM {nim_t.strip()} sudah punya ijazah.")
                        if kontrak.functions.daftarIjazah(cert_id.strip()).call()[9]:
                            galat.append(f"Nomor ijazah {cert_id.strip()} sudah dipakai.")
                        if kontrak.functions.hashSudahTerdaftar(hash_file(pdf_t)).call():
                            galat.append("File PDF ini sudah pernah didaftarkan.")
                    except Exception as e:
                        galat.append(f"Gagal memeriksa data di kontrak: {rapikan_error(e)}")
                if galat:
                    for g in galat:
                        st.warning(g)
                else:
                    kirim_transaksi(
                        kontrak.functions.terbitkanIjazah(
                            cert_id.strip(), nim_t.strip(), ipk.strip().replace(",", "."), tgl.strip(), hash_file(pdf_t)
                        )
                    )

    with tab_cabut:
        with st.container(key="card_cabut"):
            judul_kartu(
                "Cabut ijazah",
                "Ijazah yang dicabut akan tampil sebagai “dicabut” saat diverifikasi. Tindakan ini tercatat permanen.",
                "Authority", "auth",
            )
            cert_c = st.text_input("Nomor ijazah", key="c_cert", placeholder="Contoh: IJZ-2025-001")
            alasan = st.text_input("Alasan pencabutan", key="c_alasan")
            st.write("")
            if st.button("Cabut ijazah", type="primary"):
                if not (cert_c and alasan):
                    st.warning("Isi nomor ijazah dan alasan pencabutan.")
                else:
                    kirim_transaksi(kontrak.functions.cabutIjazah(cert_c, alasan))

st.write("")
st.caption("CekIjazah • Hardhat • Smart Contract ValiditasIjazah • Streamlit")
