import streamlit as st
import pandas as pd
import requests
import feedparser
from urllib.parse import quote_plus
from datetime import datetime, timezone
from pathlib import Path
import io
import json
import uuid
import html

try:
    import yfinance as yf
except Exception:
    yf = None

st.set_page_config(
    page_title="Gold Intelligence MVP",
    page_icon="🟡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# STYLE
# ------------------------------------------------------------
st.markdown("""
<style>
    .stApp { background: #080b10; color: #f5f5f5; }
    [data-testid="stSidebar"] { background: #0d1117; }
    .small-muted { color: #8b949e; font-size: 0.82rem; letter-spacing: 0.02rem; }
    .section-card {
        background: linear-gradient(135deg, #111827 0%, #0b0f16 100%);
        border: 1px solid #222b38;
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0 0 18px rgba(0,0,0,0.25);
    }
    .bias-card-green {
        background: rgba(20, 83, 45, 0.25);
        border: 1px solid rgba(74, 222, 128, 0.35);
        border-radius: 16px;
        padding: 18px;
        text-align: center;
    }
    .bias-card-red {
        background: rgba(127, 29, 29, 0.25);
        border: 1px solid rgba(248, 113, 113, 0.35);
        border-radius: 16px;
        padding: 18px;
        text-align: center;
    }
    .bias-card-neutral {
        background: rgba(113, 63, 18, 0.22);
        border: 1px solid rgba(251, 191, 36, 0.35);
        border-radius: 16px;
        padding: 18px;
        text-align: center;
    }
    .big-number-green { color: #5ee69a; font-size: 3rem; font-weight: 800; margin: 0; }
    .big-number-red { color: #ff6b6b; font-size: 3rem; font-weight: 800; margin: 0; }
    .bias-title {
        color: #e5e7eb;
        font-size: 1rem;
        font-weight: 700;
        letter-spacing: 0.15rem;
        text-transform: uppercase;
    }
    .driver-pill {
        display: inline-block;
        background: #151b24;
        border: 1px solid #2a3340;
        border-radius: 999px;
        padding: 7px 11px;
        margin: 4px 4px 4px 0;
        font-size: 0.85rem;
        color: #d1d5db;
    }
    .summary-box {
        background: #0f1621;
        border: 1px solid #263244;
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 10px;
    }
    a { color: #9ccaff !important; }
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
/* ------------------------------------------------------------
   V10.1 UI POLISH
------------------------------------------------------------ */

/* App base */
.stApp {
    background: #070a10 !important;
}

/* Sidebar container */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080d16 0%, #05080d 100%) !important;
    border-right: 1px solid #1e293b !important;
}

/* Sidebar spacing */
[data-testid="stSidebar"] > div {
    padding-top: 1.1rem !important;
    padding-left: 0.9rem !important;
    padding-right: 0.9rem !important;
}

/* Sidebar text */
[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
    opacity: 1 !important;
}

/* Sidebar title */
[data-testid="stSidebar"] h1 {
    color: #ffffff !important;
    font-size: 1.32rem !important;
    font-weight: 850 !important;
    letter-spacing: -0.01rem !important;
}

/* Section titles */
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
    font-size: 0.98rem !important;
    font-weight: 850 !important;
    margin-top: 0.9rem !important;
    margin-bottom: 0.45rem !important;
}

/* Sidebar labels */
[data-testid="stSidebar"] label {
    color: #f8fafc !important;
    font-size: 0.80rem !important;
    font-weight: 750 !important;
}

/* Captions */
[data-testid="stSidebar"] p {
    color: #aab6c7 !important;
    font-size: 0.80rem !important;
    line-height: 1.35rem !important;
}

/* Dividers */
[data-testid="stSidebar"] hr {
    border-color: #1e293b !important;
    margin-top: 1rem !important;
    margin-bottom: 1rem !important;
}

/* Expander container */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: #0b1220 !important;
    border: 1px solid #1f2a3b !important;
    border-radius: 12px !important;
    margin-bottom: 0.65rem !important;
    overflow: hidden !important;
}

/* Expander header */
[data-testid="stSidebar"] [data-testid="stExpander"] details summary {
    background: #101827 !important;
    border-radius: 10px !important;
    min-height: 2.4rem !important;
}

/* Text areas and text inputs */
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] input {
    background: #0b111c !important;
    color: #ffffff !important;
    border: 1px solid #2b3648 !important;
    border-radius: 9px !important;
    box-shadow: none !important;
}

/* Text area focus */
[data-testid="stSidebar"] textarea:focus,
[data-testid="stSidebar"] input:focus {
    border: 1px solid #fbbf24 !important;
    box-shadow: 0 0 0 1px rgba(251,191,36,0.35) !important;
}

/* Select boxes */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #0b111c !important;
    color: #ffffff !important;
    border: 1px solid #2b3648 !important;
    border-radius: 9px !important;
    min-height: 2.35rem !important;
}

/* Select text */
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] div {
    color: #ffffff !important;
}

/* Buttons */
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(180deg, #fbbf24 0%, #f59e0b 100%) !important;
    color: #111827 !important;
    border: 1px solid #d99706 !important;
    border-radius: 10px !important;
    font-weight: 850 !important;
    padding: 0.55rem 0.75rem !important;
    box-shadow: 0 0 0 1px rgba(251,191,36,0.15), 0 8px 18px rgba(0,0,0,0.22) !important;
}

/* Secondary button style */
[data-testid="stSidebar"] .stButton > button:hover {
    background: #f59e0b !important;
    color: #111827 !important;
    border-color: #fbbf24 !important;
}

/* Toggle */
[data-testid="stSidebar"] [data-testid="stToggle"] {
    margin-top: 0.25rem !important;
    margin-bottom: 0.7rem !important;
}

/* Slider value and labels */
[data-testid="stSidebar"] [data-testid="stSlider"] {
    padding-top: 0.2rem !important;
    padding-bottom: 0.45rem !important;
}

/* Sidebar widget spacing */
[data-testid="stSidebar"] .stTextArea,
[data-testid="stSidebar"] .stSelectbox,
[data-testid="stSidebar"] .stSlider,
[data-testid="stSidebar"] .stButton {
    margin-bottom: 0.7rem !important;
}

/* Main section cards */
.section-card {
    background: linear-gradient(135deg, #0d1420 0%, #080c13 100%) !important;
    border: 1px solid #202a39 !important;
}

/* Dark HTML tables */
.dark-table-wrap {
    width: 100%;
    overflow-x: auto;
    border: 1px solid #232d3b;
    border-radius: 12px;
    background: #080c13;
    margin-top: 0.6rem;
    margin-bottom: 1rem;
}

.dark-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
    color: #e5e7eb;
    min-width: 900px;
}

.dark-table thead th {
    background: #151b26;
    color: #cbd5e1;
    text-align: left;
    padding: 0.72rem 0.75rem;
    font-weight: 800;
    border-bottom: 1px solid #263244;
    white-space: nowrap;
}

.dark-table tbody td {
    padding: 0.68rem 0.75rem;
    border-bottom: 1px solid #1f2937;
    white-space: nowrap;
    color: #f3f4f6;
}

.dark-table tbody tr:nth-child(even) td {
    background: #0b111a;
}

.dark-table tbody tr:hover td {
    background: #111827;
}

.dark-table a {
    color: #93c5fd !important;
    text-decoration: none !important;
}

.dark-table .muted-cell {
    color: #94a3b8 !important;
}

/* Small cards */
.clean-note {
    color: #aab6c7;
    font-size: 0.9rem;
    margin-top: -0.2rem;
    margin-bottom: 0.9rem;
}
</style>
""", unsafe_allow_html=True)



# ------------------------------------------------------------
# GENERIC SCORING HELPERS
# ------------------------------------------------------------

st.markdown("""
<style>
/* ------------------------------------------------------------
   V10.2 BUTTON TEXT VISIBILITY FIX
   Streamlit buttons contain nested p/span elements, so the
   button text needs its own explicit override.
------------------------------------------------------------ */

/* Sidebar buttons - yellow with dark readable text */
[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] .stButton > button:focus,
[data-testid="stSidebar"] .stButton > button:active {
    background: linear-gradient(180deg, #fbbf24 0%, #f59e0b 100%) !important;
    border: 1px solid #d99706 !important;
    border-radius: 10px !important;
    box-shadow: 0 0 0 1px rgba(251,191,36,0.18), 0 8px 18px rgba(0,0,0,0.22) !important;
}

/* Force readable text inside buttons */
[data-testid="stSidebar"] .stButton > button *,
[data-testid="stSidebar"] .stButton > button p,
[data-testid="stSidebar"] .stButton > button span,
[data-testid="stSidebar"] .stButton > button div {
    color: #111827 !important;
    opacity: 1 !important;
    font-weight: 850 !important;
    text-shadow: none !important;
}

/* Hover state */
[data-testid="stSidebar"] .stButton > button:hover {
    background: #f59e0b !important;
    border-color: #fbbf24 !important;
}

[data-testid="stSidebar"] .stButton > button:hover *,
[data-testid="stSidebar"] .stButton > button:hover p,
[data-testid="stSidebar"] .stButton > button:hover span {
    color: #111827 !important;
}

/* Disabled buttons - still readable */
[data-testid="stSidebar"] .stButton > button:disabled,
[data-testid="stSidebar"] .stButton > button:disabled * {
    background: #374151 !important;
    color: #cbd5e1 !important;
    border-color: #4b5563 !important;
    opacity: 0.95 !important;
}

/* Download buttons in main content */
.stDownloadButton > button,
.stDownloadButton > button:focus,
.stDownloadButton > button:active {
    background: #111827 !important;
    border: 1px solid #374151 !important;
    border-radius: 10px !important;
}

.stDownloadButton > button *,
.stDownloadButton > button p,
.stDownloadButton > button span {
    color: #f8fafc !important;
    opacity: 1 !important;
    font-weight: 750 !important;
}

/* Main content buttons, if any */
[data-testid="stAppViewContainer"] .stButton > button *,
[data-testid="stAppViewContainer"] .stButton > button p,
[data-testid="stAppViewContainer"] .stButton > button span {
    opacity: 1 !important;
}
</style>
""", unsafe_allow_html=True)


def score_direction(label: str, weight: float):
    label_lower = str(label).lower()

    if "supports gold" in label_lower:
        return weight, 0
    if "opposes gold" in label_lower:
        return 0, weight

    return weight / 2, weight / 2


def get_bias(support_pct, oppose_pct):
    edge = abs(support_pct - oppose_pct)

    if support_pct >= 65:
        bias = "BULLISH GOLD"
        card = "bias-card-green"
        action = "Only look for long setups after your TradingView AMD / MSS confirmation."
    elif oppose_pct >= 65:
        bias = "BEARISH GOLD"
        card = "bias-card-red"
        action = "Only look for short setups after your TradingView AMD / MSS confirmation."
    else:
        bias = "MIXED / NO CLEAN EDGE"
        card = "bias-card-neutral"
        action = "Avoid forcing trades. Wait for cleaner macro alignment or reduce risk."

    if edge >= 40:
        confidence = "Decisive"
    elif edge >= 20:
        confidence = "Strong"
    elif edge >= 10:
        confidence = "Moderate"
    else:
        confidence = "Weak"

    return bias, confidence, action, edge, card


def explanation_for_driver(driver_name, state, support_points, oppose_points):
    if support_points > oppose_points:
        impact = "Supporting gold"
    elif oppose_points > support_points:
        impact = "Opposing gold"
    else:
        impact = "Neutral / mixed"

    explanations = {
        "DXY / USD": {
            "support": "A weaker dollar usually supports gold because XAU/USD becomes less expensive for non-dollar buyers.",
            "oppose": "A stronger dollar usually pressures gold because XAU/USD becomes more expensive and dollar demand is stronger.",
            "neutral": "The dollar signal is not strong enough to add directional conviction."
        },
        "US10Y": {
            "support": "Falling nominal yields can support gold because the opportunity cost of holding non-yielding gold falls.",
            "oppose": "Rising nominal yields can pressure gold because the opportunity cost of holding non-yielding gold rises.",
            "neutral": "The nominal yield signal is not strong enough to add directional conviction."
        },
        "Real yields": {
            "support": "Falling real yields are usually supportive for gold because inflation-adjusted bond returns are less attractive.",
            "oppose": "Rising real yields are one of the cleaner bearish macro drivers for gold.",
            "neutral": "The real-yield signal is not strong enough to add directional conviction."
        },
        "Fed tone": {
            "support": "A dovish Fed tone can support gold by increasing rate-cut expectations or lowering yield pressure.",
            "oppose": "A hawkish Fed tone can pressure gold by supporting yields, real yields and the dollar.",
            "neutral": "Fed tone is not adding clear directional conviction."
        },
        "Geopolitics": {
            "support": "Escalation can support gold through safe-haven demand.",
            "oppose": "De-escalation can reduce safe-haven demand and pressure gold.",
            "neutral": "Geopolitics is not adding clear directional conviction."
        },
        "Risk sentiment": {
            "support": "Risk-off conditions can support gold if investors seek safety.",
            "oppose": "Risk-on conditions can reduce safe-haven demand for gold.",
            "neutral": "Risk sentiment is not adding clear directional conviction."
        },
        "Gold news": {
            "support": "Filtered gold headlines contain more supportive terms than opposing terms.",
            "oppose": "Filtered gold headlines contain more opposing terms than supportive terms.",
            "neutral": "Filtered gold headlines are mixed or unclear."
        }
    }

    e = explanations.get(driver_name, {"support": "This driver supports gold.", "oppose": "This driver opposes gold.", "neutral": "This driver is mixed."})

    if impact == "Supporting gold":
        return impact, e["support"]
    if impact == "Opposing gold":
        return impact, e["oppose"]
    return impact, e["neutral"]


# ------------------------------------------------------------
# GOLD NEWS CLASSIFICATION
# ------------------------------------------------------------
SUPPORT_KEYWORDS = [
    "safe haven", "safe-haven", "geopolitical tension", "war escalates",
    "escalation", "sanctions", "missile", "attack", "conflict",
    "recession", "bank crisis", "financial stress", "risk off", "risk-off",
    "dollar weakens", "weaker dollar", "dxy falls", "yields fall",
    "lower yields", "real yields fall", "rate cut", "fed cut", "dovish",
    "inflation cools", "soft inflation", "jobless claims rise",
    "weak jobs", "unemployment rises", "central bank buying",
    "gold rises", "gold gains", "gold climbs", "bullion rises", "bullion gains"
]

OPPOSE_KEYWORDS = [
    "strong dollar", "dollar rises", "dollar strengthens", "dxy rises",
    "yields rise", "higher yields", "real yields rise", "hawkish",
    "higher for longer", "inflation rises", "hot inflation",
    "strong jobs", "payrolls beat", "risk appetite", "risk on", "risk-on",
    "stocks rally", "ceasefire", "de-escalation", "peace deal",
    "fed hikes", "rate hike", "gold falls", "gold slips", "gold drops",
    "bullion falls", "bullion slips"
]

GOLD_RELEVANCE_TERMS = [
    "gold price", "xauusd", "xau/usd", "spot gold", "gold futures",
    "bullion", "precious metal", "precious metals", "comex gold",
    "gold market", "gold forecast", "gold outlook", "gold near",
    "gold falls", "gold rises", "gold slips", "gold gains", "gold climbs",
    "gold drops", "gold correction", "gold rally", "gold selloff",
    "gold sell-off", "gold demand", "gold etf", "gold holdings",
    "central bank gold"
]

GOLD_NOISE_TERMS = [
    "gold medal", "gold medals", "gold coins", "gold coin", "shipwreck",
    "football", "soccer", "nike", "mercurial", "boccia", "astronomical",
    "birthday honours", "knighted", "award", "awards", "olympic", "olympics",
    "jewellery", "jewelry", "wedding", "dress", "watch", "watching",
    "golden retriever", "gold coast", "gold rush tv"
]


def is_relevant_gold_article(title: str, summary: str = ""):
    text = f"{title or ''} {summary or ''}".lower()

    if any(term in text for term in GOLD_NOISE_TERMS):
        return False

    return any(term in text for term in GOLD_RELEVANCE_TERMS)


def classify_gold_article(title: str, description: str = ""):
    text = f"{title or ''} {description or ''}".lower()

    support_hits = [kw for kw in SUPPORT_KEYWORDS if kw in text]
    oppose_hits = [kw for kw in OPPOSE_KEYWORDS if kw in text]

    if len(support_hits) > len(oppose_hits):
        return "Supporting gold", support_hits[:3]
    if len(oppose_hits) > len(support_hits):
        return "Opposing gold", oppose_hits[:3]

    return "Neutral / unclear", []


def calculate_news_score(df: pd.DataFrame, weight: float):
    if df.empty:
        return weight / 2, weight / 2

    support_count = int((df["Classification"] == "Supporting gold").sum())
    oppose_count = int((df["Classification"] == "Opposing gold").sum())

    total_directional = support_count + oppose_count

    if total_directional == 0:
        return weight / 2, weight / 2

    support_points = weight * (support_count / total_directional)
    oppose_points = weight * (oppose_count / total_directional)

    return support_points, oppose_points


# ------------------------------------------------------------
# FED TONE INTELLIGENCE
# ------------------------------------------------------------
HAWKISH_KEYWORDS = [
    "hawkish", "higher for longer", "restrictive", "restrictive policy",
    "keep policy restrictive", "inflation risks", "upside inflation",
    "sticky inflation", "elevated inflation", "inflation remains",
    "persistent inflation", "price pressures", "above target",
    "no rush to cut", "no hurry to cut", "not ready to cut",
    "too early to cut", "wait before cutting", "keep rates high",
    "hold rates", "rates steady", "keeps rates steady",
    "rate hike", "rate hikes", "rate rise", "rate rises", "rates rise",
    "rate increase", "rate increases", "further tightening",
    "tighter policy", "tilt towards rate rise", "tilt toward rate rise",
    "strong labor market", "strong labour market", "resilient economy",
    "solid economy", "hot inflation"
]

DOVISH_KEYWORDS = [
    "dovish", "rate cut", "rate cuts", "cut rates", "lower rates",
    "rates lower", "easing", "policy easing", "easier policy",
    "cooling inflation", "inflation cools", "inflation easing",
    "soft inflation", "weak jobs", "labor market weakens",
    "labour market weakens", "unemployment rises", "slowdown",
    "growth slows", "recession risk", "downside risks",
    "less restrictive", "cuts likely", "cuts expected",
    "signals cuts", "opens door to cuts"
]


FED_RELEVANCE_TERMS = [
    "federal reserve", "fomc", "powell", "fed officials", "fed official",
    "fed governor", "fed chair", "interest rates", "rate cut", "rate cuts",
    "rate hike", "rate hikes", "rate rise", "rates steady", "monetary policy",
    "inflation", "jobs", "labor market", "labour market", "treasury yields",
    "higher for longer", "restrictive"
]

FED_NOISE_TERMS = [
    "dies", "died", "death", "obituary", "longtime head", "former chairman",
    "alan greenspan dies", "aged", "tribute", "museum", "athletic",
    "promoted", "football", "college", "gold", "scholarship"
]


def is_relevant_fed_article(title: str, summary: str = ""):
    text = f"{title or ''} {summary or ''}".lower()

    if any(term in text for term in FED_NOISE_TERMS):
        return False

    return any(term in text for term in FED_RELEVANCE_TERMS)


def classify_fed_article(title: str, summary: str = ""):
    text = f"{title or ''} {summary or ''}".lower()

    hawkish_hits = [kw for kw in HAWKISH_KEYWORDS if kw in text]
    dovish_hits = [kw for kw in DOVISH_KEYWORDS if kw in text]

    if len(hawkish_hits) > len(dovish_hits):
        return "Hawkish", hawkish_hits[:4]
    if len(dovish_hits) > len(hawkish_hits):
        return "Dovish", dovish_hits[:4]

    return "Neutral / unclear", []


def build_fed_df(entries, max_records):
    rows = []

    for entry in entries[:max_records]:
        title = entry.get("title", "")
        summary = entry.get("summary", "")
        source = ""

        try:
            source = entry.get("source", {}).get("title", "")
        except Exception:
            source = ""

        if not is_relevant_fed_article(title, summary):
            continue

        tone, matched = classify_fed_article(title, summary)

        rows.append({
            "Time": entry.get("published", ""),
            "Source": source,
            "Title": title,
            "Fed tone": tone,
            "Matched terms": ", ".join(matched),
            "URL": entry.get("link", "")
        })

    return pd.DataFrame(rows)


def fed_tone_from_df(df: pd.DataFrame):
    if df.empty:
        return {
            "state": "Flat / mixed",
            "tone": "Neutral / unclear",
            "confidence": 0,
            "hawkish": 0,
            "dovish": 0,
            "neutral": 0,
            "reason": "No Fed tone articles loaded."
        }

    hawkish = int((df["Fed tone"] == "Hawkish").sum())
    dovish = int((df["Fed tone"] == "Dovish").sum())
    neutral = int((df["Fed tone"] == "Neutral / unclear").sum())
    directional = hawkish + dovish

    if directional == 0:
        return {
            "state": "Flat / mixed",
            "tone": "Neutral / unclear",
            "confidence": 0,
            "hawkish": hawkish,
            "dovish": dovish,
            "neutral": neutral,
            "reason": "Fed headlines are present but not directionally clear."
        }

    edge = abs(hawkish - dovish)
    confidence = round((edge / max(directional, 1)) * 100, 0)

    if hawkish > dovish:
        return {
            "state": "Hawkish Fed — opposes gold",
            "tone": "Hawkish",
            "confidence": confidence,
            "hawkish": hawkish,
            "dovish": dovish,
            "neutral": neutral,
            "reason": "More Fed-related headlines contain hawkish language than dovish language."
        }

    if dovish > hawkish:
        return {
            "state": "Dovish Fed — supports gold",
            "tone": "Dovish",
            "confidence": confidence,
            "hawkish": hawkish,
            "dovish": dovish,
            "neutral": neutral,
            "reason": "More Fed-related headlines contain dovish language than hawkish language."
        }

    return {
        "state": "Flat / mixed",
        "tone": "Neutral / unclear",
        "confidence": 0,
        "hawkish": hawkish,
        "dovish": dovish,
        "neutral": neutral,
        "reason": "Fed headlines are evenly split."
    }


# ------------------------------------------------------------
# FEED FETCHERS
# ------------------------------------------------------------
def fetch_google_rss(query: str):
    encoded_query = quote_plus(query)
    url = (
        "https://news.google.com/rss/search"
        f"?q={encoded_query}"
        "&hl=en-GB"
        "&gl=GB"
        "&ceid=GB:en"
    )
    headers = {"User-Agent": "Mozilla/5.0 GoldIntelligenceMVP/1.0"}

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    return feedparser.parse(response.content)


def fetch_google_gold_news(query: str, max_records: int = 10):
    try:
        feed = fetch_google_rss(query)

        if getattr(feed, "bozo", False) and not feed.entries:
            return pd.DataFrame(), "Google News returned a feed parse warning and no articles."

        rows = []
        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")

            if not is_relevant_gold_article(title, summary):
                continue

            source = ""
            try:
                source = entry.get("source", {}).get("title", "")
            except Exception:
                source = ""

            classification, matched = classify_gold_article(title, summary)

            rows.append({
                "Time": entry.get("published", ""),
                "Source": source,
                "Title": title,
                "Classification": classification,
                "Matched terms": ", ".join(matched),
                "URL": entry.get("link", "")
            })

            if len(rows) >= max_records:
                break

        return pd.DataFrame(rows), None

    except Exception as e:
        return pd.DataFrame(), f"Could not pull Google News RSS right now: {e}"


def fetch_google_fed_tone(query: str, max_records: int = 10):
    try:
        feed = fetch_google_rss(query)

        if getattr(feed, "bozo", False) and not feed.entries:
            return pd.DataFrame(), "Google News returned a feed parse warning and no Fed articles."

        df = build_fed_df(feed.entries, max_records)
        return df, None

    except Exception as e:
        return pd.DataFrame(), f"Could not pull Fed tone news right now: {e}"


# ------------------------------------------------------------
# MARKET DATA FETCHERS
# ------------------------------------------------------------
def fetch_yahoo_last_close(ticker: str, name: str):
    if yf is None:
        return {
            "Name": name, "Ticker": ticker, "Latest": None, "Previous": None,
            "Change": None, "Change %": None, "Date": "",
            "Error": "yfinance is not installed or could not import."
        }

    try:
        data = yf.Ticker(ticker).history(period="10d", interval="1d", auto_adjust=False)

        if data is None or data.empty or "Close" not in data.columns:
            return {
                "Name": name, "Ticker": ticker, "Latest": None, "Previous": None,
                "Change": None, "Change %": None, "Date": "",
                "Error": "No usable data returned."
            }

        close = data["Close"].dropna()

        if len(close) < 2:
            return {
                "Name": name, "Ticker": ticker,
                "Latest": float(close.iloc[-1]) if len(close) else None,
                "Previous": None, "Change": None, "Change %": None,
                "Date": str(close.index[-1].date()) if len(close) else "",
                "Error": "Not enough data to calculate change."
            }

        latest = float(close.iloc[-1])
        previous = float(close.iloc[-2])
        change = latest - previous
        change_pct = (change / previous) * 100 if previous else None

        return {
            "Name": name, "Ticker": ticker, "Latest": latest, "Previous": previous,
            "Change": change, "Change %": change_pct,
            "Date": str(close.index[-1].date()), "Error": None
        }

    except Exception as e:
        return {
            "Name": name, "Ticker": ticker, "Latest": None, "Previous": None,
            "Change": None, "Change %": None, "Date": "", "Error": str(e)
        }


def fetch_fred_series(series_id: str, name: str):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"

    try:
        df = pd.read_csv(url)

        if df.empty or series_id not in df.columns:
            return {
                "Name": name, "Series": series_id, "Latest": None, "Previous": None,
                "Change": None, "Change bps": None, "Date": "",
                "Error": "No usable FRED data returned."
            }

        df[series_id] = pd.to_numeric(df[series_id], errors="coerce")
        df = df.dropna(subset=[series_id])

        if len(df) < 2:
            return {
                "Name": name, "Series": series_id,
                "Latest": float(df[series_id].iloc[-1]) if len(df) else None,
                "Previous": None, "Change": None, "Change bps": None,
                "Date": str(df["observation_date"].iloc[-1]) if len(df) else "",
                "Error": "Not enough data to calculate change."
            }

        latest = float(df[series_id].iloc[-1])
        previous = float(df[series_id].iloc[-2])
        change = latest - previous

        return {
            "Name": name, "Series": series_id, "Latest": latest, "Previous": previous,
            "Change": change, "Change bps": change * 100,
            "Date": str(df["observation_date"].iloc[-1]), "Error": None
        }

    except Exception as e:
        return {
            "Name": name, "Series": series_id, "Latest": None, "Previous": None,
            "Change": None, "Change bps": None, "Date": "", "Error": str(e)
        }


def classify_dxy(row):
    cp = row.get("Change %")
    if cp is None:
        return "Flat / mixed"
    if cp >= 0.25:
        return "Stronger USD — opposes gold"
    if cp <= -0.25:
        return "Weaker USD — supports gold"
    return "Flat / mixed"


def classify_yield(row, label):
    bps = row.get("Change bps")
    if bps is None:
        return "Flat / mixed"
    if bps >= 5:
        return f"Rising {label} — opposes gold"
    if bps <= -5:
        return f"Falling {label} — supports gold"
    return "Flat / mixed"


def classify_real_yield(row):
    bps = row.get("Change bps")
    if bps is None:
        return "Flat / mixed"
    if bps >= 3:
        return "Rising real yields — opposes gold"
    if bps <= -3:
        return "Falling real yields — supports gold"
    return "Flat / mixed"


def classify_risk(spx_row, vix_row):
    spx_cp = spx_row.get("Change %")
    vix_cp = vix_row.get("Change %")

    if spx_cp is None or vix_cp is None:
        return "Flat / mixed"

    if spx_cp >= 0.4 and vix_cp <= -2.0:
        return "Risk-on — opposes gold"
    if spx_cp <= -0.4 and vix_cp >= 2.0:
        return "Risk-off — supports gold"

    return "Flat / mixed"


def fetch_market_data():
    dxy = fetch_yahoo_last_close("DX-Y.NYB", "US Dollar Index")
    spot_xauusd = fetch_yahoo_last_close("XAUUSD=X", "Spot XAUUSD")
    gold = fetch_yahoo_last_close("GC=F", "Gold Futures")
    spx = fetch_yahoo_last_close("^GSPC", "S&P 500")
    vix = fetch_yahoo_last_close("^VIX", "VIX")
    nominal_10y = fetch_fred_series("DGS10", "US 10Y Yield")
    real_10y = fetch_fred_series("DFII10", "US 10Y Real Yield")

    rows = [spot_xauusd, gold, dxy, spx, vix, nominal_10y, real_10y]

    drivers = {
        "dxy": classify_dxy(dxy),
        "nominal_yields": classify_yield(nominal_10y, "yields"),
        "real_yields": classify_real_yield(real_10y),
        "risk_mood": classify_risk(spx, vix),
    }

    return rows, drivers




# ------------------------------------------------------------
# SCORE LOGGER HELPERS
# ------------------------------------------------------------
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
SCORE_LOG_PATH = DATA_DIR / "score_history.csv"


def find_market_value(market_rows, name, key):
    for row in market_rows:
        if row.get("Name") == name:
            return row.get(key)
    return None


def build_snapshot(
    support_pct,
    oppose_pct,
    bias,
    confidence,
    edge,
    driver_df,
    market_rows,
    fed_result,
    geo,
    article_df,
    chart_screenshot_url=None,
    chart_screenshot_path=None,
    chart_screenshot_filename=None,
    chart_timeframe="",
    chart_setup_tag="",
):
    now = datetime.now(timezone.utc)

    spot_xauusd_latest = find_market_value(market_rows, "Spot XAUUSD", "Latest")
    spot_xauusd_change_pct = find_market_value(market_rows, "Spot XAUUSD", "Change %")
    gold_futures_latest = find_market_value(market_rows, "Gold Futures", "Latest")
    gold_futures_change_pct = find_market_value(market_rows, "Gold Futures", "Change %")
    dxy_latest = find_market_value(market_rows, "US Dollar Index", "Latest")
    dxy_change_pct = find_market_value(market_rows, "US Dollar Index", "Change %")
    us10y_latest = find_market_value(market_rows, "US 10Y Yield", "Latest")
    us10y_bps = find_market_value(market_rows, "US 10Y Yield", "Change bps")
    real_yield_latest = find_market_value(market_rows, "US 10Y Real Yield", "Latest")
    real_yield_bps = find_market_value(market_rows, "US 10Y Real Yield", "Change bps")
    spx_change_pct = find_market_value(market_rows, "S&P 500", "Change %")
    vix_change_pct = find_market_value(market_rows, "VIX", "Change %")

    def state_for(driver):
        match = driver_df.loc[driver_df["Driver"] == driver, "State"]
        return match.iloc[0] if not match.empty else ""

    snapshot = {
        "timestamp_utc": now.strftime("%Y-%m-%d %H:%M:%S"),
        "supporting_gold_pct": support_pct,
        "opposing_gold_pct": oppose_pct,
        "bias": bias,
        "confidence": confidence,
        "edge_pts": round(edge, 1),
        "spot_xauusd_latest": None if spot_xauusd_latest is None else round(float(spot_xauusd_latest), 4),
        "spot_xauusd_change_pct": None if spot_xauusd_change_pct is None else round(float(spot_xauusd_change_pct), 4),
        "gold_futures_latest": None if gold_futures_latest is None else round(float(gold_futures_latest), 4),
        "gold_futures_change_pct": None if gold_futures_change_pct is None else round(float(gold_futures_change_pct), 4),
        "dxy_latest": None if dxy_latest is None else round(float(dxy_latest), 4),
        "dxy_change_pct": None if dxy_change_pct is None else round(float(dxy_change_pct), 4),
        "us10y_latest": None if us10y_latest is None else round(float(us10y_latest), 4),
        "us10y_change_bps": None if us10y_bps is None else round(float(us10y_bps), 2),
        "real_yield_latest": None if real_yield_latest is None else round(float(real_yield_latest), 4),
        "real_yield_change_bps": None if real_yield_bps is None else round(float(real_yield_bps), 2),
        "spx_change_pct": None if spx_change_pct is None else round(float(spx_change_pct), 4),
        "vix_change_pct": None if vix_change_pct is None else round(float(vix_change_pct), 4),
        "dxy_state": state_for("DXY / USD"),
        "us10y_state": state_for("US10Y"),
        "real_yields_state": state_for("Real yields"),
        "fed_tone_state": state_for("Fed tone"),
        "fed_tone_label": fed_result.get("tone", "Neutral / unclear"),
        "fed_tone_confidence": fed_result.get("confidence", 0),
        "geopolitics_state": geo,
        "risk_sentiment_state": state_for("Risk sentiment"),
        "gold_news_state": state_for("Gold news"),
        "gold_news_articles": 0 if article_df.empty else len(article_df),
        "notes": "",
        "chart_screenshot_url": chart_screenshot_url or "",
        "chart_screenshot_path": chart_screenshot_path or "",
        "chart_screenshot_filename": chart_screenshot_filename or "",
        "chart_timeframe": chart_timeframe or "",
        "chart_setup_tag": chart_setup_tag or "",
        "price_1h_later": "",
        "price_4h_later": "",
        "bias_result_1h": "",
        "bias_result_4h": "",
    }

    return snapshot


def load_score_history():
    if SCORE_LOG_PATH.exists():
        try:
            return pd.read_csv(SCORE_LOG_PATH)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


def save_score_snapshot(snapshot):
    df_new = pd.DataFrame([snapshot])
    df_old = load_score_history()

    if df_old.empty:
        df_out = df_new
    else:
        df_out = pd.concat([df_old, df_new], ignore_index=True)

    df_out.to_csv(SCORE_LOG_PATH, index=False)
    return df_out


def clear_score_history():
    if SCORE_LOG_PATH.exists():
        SCORE_LOG_PATH.unlink()





# ------------------------------------------------------------
# DARK TABLE RENDERER
# ------------------------------------------------------------
def render_dark_table(df, max_rows=None, empty_message="No rows to display."):
    if df is None or df.empty:
        st.info(empty_message)
        return

    view = df.copy()

    if max_rows is not None:
        view = view.head(max_rows)

    def fmt_value(value):
        if pd.isna(value):
            return "<span class='muted-cell'>None</span>"

        text = str(value)

        if text.startswith("http://") or text.startswith("https://"):
            safe_url = html.escape(text, quote=True)
            return f"<a href='{safe_url}' target='_blank'>Open link</a>"

        if len(text) > 90:
            text = text[:87] + "..."

        return html.escape(text)

    headers = "".join(f"<th>{html.escape(str(col))}</th>" for col in view.columns)

    body_rows = []
    for _, row in view.iterrows():
        cells = "".join(f"<td>{fmt_value(row[col])}</td>" for col in view.columns)
        body_rows.append(f"<tr>{cells}</tr>")

    table_html = f"""
    <div class="dark-table-wrap">
        <table class="dark-table">
            <thead><tr>{headers}</tr></thead>
            <tbody>{''.join(body_rows)}</tbody>
        </table>
    </div>
    """

    st.markdown(table_html, unsafe_allow_html=True)


# ------------------------------------------------------------
# OPTIONAL SUPABASE LOGGER
# ------------------------------------------------------------
SUPABASE_TABLE_NAME = "score_history"


def supabase_config_available():
    try:
        return bool(st.secrets.get("supabase_url")) and bool(st.secrets.get("supabase_key"))
    except Exception:
        return False


def clean_snapshot_for_supabase(snapshot):
    """
    Keep the Supabase payload clean. Blank / None values are omitted so optional
    columns do not break older tables.
    """
    cleaned = {}
    for key, value in snapshot.items():
        try:
            if value is None:
                continue
            if isinstance(value, str) and value.strip() == "":
                continue
            if pd.isna(value):
                continue
        except Exception:
            pass
        cleaned[key] = value
    return cleaned


def append_snapshot_to_supabase(snapshot):
    if not supabase_config_available():
        return False, "Supabase is not configured. Add Streamlit secrets first."

    try:
        supabase_url = str(st.secrets["supabase_url"]).rstrip("/")
        supabase_key = str(st.secrets["supabase_key"])
        table_name = str(st.secrets.get("supabase_table_name", SUPABASE_TABLE_NAME))

        endpoint = f"{supabase_url}/rest/v1/{table_name}"

        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }

        payload = clean_snapshot_for_supabase(snapshot)

        response = requests.post(endpoint, headers=headers, json=payload, timeout=20)

        if response.status_code not in (200, 201, 204):
            return False, f"Supabase save failed: {response.status_code} {response.text[:300]}"

        return True, "Snapshot also saved to Supabase."

    except Exception as e:
        return False, f"Supabase save failed: {e}"



