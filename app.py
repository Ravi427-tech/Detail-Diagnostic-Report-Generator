"""
DDR Pipeline — Beautiful Streamlit UI (Groq Version - FREE)
Complete dark-themed professional UI with working CSS overrides.
Run with: streamlit run app.py
"""

import os, sys, json, tempfile
import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

# ── MUST be very first Streamlit call ─────────────────────────────────────────
st.set_page_config(
    page_title="DDR Report Generator",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── INJECT FULL CUSTOM THEME ──────────────────────────────────────────────────
st.markdown("""
<style>
/* ═══════════════════════════════════════════════════════
   GLOBAL RESET & DARK BASE
═══════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg:      #080B0F;
  --surface: #0F1318;
  --card:    #151A21;
  --border:  #1E2530;
  --border2: #252D38;
  --yellow:  #F0A500;
  --yellow2: #FFD060;
  --lime:    #6BCB5A;
  --red:     #E05252;
  --orange:  #E08C30;
  --white:   #EEF0F3;
  --grey:    #5A6472;
  --grey2:   #3A424E;
  --mono:    'JetBrains Mono', monospace;
  --sans:    'Inter', sans-serif;
  --display: 'Syne', sans-serif;
}

html, body { background: var(--bg) !important; }

/* Remove all Streamlit chrome */
#root > div:first-child { background: var(--bg) !important; }
.stApp { background: var(--bg) !important; }
[data-testid="stAppViewContainer"] { background: var(--bg) !important; }
[data-testid="stHeader"] { background: transparent !important; height: 0 !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
footer, #MainMenu { display: none !important; }
.stDeployButton { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }

/* Block container */
.block-container {
  padding: 0 !important;
  max-width: 100% !important;
}

.main .block-container { padding: 0 !important; }

/* ═══════════════════════════════════════════════════════
   INPUT WIDGETS — DARK OVERRIDE
═══════════════════════════════════════════════════════ */
div[data-baseweb="input"] {
  background: var(--card) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 8px !important;
}

div[data-baseweb="input"]:focus-within {
  border-color: var(--yellow) !important;
  box-shadow: 0 0 0 3px rgba(240,165,0,0.1) !important;
}

div[data-baseweb="input"] input {
  background: transparent !important;
  color: var(--white) !important;
  font-family: var(--sans) !important;
  font-size: 0.875rem !important;
  caret-color: var(--yellow) !important;
}

div[data-baseweb="input"] input::placeholder { color: var(--grey) !important; }

/* File uploader */
[data-testid="stFileUploadDropzone"] {
  background: var(--card) !important;
  border: 1.5px dashed var(--border2) !important;
  border-radius: 10px !important;
  transition: all 0.2s !important;
}

[data-testid="stFileUploadDropzone"]:hover {
  border-color: var(--yellow) !important;
  background: rgba(240,165,0,0.03) !important;
}

[data-testid="stFileUploadDropzone"] p,
[data-testid="stFileUploadDropzone"] span,
[data-testid="stFileUploadDropzone"] small {
  color: var(--grey) !important;
  font-family: var(--sans) !important;
}

[data-testid="stFileUploaderFileName"] {
  color: var(--lime) !important;
  font-family: var(--mono) !important;
  font-size: 0.78rem !important;
}

/* Buttons */
.stButton > button {
  background: var(--yellow) !important;
  color: #080B0F !important;
  font-family: var(--display) !important;
  font-weight: 700 !important;
  font-size: 0.9rem !important;
  border: none !important;
  border-radius: 8px !important;
  padding: 0.7rem 1.5rem !important;
  letter-spacing: 0.01em !important;
  transition: all 0.18s ease !important;
  box-shadow: 0 2px 12px rgba(240,165,0,0.25) !important;
}

.stButton > button:hover {
  background: var(--yellow2) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(240,165,0,0.35) !important;
}

.stButton > button:disabled {
  background: var(--border2) !important;
  color: var(--grey) !important;
  box-shadow: none !important;
  transform: none !important;
  cursor: not-allowed !important;
}

/* Download button */
.stDownloadButton > button {
  background: transparent !important;
  color: var(--yellow) !important;
  border: 1.5px solid var(--yellow) !important;
  font-family: var(--display) !important;
  font-weight: 700 !important;
  border-radius: 8px !important;
  transition: all 0.18s !important;
  box-shadow: none !important;
}

.stDownloadButton > button:hover {
  background: rgba(240,165,0,0.08) !important;
  transform: translateY(-1px) !important;
}

/* Progress bar */
[data-testid="stProgressBar"] > div {
  background: var(--border) !important;
  border-radius: 6px !important;
  height: 6px !important;
}

[data-testid="stProgressBar"] > div > div {
  background: linear-gradient(90deg, var(--yellow), var(--yellow2)) !important;
  border-radius: 6px !important;
}

/* Alerts */
[data-testid="stAlert"] {
  border-radius: 10px !important;
  border-left: 3px solid !important;
  font-family: var(--sans) !important;
}

div[data-baseweb="notification"][kind="positive"],
.stSuccess {
  background: rgba(107,203,90,0.08) !important;
  border-color: var(--lime) !important;
  color: var(--lime) !important;
}

.stError {
  background: rgba(224,82,82,0.08) !important;
  border-color: var(--red) !important;
}

.stInfo {
  background: rgba(240,165,0,0.06) !important;
  border-color: rgba(240,165,0,0.3) !important;
}

/* Metrics */
[data-testid="metric-container"] {
  background: var(--card) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 10px !important;
  padding: 1.1rem 1.2rem !important;
  transition: border-color 0.2s !important;
}

[data-testid="metric-container"]:hover {
  border-color: rgba(240,165,0,0.3) !important;
}

[data-testid="metric-container"] label {
  color: var(--grey) !important;
  font-family: var(--mono) !important;
  font-size: 0.65rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
}

[data-testid="stMetricValue"] {
  color: var(--yellow) !important;
  font-family: var(--display) !important;
  font-size: 1.8rem !important;
  font-weight: 800 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  background: var(--card) !important;
  border-bottom: 1px solid var(--border2) !important;
  gap: 0 !important;
  padding: 0 1rem !important;
}

.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--grey) !important;
  font-family: var(--mono) !important;
  font-size: 0.72rem !important;
  letter-spacing: 0.04em !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  padding: 0.7rem 1rem !important;
  transition: all 0.2s !important;
}

.stTabs [aria-selected="true"] {
  color: var(--yellow) !important;
  border-bottom-color: var(--yellow) !important;
  background: transparent !important;
}

.stTabs [data-baseweb="tab-panel"] {
  background: var(--card) !important;
  border: 1px solid var(--border2) !important;
  border-top: none !important;
  border-radius: 0 0 10px 10px !important;
  padding: 1.5rem !important;
}

/* Expander */
details {
  background: var(--card) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 8px !important;
  overflow: hidden !important;
}

summary {
  background: var(--surface) !important;
  color: var(--white) !important;
  font-family: var(--mono) !important;
  font-size: 0.78rem !important;
  padding: 0.8rem 1rem !important;
}

/* Text */
h1, h2, h3 {
  font-family: var(--display) !important;
  color: var(--white) !important;
}

p, li, span, div {
  font-family: var(--sans) !important;
}

hr { border-color: var(--border) !important; }

/* Labels above widgets */
label[data-testid="stWidgetLabel"] {
  color: var(--grey) !important;
  font-family: var(--mono) !important;
  font-size: 0.68rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.06em !important;
}

/* Code blocks */
code, pre {
  background: var(--surface) !important;
  color: var(--yellow2) !important;
  font-family: var(--mono) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 6px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--grey2); }

/* ═══════════════════════════════════════════════════════
   CUSTOM COMPONENTS
═══════════════════════════════════════════════════════ */

/* Topbar */
.topbar {
  background: rgba(8,11,15,0.96);
  border-bottom: 1px solid var(--border2);
  padding: 0.85rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky; top: 0; z-index: 999;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.topbar-brand {
  display: flex; align-items: center; gap: 0.6rem;
  font-family: var(--display);
  font-weight: 800; font-size: 1rem;
  color: var(--white); letter-spacing: -0.02em;
}

.brand-dot {
  width: 9px; height: 9px;
  background: var(--yellow); border-radius: 50%;
  display: inline-block;
  box-shadow: 0 0 8px rgba(240,165,0,0.6);
  animation: glow 2s ease-in-out infinite;
}

@keyframes glow {
  0%,100% { box-shadow: 0 0 6px rgba(240,165,0,0.5); }
  50%      { box-shadow: 0 0 14px rgba(240,165,0,0.9); }
}

.topbar-pill {
  font-family: var(--mono); font-size: 0.65rem;
  color: var(--yellow);
  background: rgba(240,165,0,0.1);
  border: 1px solid rgba(240,165,0,0.25);
  padding: 0.22rem 0.75rem; border-radius: 100px;
  letter-spacing: 0.05em;
}

/* Hero */
.hero {
  background: var(--bg);
  padding: 4.5rem 2rem 3.5rem;
  text-align: center;
  position: relative; overflow: hidden;
  border-bottom: 1px solid var(--border);
}

.hero-grid {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.018) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(ellipse 85% 70% at 50% 50%, black, transparent);
  pointer-events: none;
}

.hero-glow {
  position: absolute; width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(240,165,0,0.07) 0%, transparent 65%);
  top: 50%; left: 50%; transform: translate(-50%,-50%);
  pointer-events: none;
}

.hero-eyebrow {
  font-family: var(--mono); font-size: 0.68rem;
  letter-spacing: 0.16em; color: var(--yellow);
  text-transform: uppercase; margin-bottom: 1.2rem;
  position: relative; z-index: 1;
}

.hero-h1 {
  font-family: var(--display); font-weight: 800;
  font-size: clamp(2.2rem, 5.5vw, 4.2rem);
  line-height: 1; letter-spacing: -0.04em;
  color: var(--white); margin-bottom: 0.9rem;
  position: relative; z-index: 1;
}

.hero-h1 em { color: var(--yellow); font-style: normal; }

.hero-lead {
  font-size: 1rem; color: var(--grey);
  max-width: 440px; margin: 0 auto 0;
  font-weight: 400; line-height: 1.7;
  position: relative; z-index: 1;
}

/* Stat strip */
.stat-strip {
  display: flex; justify-content: center;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}

.stat-cell {
  flex: 1; max-width: 160px;
  padding: 1.2rem 1rem; text-align: center;
  border-right: 1px solid var(--border);
  transition: background 0.2s;
}
.stat-cell:last-child { border-right: none; }
.stat-cell:hover { background: var(--card); }

.stat-n {
  font-family: var(--display); font-weight: 800;
  font-size: 1.6rem; color: var(--yellow); line-height: 1;
  margin-bottom: 0.2rem;
}

.stat-l {
  font-family: var(--mono); font-size: 0.6rem;
  color: var(--grey); letter-spacing: 0.08em; text-transform: uppercase;
}

/* Section wrapper */
.wrap { max-width: 1280px; margin: 0 auto; padding: 2.5rem 2rem; }

/* Config card */
.cfg-card {
  background: var(--card);
  border: 1px solid var(--border2);
  border-radius: 12px;
  padding: 1.8rem;
  position: sticky; top: 4rem;
}

.cfg-title {
  font-family: var(--display); font-weight: 800;
  font-size: 0.88rem; color: var(--white);
  display: flex; align-items: center; gap: 0.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1.4rem;
}

.cfg-title::before {
  content: '';
  display: block; width: 3px; height: 14px;
  background: var(--yellow); border-radius: 2px;
}

.fld-lbl {
  font-family: var(--mono); font-size: 0.62rem;
  color: var(--grey); letter-spacing: 0.08em;
  text-transform: uppercase; margin-bottom: 0.35rem;
  display: block;
}

.tip {
  background: rgba(240,165,0,0.06);
  border: 1px solid rgba(240,165,0,0.14);
  border-radius: 6px;
  padding: 0.55rem 0.8rem;
  font-family: var(--mono); font-size: 0.65rem;
  color: #7A6A40; line-height: 1.5; margin-top: 0.3rem;
}
.tip a { color: var(--yellow); text-decoration: none; }

.upload-lbl {
  font-family: var(--mono); font-size: 0.62rem;
  color: var(--grey); letter-spacing: 0.08em;
  text-transform: uppercase; display: block; margin-bottom: 0.35rem;
}

.file-ok {
  font-family: var(--mono); font-size: 0.68rem;
  color: var(--lime); margin-top: 0.25rem;
}

.divider { height: 1px; background: var(--border); margin: 1.2rem 0; }

/* Steps tracker */
.tracker-card {
  background: var(--card);
  border: 1px solid var(--border2);
  border-radius: 12px; overflow: hidden;
  margin-bottom: 1.2rem;
}

.tracker-head {
  background: var(--surface);
  border-bottom: 1px solid var(--border2);
  padding: 0.85rem 1.2rem;
  font-family: var(--display); font-weight: 800;
  font-size: 0.8rem; color: var(--white);
  display: flex; align-items: center; gap: 0.5rem;
}

.step-row {
  display: flex; align-items: center; gap: 0.85rem;
  padding: 0.75rem 1.2rem;
  border-bottom: 1px solid var(--border);
  transition: background 0.2s;
}
.step-row:last-child { border-bottom: none; }
.step-row.s-waiting { background: transparent; }
.step-row.s-running { background: rgba(240,165,0,0.04); }
.step-row.s-done    { background: rgba(107,203,90,0.04); }
.step-row.s-error   { background: rgba(224,82,82,0.04); }

.step-badge {
  width: 27px; height: 27px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--mono); font-size: 0.62rem;
  flex-shrink: 0;
}
.s-waiting .step-badge { background: var(--surface); border: 1px solid var(--border2); color: var(--grey); }
.s-running .step-badge { background: rgba(240,165,0,0.12); border: 1px solid rgba(240,165,0,0.35); color: var(--yellow); animation: spin-ring 1.4s linear infinite; }
.s-done    .step-badge { background: rgba(107,203,90,0.12); border: 1px solid rgba(107,203,90,0.35); color: var(--lime); }
.s-error   .step-badge { background: rgba(224,82,82,0.12); border: 1px solid rgba(224,82,82,0.35); color: var(--red); }

@keyframes spin-ring {
  0%   { box-shadow: 0 0 0 0 rgba(240,165,0,0.4); }
  50%  { box-shadow: 0 0 0 5px rgba(240,165,0,0); }
  100% { box-shadow: 0 0 0 0 rgba(240,165,0,0); }
}

.step-info { flex: 1; }
.step-name { font-size: 0.8rem; font-weight: 500; }
.s-waiting .step-name { color: var(--grey); }
.s-running .step-name, .s-done .step-name { color: var(--white); }

.step-sub {
  font-family: var(--mono); font-size: 0.62rem;
  margin-top: 0.08rem; display: block;
}
.s-waiting .step-sub { color: var(--grey2); }
.s-running .step-sub { color: var(--yellow); }
.s-done    .step-sub { color: var(--lime); }

.step-time {
  font-family: var(--mono); font-size: 0.6rem; color: var(--grey2);
}
.s-done .step-time { color: var(--lime); }

/* Results card */
.res-card {
  background: var(--card);
  border: 1px solid var(--border2);
  border-radius: 12px; overflow: hidden;
  margin-bottom: 1.2rem;
}

.res-head {
  background: var(--surface);
  border-bottom: 1px solid var(--border2);
  padding: 0.85rem 1.2rem;
  font-family: var(--display); font-weight: 800;
  font-size: 0.8rem; color: var(--white);
  display: flex; align-items: center; gap: 0.5rem;
}

.res-body { padding: 1.2rem; }

/* Area observation cards */
.obs-card {
  background: var(--surface);
  border: 1px solid var(--border2);
  border-radius: 8px;
  margin-bottom: 0.7rem; overflow: hidden;
}

.obs-head {
  padding: 0.55rem 0.9rem;
  background: var(--card);
  border-bottom: 1px solid var(--border2);
  display: flex; justify-content: space-between; align-items: center;
}

.obs-name {
  font-family: var(--display); font-weight: 800;
  font-size: 0.78rem; color: var(--yellow);
}

.sev-pill {
  font-family: var(--mono); font-size: 0.58rem;
  font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 0.14rem 0.55rem; border-radius: 100px;
}
.sev-critical { background:rgba(224,82,82,0.14);  color:#E57373; border:1px solid rgba(224,82,82,0.3); }
.sev-high     { background:rgba(224,140,48,0.14); color:#FFB74D; border:1px solid rgba(224,140,48,0.3); }
.sev-medium   { background:rgba(255,210,60,0.1);  color:#FFD740; border:1px solid rgba(255,210,60,0.25); }
.sev-low      { background:rgba(107,203,90,0.1);  color:#81C784; border:1px solid rgba(107,203,90,0.25); }

.obs-body {
  padding: 0.8rem 0.9rem;
  display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem;
}

.obs-col h5 {
  font-family: var(--mono); font-size: 0.58rem;
  text-transform: uppercase; letter-spacing: 0.07em;
  color: var(--grey2); margin-bottom: 0.4rem;
}

.obs-item {
  display: flex; gap: 0.4rem;
  font-size: 0.74rem; color: rgba(238,240,243,0.7);
  line-height: 1.45; padding: 0.15rem 0;
  border-bottom: 1px solid rgba(255,255,255,0.025);
}

.obs-item::before { content:'—'; color:var(--yellow); font-size:0.6rem; flex-shrink:0; margin-top:0.12rem; }

/* Condition table */
.ct { width:100%; border-collapse:collapse; font-size:0.73rem; }
.ct th {
  background: var(--surface); padding: 0.42rem 0.7rem;
  text-align:left; font-family:var(--mono); font-size:0.6rem;
  text-transform:uppercase; letter-spacing:0.04em; color:var(--grey);
  border-bottom:1px solid var(--border2);
}
.ct th.tg{color:#81C784;} .ct th.tm{color:#FFB74D;} .ct th.tp{color:#E57373;}
.ct td {
  padding:0.4rem 0.7rem; border-bottom:1px solid rgba(255,255,255,0.03);
  color:rgba(238,240,243,0.72); vertical-align:middle;
}
.ct tr:nth-child(even) td{background:rgba(255,255,255,0.018);}
.cg{color:#81C784;font-size:0.85rem;} .cm{color:#FFB74D;font-size:0.85rem;} .cp{color:#E57373;font-size:0.85rem;}

/* Summary table */
.st { width:100%; border-collapse:collapse; font-size:0.74rem; }
.st thead tr { background: rgba(26,58,107,0.8); }
.st th { padding:0.5rem 0.8rem; color:white; font-family:var(--mono); font-size:0.62rem; text-transform:uppercase; letter-spacing:0.04em; text-align:left; }
.st td { padding:0.45rem 0.8rem; border-bottom:1px solid var(--border); color:rgba(238,240,243,0.72); vertical-align:top; }
.st tr:nth-child(odd) td{background:rgba(200,216,240,0.04);}
.pt{color:var(--yellow);font-family:var(--mono);font-weight:700;}

/* Rec groups */
.rg { margin-bottom:1.1rem; }
.rg-title {
  display:inline-block; font-family:var(--display); font-weight:700;
  font-size:0.72rem; padding:0.28rem 0.75rem; border-radius:4px; margin-bottom:0.55rem;
}
.rg-imm{background:rgba(224,82,82,0.1);  color:#E57373;}
.rg-sht{background:rgba(224,140,48,0.1); color:#FFB74D;}
.rg-lng{background:rgba(107,203,90,0.1); color:#81C784;}

.ri {
  display:flex; gap:0.45rem; font-size:0.76rem;
  color:rgba(238,240,243,0.72); padding:0.28rem 0;
  line-height:1.5; border-bottom:1px solid rgba(255,255,255,0.03);
}
.ri::before{content:'▸';color:var(--yellow);font-size:0.62rem;flex-shrink:0;margin-top:0.15rem;}

/* Severity grid */
.sv-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(110px,1fr)); gap:0.7rem; }
.sv-cell { background:var(--surface); border:1px solid var(--border2); border-radius:8px; padding:0.9rem; text-align:center; }
.sv-lbl{font-family:var(--mono);font-size:0.6rem;color:var(--grey);margin-bottom:0.3rem;text-transform:uppercase;letter-spacing:0.05em;}
.sv-val{font-family:var(--display);font-weight:800;font-size:0.8rem;}

/* Overall severity box */
.ov-box {
  background:var(--surface); border:1px solid var(--border2);
  border-radius:8px; padding:1.1rem; margin-top:1rem;
}
.ov-lbl{font-family:var(--mono);font-size:0.6rem;color:var(--grey);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.4rem;}
.ov-val{font-family:var(--display);font-weight:800;font-size:1.5rem;}

/* Empty state */
.empty-state {
  text-align:center; padding:4rem 1rem;
  color:var(--grey);
}
.empty-icon{font-size:3rem;margin-bottom:1rem;}
.empty-title{font-family:var(--display);font-weight:800;font-size:1.05rem;color:var(--white);margin-bottom:0.5rem;}
.empty-sub{font-size:0.82rem;max-width:280px;margin:0 auto;line-height:1.6;}

/* Footer */
.pg-footer {
  border-top:1px solid var(--border);
  padding:1.2rem 2rem;
  display:flex; justify-content:space-between; align-items:center;
  font-size:0.72rem; color:var(--grey2); font-family:var(--mono);
}
.pg-footer a{color:var(--yellow);text-decoration:none;}
</style>
""", unsafe_allow_html=True)

# ── Pipeline imports ───────────────────────────────────────────────────────────
from phase1_parser       import parse_both_documents
from phase2_extractor    import run_phase2
from phase3_merger       import run_phase3
from phase4_image_associator import run_phase4
from phase5_generator    import run_phase5
from phase6_assembler    import run_phase6

# ─────────────────────────────────────────────────────────────────────────────
# TOP BAR
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div class="topbar-brand">
    <span class="brand-dot"></span>
    DDR Report Generator
  </div>
  <span class="topbar-pill">Groq · LLaMA 3.3 · Free</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-grid"></div>
  <div class="hero-glow"></div>
  <div class="hero-eyebrow">AI · Free · Professional</div>
  <h1 class="hero-h1">Detailed Diagnostic<br><em>Report Generator</em></h1>
</div>

<div class="stat-strip">
  <div class="stat-cell"><div class="stat-n">6</div><div class="stat-l">AI Phases</div></div>
  <div class="stat-cell"><div class="stat-n">&lt;2m</div><div class="stat-l">Generation</div></div>
  <div class="stat-cell"><div class="stat-n">7</div><div class="stat-l">DDR Sections</div></div>
  <div class="stat-cell"><div class="stat-n">Free</div><div class="stat-l">Groq API</div></div>
  <div class="stat-cell"><div class="stat-n">PDF</div><div class="stat-l">Output</div></div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN LAYOUT
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="wrap">', unsafe_allow_html=True)

left, right = st.columns([5, 8], gap="large")

# ══════════════════════════════════════
# LEFT — Config form
# ══════════════════════════════════════
with left:
    st.markdown('<div class="cfg-card">', unsafe_allow_html=True)
    st.markdown('<div class="cfg-title">Configuration</div>', unsafe_allow_html=True)

    st.markdown('<span class="fld-lbl">🔑 Groq API Key</span>', unsafe_allow_html=True)
    api_key = st.text_input("api_key", placeholder="gsk_···",
                             type="password", label_visibility="collapsed")
    st.markdown('<div class="tip">Free key at <a href="https://console.groq.com" target="_blank">console.groq.com</a> — 30 seconds to get</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="fld-lbl">🏢 Property Name</span>', unsafe_allow_html=True)
    property_name = st.text_input("prop", placeholder="e.g. Flat No-8/63, Yamuna CHS",
                                   value="Site Inspection", label_visibility="collapsed")

    st.markdown('<span class="fld-lbl">👤 Inspector Name</span>', unsafe_allow_html=True)
    inspector = st.text_input("insp", placeholder="e.g. Tushar Rahane",
                               label_visibility="collapsed")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="cfg-title">Upload Documents</div>', unsafe_allow_html=True)

    st.markdown('<span class="upload-lbl">📋 Inspection Report PDF</span>', unsafe_allow_html=True)
    insp_file = st.file_uploader("insp_pdf", type=["pdf"],
                                  label_visibility="collapsed", key="insp_up")
    if insp_file:
        mb = len(insp_file.getvalue()) / 1024 / 1024
        st.markdown(f'<div class="file-ok">✓ {insp_file.name} ({mb:.1f} MB)</div>', unsafe_allow_html=True)

    st.markdown('<span class="upload-lbl">🌡️ Thermal Report PDF</span>', unsafe_allow_html=True)
    therm_file = st.file_uploader("therm_pdf", type=["pdf"],
                                   label_visibility="collapsed", key="therm_up")
    if therm_file:
        mb = len(therm_file.getvalue()) / 1024 / 1024
        st.markdown(f'<div class="file-ok">✓ {therm_file.name} ({mb:.1f} MB)</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    ready = bool(api_key and insp_file and therm_file)
    run = st.button("⚡  Generate DDR Report", disabled=not ready,
                     use_container_width=True)

    if not ready:
        missing = []
        if not api_key: missing.append("API key")
        if not insp_file: missing.append("Inspection PDF")
        if not therm_file: missing.append("Thermal PDF")
        st.markdown(f'<div style="text-align:center;font-family:var(--mono);font-size:0.62rem;color:#3A424E;margin-top:0.5rem;">Missing: {", ".join(missing)}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # /cfg-card

# ══════════════════════════════════════
# RIGHT — Tracker + Results
# ══════════════════════════════════════
with right:

    STEPS = [
        ("01", "Parse Documents",             "Extract text & images from both PDFs"),
        ("02", "Extract Observations (AI)",   "LLaMA 3.3 structures the raw data"),
        ("03", "Merge & Deduplicate",         "Combine inspection + thermal by area"),
        ("04", "Associate Images",            "Link images to report sections"),
        ("05", "Generate DDR Text (AI)",      "Write all 7 DDR sections"),
        ("06", "Assemble PDF",                "Build the branded final document"),
    ]

    # ── Tracker card ─────────────────────────────────────────────────────────
    st.markdown("""
    <div class="tracker-card">
      <div class="tracker-head">🔄 Pipeline Status</div>
    """, unsafe_allow_html=True)

    placeholders = [st.empty() for _ in STEPS]

    def render(states):
        for i, (num, title, sub) in enumerate(STEPS):
            s    = states.get(i, "waiting")
            sub_ = states.get(f"s{i}", sub)
            tm   = states.get(f"t{i}", "")
            icon = "✓" if s=="done" else ("✕" if s=="error" else ("◎" if s=="running" else num))
            placeholders[i].markdown(f"""
            <div class="step-row s-{s}">
              <div class="step-badge">{icon}</div>
              <div class="step-info">
                <span class="step-name">{title}</span>
                <span class="step-sub">{sub_}</span>
              </div>
              <span class="step-time">{tm}</span>
            </div>
            """, unsafe_allow_html=True)

    render({})
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Empty state ───────────────────────────────────────────────────────────
    if not run:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">🏗️</div>
          <div class="empty-title">Ready to Generate</div>
          <div class="empty-sub">Complete the configuration on the left and click Generate to start.</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Pipeline execution ────────────────────────────────────────────────────
    if run and ready:
        import time
        os.environ["GROQ_API_KEY"] = api_key

        with tempfile.TemporaryDirectory() as tmp:
            ipath = os.path.join(tmp, "inspection.pdf")
            tpath = os.path.join(tmp, "thermal.pdf")
            ws    = os.path.join(tmp, "ws")
            os.makedirs(ws, exist_ok=True)
            with open(ipath,"wb") as f: f.write(insp_file.getvalue())
            with open(tpath,"wb") as f: f.write(therm_file.getvalue())

            pbar = st.progress(0)
            st_ = {}

            def act(i, msg):
                st_[i] = "running"; st_[f"s{i}"] = msg
                render(st_); pbar.progress(i*14 + 5)

            def done(i, msg, t):
                st_[i] = "done"; st_[f"s{i}"] = msg; st_[f"t{i}"] = f"{t:.1f}s"
                render(st_)

            try:
                t0 = time.time()
                act(0, "Parsing PDFs...")
                id_, td_ = parse_both_documents(ipath, tpath, ws)
                np_ = len(id_["pages"]) + len(td_["pages"])
                ni_ = len(id_["images"]) + len(td_["images"])
                done(0, f"✓ {np_} pages · {ni_} images", time.time()-t0)
                pbar.progress(18)

                t0 = time.time()
                act(1, "Sending to LLaMA 3.3 via Groq...")
                io_, tf_ = run_phase2(id_, td_, ws)
                done(1, f"✓ {len(io_)} inspection · {len(tf_)} thermal blocks", time.time()-t0)
                pbar.progress(36)

                t0 = time.time()
                act(2, "Merging areas, detecting conflicts...")
                mr_ = run_phase3(io_, tf_, ws)
                cf_ = sum(1 for r in mr_ if r.get("conflicts"))
                done(2, f"✓ {len(mr_)} areas merged · {cf_} conflict(s)", time.time()-t0)
                pbar.progress(50)

                t0 = time.time()
                act(3, "Associating images to areas...")
                mr_ = run_phase4(mr_, id_, td_, ws)
                ti_ = sum(len(r.get("images",[])) for r in mr_)
                done(3, f"✓ {ti_} image(s) associated", time.time()-t0)
                pbar.progress(62)

                t0 = time.time()
                act(4, "LLaMA 3.3 writing DDR sections...")
                rt_, sc_ = run_phase5(mr_, ws)
                done(4, f"✓ {len(sc_)} sections · {len(rt_):,} chars", time.time()-t0)
                pbar.progress(80)

                t0 = time.time()
                act(5, "ReportLab assembling branded PDF...")
                pdf_path = run_phase6(mr_, sc_, ws, property_name)
                done(5, "✓ DDR_Report.pdf ready", time.time()-t0)
                pbar.progress(100)

                # ── SUCCESS ───────────────────────────────────────────────
                st.success("🎉 **DDR Report Generated Successfully!**")

                with open(pdf_path,"rb") as f: pdf_bytes = f.read()

                dc, mc = st.columns(2)
                with dc:
                    st.download_button("⬇️  Download PDF", pdf_bytes,
                        "DDR_Report.pdf", "application/pdf",
                        use_container_width=True)
                with mc:
                    mdp = os.path.join(ws, "ddr_report_text.md")
                    if os.path.exists(mdp):
                        with open(mdp) as f:
                            st.download_button("📄  Download Markdown", f.read(),
                                "DDR_Report.md", "text/markdown",
                                use_container_width=True)

                # ── Metrics ───────────────────────────────────────────────
                st.markdown("<br>", unsafe_allow_html=True)
                c1,c2,c3,c4 = st.columns(4)
                c1.metric("Areas", len(mr_))
                c2.metric("Conflicts", cf_)
                c3.metric("Images", ti_)
                c4.metric("Sections", len(sc_))

                # ── Preview tabs ──────────────────────────────────────────
                st.markdown("<br>", unsafe_allow_html=True)
                t1,t2,t3,t4,t5,t6 = st.tabs([
                    "📝 Summary", "🔍 Observations",
                    "📊 Conditions", "📋 Table",
                    "⚡ Actions", "⚠️ Severity"
                ])

                SEV = {"critical":3,"high":2,"medium":1,"low":0,"unknown":1}
                SC  = {"critical":"sev-critical","high":"sev-high",
                       "medium":"sev-medium","low":"sev-low"}

                # Tab 1 ── Summary
                with t1:
                    s1 = sc_.get("1. Property Issue Summary","Not Available")
                    st.markdown(f"""
                    <div style="background:var(--surface);border:1px solid var(--border2);
                         border-radius:8px;padding:1.2rem;font-size:0.83rem;
                         color:rgba(238,240,243,0.8);line-height:1.75;">
                      <div style="font-family:var(--mono);font-size:0.6rem;color:var(--yellow);
                           letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.7rem;">
                        PROPERTY ISSUE SUMMARY
                      </div>
                      {s1}
                    </div>""", unsafe_allow_html=True)

                # Tab 2 ── Observations
                with t2:
                    for rec in mr_:
                        area  = rec.get("area_name","Unknown")
                        insp_ = rec.get("inspection") or {}
                        th_   = rec.get("thermal") or {}
                        sev   = insp_.get("severity_hint","medium").lower()
                        obs   = insp_.get("observations") or []
                        anom  = th_.get("thermal_anomalies") or []
                        rd    = th_.get("temperature_readings") or {}
                        temps = " | ".join(f"{k.replace('_',' ').title()}: {v}°C"
                                           for k,v in rd.items() if v is not None)

                        obs_h  = "".join(f'<div class="obs-item">{o}</div>' for o in obs) \
                                 or '<div style="color:var(--grey2);font-size:0.72rem">Not Available</div>'
                        anom_h = "".join(f'<div class="obs-item">{a}</div>' for a in anom) \
                                 or '<div style="color:var(--grey2);font-size:0.72rem">Not Available</div>'
                        temp_h = f'<div style="font-family:var(--mono);font-size:0.65rem;color:var(--yellow);margin-top:0.5rem">{temps}</div>' if temps else ""

                        st.markdown(f"""
                        <div class="obs-card">
                          <div class="obs-head">
                            <span class="obs-name">▸ {area.upper()}</span>
                            <span class="sev-pill {SC.get(sev,'sev-medium')}">{sev.upper()}</span>
                          </div>
                          <div class="obs-body">
                            <div class="obs-col">
                              <h5>Inspection Findings</h5>{obs_h}
                            </div>
                            <div class="obs-col">
                              <h5>Thermal Findings</h5>{anom_h}{temp_h}
                            </div>
                          </div>
                        </div>""", unsafe_allow_html=True)

                # Tab 3 ── Conditions
                with t3:
                    for rec in mr_:
                        area  = rec.get("area_name","Unknown")
                        insp_ = rec.get("inspection") or {}
                        th_   = rec.get("thermal") or {}
                        sev   = insp_.get("severity_hint","medium").lower()
                        obs   = insp_.get("observations") or ["General assessment"]
                        anom  = th_.get("thermal_anomalies") or []

                        def cond(s):
                            r = SEV.get(s,1)
                            if r==0: return '<span class="cg">✓</span>','',''
                            if r==1: return '','<span class="cm">✓</span>',''
                            return '','','<span class="cp">✓</span>'

                        rows = ""
                        for i,ob in enumerate(obs[:5]):
                            g,m,p = cond(sev)
                            rows += f"<tr><td>{i+1}</td><td>{ob[:80]}</td><td style='text-align:center'>{g}</td><td style='text-align:center'>{m}</td><td style='text-align:center'>{p}</td><td style='color:var(--grey2);font-size:0.65rem'></td></tr>"
                        if anom:
                            ts=th_.get("severity_hint","medium").lower()
                            g,m,p=cond(ts)
                            rows += f"<tr><td>{len(obs[:5])+1}</td><td style='color:var(--yellow)'>{anom[0][:70]}</td><td style='text-align:center'>{g}</td><td style='text-align:center'>{m}</td><td style='text-align:center'>{p}</td><td style='color:var(--yellow);font-size:0.65rem'>{th_.get('probable_cause_hint','')}</td></tr>"

                        st.markdown(f"""
                        <div style="margin-bottom:1.4rem">
                          <div style="font-family:var(--display);font-weight:800;font-size:0.78rem;
                               color:var(--yellow);padding:0.45rem 0.8rem;
                               border-left:3px solid var(--yellow);background:var(--surface);
                               margin-bottom:0.5rem">{area} — Condition Table</div>
                          <table class="ct">
                            <thead><tr>
                              <th style="width:32px">Sr</th><th>Input Type</th>
                              <th class="tg" style="width:52px">Good</th>
                              <th class="tm" style="width:62px">Moderate</th>
                              <th class="tp" style="width:48px">Poor</th>
                              <th>Remarks</th>
                            </tr></thead>
                            <tbody>{rows}</tbody>
                          </table>
                          <div style="font-size:0.6rem;color:var(--grey2);margin-top:0.3rem;font-family:var(--mono)">
                            Good = No Action · Moderate = Repairs Needed · Poor = Immediate Action
                          </div>
                        </div>""", unsafe_allow_html=True)

                # Tab 4 ── Summary table
                with t4:
                    rows = ""
                    for i,rec in enumerate(mr_):
                        insp_=(rec.get("inspection") or {})
                        th_  =(rec.get("thermal") or {})
                        neg  =(insp_.get("observations") or ["Not Available"])
                        pos  =(th_.get("thermal_anomalies") or ["Not Available"])
                        pt   =f"4.{i+1}"
                        rows += f'<tr><td class="pt">{pt}</td><td>{neg[0][:100]}</td><td class="pt">{pt}</td><td>{pos[0][:100]}</td></tr>'
                    st.markdown(f"""
                    <table class="st">
                      <thead><tr>
                        <th style="width:55px">Point No</th>
                        <th>Impacted Area (−ve Side)</th>
                        <th style="width:55px">Point No</th>
                        <th>Exposed Area (+ve Side)</th>
                      </tr></thead>
                      <tbody>{rows}</tbody>
                    </table>""", unsafe_allow_html=True)

                # Tab 5 ── Actions
                with t5:
                    s5 = sc_.get("5. Recommended Actions","Not Available")
                    grp = {"imm":[], "sht":[], "lng":[]}
                    cur = None
                    for ln in s5.split("\n"):
                        l = ln.strip()
                        if not l: continue
                        if any(w in l.lower() for w in ["immediate","critical","high"]):  cur="imm"
                        elif any(w in l.lower() for w in ["short","medium","week"]):      cur="sht"
                        elif any(w in l.lower() for w in ["long","low","preventive"]):    cur="lng"
                        elif cur:
                            t=l.lstrip("-•*#▸ ").strip()
                            if t and not t.startswith("**") and len(t)>8: grp[cur].append(t)

                    # Fallback: distribute lines evenly
                    if not any(grp.values()):
                        items=[l.lstrip("-•*#▸ ").strip() for l in s5.split("\n") if l.strip() and len(l.strip())>10]
                        grp["imm"]=items[:3]; grp["sht"]=items[3:6]; grp["lng"]=items[6:]

                    labels={"imm":("⚡ Immediate (Critical/High)","rg-imm"),
                            "sht":("🔧 Short-term (Medium)","rg-sht"),
                            "lng":("📅 Long-term (Low)","rg-lng")}
                    html=""
                    for k,(lbl,cls) in labels.items():
                        items=grp[k]
                        if not items: items=["See report for details"]
                        ihtml="".join(f'<div class="ri">{it}</div>' for it in items[:5])
                        html+=f'<div class="rg"><div class="rg-title {cls}">{lbl}</div>{ihtml}</div>'
                    st.markdown(html, unsafe_allow_html=True)

                # Tab 6 ── Severity
                with t6:
                    cells=""
                    overall_r=0; overall_s="low"
                    for rec in mr_:
                        area=rec.get("area_name","")
                        isev=(rec.get("inspection") or {}).get("severity_hint","medium").lower()
                        tsev=(rec.get("thermal") or {}).get("severity_hint","medium").lower()
                        osev=isev if SEV.get(isev,1)>=SEV.get(tsev,1) else tsev
                        if SEV.get(osev,1)>overall_r: overall_r=SEV.get(osev,1); overall_s=osev
                        cells+=f'<div class="sv-cell"><div class="sv-lbl">{area}</div><div class="sv-val {SC.get(osev,"sev-medium")}">{osev.upper()}</div></div>'

                    ov_cls=SC.get(overall_s,"sev-medium")
                    st.markdown(f"""
                    <div class="sv-grid">{cells}</div>
                    <div class="ov-box">
                      <div class="ov-lbl">Overall Property Severity</div>
                      <div class="ov-val {ov_cls}">{overall_s.upper()}</div>
                    </div>""", unsafe_allow_html=True)

                with st.expander("👁️  View Raw Report Text"):
                    st.code(rt_, language="markdown")

            except Exception as e:
                import traceback
                for i in range(6):
                    if st_.get(i)=="running":
                        st_[i]="error"; st_[f"s{i}"]=f"✕ {str(e)[:60]}"
                render(st_)
                st.error(f"**Pipeline Error:** {e}")
                with st.expander("Show traceback"):
                    st.code(traceback.format_exc())

st.markdown("</div>", unsafe_allow_html=True)  # /wrap

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="pg-footer">
  <span>DDR Report Generator · Groq + LLaMA 3.3 · ReportLab · Python</span>
  <a href="https://console.groq.com" target="_blank">Get free API key →</a>
</div>
""", unsafe_allow_html=True)

