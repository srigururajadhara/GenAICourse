from __future__ import annotations

import os
import html
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Guru | Agricultural Scheme Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root {
  --forest: #123B2D;
  --forest-2: #19563E;
  --green: #16734B;
  --green-bright: #21875A;
  --lime: #D7EBC2;
  --ink: #182D24;
  --muted: #5A6F63;
  --line: #DCE7DE;
  --paper: #F4F7F2;
  --white: #FFFFFF;
}
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: var(--paper); color: var(--ink); }
[data-testid="stAppViewContainer"] { background: var(--paper); }
[data-testid="stMainBlockContainer"], .block-container {
  width: 100% !important; max-width: 1560px !important;
  padding: 2rem clamp(1.1rem, 3vw, 3rem) 3.5rem !important;
}

/* Sidebar: deep forest surface with bright, readable controls. */
section[data-testid="stSidebar"] {
  background: linear-gradient(175deg, #123B2D 0%, #164B36 58%, #103629 100%) !important;
  min-width: 300px !important; max-width: 300px !important;
  border-right: 1px solid rgba(255,255,255,.08);
}
section[data-testid="stSidebar"] > div { background: transparent !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
  color: #F1F7F2 !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { font-size: .94rem; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
  font-size: .88rem !important; font-weight: 700 !important; letter-spacing: .01em;
}
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-testid="stNumberInput"] input {
  background: #FFFFFF !important; color: #18372A !important;
  -webkit-text-fill-color: #18372A !important;
  border: 1px solid #C9D9CC !important; border-radius: 10px !important;
  min-height: 42px;
}
[data-testid="stSidebar"] [data-baseweb="select"] *,
[data-testid="stSidebar"] [data-testid="stNumberInput"] button {
  color: #18372A !important;
}
[data-testid="stSidebar"] input::placeholder,
[data-testid="stSidebar"] textarea::placeholder {
  color: #718176 !important; -webkit-text-fill-color: #718176 !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
  background: rgba(255,255,255,.08) !important; border-radius: 14px;
  border: 1px solid rgba(255,255,255,.18) !important; padding: 8px;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
  background: #F8FBF7 !important; border: 1px dashed #8AAE95 !important;
  border-radius: 10px !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] *,
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small {
  color: #254735 !important; -webkit-text-fill-color: #254735 !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
  background: #E7F1E6 !important; border: 1px solid #BDD2BE !important;
  color: #1B563A !important;
}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: #C5D8CA !important; }