def upload_screenshot_to_supabase(uploaded_file, timestamp_utc):
    """
    Upload a TradingView screenshot to Supabase Storage and return a public URL.
    Requires a public bucket, default name: chart-screenshots.
    """
    if uploaded_file is None:
        return None, None, None

    if not supabase_config_available():
        return None, None, "Supabase is not configured. Screenshot was not uploaded."

    try:
        supabase_url = str(st.secrets["supabase_url"]).rstrip("/")
        supabase_key = str(st.secrets["supabase_key"])
        bucket_name = str(st.secrets.get("supabase_storage_bucket", "chart-screenshots"))

        original_name = uploaded_file.name or "tradingview_screenshot.png"
        safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", original_name)
        extension = safe_name.split(".")[-1].lower() if "." in safe_name else "png"

        ts_path = re.sub(r"[^0-9A-Za-z_-]", "_", timestamp_utc)
        object_path = f"{timestamp_utc[:10]}/{ts_path}_{uuid.uuid4().hex[:8]}.{extension}"

        endpoint = f"{supabase_url}/storage/v1/object/{bucket_name}/{object_path}"

        file_bytes = uploaded_file.getvalue()
        content_type = getattr(uploaded_file, "type", None) or "application/octet-stream"

        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": content_type,
            "x-upsert": "false",
        }

        response = requests.post(endpoint, headers=headers, data=file_bytes, timeout=30)

        if response.status_code not in (200, 201):
            return None, object_path, f"Screenshot upload failed: {response.status_code} {response.text[:300]}"

        public_url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/{object_path}"
        return public_url, object_path, "Screenshot uploaded to Supabase Storage."

    except Exception as e:
        return None, None, f"Screenshot upload failed: {e}"


