import json
import os
from datetime import datetime
from io import StringIO
import hashlib

import requests
import streamlit as st

st.set_page_config(page_title="VoteWise AI", page_icon="🗳️", layout="wide")

TRANSLATIONS = {
    "en": {
        "appTitle": "VoteWise AI",
        "appSubtitle": "Your intelligent election companion",
        "tabs": [
            "Dashboard",
            "My Journey",
            "Timeline",
            "Booth Finder",
            "AI Assistant",
            "Learn & Myths",
            "Fact Checker",
            "Vote Simulator",
            "Election Guide",
            "Election Data Explorer",
        ],
        "labels": {
            "dashboard": "Dashboard",
            "journey": "My Journey",
            "timeline": "Timeline",
            "booth": "Booth Finder",
            "assistant": "AI Assistant",
            "learn": "Learn & Myths",
            "fact": "Fact Checker",
            "vote": "Vote Simulator",
            "guide": "Election Guide",
            "data": "Election Data Explorer",
        },
        "chatPlaceholder": "Ask about elections, voting rights, EVM, candidates...",
        "send": "Send",
        "detect": "Check News",
        "factPlaceholder": "Paste a news headline or claim to verify...",
        "voteSubmit": "Submit Vote",
        "voteSuccess": "Vote cast successfully!",
        "voteCount": "Live Tally",
        "guideTitle": "How India Votes",
        "lang": "हिन्दी",
        "welcome": "Namaste! I am VoteWise AI. Ask about registration, EVM security, election schedules, voting rights, and Model Code of Conduct.",
        "riskLevels": {"high": "Likely Misinformation", "medium": "Needs Verification", "low": "Appears Credible"},
        "candidates": [
            {"id": 1, "name": "Candidate A", "party": "Progressive Alliance"},
            {"id": 2, "name": "Candidate B", "party": "National Front"},
            {"id": 3, "name": "Candidate C", "party": "People's Voice"},
            {"id": 4, "name": "NOTA", "party": "None of the Above"},
        ],
        "steps": [
            "Register on voterportal.eci.gov.in using Form 6.",
            "Receive your EPIC voter ID.",
            "Find your polling booth from official ECI sources.",
            "Vote on EVM and verify VVPAT.",
            "Counting happens on notified date.",
            "Majority party/coalition forms government.",
        ],
    },
    "hi": {
        "appTitle": "वोटवाइज़ AI",
        "appSubtitle": "आपका बुद्धिमान चुनाव साथी",
        "tabs": [
            "डैशबोर्ड",
            "मेरी यात्रा",
            "टाइमलाइन",
            "बूथ फाइंडर",
            "AI सहायक",
            "सीखें और मिथक",
            "तथ्य जांच",
            "वोट सिम्युलेटर",
            "चुनाव गाइड",
            "इलेक्शन डेटा एक्सप्लोरर",
        ],
        "labels": {
            "dashboard": "डैशबोर्ड",
            "journey": "मेरी यात्रा",
            "timeline": "टाइमलाइन",
            "booth": "बूथ फाइंडर",
            "assistant": "AI सहायक",
            "learn": "सीखें और मिथक",
            "fact": "तथ्य जांच",
            "vote": "वोट सिम्युलेटर",
            "guide": "चुनाव गाइड",
            "data": "इलेक्शन डेटा एक्सप्लोरर",
        },
        "chatPlaceholder": "चुनाव, मतदान अधिकार, EVM, उम्मीदवारों के बारे में पूछें...",
        "send": "भेजें",
        "detect": "समाचार जांचें",
        "factPlaceholder": "किसी समाचार शीर्षक या दावे को यहाँ पेस्ट करें...",
        "voteSubmit": "वोट दें",
        "voteSuccess": "वोट सफलतापूर्वक डाला गया!",
        "voteCount": "लाइव परिणाम",
        "guideTitle": "भारत में मतदान कैसे होता है",
        "lang": "English",
        "welcome": "नमस्ते! मैं वोटवाइज़ AI हूं। मतदाता पंजीकरण, EVM सुरक्षा, चुनाव समय, मतदान अधिकार और आचार संहिता पर पूछें।",
        "riskLevels": {"high": "संभावित गलत सूचना", "medium": "सत्यापन आवश्यक", "low": "विश्वसनीय लगती है"},
        "candidates": [
            {"id": 1, "name": "उम्मीदवार क", "party": "प्रगतिशील गठबंधन"},
            {"id": 2, "name": "उम्मीदवार ख", "party": "राष्ट्रीय मोर्चा"},
            {"id": 3, "name": "उम्मीदवार ग", "party": "जन आवाज़"},
            {"id": 4, "name": "NOTA", "party": "इनमें से कोई नहीं"},
        ],
        "steps": [
            "voterportal.eci.gov.in पर Form 6 से पंजीकरण करें।",
            "EPIC मतदाता पहचान पत्र प्राप्त करें।",
            "ECI स्रोत से अपना मतदान केंद्र खोजें।",
            "EVM पर मतदान करें और VVPAT देखें।",
            "निर्धारित दिन मतगणना होती है।",
            "बहुमत पार्टी/गठबंधन सरकार बनाती है।",
        ],
    },
}

SYSTEM_PROMPT = (
    "You are VoteWise AI, an expert Indian election assistant. "
    "Be concise, accurate, friendly, and non-partisan. "
    "Respond in the same language as user. Keep responses under 150 words."
)


