import streamlit as st
import os, re, json


def load_css(filepath: str):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base, filepath)
    with open(full_path, "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# ── SVG helpers ───────────────────────────────────────────────────────────────
def icon_bus(size=20, color="#0D9488"):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
        viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round">
        <path d="M8 6v6M15 6v6M2 12h19.6M18 18h3s.5-1.7.8-2.8c.1-.4.2-.8.2-1.2
            0-.4-.1-.8-.2-1.2l-1.4-5C20.1 6.8 19.1 6 18 6H4a2 2 0 0 0-2 2v10h3"/>
        <circle cx="7" cy="18" r="2"/>
        <path d="M9 18h5"/>
        <circle cx="16" cy="18" r="2"/>
    </svg>"""

def icon_chat(size=20, color="#2563EB"):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
        viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
    </svg>"""

def icon_map(size=20, color="#2563EB"):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
        viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round">
        <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/>
        <line x1="9" y1="3" x2="9" y2="18"/>
        <line x1="15" y1="6" x2="15" y2="21"/>
    </svg>"""


# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sb-brand">
            <div class="sb-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
                    viewBox="0 0 24 24" fill="none" stroke="#0D9488" stroke-width="2"
                    stroke-linecap="round" stroke-linejoin="round">
                    <path d="M8 6v6M15 6v6M2 12h19.6M18 18h3s.5-1.7.8-2.8c.1-.4.2-.8.2-1.2
                        0-.4-.1-.8-.2-1.2l-1.4-5C20.1 6.8 19.1 6 18 6H4a2 2 0 0 0-2 2v10h3"/>
                    <circle cx="7" cy="18" r="2"/>
                    <path d="M9 18h5"/>
                    <circle cx="16" cy="18" r="2"/>
                </svg>
            </div>
            <div class="sb-brand-text">
                <span class="sb-name">RoutaGo</span>
                <span class="sb-sub">Cebu Jeepney Guide</span>
            </div>
        </div>
        <div class="sb-sep"></div>
        <div class="sb-section-label">MENU</div>
        """, unsafe_allow_html=True)

        st.page_link("RoutaGo.py",               label="Chat Assistant")
        st.page_link("pages/1_Plan_My_Route.py", label="Plan My Route")
        st.page_link("pages/2_Safety_Tips.py",   label="Safety Tips")
        st.page_link("pages/3_Saved_Routes.py",  label="Saved Routes")

        st.markdown("""
        <div class="sb-sep"></div>
        <div class="sb-section-label">INFO</div>
        <div class="sb-info-item">
            <span class="sb-dot" style="background:#F59E0B;"></span>Cebu City, PH
        </div>
        <div class="sb-info-item">
            <span class="sb-dot" style="background:#0D9488;"></span>Route 01K available
        </div>
        """, unsafe_allow_html=True)

        if "dark_mode" not in st.session_state:
            st.session_state.dark_mode = False

        st.markdown('<div class="sb-sep" style="margin-top:auto;margin-bottom:0.5rem;"></div>', unsafe_allow_html=True)

        col_label, col_btn = st.columns([3, 1])
        with col_label:
            st.markdown('<span class="sb-dark-label">Dark Mode</span>', unsafe_allow_html=True)
        with col_btn:
            if st.button("\u200b", key="dark_toggle", help="Toggle dark mode"):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()

        st.markdown('<div class="sb-ver">RoutaGo v1.0.0</div>', unsafe_allow_html=True)