def fetch_supabase_history(limit=100):
    if not supabase_config_available():
        return pd.DataFrame(), "Supabase is not configured."

    try:
        supabase_url = str(st.secrets["supabase_url"]).rstrip("/")
        supabase_key = str(st.secrets["supabase_key"])
        table_name = str(st.secrets.get("supabase_table_name", SUPABASE_TABLE_NAME))

        endpoint = f"{supabase_url}/rest/v1/{table_name}"

        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
        }

        params = {
            "select": "*",
            "order": "timestamp_utc.desc",
            "limit": str(limit),
        }

        response = requests.get(endpoint, headers=headers, params=params, timeout=20)

        if response.status_code != 200:
            return pd.DataFrame(), f"Supabase history load failed: {response.status_code} {response.text[:300]}"

        data = response.json()
        return pd.DataFrame(data), None

    except Exception as e:
        return pd.DataFrame(), f"Supabase history load failed: {e}"


# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------
defaults = {
    "article_df": pd.DataFrame(),
    "news_error": None,
    "last_news_fetch": None,
    "market_rows": [],
    "market_drivers": {},
    "market_error": None,
    "last_market_fetch": None,
    "fed_df": pd.DataFrame(),
    "fed_error": None,
    "last_fed_fetch": None,
    "fed_result": {
        "state": "Flat / mixed",
        "tone": "Neutral / unclear",
        "confidence": 0,
        "hawkish": 0,
        "dovish": 0,
        "neutral": 0,
        "reason": "No Fed tone articles loaded."
    },
    "last_snapshot_saved": None,
    "last_supabase_status": None,
    "supabase_history_df": pd.DataFrame(),
    "last_supabase_load_status": None,
    "last_screenshot_status": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
st.sidebar.title("Gold Intelligence MVP")
st.sidebar.caption("V10.1 · cleaner sidebar · dark tables · Supabase logging")

st.sidebar.markdown("---")
st.sidebar.subheader("Quick Actions")

auto_macro = st.sidebar.toggle("Auto macro drivers", value=True)
fetch_market = st.sidebar.button("Fetch market data now", type="primary")

if fetch_market:
    with st.spinner("Fetching market data..."):
        try:
            rows, drivers = fetch_market_data()
            st.session_state.market_rows = rows
            st.session_state.market_drivers = drivers
            st.session_state.market_error = None
            st.session_state.last_market_fetch = datetime.now(timezone.utc)
        except Exception as e:
            st.session_state.market_error = str(e)

with st.sidebar.expander("Fed Tone Intelligence", expanded=False):
    auto_fed = st.toggle("Use automatic Fed tone", value=True)

    fed_query = st.text_area(
        "Fed tone search query",
        value='"Federal Reserve" OR FOMC OR Powell OR "Fed officials" OR "interest rates" OR "rate cuts" OR "rate hike" OR "higher for longer"',
        height=80
    )

    fed_max_records = st.slider(
        "Fed articles",
        min_value=5,
        max_value=30,
        value=10,
        step=5
    )

    fetch_fed = st.button("Fetch Fed tone now")

if fetch_fed:
    with st.spinner("Fetching Fed tone news..."):
        df, err = fetch_google_fed_tone(fed_query, fed_max_records)
        st.session_state.fed_df = df
        st.session_state.fed_error = err
        st.session_state.fed_result = fed_tone_from_df(df)
        st.session_state.last_fed_fetch = datetime.now(timezone.utc)

with st.sidebar.expander("Gold News Feed", expanded=False):
    gold_query = st.text_area(
        "Gold news search query",
        value='"gold price" OR XAUUSD OR "spot gold" OR "gold futures" OR bullion OR "gold forecast"',
        height=90
    )

    gold_max_records = st.slider(
        "Gold articles",
        min_value=5,
        max_value=30,
        value=10,
        step=5
    )

    fetch_news = st.button("Fetch gold news now")
    clear_news = st.button("Clear gold news cache")

if fetch_news:
    with st.spinner("Fetching filtered gold news..."):
        df, err = fetch_google_gold_news(gold_query, max_records=gold_max_records)
        st.session_state.article_df = df
        st.session_state.news_error = err
        st.session_state.last_news_fetch = datetime.now(timezone.utc)

if clear_news:
    st.session_state.article_df = pd.DataFrame()
    st.session_state.news_error = None
    st.session_state.last_news_fetch = None

with st.sidebar.expander("Manual Overrides", expanded=False):
    manual_dxy = st.selectbox("DXY / USD", ["Flat / mixed", "Stronger USD — opposes gold", "Weaker USD — supports gold"], index=0)
    manual_nominal_yields = st.selectbox("US 10Y yield", ["Flat / mixed", "Rising yields — opposes gold", "Falling yields — supports gold"], index=0)
    manual_real_yields = st.selectbox("US real yields", ["Flat / mixed", "Rising real yields — opposes gold", "Falling real yields — supports gold"], index=0)
    manual_fed_tone = st.selectbox("Fed tone", ["Flat / mixed", "Hawkish Fed — opposes gold", "Dovish Fed — supports gold"], index=0)
    manual_geo = st.selectbox("Geopolitical risk", ["Flat / mixed", "De-escalation / ceasefire — opposes gold", "Escalation / safe-haven demand — supports gold"], index=0)
    manual_risk_mood = st.selectbox("Risk sentiment", ["Flat / mixed", "Risk-on — opposes gold", "Risk-off — supports gold"], index=0)

with st.sidebar.expander("Model Weights", expanded=False):
    w_dxy = st.slider("DXY weight", 0, 40, 20)
    w_nominal_yields = st.slider("US10Y weight", 0, 40, 15)
    w_real_yields = st.slider("Real yield weight", 0, 40, 25)
    w_fed = st.slider("Fed tone weight", 0, 30, 15)
    w_geo = st.slider("Geopolitical weight", 0, 30, 15)
    w_risk = st.slider("Risk sentiment weight", 0, 20, 5)
    w_news = st.slider("Gold news weight", 0, 40, 10)

st.sidebar.markdown("---")
st.sidebar.subheader("Score Logger")
st.sidebar.caption("Save snapshots during London / New York review to build evidence over time.")

snapshot_note = st.sidebar.text_area(
    "Snapshot note",
    value="",
    height=80,
    help="Optional: add chart context, e.g. London sweep + bearish MSS."
)

st.sidebar.markdown("**Chart Evidence**")
chart_timeframe = st.sidebar.selectbox(
    "Chart timeframe",
    ["Not set", "1m", "5m", "15m", "30m", "1H", "2H", "4H", "1D"],
    index=0
)

chart_setup_tag = st.sidebar.selectbox(
    "Setup tag",
    [
        "Not set",
        "Asia range",
        "London sweep",
        "New York sweep",
        "Bullish MSS",
        "Bearish MSS",
        "Bullish reclaim",
        "Bearish rejection",
        "No clean setup",
        "Other",
    ],
    index=0
)

uploaded_chart_screenshot = st.sidebar.file_uploader(
    "Upload TradingView screenshot",
    type=["png", "jpg", "jpeg", "webp"],
    help="Upload the chart screenshot that supports this bias snapshot."
)

if uploaded_chart_screenshot is not None:
    st.sidebar.image(uploaded_chart_screenshot, caption="Screenshot ready", use_container_width=True)

save_to_supabase = st.sidebar.toggle(
    "Also save to Supabase",
    value=False,
    help="Requires Streamlit secrets. Local CSV still works without this."
)

save_snapshot_clicked = st.sidebar.button("Save bias snapshot")
clear_history_clicked = st.sidebar.button("Clear local history")
load_supabase_clicked = st.sidebar.button("Load cloud history")

# ------------------------------------------------------------
# ACTIVE DRIVERS
# ------------------------------------------------------------
auto_drivers = st.session_state.market_drivers

if auto_macro and auto_drivers:
    dxy = auto_drivers.get("dxy", manual_dxy)
    nominal_yields = auto_drivers.get("nominal_yields", manual_nominal_yields)
    real_yields = auto_drivers.get("real_yields", manual_real_yields)
    risk_mood = auto_drivers.get("risk_mood", manual_risk_mood)
else:
    dxy = manual_dxy
    nominal_yields = manual_nominal_yields
    real_yields = manual_real_yields
    risk_mood = manual_risk_mood

fed_result = st.session_state.fed_result

if auto_fed and fed_result.get("tone") != "Neutral / unclear":
    fed_tone = fed_result.get("state", manual_fed_tone)
    fed_source = "Auto Fed tone"
else:
    fed_tone = manual_fed_tone
    fed_source = "Manual"

geo = manual_geo

# ------------------------------------------------------------
# MAIN DASHBOARD
# ------------------------------------------------------------
st.markdown("<div class='small-muted'>KILLZONE-STYLE GOLD INTELLIGENCE MVP</div>", unsafe_allow_html=True)
st.title("XAU / USD Macro Bias Dashboard")
st.caption("Bias filter only. Entries still come from TradingView structure.")
st.markdown("<div class='small-muted'>VERSION V10.3 · SCREENSHOT LOGGER · DARK TABLES · SUPABASE LOGGING</div>", unsafe_allow_html=True)

if st.session_state.market_error:
    st.warning(f"Market data issue: {st.session_state.market_error}")
elif st.session_state.last_market_fetch:
    st.success(f"Market data last fetched: {st.session_state.last_market_fetch.strftime('%Y-%m-%d %H:%M:%S UTC')}")
else:
    st.info("Press **Fetch market data now** in the sidebar.")

if st.session_state.fed_error:
    st.warning(st.session_state.fed_error)
elif st.session_state.last_fed_fetch:
    st.success(f"Fed tone last fetched: {st.session_state.last_fed_fetch.strftime('%Y-%m-%d %H:%M:%S UTC')}")

if st.session_state.news_error:
    st.warning(st.session_state.news_error)
elif st.session_state.last_news_fetch:
    st.success(f"Gold news last fetched: {st.session_state.last_news_fetch.strftime('%Y-%m-%d %H:%M:%S UTC')}")

article_df = st.session_state.article_df

support = 0
oppose = 0
driver_rows = []

driver_inputs = [
    ("DXY / USD", dxy, w_dxy, "Auto" if auto_macro and auto_drivers else "Manual"),
    ("US10Y", nominal_yields, w_nominal_yields, "Auto" if auto_macro and auto_drivers else "Manual"),
    ("Real yields", real_yields, w_real_yields, "Auto" if auto_macro and auto_drivers else "Manual"),
    ("Fed tone", fed_tone, w_fed, fed_source),
    ("Geopolitics", geo, w_geo, "Manual"),
    ("Risk sentiment", risk_mood, w_risk, "Auto" if auto_macro and auto_drivers else "Manual"),
]

for driver_name, selected, weight, source in driver_inputs:
    s, o = score_direction(selected, weight)
    support += s
    oppose += o
    impact, reason = explanation_for_driver(driver_name, selected, s, o)
    driver_rows.append({
        "Driver": driver_name,
        "Source": source,
        "State": selected,
        "Weight": weight,
        "Supporting pts": round(s, 1),
        "Opposing pts": round(o, 1),
        "Net": round(s - o, 1),
        "Impact": impact,
        "Why it matters": reason
    })

news_support, news_oppose = calculate_news_score(article_df, w_news)
support += news_support
oppose += news_oppose

support_news_count = int((article_df["Classification"] == "Supporting gold").sum()) if not article_df.empty else 0
oppose_news_count = int((article_df["Classification"] == "Opposing gold").sum()) if not article_df.empty else 0
neutral_news_count = int((article_df["Classification"] == "Neutral / unclear").sum()) if not article_df.empty else 0

news_impact, news_reason = explanation_for_driver("Gold news", "Gold news classification", news_support, news_oppose)

driver_rows.append({
    "Driver": "Gold news",
    "Source": "Google News RSS filtered",
    "State": f"{support_news_count} support / {oppose_news_count} oppose / {neutral_news_count} neutral",
    "Weight": w_news,
    "Supporting pts": round(news_support, 1),
    "Opposing pts": round(news_oppose, 1),
    "Net": round(news_support - news_oppose, 1),
    "Impact": news_impact,
    "Why it matters": news_reason
})

driver_df = pd.DataFrame(driver_rows)

total = support + oppose
support_pct = round((support / total) * 100, 1) if total else 50.0
oppose_pct = round(100 - support_pct, 1)

bias, confidence, action, edge, card = get_bias(support_pct, oppose_pct)

if clear_history_clicked:
    clear_score_history()
    st.session_state.last_snapshot_saved = "Score history cleared."

if save_snapshot_clicked:
    save_timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    screenshot_url = None
    screenshot_path = None
    screenshot_msg = None

    if uploaded_chart_screenshot is not None:
        screenshot_url, screenshot_path, screenshot_msg = upload_screenshot_to_supabase(
            uploaded_chart_screenshot,
            save_timestamp_utc
        )
        st.session_state.last_screenshot_status = screenshot_msg

    snapshot = build_snapshot(
        support_pct=support_pct,
        oppose_pct=oppose_pct,
        bias=bias,
        confidence=confidence,
        edge=edge,
        driver_df=driver_df,
        market_rows=st.session_state.market_rows,
        fed_result=fed_result,
        geo=geo,
        article_df=article_df,
        chart_screenshot_url=screenshot_url,
        chart_screenshot_path=screenshot_path,
        chart_screenshot_filename=uploaded_chart_screenshot.name if uploaded_chart_screenshot is not None else None,
        chart_timeframe=chart_timeframe,
        chart_setup_tag=chart_setup_tag,
    )
    snapshot["timestamp_utc"] = save_timestamp_utc
    snapshot["notes"] = snapshot_note
    save_score_snapshot(snapshot)
    st.session_state.last_snapshot_saved = f"Saved local snapshot at {snapshot['timestamp_utc']} UTC."

    if save_to_supabase:
        ok, msg = append_snapshot_to_supabase(snapshot)
        st.session_state.last_supabase_status = msg

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    <div class="bias-card-green">
        <div class="bias-title">Supporting Gold</div>
        <p class="big-number-green">{support_pct}%</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="bias-card-red">
        <div class="bias-title">Opposing Gold</div>
        <p class="big-number-red">{oppose_pct}%</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div class="{card}">
    <div class="bias-title">Macro Bias · {bias}</div>
    <p style="font-size: 1.1rem; margin-top: 8px;">{round(edge, 1)} pt edge · {confidence}</p>
    <p style="color:#d1d5db;">{action}</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# SCORE LOGGER PANEL
# ------------------------------------------------------------
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("Score Logger")

if st.session_state.last_snapshot_saved:
    st.success(st.session_state.last_snapshot_saved)

if st.session_state.last_screenshot_status:
    if "failed" in str(st.session_state.last_screenshot_status).lower() or "not uploaded" in str(st.session_state.last_screenshot_status).lower():
        st.warning(st.session_state.last_screenshot_status)
    else:
        st.success(st.session_state.last_screenshot_status)

if st.session_state.last_supabase_status:
    if "failed" in st.session_state.last_supabase_status.lower() or "not configured" in st.session_state.last_supabase_status.lower():
        st.warning(st.session_state.last_supabase_status)
    else:
        st.success(st.session_state.last_supabase_status)

if supabase_config_available():
    st.info("Supabase logging is configured. Use the sidebar toggle if you want each snapshot saved to Supabase as well.")
else:
    st.caption("Supabase logging is optional. Local CSV logging works now; Supabase needs Streamlit secrets configured after deployment.")

history_df = load_score_history()

if load_supabase_clicked:
    cloud_df, cloud_err = fetch_supabase_history(limit=100)
    st.session_state.supabase_history_df = cloud_df
    st.session_state.last_supabase_load_status = cloud_err or f"Loaded {len(cloud_df)} Supabase rows."

l1, l2, l3 = st.columns(3)
l1.metric("Saved snapshots", len(history_df))
l2.metric("Latest bias", bias)
l3.metric("Latest edge", f"{round(edge, 1)} pts")

st.caption("Use this to validate the tool. Save snapshots before London / New York trades, then later add 1H/4H outcome columns in the exported CSV.")

if history_df.empty:
    st.info("No snapshots saved yet. Add an optional note in the sidebar, then press **Save current bias snapshot**.")
else:
    render_dark_table(history_df.tail(25).sort_index(ascending=False), empty_message='No local snapshots saved yet.')
    csv_bytes = history_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download local score history CSV",
        data=csv_bytes,
        file_name="gold_intelligence_score_history.csv",
        mime="text/csv",
    )