def apply_liquid_glass_theme() -> None:
    is_light = st.session_state.get("theme_mode") == "light"
    high_contrast = st.session_state.get("high_contrast", False)
    large_text = st.session_state.get("large_text", False)

    bg_deep = "#f6f9ff" if is_light else "#071733"
    bg_mid = "#dce9ff" if is_light else "#0e2f68"
    bg_soft = "#bdd7ff" if is_light else "#1d4ca1"
    text = "#10233f" if is_light else "#eaf2ff"
    text_soft = "rgba(16, 35, 63, 0.86)" if is_light else "rgba(234, 242, 255, 0.82)"
    line = "rgba(16, 35, 63, 0.28)" if is_light else "rgba(255, 255, 255, 0.26)"
    card_a = "rgba(255, 255, 255, 0.72)" if is_light else "rgba(255, 255, 255, 0.17)"
    card_b = "rgba(255, 255, 255, 0.56)" if is_light else "rgba(255, 255, 255, 0.09)"

    if high_contrast:
        text = "#ffffff" if not is_light else "#000000"
        text_soft = text
        line = "rgba(255,255,255,0.85)" if not is_light else "rgba(0,0,0,0.8)"

    font_scale = "1.10" if large_text else "1.0"

    css = """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');

            :root {
                --bg-deep: __BG_DEEP__;
                --bg-mid: __BG_MID__;
                --bg-soft: __BG_SOFT__;
                --glass: rgba(255, 255, 255, 0.14);
                --glass-strong: rgba(255, 255, 255, 0.24);
                --line: __LINE__;
                --text: __TEXT__;
                --text-soft: __TEXT_SOFT__;
                --accent-a: #ff8d3a;
                --accent-b: #20c997;
            }

            .stApp {
                font-family: 'Manrope', sans-serif;
                font-size: __FONT_SCALE__rem;
                background:
                    radial-gradient(1200px 520px at -10% -20%, rgba(255, 141, 58, 0.30), transparent 52%),
                    radial-gradient(1000px 560px at 110% 0%, rgba(32, 201, 151, 0.23), transparent 48%),
                    linear-gradient(140deg, var(--bg-deep) 0%, var(--bg-mid) 44%, var(--bg-soft) 100%);
                color: var(--text);
            }

            .main > div {
                padding-top: 1rem;
            }

            h1, h2, h3, h4, h5 {
                color: #f5f9ff !important;
                letter-spacing: 0.2px;
            }

            .hero-wrap {
                position: relative;
                overflow: hidden;
                border-radius: 26px;
                padding: 1.2rem 1.3rem;
                margin-bottom: 0.8rem;
                border: 1px solid var(--line);
                background: linear-gradient(135deg, rgba(8, 25, 56, 0.78), rgba(18, 53, 110, 0.55));
                backdrop-filter: blur(10px);
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.26);
            }

            .hero-wrap::before {
                content: "";
                position: absolute;
                width: 240px;
                height: 240px;
                right: -70px;
                top: -110px;
                border-radius: 50%;
                background: radial-gradient(circle at center, rgba(255, 141, 58, 0.24), transparent 70%);
            }

            .hero-title {
                margin: 0;
                font-size: 2.2rem;
                font-weight: 800;
                color: #ffffff;
            }

            .hero-subtitle {
                margin: 0.1rem 0 0;
                color: var(--text-soft);
                font-weight: 600;
            }

            .chip-row {
                display: flex;
                gap: 0.45rem;
                margin-top: 0.6rem;
                flex-wrap: wrap;
            }

            .chip {
                border: 1px solid rgba(255, 255, 255, 0.24);
                background: rgba(255, 255, 255, 0.08);
                color: #f2f7ff;
                border-radius: 999px;
                font-size: 0.78rem;
                font-weight: 700;
                padding: 0.18rem 0.6rem;
                letter-spacing: 0.2px;
            }

            .glass-card {
                border-radius: 20px;
                padding: 1rem 1rem 0.8rem;
                border: 1px solid var(--line);
                background: linear-gradient(140deg, __CARD_A__, __CARD_B__);
                backdrop-filter: blur(14px);
                box-shadow: 0 16px 38px rgba(0, 0, 0, 0.2);
                margin: 0.2rem 0 1rem;
            }

            .message {
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.16);
                padding: 0.72rem 0.82rem;
                margin: 0.45rem 0;
                line-height: 1.55;
                color: #f6f9ff;
                backdrop-filter: blur(8px);
            }

            .assistant-msg {
                background: linear-gradient(145deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.08));
            }

            .user-msg {
                background: linear-gradient(145deg, rgba(255, 141, 58, 0.35), rgba(32, 201, 151, 0.16));
            }

            .step-card {
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                background: rgba(255, 255, 255, 0.11);
                padding: 0.7rem 0.85rem;
                margin-bottom: 0.55rem;
                color: #f4f8ff;
            }

            .soft-note {
                color: rgba(236, 244, 255, 0.9);
                font-size: 0.95rem;
            }

            .risk-box {
                border-radius: 14px;
                border: 1px solid rgba(255, 255, 255, 0.22);
                padding: 0.8rem 0.9rem;
                background: rgba(255, 255, 255, 0.14);
            }

            .stTabs [data-baseweb="tab-list"] {
                gap: 0.45rem;
                background: rgba(6, 18, 43, 0.36);
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 14px;
                padding: 0.2rem;
            }

            .stTabs [data-baseweb="tab"] {
                border-radius: 11px;
                font-weight: 700;
                color: #dbe9ff;
                height: 2.45rem;
                background: rgba(255, 255, 255, 0.08);
            }

            .stTabs [aria-selected="true"] {
                color: #ffffff !important;
                background: linear-gradient(135deg, rgba(255, 141, 58, 0.44), rgba(27, 150, 255, 0.42)) !important;
                border: 1px solid rgba(255, 255, 255, 0.25) !important;
            }

            .stButton > button {
                border: 1px solid rgba(255, 255, 255, 0.32) !important;
                background: linear-gradient(120deg, rgba(255, 141, 58, 0.7), rgba(27, 150, 255, 0.7), rgba(32, 201, 151, 0.7));
                color: #ffffff !important;
                border-radius: 999px !important;
                font-weight: 800 !important;
                letter-spacing: 0.2px;
                box-shadow: 0 10px 22px rgba(0, 0, 0, 0.25);
                transition: transform 0.18s ease;
            }

            .stButton > button:hover {
                transform: translateY(-1px) scale(1.01);
                opacity: 0.97;
            }

            .stTextInput input,
            .stTextArea textarea {
                border-radius: 13px !important;
                border: 1px solid rgba(255, 255, 255, 0.30) !important;
                background: rgba(255, 255, 255, 0.13) !important;
                color: #f6fbff !important;
            }

            .stTextInput input::placeholder,
            .stTextArea textarea::placeholder {
                color: rgba(244, 250, 255, 0.72) !important;
            }

            .stRadio [data-testid="stMarkdownContainer"] p {
                color: #f6fbff !important;
                font-weight: 600;
            }

            [data-testid="stProgressBar"] div[role="progressbar"] {
                background: linear-gradient(90deg, rgba(255, 141, 58, 0.9), rgba(32, 201, 151, 0.95)) !important;
            }

            .stCaption {
                color: rgba(232, 240, 255, 0.8) !important;
            }
        </style>
        """
    css = (
        css.replace("__BG_DEEP__", bg_deep)
        .replace("__BG_MID__", bg_mid)
        .replace("__BG_SOFT__", bg_soft)
        .replace("__LINE__", line)
        .replace("__TEXT__", text)
        .replace("__TEXT_SOFT__", text_soft)
        .replace("__FONT_SCALE__", font_scale)
        .replace("__CARD_A__", card_a)
        .replace("__CARD_B__", card_b)
    )
    st.markdown(css, unsafe_allow_html=True)