# ── Dark mode ─────────────────────────────────────────────────────────────────
def inject_dark_mode():
    if st.session_state.get("dark_mode", False):
        st.markdown("""
        <style>
        html, body, .stApp { background-color: #0F172A !important; color: #F1F5F9 !important; }
        .main .block-container { background: transparent !important; padding-top: 1.5rem !important; }
        .stApp { --bg: #0F172A; --surface: #1E293B; --border: #2D3748; --text-1: #F1F5F9; --text-2: #CBD5E1; --text-3: #94A3B8; --text-4: #475569; --blue-light: rgba(37,99,235,0.15); --teal-light: rgba(13,148,136,0.15); }
        [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > .main { background-color: #0F172A !important; }
        [data-testid="stBottom"], [data-testid="stBottom"] > div, [data-testid="stBottom"] > div > div { background-color: #0F172A !important; }
        [data-testid="stChatInput"] { background: #1E293B !important; border-color: #2D3748 !important; }
        [data-testid="stChatInput"] textarea { color: #F1F5F9 !important; }
        [data-testid="stChatInput"] textarea::placeholder { color: #475569 !important; }
        .rg-page-header { border-bottom: 1px solid #1E293B !important; }
        .rg-page-header-icon { background: rgba(37,99,235,0.2) !important; border-color: rgba(37,99,235,0.35) !important; }
        .rg-page-header-text h1 { color: #F1F5F9 !important; }
        .rg-page-header-text p { color: #64748B !important; }
        .rg-welcome h2 { color: #F1F5F9 !important; }
        .rg-welcome p { color: #64748B !important; }
        .rg-welcome-logo { background: #1E293B !important; border-color: #2D3748 !important; }
        .rg-chip { background: #1E293B !important; border-color: #2D3748 !important; color: #94A3B8 !important; box-shadow: none !important; }
        .rg-chip:hover { background: #1E3A5F !important; border-color: #3B82F6 !important; color: #93C5FD !important; }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) { background: #1E293B !important; border-color: #2D3748 !important; color: #CBD5E1 !important; }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) p,
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) li,
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) span,
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) div,
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .rg-response-body { color: #CBD5E1 !important; }
        .rg-response-body { color: #CBD5E1 !important; }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { background: #162032 !important; border-color: #1E3A5F !important; border-left-color: #3B82F6 !important; }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p,
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) span { color: #93C5FD !important; }
        .rg-route-card-wrap { color: #CBD5E1 !important; }
        .rg-route-header { color: #F1F5F9 !important; }
        .rg-route-subtitle { color: #64748B !important; }
        .rg-step-num { background: #1E3A5F !important; border-color: #2563EB !important; color: #93C5FD !important; }
        .rg-step-text { color: #CBD5E1 !important; }
        .rg-card-fare { background: #1C1505 !important; border-color: #78350F !important; }
        .rg-card-fare .rg-card-label { color: #FCD34D !important; }
        .rg-card-fare .rg-card-sub { color: #D97706 !important; }
        .rg-fare-amount { color: #FBBF24 !important; }
        .rg-card-dropoff { background: #0F1E3D !important; border-color: #1D4ED8 !important; border-left-color: #3B82F6 !important; }
        .rg-card-dropoff .rg-card-label { color: #93C5FD !important; }
        .rg-card-dropoff .rg-card-body { color: #BFDBFE !important; }
        .rg-card-tips { background: #0A1F12 !important; border-color: #166534 !important; border-left-color: #16A34A !important; }
        .rg-card-tips .rg-card-label { color: #86EFAC !important; }
        .rg-tip-item { color: #BBF7D0 !important; border-bottom-color: #14532D !important; }
        </style>
        <script>
        (function paintBtn() {
            const btn = window.parent.document.querySelector('[data-testid="stChatInputSubmitButton"] button');
            if (btn) {
                btn.style.setProperty('background', '#2563EB', 'important');
                btn.style.setProperty('background-color', '#2563EB', 'important');
                btn.style.setProperty('border', 'none', 'important');
                btn.style.setProperty('border-radius', '10px', 'important');
                btn.style.setProperty('opacity', '0.88', 'important');
                btn.onmouseenter = () => btn.style.setProperty('background','#1D4ED8','important');
                btn.onmouseleave = () => btn.style.setProperty('background','#2563EB','important');
            } else { setTimeout(paintBtn, 100); }
        })();
        </script>
        """, unsafe_allow_html=True)


# ── Response formatter ────────────────────────────────────────────────────────
def _badge(text):
    """Convert **CODE** to a teal monospace badge span."""
    return re.sub(r'\*\*(.*?)\*\*', r"<span class='jeep-code'>\1</span>", text)


def format_response(text: str) -> str:
    """
    Parses JSON from the LLM and renders structured route cards.
    Falls back to plain text with bold badges if JSON is absent/malformed.
    All HTML is built with zero leading whitespace — st.markdown() turns
    4-space-indented lines into code blocks.
    """
    # Strip any markdown fences the model may have added
    clean = re.sub(r"```json|```", "", text).strip()

    # Attempt JSON parse
    try:
        data = json.loads(clean)
    except Exception:
        return "<div class='rg-response-body'>" + _badge(text).replace("\n", "<br>") + "</div>"

    # Plain text / greeting / error
    if data.get("type") == "text":
        msg = data.get("message", "")
        return "<div class='rg-response-body'>" + _badge(msg).replace("\n", "<br>") + "</div>"

    # Route card
    route_code  = data.get("route_code", "")
    origin      = data.get("origin", "")
    destination = data.get("destination", "")
    steps       = data.get("steps", [])
    fare        = data.get("fare", "")
    fare_note   = data.get("fare_note", "")
    dropoff     = data.get("dropoff", "")
    tips        = data.get("tips", [])

    # Numbered steps
    steps_html = "".join(
        '<div class="rg-step">'
        + f'<div class="rg-step-num">{i}</div>'
        + f'<div class="rg-step-text">{_badge(s)}</div>'
        + '</div>'
        for i, s in enumerate(steps, 1)
    )

    # Fare card
    fare_block = (
        '<div class="rg-card rg-card-fare">'
        + '<div class="rg-card-label">FARE ESTIMATE</div>'
        + f'<div class="rg-fare-amount">{fare}</div>'
        + f'<div class="rg-card-sub">{fare_note}</div>'
        + '</div>'
    ) if fare else ""

    # Drop-off card
    dropoff_block = (
        '<div class="rg-card rg-card-dropoff">'
        + '<div class="rg-card-label">WHERE TO STOP (DROP OFF)</div>'
        + f'<div class="rg-card-body">{dropoff}</div>'
        + '</div>'
    ) if dropoff else ""

    # Tips card
    tips_block = (
        '<div class="rg-card rg-card-tips">'
        + '<div class="rg-card-label">TIPS</div>'
        + "".join(f'<div class="rg-tip-item">{t}</div>' for t in tips)
        + '</div>'
    ) if tips else ""

    # Header
    if origin and destination:
        header = (
            "Route: <strong style='color:#2563EB'>" + origin
            + "</strong> &rarr; <strong style='color:#2563EB'>" + destination + "</strong>"
        )
    else:
        header = "<strong>" + route_code + "</strong>"

    return (
        '<div class="rg-route-card-wrap">'
        + '<div class="rg-route-header">'
       + (f'<span class="jeep-code rg-route-code">{route_code}</span>' if route_code else '')
        + header
        + '</div>'
        + '<div class="rg-route-subtitle">Follow these step-by-step directions</div>'
        + f'<div class="rg-steps">{steps_html}</div>'
        + fare_block
        + dropoff_block
        + tips_block
        + '</div>'
    )