if st.session_state.last_supabase_load_status:
    if "failed" in str(st.session_state.last_supabase_load_status).lower():
        st.warning(st.session_state.last_supabase_load_status)
    else:
        st.success(st.session_state.last_supabase_load_status)

if not st.session_state.supabase_history_df.empty:
    st.subheader("Supabase Cloud History")
    render_dark_table(st.session_state.supabase_history_df, empty_message='No Supabase history loaded yet.')
    cloud_csv = st.session_state.supabase_history_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Supabase history CSV",
        data=cloud_csv,
        file_name="gold_intelligence_supabase_history.csv",
        mime="text/csv",
    )

with st.expander("How to validate this properly"):
    st.write("Do not judge the tool from one reading. Save snapshots at consistent decision points, then check whether price moved with or against the bias.")
    st.write("Suggested routine:")
    st.write("- Save a snapshot after Asia completes.")
    st.write("- Save another near London open.")
    st.write("- Save another near New York open.")
    st.write("- Later, fill in price_1h_later, price_4h_later, bias_result_1h and bias_result_4h in the downloaded CSV.")
    st.write("- Only trust the score more if it repeatedly keeps you out of bad trades or aligns with clean moves.")

st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# FED TONE PANEL
# ------------------------------------------------------------
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("Fed Tone Intelligence")