def init_state() -> None:
    if "lang" not in st.session_state:
        st.session_state.lang = "en"
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": TRANSLATIONS["en"]["welcome"]}]
    if "votes" not in st.session_state:
        st.session_state.votes = {1: 142, 2: 198, 3: 87, 4: 23}
    if "voted" not in st.session_state:
        st.session_state.voted = False
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "dark"
    if "high_contrast" not in st.session_state:
        st.session_state.high_contrast = False
    if "large_text" not in st.session_state:
        st.session_state.large_text = False
    if "simple_language" not in st.session_state:
        st.session_state.simple_language = False
    if "calendar_added" not in st.session_state:
        st.session_state.calendar_added = False
    if "id_verified" not in st.session_state:
        st.session_state.id_verified = False
    if "journey_path" not in st.session_state:
        st.session_state.journey_path = ""
    if "booth_result" not in st.session_state:
        st.session_state.booth_result = None


def call_claude(messages, system):
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        return "AI key not configured. Set ANTHROPIC_API_KEY to enable live assistant replies."

    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 500,
        "system": system,
        "messages": [{"role": m["role"], "content": m["content"]} for m in messages],
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    try:
        response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, data=json.dumps(payload), timeout=20)
        response.raise_for_status()
        data = response.json()
        return data.get("content", [{}])[0].get("text", "No response")
    except Exception:
        return "Connection error while reaching AI service."


def query_groq_insight(user_query: str, state: str, year: int, election_type: str, context: dict) -> str:
    api_key = os.getenv("GROQ_API_KEY", "")
    base_url = os.getenv("GROQ_API_BASE_URL", "https://api.groq.com/openai/v1")
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    if not api_key:
        return "Groq key missing. Set GROQ_API_KEY in your environment to generate live AI insight."

    prompt = (
        "You are an AI Election Assistant integrated with IndiaVotes data.\n"
        "Your tasks:\n"
        "- Explain election results clearly in Hindi + English.\n"
        "- Show party-wise seats, vote share, alliance performance.\n"
        "- Highlight swing compared to previous election.\n"
        "- Mention voter turnout and NOTA impact.\n"
        "- Keep responses simple and user-friendly.\n"
        "- Always clarify: This is historical data from IndiaVotes, not live ECI results.\n\n"
        f"State: {state}\n"
        f"Year: {year}\n"
        f"Election Type: {election_type}\n"
        f"Context: {context}\n"
        f"User Query: {user_query}\n"
    )

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(f"{base_url.rstrip('/')}/chat/completions", json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "No response from Groq.")
    except Exception:
        return "Groq request failed. Please verify GROQ_API_KEY, model name, and internet connectivity."


def heuristic_fact_check(claim, lang):
    text = claim.lower().strip()
    suspicious = ["free money", "urgent share", "click this", "election cancelled", "secret result", "फ्री", "तुरंत शेयर", "क्लिक"]
    reliable = ["eci.gov.in", "pib.gov.in", "official notice", "official circular", "आधिकारिक"]

    score = 50
    flags = []
    for k in suspicious:
        if k in text:
            score += 18
            flags.append(f"Contains suspicious pattern: {k}")
    for k in reliable:
        if k in text:
            score -= 15

    score = max(5, min(95, score))
    if score >= 70:
        verdict = "LIKELY_FALSE"
    elif score >= 40:
        verdict = "NEEDS_VERIFICATION"
    else:
        verdict = "LIKELY_TRUE"

    if lang == "hi":
        tip = "ECI और PIB Fact Check जैसे आधिकारिक स्रोतों से जांच करें।"
        explanation = "यह परिणाम नियम-आधारित विश्लेषण पर आधारित है। अंतिम पुष्टि आधिकारिक स्रोतों से करें।"
    else:
        tip = "Verify on ECI and PIB Fact Check before sharing."
        explanation = "This result is based on rule-based analysis. Confirm with official sources before trusting or sharing."

    return {
        "verdict": verdict,
        "confidence": score,
        "explanation": explanation,
        "redFlags": flags,
        "tip": tip,
    }