/* Main page typography and navigation. */
h1, h2, h3, h4, p, label { color: var(--ink); }
[data-testid="stMarkdownContainer"] p { color: var(--ink); }
[data-testid="stWidgetLabel"] p { color: #314B3D !important; font-weight: 700 !important; font-size: .92rem !important; }
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  background: #FFFFFF !important; color: #1A3025 !important;
  -webkit-text-fill-color: #1A3025 !important; border-color: #C9D9CD !important;
  border-radius: 11px !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder { color: #7A8A7F !important; }

/* Hero and status. */
.hero {
  background: linear-gradient(118deg, #103D2C 0%, #176846 58%, #27865A 100%);
  border-radius: 25px; padding: clamp(26px, 3vw, 42px);
  color: #FFFFFF; box-shadow: 0 16px 38px rgba(20,68,44,.16);
  position: relative; overflow: hidden; min-height: 188px;
}
.hero:after { content: '🌾'; position: absolute; right: 42px; top: 12px; font-size: 104px; opacity: .16; transform: rotate(-12deg); }
.hero h1 { font-family: 'Manrope', sans-serif; font-weight: 800; font-size: clamp(1.8rem, 3vw, 2.65rem); line-height: 1.12; margin: 0 0 12px; color: #FFFFFF !important; letter-spacing: -.035em; }
.hero p { margin: 0; color: #E1F0E5 !important; font-size: 1.04rem; line-height: 1.65; max-width: 790px; }
.eyebrow { color: #C2E5CC !important; font-size: .78rem; text-transform: uppercase; letter-spacing: .15em; font-weight: 800; margin-bottom: 13px; }
.api-badge { display: inline-flex; align-items: center; gap: 8px; margin-top: 18px; padding: 7px 12px; border-radius: 999px; background: rgba(255,255,255,.14); color: #FFFFFF; font-size: .8rem; font-weight: 700; border: 1px solid rgba(255,255,255,.2); }
.api-dot { width: 8px; height: 8px; display: inline-block; background: #9BE3A9; border-radius: 50%; }
.api-dot.offline { background: #FFC36B; }

/* KPI cards. */
.metric { background: #FFFFFF; border: 1px solid var(--line); border-radius: 17px; padding: 19px 20px; min-height: 112px; box-shadow: 0 5px 18px rgba(23,58,39,.045); }
.metric .label { color: #536B5D; font-size: .86rem; font-weight: 700; }
.metric .value { color: #153D2C; font-family: 'Manrope', sans-serif; font-weight: 800; font-size: 1.9rem; margin-top: 5px; }
.metric .hint { color: #687D70; font-size: .78rem; margin-top: 2px; }
.section-title { font-family: 'Manrope', sans-serif; font-size: 1.32rem; font-weight: 800; color: #173D2D !important; margin: 8px 0 4px; }
.section-sub { font-size: .94rem; color: #586F61 !important; margin-bottom: 16px; line-height: 1.5; }
.answer-card { background: #FFFFFF; border: 1px solid #DDE8DE; border-left: 5px solid #21875A; border-radius: 16px; padding: 20px 22px; color: #1B3427; line-height: 1.65; }
.source-card { background: #FFFFFF; border: 1px solid #DCE7DE; border-radius: 14px; padding: 15px 17px; margin: 9px 0; color: #203A2C; box-shadow: 0 3px 12px rgba(25,60,39,.035); }
.source-meta { color: #587163 !important; font-size: .78rem; font-weight: 800; letter-spacing: .035em; }
.source-text { color: #344E40 !important; font-size: .92rem; line-height: 1.6; margin-top: 7px; }
.pill { display: inline-block; background: #E8F3E8; color: #195C3A !important; border-radius: 999px; padding: 6px 11px; font-size: .78rem; font-weight: 800; margin-right: 6px; }
.tip { background: #EDF6EA; border: 1px solid #D2E5D1; border-radius: 13px; padding: 14px 16px; color: #294E35 !important; font-size: .9rem; line-height: 1.55; }
.empty-state { display: flex; gap: 16px; align-items: flex-start; background: #FFFDF6; border: 1px solid #EADFB8; border-left: 5px solid #D3A53D; border-radius: 16px; padding: 17px 20px; margin: 16px 0 20px; color: #453719; }
.empty-state .empty-icon { font-size: 1.7rem; line-height: 1; }
.empty-state strong { display: block; color: #463717; font-size: 1rem; margin-bottom: 4px; }
.empty-state span { color: #6B572B; font-size: .91rem; line-height: 1.5; }

/* Buttons: explicitly set both foreground and background to prevent dark-on-dark text. */
div.stButton > button, [data-testid="stBaseButton-secondary"] {
  background: #E8F1E8 !important; color: #184E34 !important;
  -webkit-text-fill-color: #184E34 !important; border: 1px solid #C9DCCB !important;
  border-radius: 12px !important; font-weight: 800 !important; min-height: 43px;
  box-shadow: none !important; transition: all .16s ease;
}
div.stButton > button:hover, [data-testid="stBaseButton-secondary"]:hover {
  background: #DCEBDD !important; color: #103D2A !important; border-color: #9DBFA3 !important;
}
/* Streamlit dims disabled buttons by default. Keep suggested prompts readable even
   before a PDF is indexed, while making the disabled state visually distinct. */
[data-testid="stButton"] > button:disabled,
[data-testid="stButton"] > button[disabled],
div.stButton > button:disabled,
div.stButton > button[disabled],
[data-testid="stBaseButton-secondary"]:disabled,
[data-testid="stBaseButton-secondary"][disabled] {
  background: #EEF3EC !important;
  color: #52695A !important;
  -webkit-text-fill-color: #52695A !important;
  border: 1px solid #C9D8CA !important;
  opacity: 1 !important;
  filter: none !important;
  box-shadow: none !important;
  cursor: not-allowed !important;
}
[data-testid="stButton"] > button:disabled *,
[data-testid="stButton"] > button[disabled] *,
div.stButton > button:disabled *,
div.stButton > button[disabled] *,
[data-testid="stBaseButton-secondary"]:disabled *,
[data-testid="stBaseButton-secondary"][disabled] * {
  color: #52695A !important;
  -webkit-text-fill-color: #52695A !important;
  opacity: 1 !important;
}
div.stButton > button[kind="primary"],
[data-testid="stBaseButton-primary"],
button[data-testid="stBaseButton-primary"] {
  background: #176B45 !important; color: #FFFFFF !important;
  -webkit-text-fill-color: #FFFFFF !important; border: 1px solid #176B45 !important;
}
div.stButton > button[kind="primary"]:hover,
[data-testid="stBaseButton-primary"]:hover {
  background: #105638 !important; color: #FFFFFF !important; border-color: #105638 !important;
}
[data-testid="stSidebar"] div.stButton > button[kind="primary"],
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
  background: #D6EBC3 !important; color: #163A29 !important;
  -webkit-text-fill-color: #163A29 !important; border-color: #D6EBC3 !important;
}
[data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover,
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:hover {
  background: #C3E0AB !important; color: #123324 !important;
}

/* Tabs, chat, alerts, and evidence. */
.stTabs [data-baseweb="tab-list"] { gap: 9px; border-bottom: 1px solid #D8E4D9; }
.stTabs [data-baseweb="tab"] { background: #E8F0E8 !important; border-radius: 11px 11px 0 0; padding: 12px 18px; color: #315541 !important; font-weight: 800; }
.stTabs [data-baseweb="tab"] * { color: #315541 !important; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { background: #176B45 !important; color: #FFFFFF !important; }
.stTabs [data-baseweb="tab"][aria-selected="true"] * { color: #FFFFFF !important; }
div[data-testid="stChatMessage"] { background: #FFFFFF; border: 1px solid #DCE7DE; border-radius: 16px; padding: 13px 16px; margin: 10px 0; color: #1C3427; }
div[data-testid="stChatMessage"] p { color: #1C3427 !important; font-size: .97rem; line-height: 1.65; }
div[data-testid="stChatInput"] textarea { background: #FFFFFF !important; color: #1A3025 !important; -webkit-text-fill-color: #1A3025 !important; border: 1px solid #BFD2C3 !important; border-radius: 14px !important; }
[data-testid="stAlert"] { border-radius: 13px !important; }
[data-testid="stAlert"] * { color: #263D30 !important; }
[data-testid="stExpander"] { background: #FFFFFF; border: 1px solid #DCE7DE; border-radius: 13px; }
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * { color: #234634 !important; font-weight: 700; }
hr { border-color: #DDE7DE !important; }
small, .muted { color: #617669; }


/* ================================================================
   GURU GLOBAL CONTRAST & READABILITY GUARD
   Keep the light content canvas and forest sidebar, but never allow
   Streamlit defaults or disabled states to create low-contrast text.
   ================================================================ */
:root { color-scheme: light !important; }
html, body, .stApp, [data-testid="stAppViewContainer"] {
  color-scheme: light !important;
}
main, [data-testid="stMain"] {
  color: #19372A !important;
}
main [data-testid="stMarkdownContainer"] {
  color: #19372A !important;
}
main [data-testid="stCaptionContainer"] p,
main [data-testid="stCaptionContainer"] span,
main .stCaption,
main small {
  color: #52685A !important;
}
main a { color: #126443 !important; text-decoration-thickness: 1px; }
main a:hover { color: #0B4B31 !important; }
main code, main pre {
  color: #173B2D !important;
  background: #EAF0E8 !important;
  border: 1px solid #D7E2D6 !important;
}
main blockquote { color: #294637 !important; border-left-color: #39845B !important; }

/* All Streamlit buttons: readable in normal, hover, focus and disabled states. */
button,
button[kind],
button[data-testid^="stBaseButton"],
[data-testid^="stBaseButton"] {
  background: #E8F1E8 !important;
  color: #174A32 !important;
  -webkit-text-fill-color: #174A32 !important;
  border: 1px solid #C5D9C8 !important;
  opacity: 1 !important;
  filter: none !important;
  text-shadow: none !important;
}
button *,
button[kind] *,
button[data-testid^="stBaseButton"] *,
[data-testid^="stBaseButton"] * {
  color: #174A32 !important;
  -webkit-text-fill-color: #174A32 !important;
  opacity: 1 !important;
  text-shadow: none !important;
}
button:hover,
button[kind]:hover,
button[data-testid^="stBaseButton"]:hover,
[data-testid^="stBaseButton"]:hover {
  background: #D8E9D9 !important;
  color: #103D2A !important;
  -webkit-text-fill-color: #103D2A !important;
  border-color: #91B69A !important;
}
button:focus-visible,
button[data-testid^="stBaseButton"]:focus-visible {
  outline: 3px solid #77A987 !important;
  outline-offset: 2px !important;
}
button:disabled,
button[disabled],
button[data-testid^="stBaseButton"]:disabled,
button[data-testid^="stBaseButton"][disabled] {
  background: #EDF2EA !important;
  color: #4B6253 !important;
  -webkit-text-fill-color: #4B6253 !important;
  border-color: #CBD8C9 !important;
  opacity: 1 !important;
  filter: none !important;
  cursor: not-allowed !important;
}
button:disabled *,
button[disabled] *,
button[data-testid^="stBaseButton"]:disabled *,
button[data-testid^="stBaseButton"][disabled] * {
  color: #4B6253 !important;
  -webkit-text-fill-color: #4B6253 !important;
  opacity: 1 !important;
}
/* Primary actions retain the stronger green treatment. */
button[kind="primary"],
button[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-primary"] {
  background: #176B45 !important;
  color: #FFFFFF !important;
  -webkit-text-fill-color: #FFFFFF !important;
  border-color: #176B45 !important;
}
button[kind="primary"] *,
button[data-testid="stBaseButton-primary"] *,
[data-testid="stBaseButton-primary"] * {
  color: #FFFFFF !important;
  -webkit-text-fill-color: #FFFFFF !important;
}
button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover,
[data-testid="stBaseButton-primary"]:hover {
  background: #105638 !important;
  border-color: #105638 !important;
}
button[kind="primary"]:disabled,
button[data-testid="stBaseButton-primary"]:disabled {
  background: #E5EBE4 !important;
  color: #52665A !important;
  -webkit-text-fill-color: #52665A !important;
  border-color: #CBD8C9 !important;
}
button[kind="primary"]:disabled *,
button[data-testid="stBaseButton-primary"]:disabled * {
  color: #52665A !important;
  -webkit-text-fill-color: #52665A !important;
}
/* Sidebar primary action is a light-lime button on the forest surface. */
[data-testid="stSidebar"] button[kind="primary"],
[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {
  background: #D6EBC3 !important;
  color: #163A29 !important;
  -webkit-text-fill-color: #163A29 !important;
  border-color: #D6EBC3 !important;
}
[data-testid="stSidebar"] button[kind="primary"] *,
[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] * {
  color: #163A29 !important;
  -webkit-text-fill-color: #163A29 !important;
}

/* Inputs, dropdowns, labels and option menus. */
main [data-testid="stWidgetLabel"],
main [data-testid="stWidgetLabel"] *,
main [data-testid="stWidgetLabel"] p,
main label,
main [data-testid="stRadio"] label,
main [data-testid="stCheckbox"] label,
main [data-testid="stCheckbox"] label *,
main [data-testid="stRadio"] label * {
  color: #263F32 !important;
  -webkit-text-fill-color: #263F32 !important;
}
main input,
main textarea,
main [role="combobox"],
main [data-baseweb="select"] > div,
main [data-testid="stDateInput"] input,
main [data-testid="stTimeInput"] input {
  background-color: #FFFFFF !important;
  color: #19372A !important;
  -webkit-text-fill-color: #19372A !important;
  border-color: #BFCFC2 !important;
}
main input::placeholder,
main textarea::placeholder {
  color: #667A6C !important;
  -webkit-text-fill-color: #667A6C !important;
  opacity: 1 !important;
}
main input:disabled,
main textarea:disabled {
  background: #EEF2EC !important;
  color: #52665A !important;
  -webkit-text-fill-color: #52665A !important;
  opacity: 1 !important;
}
main [data-testid="stSelectbox"] [data-baseweb="select"] *,
main [data-testid="stMultiSelect"] [data-baseweb="select"] * {
  color: #19372A !important;
  -webkit-text-fill-color: #19372A !important;
}
/* Dropdowns are sometimes rendered in a portal outside the widget container. */
[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"] {
  background: #FFFFFF !important;
  color: #19372A !important;
  border: 1px solid #D2DED3 !important;
}
[role="option"],
[data-baseweb="menu"] *,
[role="listbox"] * {
  color: #19372A !important;
  -webkit-text-fill-color: #19372A !important;
}
[role="option"]:hover,
[role="option"][aria-selected="true"] {
  background: #E8F2E7 !important;
}

/* Chat, tabs, alerts, expanders and data tables. */
.stTabs [data-baseweb="tab"] {
  background: #E8F0E8 !important;
  color: #244B35 !important;
  -webkit-text-fill-color: #244B35 !important;
}
.stTabs [data-baseweb="tab"] * {
  color: #244B35 !important;
  -webkit-text-fill-color: #244B35 !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"],
.stTabs [data-baseweb="tab"][aria-selected="true"] * {
  background: #176B45 !important;
  color: #FFFFFF !important;
  -webkit-text-fill-color: #FFFFFF !important;
}
div[data-testid="stChatMessage"] {
  background: #FFFFFF !important;
  color: #19372A !important;
  border-color: #D5E1D6 !important;
}
div[data-testid="stChatMessage"] * {
  color: #19372A;
}
div[data-testid="stChatInput"] textarea {
  background: #FFFFFF !important;
  color: #19372A !important;
  -webkit-text-fill-color: #19372A !important;
}
div[data-testid="stChatInput"] textarea::placeholder {
  color: #64796B !important;
  -webkit-text-fill-color: #64796B !important;
}
[data-testid="stAlert"] {
  background: #F0F6EF !important;
  border: 1px solid #D1E1D0 !important;
  color: #243D2E !important;
}
[data-testid="stAlert"] * {
  color: #243D2E !important;
  -webkit-text-fill-color: #243D2E !important;
}
[data-testid="stExpander"] {
  background: #FFFFFF !important;
  border-color: #D5E1D6 !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary * {
  color: #234634 !important;
  -webkit-text-fill-color: #234634 !important;
}
[data-testid="stMetric"] label,
[data-testid="stMetric"] label *,
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {
  color: #19372A !important;
  -webkit-text-fill-color: #19372A !important;
}
[data-testid="stDataFrame"],
[data-testid="stTable"] {
  color: #19372A !important;
}
[data-testid="stFileUploaderDropzone"] {
  background: #F8FBF7 !important;
}
[data-testid="stFileUploaderDropzone"] *,
[data-testid="stFileUploaderDropzone"] small {
  color: #254735 !important;
  -webkit-text-fill-color: #254735 !important;
}

/* Keep custom content cards readable even when Streamlit theme defaults vary. */
.answer-card, .answer-card *,
.source-card, .source-card *,
.tip, .tip *,
.empty-state, .empty-state *,
.metric, .metric *,
.section-title, .section-sub {
  text-shadow: none !important;
}
.answer-card { color: #1B3427 !important; }
.answer-card * { color: inherit; }
.source-card { color: #203A2C !important; }
.tip { color: #294E35 !important; }
.empty-state { color: #453719 !important; }
.metric .label { color: #405B4A !important; }
.metric .value { color: #153D2C !important; }
.metric .hint { color: #52685A !important; }
.section-title { color: #173D2D !important; }
.section-sub { color: #4B6354 !important; }

@media (max-width: 900px) {
  section[data-testid="stSidebar"] { min-width: 0 !important; max-width: 100% !important; }
  [data-testid="stMainBlockContainer"], .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
  .hero { padding: 24px; }
  .hero:after { right: 10px; font-size: 68px; }
}
</style>
""", unsafe_allow_html=True)


def api_get(path: str):
    return requests.get(f"{API_URL}{path}", timeout=10)


def api_post(path: str, **kwargs):
    return requests.post(f"{API_URL}{path}", timeout=180, **kwargs)


def show_metric(col, label: str, value: str, hint: str):
    col.markdown(f'<div class="metric"><div class="label">{label}</div><div class="value">{value}</div><div class="hint">{hint}</div></div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# Sidebar: farmer context + source management
with st.sidebar:
    st.markdown("<div style='font-family:Manrope;font-size:1.35rem;font-weight:800;margin:8px 0 0'>🌾 Guru</div><div style='font-size:.77rem;color:#BED5C6;margin-bottom:20px'>Your trusted scheme companion</div>", unsafe_allow_html=True)
    st.markdown("**FARMER PROFILE**")
    state = st.selectbox("State", ["Tamil Nadu", "Karnataka", "Andhra Pradesh", "Telangana", "Kerala", "Maharashtra", "Gujarat", "Rajasthan", "Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh", "West Bengal", "Odisha", "Bihar", "Assam", "Chhattisgarh", "Jharkhand", "Uttarakhand", "Himachal Pradesh", "Goa", "Other", "Not specified"], index=0)
    district = st.text_input("District", placeholder="e.g. Coimbatore")
    farmer_type = st.selectbox("Farmer type", ["Small farmer", "Marginal farmer", "Other farmer", "Tenant farmer", "Sharecropper", "Not specified"])
    land_size = st.number_input("Land holding (acres)", min_value=0.0, max_value=10000.0, value=0.0, step=0.5)
    social_category = st.selectbox("Category (optional)", ["Not specified", "General", "SC", "ST", "OBC", "Other"])
    crop = st.text_input("Main crop (optional)", placeholder="e.g. paddy, groundnut")
    irrigation = st.selectbox("Irrigation", ["Not specified", "Rainfed", "Canal", "Borewell", "Drip / sprinkler", "Other"])
    language = st.selectbox("Answer language", ["English", "Tamil", "Hindi", "Kannada", "Telugu", "Malayalam"], index=0)
    farmer_profile = {
        "state": state if state != "Not specified" else None,
        "district": district or None,
        "farmer_type": farmer_type if farmer_type != "Not specified" else None,
        "land_size_acres": land_size if land_size > 0 else None,
        "social_category": social_category if social_category != "Not specified" else None,
        "crop": crop or None,
        "irrigation": irrigation if irrigation != "Not specified" else None,
    }
    st.divider()
    st.markdown("**ADD OFFICIAL SCHEME PDFs**")
    uploaded_files = st.file_uploader("Upload government scheme documents", type=["pdf"], accept_multiple_files=True, help="Use official Central or State Government PDFs. Maximum 30 MB per file.")
    doc_state = st.selectbox("Document applies to", ["All India", "Tamil Nadu", "Karnataka", "Andhra Pradesh", "Telangana", "Kerala", "Other"], key="doc_state")
    doc_category = st.selectbox("Document category", ["Government scheme", "Crop insurance", "Credit / loan", "Subsidy", "Irrigation", "Farm mechanisation", "Horticulture", "Livestock", "Other"], key="doc_category")
    if st.button("Build / Refresh Knowledge Base", type="primary", use_container_width=True, disabled=not uploaded_files):
        try:
            files = [("files", (f.name, f.getvalue(), "application/pdf")) for f in uploaded_files]
            with st.spinner("Extracting PDF pages, creating chunks and building FAISS index…"):
                result = api_post("/api/v1/ingest", files=files, data={"state": doc_state, "category": doc_category})
            if result.ok:
                st.success(f"Indexed {result.json().get('documents')} document(s), {result.json().get('pages')} pages and {result.json().get('chunks')} chunks.")
                st.rerun()
            else:
                st.error(result.json().get("detail", result.text))
        except requests.RequestException as exc:
            st.error(f"Could not reach the API: {exc}")
    st.caption("Only upload documents you are permitted to use. The app stores PDFs locally in data/pdfs/.")

# API and knowledge base status
try:
    health_response = api_get("/health")
    health = health_response.json() if health_response.ok else {}
    api_online = health_response.ok
except requests.RequestException:
    health, api_online = {}, False

api_label = "Backend connected" if api_online else "Backend offline"
api_class = "api-dot" if api_online else "api-dot offline"
st.markdown(f"<div class='hero'><div class='eyebrow'>AGRICULTURAL GOVERNMENT SCHEME INTELLIGENCE</div><h1>Understand schemes. Unlock support.</h1><p>Ask questions in your language, explore eligibility conditions, and get answers grounded in your uploaded official documents—with page-level evidence.</p><span class='api-badge'><i class='{api_class}'></i>{api_label}</span></div>", unsafe_allow_html=True)
st.write("")

if api_online:
    try:
        kb = api_get("/api/v1/knowledge-base").json()
    except requests.RequestException:
        kb = {}
else:
    kb = {}

m1, m2, m3, m4 = st.columns(4)
show_metric(m1, "Knowledge base", "Ready" if kb.get("indexed") else "Not built", "FAISS vector index")
show_metric(m2, "Documents", str(kb.get("documents", 0)), "Official PDFs uploaded")
show_metric(m3, "Pages processed", str(kb.get("pages", 0)), "Extracted document pages")
show_metric(m4, "Searchable chunks", str(kb.get("chunks", 0)), "Context segments indexed")

if api_online and not kb.get("indexed"):
    st.markdown("<div class='empty-state'><div class='empty-icon'>📄</div><div><strong>Your knowledge base is not ready yet.</strong><span>Upload at least one official agricultural scheme PDF from the left panel, then select <b>Build / Refresh Knowledge Base</b>. Guru will enable chat after the document is indexed.</span></div></div>", unsafe_allow_html=True)

if not api_online:
    st.error("The FastAPI service is offline. Start it in a terminal with: `uvicorn api.main:app --reload --port 8000`")

st.write("")
tab_chat, tab_eligibility, tab_library = st.tabs(["💬 Ask Guru", "✅ Eligibility guidance", "📚 Knowledge base"])


def submit_question(question: str):
    if not question.strip():
        return
    if not api_online:
        st.error("Guru's backend API is offline. Start FastAPI and try again.")
        return
    if not kb.get("indexed"):
        st.warning("Upload and index at least one official scheme PDF before asking Guru a question.")
        return
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-8:]]
    payload = {
        "question": question,
        "language": language,
        "farmer_profile": farmer_profile,
        "chat_history": history,
    }
    with st.spinner("Searching your scheme documents and preparing an evidence-based answer…"):
        response = api_post("/api/v1/query", json=payload)
    if response.ok:
        data = response.json()
        st.session_state.messages.append({"role": "user", "content": question})
        st.session_state.messages.append({"role": "assistant", "content": data["answer"], "result": data})
        st.session_state.last_result = data
    else:
        st.error(response.json().get("detail", response.text))

with tab_chat:
    left, right = st.columns([1.7, 1])
    with left:
        st.markdown("<div class='section-title'>Ask a farming scheme question</div><div class='section-sub'>Get practical explanations grounded in the PDF documents you have indexed.</div>", unsafe_allow_html=True)
        starters = [
            "What are the benefits and eligibility conditions of PM-KISAN?",
            "What documents are needed to apply for crop insurance?",
            "Are there any subsidies for drip irrigation in my state?",
        ]
        scols = st.columns(3)
        for idx, starter in enumerate(starters):
            if scols[idx].button(["PM-KISAN details", "Crop insurance", "Irrigation subsidy"][idx], use_container_width=True, key=f"starter_{idx}", disabled=not (api_online and kb.get("indexed"))):
                submit_question(starter)
        if not st.session_state.messages and kb.get("indexed"):
            st.markdown("<div class='answer-card'><b>Welcome to Guru.</b><br>Ask about scheme benefits, eligibility, documents, subsidy amounts or application steps. Every answer is grounded in your indexed documents.</div>", unsafe_allow_html=True)
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant" and message.get("result"):
                    result = message["result"]
                    with st.expander(f"📎 Evidence used ({len(result.get('citations', []))} source passages)"):
                        st.caption(result.get("retrieval_note", ""))
                        for cite in result.get("citations", []):
                            page = f" · Page {cite['page']}" if cite.get("page") else ""
                            source_id = html.escape(str(cite.get("source_id", "")))
                            source_name = html.escape(str(cite.get("source", "Unknown PDF")))
                            state_name = html.escape(str(cite.get("state") or "State not tagged"))
                            excerpt = html.escape(str(cite.get("excerpt", "")))
                            st.markdown(f"<div class='source-card'><div class='source-meta'>[{source_id}] {source_name}{page} · {state_name}</div><div class='source-text'>{excerpt}</div></div>", unsafe_allow_html=True)
                    if result.get("suggested_questions"):
                        st.caption("You could also ask: " + " · ".join(result["suggested_questions"]))
        prompt = st.chat_input("Ask about benefits, eligibility, documents, subsidy amount or application steps…", disabled=not (api_online and kb.get("indexed")))
        if prompt:
            submit_question(prompt)
            st.rerun()
    with right:
        st.markdown("<div class='section-title'>Your farmer profile</div><div class='section-sub'>Used only as context when comparing your details with scheme rules.</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='source-card'><div class='source-meta'>LOCATION</div><b>{html.escape(state)}</b><div class='source-text'>{html.escape(district or 'District not added')}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='source-card'><div class='source-meta'>FARM PROFILE</div><b>{html.escape(farmer_type)}</b><div class='source-text'>{land_size:g} acre(s) · {html.escape(social_category)} · {html.escape(crop or 'Crop not added')}</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='tip'>Guru does not submit applications or guarantee benefits. Always verify current rules with the relevant Agriculture Department or official scheme portal.</div>", unsafe_allow_html=True)
        if st.button("Clear conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.last_result = None
            st.rerun()

with tab_eligibility:
    st.markdown("<div class='section-title'>Check scheme fit against your profile</div><div class='section-sub'>This is an evidence-based preliminary assessment—not an official eligibility decision.</div>", unsafe_allow_html=True)
    e1, e2 = st.columns([1.2, 1])
    with e1:
        scheme_name = st.text_input("Scheme name (optional)", placeholder="e.g. PM-KISAN, PMFBY, state drip irrigation subsidy")
        eligibility_question = st.text_area("What would you like to verify?", value="Based only on the uploaded official documents, assess whether my farmer profile appears to meet the eligibility conditions. List every condition as Met, Not met, or Needs verification. Also list required documents and application steps if present.", height=150)
        if st.button("Assess scheme fit", type="primary", disabled=not api_online):
            q = f"For {scheme_name or 'the relevant scheme'}, {eligibility_question}"
            submit_question(q)
            st.session_state.eligibility_submitted = True
    with e2:
        st.markdown("**Profile details being checked**")
        for label, value in [("State", state), ("District", district or "Not specified"), ("Farmer type", farmer_type), ("Land holding", f"{land_size:g} acres" if land_size else "Not specified"), ("Social category", social_category), ("Crop", crop or "Not specified"), ("Irrigation", irrigation)]:
            st.markdown(f"<div class='source-card' style='padding:9px 12px'><div class='source-meta'>{html.escape(label.upper())}</div><b>{html.escape(str(value))}</b></div>", unsafe_allow_html=True)
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
        st.markdown("#### Latest assessment")
        st.markdown(f"<div class='answer-card'>{st.session_state.messages[-1]['content']}</div>", unsafe_allow_html=True)
        result = st.session_state.messages[-1].get("result", {})
        for cite in result.get("citations", []):
            st.caption(f"[{cite['source_id']}] {cite['source']} — page {cite.get('page', 'n/a')}")

with tab_library:
    st.markdown("<div class='section-title'>Your indexed scheme library</div><div class='section-sub'>See which official PDFs are available to the assistant and when the index was last rebuilt.</div>", unsafe_allow_html=True)
    if kb.get("files"):
        for item in kb["files"]:
            status = item.get("status", "Indexed")
            with st.expander(f"📄 {item.get('filename')}  ·  {status}"):
                c1, c2, c3 = st.columns(3)
                c1.metric("State", item.get("state", "All India"))
                c2.metric("Pages", item.get("pages", 0))
                c3.metric("Chunks", item.get("chunks", 0))
                st.caption(f"Category: {item.get('category', 'Not tagged')} · Uploaded: {item.get('uploaded_at', 'Unknown')}")
    else:
        st.info("No documents have been indexed yet. Upload official PDF scheme guidelines from the sidebar and build the knowledge base.")
    if kb.get("updated_at"):
        st.caption(f"Last index build: {kb['updated_at']}")
    st.markdown("<div class='tip'>Tip: Add the current financial-year guidelines, official FAQs and state-specific orders. If a document is scanned and text cannot be extracted, this version will flag it; OCR can be added as a next enhancement.</div>", unsafe_allow_html=True)

st.markdown("<hr><div style='text-align:center;color:#52685A;font-size:.84rem'>Guru · Retrieval-Augmented Generation for agricultural scheme discovery · Verify every decision with official authorities.</div>", unsafe_allow_html=True)