f1, f2, f3, f4 = st.columns(4)
f1.metric("Fed tone", fed_result.get("tone", "Neutral / unclear"))
f2.metric("Confidence", f"{fed_result.get('confidence', 0)}%")
f3.metric("Hawkish articles", fed_result.get("hawkish", 0))
f4.metric("Dovish articles", fed_result.get("dovish", 0))

st.markdown(f"<div class='summary-box'>{fed_result.get('reason', 'No Fed tone data loaded.')}</div>", unsafe_allow_html=True)

if st.session_state.fed_df.empty:
    st.info("No Fed tone articles loaded yet. Press **Fetch Fed tone now** in the sidebar.")
else:
    render_dark_table(st.session_state.fed_df, empty_message='No Fed tone rows to display.')

st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# DRIVER EXPLANATION PANEL
# ------------------------------------------------------------
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("Driver Explanation Panel")

bearish_drivers = driver_df[driver_df["Opposing pts"] > driver_df["Supporting pts"]].sort_values("Opposing pts", ascending=False)
bullish_offsets = driver_df[driver_df["Supporting pts"] > driver_df["Opposing pts"]].sort_values("Supporting pts", ascending=False)

c1, c2, c3 = st.columns(3)
c1.metric("Total supporting pts", round(float(driver_df["Supporting pts"].sum()), 1))
c2.metric("Total opposing pts", round(float(driver_df["Opposing pts"].sum()), 1))
c3.metric("Net edge", round(float(driver_df["Opposing pts"].sum() - driver_df["Supporting pts"].sum()), 1), help="Positive = opposing gold. Negative = supporting gold.")