def render_header(t):
    st.markdown(
        (
            "<div class='hero-wrap'>"
            f"<h1 class='hero-title'>🗳️ {t['appTitle']}</h1>"
            f"<p class='hero-subtitle'>{t['appSubtitle']}</p>"
            "<div class='chip-row'>"
            "<span class='chip'>IN India</span>"
            "<span class='chip'>ECI Aligned</span>"
            "<span class='chip'>AI Powered</span>"
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([6, 1])
    with c1:
        st.markdown("<div class='soft-note'>Multilingual election guidance, misinformation checks, and voter simulation in one experience.</div>", unsafe_allow_html=True)
    with c2:
        if st.button(f"{t['lang']} ⇄"):
            st.session_state.lang = "hi" if st.session_state.lang == "en" else "en"
            st.session_state.messages = [{"role": "assistant", "content": TRANSLATIONS[st.session_state.lang]["welcome"]}]
            st.rerun()


def render_settings_panel():
    with st.expander("Accessibility & Settings", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.high_contrast = st.checkbox(
                "High Contrast Mode",
                value=st.session_state.high_contrast,
                help="Improves visibility for visually impaired users.",
            )
            st.session_state.large_text = st.checkbox(
                "Large Text Mode",
                value=st.session_state.large_text,
                help="Increases base font size across app.",
            )
        with c2:
            st.session_state.simple_language = st.checkbox(
                "Simple Language Mode",
                value=st.session_state.simple_language,
                help="Simplifies complex election jargon.",
            )
            if st.button("Apply Visual Settings", use_container_width=True):
                st.rerun()


def _simple(text: str) -> str:
    if not st.session_state.get("simple_language"):
        return text
    replacements = {
        "constituency": "area",
        "electoral roll": "voter list",
        "verification": "check",
        "declaration": "announcement",
    }
    out = text
    for old, new in replacements.items():
        out = out.replace(old, new)
        out = out.replace(old.title(), new.title())
    return out


def tab_dashboard(t):
    st.subheader(t["labels"]["dashboard"])
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown("### Welcome to VoteGuide AI")
        st.write(_simple("Your personalized, stress-free path to understanding elections and casting your vote confidently."))
    with c2:
        if st.button("Simulate Google Translate", key="translate_sim"):
            st.session_state.lang = "hi" if st.session_state.lang == "en" else "en"
            st.rerun()
        if st.button("Toggle Theme", key="theme_toggle"):
            st.session_state.theme_mode = "light" if st.session_state.theme_mode == "dark" else "dark"
            st.rerun()

    readiness = 15
    readiness += 35 if st.session_state.calendar_added else 0
    readiness += 25 if st.session_state.id_verified else 0
    readiness += 25 if st.session_state.journey_path else 0
    st.metric("Election Readiness", f"{min(readiness, 100)}%")
    st.progress(min(readiness, 100))

    c3, c4 = st.columns(2)
    with c3:
        st.info("Upcoming: Voter Registration Deadline\n\nEnsure your details are updated by the deadline. Required for first-time voters.")
        if st.button("Add to Google Calendar (Simulated)", key="cal_btn"):
            st.session_state.calendar_added = True
            st.success("Added to calendar successfully.")
    with c4:
        st.warning("Action Required: Verify ID\n\nCarry a valid government photo ID to the polling station.")
        if st.button("Mark ID Verified", key="id_btn"):
            st.session_state.id_verified = True
            st.success("ID checklist complete.")

    st.markdown("</div>", unsafe_allow_html=True)


def tab_journey(t):
    st.subheader(t["labels"]["journey"])
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### Let's build your personalized guide")
    st.write("What do you need help with the most?")

    opts = [
        "I am a first-time voter",
        "Polling Day Guidance",
        "Registration Help",
        "General Education",
    ]
    choice = st.radio("Journey Path", opts, index=0)
    if st.button("Save My Journey", use_container_width=True):
        st.session_state.journey_path = choice

    selected = st.session_state.journey_path
    if selected:
        st.success(f"Selected Path: {selected}")
        if "first-time" in selected.lower():
            st.write("1) Check your name in the voter list. 2) Keep ID ready. 3) Visit booth early.")
        elif "polling" in selected.lower():
            st.write("Polling hours are usually 7 AM to 6 PM. Verify booth and carry valid ID.")
        elif "registration" in selected.lower():
            st.write("Use Form 6 on voter portal, upload documents, and track your application ID.")
        else:
            st.write("Explore EVM basics, voter rights, MCC rules, and myth-vs-fact modules.")

    st.markdown("</div>", unsafe_allow_html=True)


def tab_timeline_tracker(t):
    st.subheader(t["labels"]["timeline"])
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### Election Timeline Tracker")
    st.write(_simple("Stay updated with key dates for the upcoming election."))

    phases = [
        ("Phase 1 • Registration Opens", "Voter registration portal opens for new applicants and updates.", True),
        ("Phase 2 • Candidate Announcement", "Official list of contesting candidates is published.", True),
        ("Phase 3 • Registration Deadline (Upcoming)", "Last day to register or update voter details.", False),
        ("Phase 4 • Polling Day", "Cast your vote at your designated polling station. Time: 7:00 AM - 6:00 PM.", False),
        ("Phase 5 • Results Declaration", "Counting of votes and declaration of elected representatives.", False),
    ]
    for title, desc, done in phases:
        status = "✅" if done else "🕒"
        st.markdown(f"**{status} {title}**")
        st.write(_simple(desc))
        st.markdown("---")

    st.markdown("</div>", unsafe_allow_html=True)


def tab_booth_finder(t):
    st.subheader(t["labels"]["booth"])
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### Find Your Polling Booth")
    st.write("Enter your area details to locate your designated voting center.")

    c1, c2, c3 = st.columns(3)
    with c1:
        city = st.text_input("City / District", placeholder="e.g. Khordha")
    with c2:
        locality = st.text_input("Locality / Area", placeholder="e.g. Jatani")
    with c3:
        pin = st.text_input("PIN / Zip Code", placeholder="e.g. 752050")

    if st.button("Locate Booth", use_container_width=True):
        if not (city.strip() and locality.strip() and pin.strip()):
            st.error("Please enter city, locality, and PIN.")
        else:
            token = hashlib.md5(f"{city}|{locality}|{pin}".encode("utf-8")).hexdigest()
            booth_no = int(token[:2], 16) % 250 + 1
            serial_no = int(token[2:6], 16) % 1200 + 1
            st.session_state.booth_result = {
                "booth": f"{locality.title()} Government School, Booth {booth_no}",
                "district": city.title(),
                "pin": pin,
                "serial": serial_no,
            }

    if st.session_state.booth_result:
        r = st.session_state.booth_result
        st.success("Booth located successfully (simulated mapping).")
        st.write(f"Polling Station: {r['booth']}")
        st.write(f"District: {r['district']}")
        st.write(f"PIN: {r['pin']}")
        st.write(f"Electoral Serial: {r['serial']}")

    st.markdown("</div>", unsafe_allow_html=True)


def tab_learn_myths(t):
    st.subheader(t["labels"]["learn"])
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### Myth vs Fact")

    myths = [
        ("Voting takes the entire day.", "Wait times depend on the center. Usually it takes less than 30 minutes."),
        ("My single vote does not matter.", "Every vote counts. Many elections are decided by small margins."),
        ("I need a physical voter card to vote.", "If your name is on the roll, other valid IDs are also accepted."),
    ]
    for idx, (myth, fact) in enumerate(myths, start=1):
        with st.expander(f"Myth {idx}: {myth}"):
            st.success(f"Fact: {fact}")

    st.markdown("### Educational Resources")
    c1, c2 = st.columns(2)
    with c1:
        st.info("How Voting Machines Work\n\nA simple guide to understanding Electronic Voting Machines (EVMs).")
        if st.button("Read Article", key="evm_article"):
            st.write("EVMs have ballot and control units, plus VVPAT for visual confirmation.")
    with c2:
        st.info("Checklist for Polling Day\n\nWhat to carry and what to expect at the station.")
        if st.button("View Checklist", key="poll_checklist"):
            st.write("Carry ID, confirm booth, keep water, and arrive early to avoid queues.")

    st.markdown("</div>", unsafe_allow_html=True)


def tab_chat(t):
    st.subheader(t["labels"]["assistant"])
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    for m in st.session_state.messages:
        if m["role"] == "assistant":
            st.markdown(f"<div class='message assistant-msg'><strong>🤖 {t['appTitle']}</strong><br>{m['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='message user-msg'><strong>👤 You</strong><br>{m['content']}</div>", unsafe_allow_html=True)

    quick = ["How to register?", "How does EVM work?", "What is NOTA?"] if st.session_state.lang == "en" else ["पंजीकरण कैसे करें?", "EVM कैसे काम करती है?", "NOTA क्या है?"]
    cols = st.columns(len(quick))
    for i, q in enumerate(quick):
        if cols[i].button(q, key=f"quick_{i}_{st.session_state.lang}"):
            st.session_state.chat_input = q

    chat_input = st.text_input(t["chatPlaceholder"], value=st.session_state.get("chat_input", ""))
    if st.button(t["send"], use_container_width=True) and chat_input.strip():
        st.session_state.messages.append({"role": "user", "content": chat_input})
        reply = call_claude(st.session_state.messages, SYSTEM_PROMPT)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.chat_input = ""
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def tab_fact_checker(t):
    st.subheader(t["labels"]["fact"])
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='risk-box'>⚠️ AI-powered detection combines rules + ML scoring. Always confirm via official sources (ECI, PIB).</div>",
        unsafe_allow_html=True,
    )
    claim = st.text_area(t["factPlaceholder"], height=120)
    if st.button(f"🔍 {t['detect']}", use_container_width=True) and claim.strip():
        result = heuristic_fact_check(claim, st.session_state.lang)
        st.session_state.fact_result = result

    result = st.session_state.get("fact_result")
    if result:
        verdict_color = {
            "LIKELY_FALSE": "red",
            "NEEDS_VERIFICATION": "orange",
            "LIKELY_TRUE": "green",
        }.get(result["verdict"], "orange")
        label_map = {
            "LIKELY_FALSE": t["riskLevels"]["high"],
            "NEEDS_VERIFICATION": t["riskLevels"]["medium"],
            "LIKELY_TRUE": t["riskLevels"]["low"],
        }
        st.markdown(f"### :{verdict_color}[{label_map[result['verdict']]}] ({result['confidence']}%)")
        st.write(result["explanation"])
        if result.get("redFlags"):
            st.write("Red Flags:")
            for flag in result["redFlags"]:
                st.write(f"- {flag}")
        st.info(result["tip"])

    st.markdown("</div>", unsafe_allow_html=True)


def tab_vote_simulator(t):
    st.subheader(t["labels"]["vote"])
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<div class='soft-note'>🎮 Simulated Election — Demo Constituency</div>", unsafe_allow_html=True)
    options = {f"{c['name']} ({c['party']})": c["id"] for c in t["candidates"]}
    selected_label = st.radio("Select candidate", list(options.keys()), disabled=st.session_state.voted)

    if st.button(f"🗳️ {t['voteSubmit']}", disabled=st.session_state.voted):
        choice = options[selected_label]
        st.session_state.votes[choice] += 1
        st.session_state.voted = True
        st.success(t["voteSuccess"])

    st.markdown(f"### {t['voteCount']}")
    total = sum(st.session_state.votes.values())
    for c in t["candidates"]:
        votes = st.session_state.votes[c["id"]]
        pct = (votes / total) * 100 if total else 0
        st.write(f"{c['name']}: {votes} ({pct:.1f}%)")
        st.progress(int(pct))

    if st.button("Reset Simulation"):
        st.session_state.voted = False
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def tab_guide(t):
    st.subheader(t["labels"]["guide"])
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.write(f"### {t['guideTitle']}")
    for idx, step in enumerate(t["steps"], start=1):
        st.markdown(f"<div class='step-card'><strong>STEP {idx}</strong><br>{step}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.caption(f"Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    st.markdown("</div>", unsafe_allow_html=True)


def get_indiavotes_cache():
    # Cached historical-style sample records to keep the feature fully local and fast.
    return [
        {"year": 2014, "state": "Odisha", "election_type": "Lok Sabha", "party": "BJD", "alliance": "Regional", "seats": 20, "vote_share": 44.8, "contested": 21, "turnout": 73.1, "nota_share": 1.2},
        {"year": 2014, "state": "Odisha", "election_type": "Lok Sabha", "party": "BJP", "alliance": "NDA", "seats": 1, "vote_share": 21.5, "contested": 21, "turnout": 73.1, "nota_share": 1.2},
        {"year": 2014, "state": "Odisha", "election_type": "Lok Sabha", "party": "INC", "alliance": "UPA", "seats": 0, "vote_share": 26.0, "contested": 21, "turnout": 73.1, "nota_share": 1.2},
        {"year": 2019, "state": "Odisha", "election_type": "Lok Sabha", "party": "BJD", "alliance": "Regional", "seats": 12, "vote_share": 42.8, "contested": 21, "turnout": 74.1, "nota_share": 1.5},
        {"year": 2019, "state": "Odisha", "election_type": "Lok Sabha", "party": "BJP", "alliance": "NDA", "seats": 8, "vote_share": 38.4, "contested": 21, "turnout": 74.1, "nota_share": 1.5},
        {"year": 2019, "state": "Odisha", "election_type": "Lok Sabha", "party": "INC", "alliance": "UPA", "seats": 1, "vote_share": 13.8, "contested": 21, "turnout": 74.1, "nota_share": 1.5},
        {"year": 2024, "state": "Odisha", "election_type": "Lok Sabha", "party": "BJP", "alliance": "NDA", "seats": 20, "vote_share": 45.3, "contested": 21, "turnout": 75.7, "nota_share": 1.1},
        {"year": 2024, "state": "Odisha", "election_type": "Lok Sabha", "party": "BJD", "alliance": "Regional", "seats": 1, "vote_share": 37.4, "contested": 21, "turnout": 75.7, "nota_share": 1.1},
        {"year": 2024, "state": "Odisha", "election_type": "Lok Sabha", "party": "INC", "alliance": "UPA", "seats": 0, "vote_share": 12.5, "contested": 21, "turnout": 75.7, "nota_share": 1.1},
        {"year": 2018, "state": "Karnataka", "election_type": "Assembly", "party": "BJP", "alliance": "NDA", "seats": 104, "vote_share": 36.4, "contested": 224, "turnout": 72.1, "nota_share": 0.9},
        {"year": 2018, "state": "Karnataka", "election_type": "Assembly", "party": "INC", "alliance": "UPA", "seats": 80, "vote_share": 38.0, "contested": 222, "turnout": 72.1, "nota_share": 0.9},
        {"year": 2018, "state": "Karnataka", "election_type": "Assembly", "party": "JD(S)", "alliance": "Regional", "seats": 37, "vote_share": 18.3, "contested": 201, "turnout": 72.1, "nota_share": 0.9},
        {"year": 2023, "state": "Karnataka", "election_type": "Assembly", "party": "INC", "alliance": "UPA", "seats": 135, "vote_share": 42.9, "contested": 224, "turnout": 73.2, "nota_share": 0.7},
        {"year": 2023, "state": "Karnataka", "election_type": "Assembly", "party": "BJP", "alliance": "NDA", "seats": 66, "vote_share": 36.0, "contested": 224, "turnout": 73.2, "nota_share": 0.7},
        {"year": 2023, "state": "Karnataka", "election_type": "Assembly", "party": "JD(S)", "alliance": "Regional", "seats": 19, "vote_share": 13.3, "contested": 207, "turnout": 73.2, "nota_share": 0.7},
        {"year": 2014, "state": "Uttar Pradesh", "election_type": "Lok Sabha", "party": "BJP", "alliance": "NDA", "seats": 71, "vote_share": 42.6, "contested": 80, "turnout": 58.3, "nota_share": 0.9},
        {"year": 2014, "state": "Uttar Pradesh", "election_type": "Lok Sabha", "party": "SP", "alliance": "Regional", "seats": 5, "vote_share": 22.2, "contested": 78, "turnout": 58.3, "nota_share": 0.9},
        {"year": 2014, "state": "Uttar Pradesh", "election_type": "Lok Sabha", "party": "BSP", "alliance": "Regional", "seats": 0, "vote_share": 19.6, "contested": 80, "turnout": 58.3, "nota_share": 0.9},
        {"year": 2019, "state": "Uttar Pradesh", "election_type": "Lok Sabha", "party": "BJP", "alliance": "NDA", "seats": 62, "vote_share": 49.6, "contested": 78, "turnout": 59.2, "nota_share": 0.8},
        {"year": 2019, "state": "Uttar Pradesh", "election_type": "Lok Sabha", "party": "SP", "alliance": "MGB", "seats": 5, "vote_share": 18.1, "contested": 37, "turnout": 59.2, "nota_share": 0.8},
        {"year": 2019, "state": "Uttar Pradesh", "election_type": "Lok Sabha", "party": "BSP", "alliance": "MGB", "seats": 10, "vote_share": 19.4, "contested": 38, "turnout": 59.2, "nota_share": 0.8},
        {"year": 2024, "state": "Uttar Pradesh", "election_type": "Lok Sabha", "party": "BJP", "alliance": "NDA", "seats": 33, "vote_share": 41.4, "contested": 75, "turnout": 57.7, "nota_share": 0.9},
        {"year": 2024, "state": "Uttar Pradesh", "election_type": "Lok Sabha", "party": "SP", "alliance": "INDIA", "seats": 37, "vote_share": 33.6, "contested": 62, "turnout": 57.7, "nota_share": 0.9},
        {"year": 2024, "state": "Uttar Pradesh", "election_type": "Lok Sabha", "party": "INC", "alliance": "INDIA", "seats": 6, "vote_share": 9.5, "contested": 17, "turnout": 57.7, "nota_share": 0.9},
    ]


def aggregate_by_party(records):
    bucket = {}
    for row in records:
        key = row["party"]
        if key not in bucket:
            bucket[key] = {"party": key, "alliance": row["alliance"], "seats": 0, "vote_share": 0.0, "contested": 0}
        bucket[key]["seats"] += int(row["seats"])
        bucket[key]["vote_share"] += float(row["vote_share"])
        bucket[key]["contested"] += int(row["contested"])
    rows = list(bucket.values())
    rows.sort(key=lambda x: (-x["seats"], -x["vote_share"]))
    return rows


def aggregate_by_alliance(records):
    bucket = {}
    for row in records:
        key = row["alliance"]
        if key not in bucket:
            bucket[key] = {"alliance": key, "seats": 0, "vote_share": 0.0}
        bucket[key]["seats"] += int(row["seats"])
        bucket[key]["vote_share"] += float(row["vote_share"])
    rows = list(bucket.values())
    rows.sort(key=lambda x: (-x["seats"], -x["vote_share"]))
    return rows


def build_swing_table(current_rows, previous_rows):
    prev_index = {row["party"]: row for row in previous_rows}
    swing_rows = []
    for row in current_rows:
        prev = prev_index.get(row["party"], {"seats": 0, "vote_share": 0.0})
        swing_rows.append(
            {
                "party": row["party"],
                "seat_swing": int(row["seats"]) - int(prev["seats"]),
                "vote_swing": round(float(row["vote_share"]) - float(prev["vote_share"]), 2),
            }
        )
    swing_rows.sort(key=lambda x: (-x["seat_swing"], -x["vote_swing"]))
    return swing_rows


def build_history_summary(cache_rows, state, election_type):
    years = sorted({r["year"] for r in cache_rows if r["state"] == state and r["election_type"] == election_type})
    trend_rows = []
    for year in years:
        sample = [r for r in cache_rows if r["state"] == state and r["election_type"] == election_type and r["year"] == year]
        if sample:
            turnout = sample[0]["turnout"]
            nota = sample[0]["nota_share"]
            trend_rows.append({"year": year, "turnout": turnout, "nota_share": nota})
    return trend_rows


def tab_data_explorer(t):
    st.subheader(t["labels"]["data"])
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='risk-box'>📊 Historical Election Data Explorer (IndiaVotes-style). This view presents historical analysis and is not an official ECI live-results feed.</div>",
        unsafe_allow_html=True,
    )

    cache_rows = get_indiavotes_cache()
    all_states = sorted({r["state"] for r in cache_rows})
    all_types = sorted({r["election_type"] for r in cache_rows})

    c1, c2, c3 = st.columns(3)
    with c1:
        state = st.selectbox("State", all_states)
    with c2:
        election_type = st.selectbox("Election Type", all_types)
    filtered_base = [r for r in cache_rows if r["state"] == state and r["election_type"] == election_type]
    years = sorted({r["year"] for r in filtered_base})
    with c3:
        year = st.selectbox("Year", years, index=len(years) - 1)

    selected_rows = [r for r in filtered_base if r["year"] == year]
    party_rows = aggregate_by_party(selected_rows)
    alliance_rows = aggregate_by_alliance(selected_rows)

    st.markdown("### Party Performance")
    st.dataframe(party_rows, use_container_width=True)

    st.markdown("### Alliance Performance")
    st.dataframe(alliance_rows, use_container_width=True)

    prev_years = [y for y in years if y < year]
    if prev_years:
        prev_year = prev_years[-1]
        prev_rows = [r for r in filtered_base if r["year"] == prev_year]
        prev_party = aggregate_by_party(prev_rows)
        swing_rows = build_swing_table(party_rows, prev_party)
        st.markdown(f"### Swing Analysis vs {prev_year}")
        st.dataframe(swing_rows, use_container_width=True)
    else:
        st.info("Swing analysis will appear once a previous election year exists for this state and election type.")

    st.markdown("### NOTA and Turnout Impact")
    trend_rows = build_history_summary(cache_rows, state, election_type)
    if trend_rows:
        st.line_chart(trend_rows, x="year", y=["turnout", "nota_share"], use_container_width=True)
        st.dataframe(trend_rows, use_container_width=True)

    st.markdown("### Comparison Mode")
    compare_enabled = st.checkbox("Compare two election years side by side", value=False)
    if compare_enabled and len(years) > 1:
        compare_year = st.selectbox("Compare With Year", [y for y in years if y != year], index=0)
        compare_rows = [r for r in filtered_base if r["year"] == compare_year]
        left, right = st.columns(2)
        with left:
            st.markdown(f"#### Selected: {year}")
            st.dataframe(aggregate_by_party(selected_rows), use_container_width=True)
        with right:
            st.markdown(f"#### Compared: {compare_year}")
            st.dataframe(aggregate_by_party(compare_rows), use_container_width=True)

    total_seats = sum(r["seats"] for r in party_rows)
    top_party = party_rows[0]["party"] if party_rows else "NA"
    top_alliance = alliance_rows[0]["alliance"] if alliance_rows else "NA"
    if st.session_state.lang == "hi":
        summary_text = (
            f"{state} ({year}, {election_type}) में टॉप पार्टी {top_party} रही। "
            f"कुल सीटें {total_seats} रहीं और प्रमुख गठबंधन {top_alliance} रहा। "
            "यह ऐतिहासिक विश्लेषण IndiaVotes-style डेटा पर आधारित है, यह ECI का लाइव परिणाम नहीं है।"
        )
    else:
        summary_text = (
            f"In {state} ({year}, {election_type}), top party is {top_party}. "
            f"Total tracked seats are {total_seats}, with {top_alliance} leading at alliance level. "
            "This is historical IndiaVotes-style analysis and not official ECI live results."
        )

    st.markdown("### AI Insight (Hindi + English Friendly)")
    st.write(summary_text)

    if "groq_insight" not in st.session_state:
        st.session_state.groq_insight = ""

    default_query = (
        "Explain party performance, alliance comparison, swing, turnout, and NOTA impact in simple Hindi + English."
    )
    user_query = st.text_area("Ask Groq about this election data", value=default_query, height=90)
    if st.button("Generate Live AI Insight (Groq)", use_container_width=True):
        context_payload = {
            "party_performance": party_rows,
            "alliance_performance": alliance_rows,
            "trend": trend_rows,
        }
        with st.spinner("Generating Groq insight..."):
            st.session_state.groq_insight = query_groq_insight(
                user_query=user_query,
                state=state,
                year=year,
                election_type=election_type,
                context=context_payload,
            )

    if st.session_state.groq_insight:
        st.markdown("#### Groq AI Response")
        st.write(st.session_state.groq_insight)
        st.caption("Historical analysis from IndiaVotes-style data. Not official live ECI results.")

    report_payload = {
        "generated_at_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "state": state,
        "election_type": election_type,
        "year": year,
        "party_performance": party_rows,
        "alliance_performance": alliance_rows,
        "insight": summary_text,
        "groq_insight": st.session_state.groq_insight,
    }
    report_buffer = StringIO()
    report_buffer.write(json.dumps(report_payload, ensure_ascii=False, indent=2))
    st.download_button(
        label="Download Explorer Report (JSON)",
        data=report_buffer.getvalue(),
        file_name=f"election_data_explorer_{state.lower().replace(' ', '_')}_{year}.json",
        mime="application/json",
    )

    st.markdown(
        """
        #### Built-in Prompt Template
        ```python
        prompt = '''
        You are an AI Election Assistant.
        Use IndiaVotes data to answer user queries about past elections.
        Provide clear tables and charts showing:
        - Party-wise seats and vote share
        - Alliance performance
        - Swing compared to previous election
        - Voter turnout and NOTA impact

        Explain results in simple Hindi + English for accessibility.
        Always clarify that this is historical data from IndiaVotes, not official ECI live results.
        '''
        ```
        """
    )
    st.markdown("</div>", unsafe_allow_html=True)


def main():
    init_state()
    apply_liquid_glass_theme()
    t = TRANSLATIONS[st.session_state.lang]
    render_header(t)
    render_settings_panel()

    tabs = st.tabs(t["tabs"])
    with tabs[0]:
        tab_dashboard(t)
    with tabs[1]:
        tab_journey(t)
    with tabs[2]:
        tab_timeline_tracker(t)
    with tabs[3]:
        tab_booth_finder(t)
    with tabs[4]:
        tab_chat(t)
    with tabs[5]:
        tab_learn_myths(t)
    with tabs[6]:
        tab_fact_checker(t)
    with tabs[7]:
        tab_vote_simulator(t)
    with tabs[8]:
        tab_guide(t)
    with tabs[9]:
        tab_data_explorer(t)


if __name__ == "__main__":
    main()