summary_lines = []
if not bearish_drivers.empty:
    top_bearish = bearish_drivers.iloc[0]
    summary_lines.append(f"Main bearish driver: **{top_bearish['Driver']}** ({top_bearish['Opposing pts']} opposing pts).")
if not bullish_offsets.empty:
    top_bullish = bullish_offsets.iloc[0]
    summary_lines.append(f"Main bullish offset: **{top_bullish['Driver']}** ({top_bullish['Supporting pts']} supporting pts).")
if not summary_lines:
    summary_lines.append("No dominant driver. The model is currently mixed.")

st.markdown("<div class='summary-box'>" + "<br>".join(summary_lines) + "</div>", unsafe_allow_html=True)

render_dark_table(driver_df, empty_message='No driver rows to display.')

with st.expander("Plain-English read"):
    if oppose_pct >= 65:
        st.write("The model has crossed the bearish permission threshold. Shorts are allowed only if TradingView confirms structure.")
    elif support_pct >= 65:
        st.write("The model has crossed the bullish permission threshold. Longs are allowed only if TradingView confirms structure.")
    else:
        st.write("The model has not crossed a clean permission threshold. Avoid forcing direction.")

    if not bearish_drivers.empty:
        st.write("Bearish pressure is mainly coming from:")
        for _, row in bearish_drivers.head(4).iterrows():
            st.write(f"- {row['Driver']}: {row['State']} ({row['Opposing pts']} opposing pts)")

    if not bullish_offsets.empty:
        st.write("Bullish offsets are:")
        for _, row in bullish_offsets.head(4).iterrows():
            st.write(f"- {row['Driver']}: {row['State']} ({row['Supporting pts']} supporting pts)")

st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# MARKET DATA
# ------------------------------------------------------------
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("Automatic Market Data")

if not st.session_state.market_rows:
    st.info("No market data loaded yet. Press **Fetch market data now** in the sidebar.")
else:
    rows = []
    for r in st.session_state.market_rows:
        rows.append({
            "Name": r.get("Name"),
            "Ticker / Series": r.get("Ticker", r.get("Series")),
            "Latest": None if r.get("Latest") is None else round(r.get("Latest"), 4),
            "Change %": None if r.get("Change %") is None else round(r.get("Change %"), 2),
            "Change bps": None if r.get("Change bps") is None else round(r.get("Change bps"), 1),
            "Date": r.get("Date"),
            "Error": r.get("Error") or ""
        })
    render_dark_table(pd.DataFrame(rows), empty_message='No market rows to display.')

st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# CURRENT DRIVER INPUTS
# ------------------------------------------------------------
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("Current Driver Inputs")

driver_mode = "Automatic market data" if auto_macro and auto_drivers else "Manual / fallback"

drivers = [
    ("Mode", driver_mode),
    ("DXY / USD", dxy),
    ("US10Y", nominal_yields),
    ("Real yields", real_yields),
    ("Fed tone", fed_tone),
    ("Geopolitics", geo),
    ("Risk sentiment", risk_mood),
]

driver_html = ""
for name, value in drivers:
    driver_html += f"<span class='driver-pill'><b>{name}:</b> {value}</span>"

st.markdown(driver_html, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# GOLD NEWS
# ------------------------------------------------------------
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("Filtered Gold News Classification")

if article_df.empty:
    st.info("No filtered gold news loaded yet, or no relevant market-focused gold articles were found. Press Fetch gold news now, or simplify the gold news query.")
else:
    a, b, c = st.columns(3)
    a.metric("Supporting articles", support_news_count)
    b.metric("Opposing articles", oppose_news_count)
    c.metric("Neutral / unclear", neutral_news_count)

    render_dark_table(article_df[["Time", "Source", "Title", "Classification", "Matched terms", "URL"]], empty_message="No gold news rows to display.")

st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# DEPLOYMENT NOTES
# ------------------------------------------------------------
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("Deployment Notes")

st.write("This folder is ready to upload to GitHub and deploy to Streamlit Community Cloud.")
st.write("For a permanent link, upload `app.py`, `requirements.txt`, `.streamlit/config.toml`, `README.md`, and `DEPLOYMENT_GUIDE.md` to a GitHub repository, then deploy the repo with main file path `app.py`.")
st.write("Configure Supabase plus a public chart-screenshots Storage bucket if you want hosted snapshots and chart screenshots to survive app restarts.")
st.warning("On free cloud hosting, local CSV storage may reset if the app restarts. Use the download button regularly. V10 includes optional Supabase logging for persistent cloud history.")

st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# TRADE RULES
# ------------------------------------------------------------
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("Trade Permission Rules")

rules = pd.DataFrame([
    {"Condition": "Opposing Gold > 65%", "Permission": "Short setups only", "Chart confirmation required": "Bearish AMD / liquidity sweep / MSS"},
    {"Condition": "Supporting Gold > 65%", "Permission": "Long setups only", "Chart confirmation required": "Bullish reclaim / MSS / continuation"},
    {"Condition": "45%–55% mixed", "Permission": "No trade or reduced risk", "Chart confirmation required": "Wait for clean alignment"},
    {"Condition": "Major news within 30 minutes", "Permission": "Avoid new trades", "Chart confirmation required": "Wait for post-news structure"},
])
render_dark_table(rules, empty_message='No rule rows to display.')
st.markdown("</div>", unsafe_allow_html=True)

st.caption(f"Last dashboard refresh: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
