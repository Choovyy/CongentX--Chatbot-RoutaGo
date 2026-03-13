import streamlit as st
import os, re, json, base64


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
        logo_data = ""
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                logo_data = base64.b64encode(f.read()).decode("utf-8")

        if "dark_mode" not in st.session_state:
            st.session_state.dark_mode = False

        current_dark_mode = st.session_state.dark_mode
        dark_mode_enabled = st.toggle(
            "Dark mode",
            value=current_dark_mode,
            key="theme_mode_toggle",
            label_visibility="collapsed",
            help="On = Dark mode, Off = Light mode"
        )
        st.session_state.dark_mode = dark_mode_enabled

        st.markdown('<div class="sb-sep" style="margin-top:0.35rem;margin-bottom:0.75rem;"></div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="sb-brand">
            <a class="sb-logo-link" href="#rg-logo-modal" aria-label="View RoutaGo logo">
                <div class="sb-icon">
                    <img src="data:image/png;base64,{logo_data}" alt="RoutaGo logo" class="sb-logo-image" />
                </div>
            </a>
            <div class="sb-brand-text">
                <span class="sb-name">RoutaGo</span>
                <span class="sb-sub">Cebu Jeepney Guide</span>
            </div>
        </div>

        <div id="rg-logo-modal" class="sb-logo-modal" aria-hidden="true">
            <a class="sb-logo-modal-backdrop" href="#" aria-label="Close"></a>
            <div class="sb-logo-modal-box" role="dialog" aria-modal="true" aria-label="RoutaGo logo full view">
                <a class="sb-logo-modal-close" href="#" aria-label="Close">&times;</a>
                <img src="data:image/png;base64,{logo_data}" alt="RoutaGo logo full view" class="sb-logo-modal-image" />
            </div>
        </div>

        <div class="sb-sep"></div>
        <div class="sb-section-label">MENU</div>
        """, unsafe_allow_html=True)

        st.page_link("RoutaGo.py",               label="Chat Assistant")
        st.page_link("pages/1_Plan_My_Route.py", label="Plan My Route")
        st.page_link("pages/2_Safety_Tips.py",   label="Safety Tips")
        st.page_link("pages/3_Cebu_Map.py",      label="Cebu Map")
        st.page_link("pages/4_Important_Signage.py", label="Traffic Rules")

        st.markdown("""
        <div class="sb-sep"></div>
        <div class="sb-section-label">INFO</div>
        <div class="sb-info-item">
            <span class="sb-dot" style="background:#F59E0B;"></span>Cebu City, PH
        </div>
        <div class="sb-info-item">
            <span class="sb-dot" style="background:#0D9488;"></span>Best in Cebu City routes
        </div>
        <div class="sb-info-item">
            <span class="sb-dot" style="background:#22C55E;"></span>Route 01K available
        </div>
        <div class="sb-info-item">
            <span class="sb-dot" style="background:#F59E0B;"></span>Use landmarks when asking
        </div>
        <div class="sb-info-item">
            <span class="sb-dot" style="background:#A78BFA;"></span><strong>Click images in Traffic Rules and Safety Tips for full view</strong>
        </div>
        <div class="sb-info-item">
            <span class="sb-dot" style="background:#34D399;"></span>"Lugar lang" = Please stop here
        </div>
        <div class="sb-info-item">
            <span class="sb-dot" style="background:#60A5FA;"></span>"Palihug" = Please
        </div>
        <div class="sb-info-item">
            <span class="sb-dot" style="background:#FBBF24;"></span>"Pila plete?" = How much is the fare?
        </div>
        <div class="sb-info-item">
            <span class="sb-dot" style="background:#F472B6;"></span>"Para" = Stop (signal word)
        </div>
        """, unsafe_allow_html=True)

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
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .rg-response-body { color: #E2E8F0 !important; font-size: 0.95rem !important; line-height: 1.76 !important; }
        .rg-response-body { color: #E2E8F0 !important; font-size: 0.95rem !important; line-height: 1.76 !important; }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { background: #162032 !important; border-color: #1E3A5F !important; border-left-color: #3B82F6 !important; }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p,
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) span { color: #93C5FD !important; }
        .rg-route-card-wrap { color: #E2E8F0 !important; }
        .rg-route-header { color: #F1F5F9 !important; }
        .rg-route-subtitle { color: #94A3B8 !important; }
        .rg-steps-label { color: #A5B4FC !important; }
        .rg-step { background: #0F1A2E !important; border-color: #334155 !important; }
        .rg-step-num { background: #1E3A5F !important; border-color: #2563EB !important; color: #93C5FD !important; }
        .rg-step-label { color: #BFDBFE !important; }
        .rg-step-text { color: #E2E8F0 !important; }
        .rg-card-fare { background: #1C1505 !important; border-color: #78350F !important; }
        .rg-card-fare .rg-card-label { color: #FCD34D !important; }
        .rg-card-fare .rg-card-sub { color: #F59E0B !important; }
        .rg-fare-amount { color: #FBBF24 !important; }
        .rg-card-dropoff { background: #0F1E3D !important; border-color: #1D4ED8 !important; border-left-color: #3B82F6 !important; }
        .rg-card-dropoff .rg-card-label { color: #93C5FD !important; }
        .rg-card-dropoff .rg-card-body { color: #BFDBFE !important; }
        .rg-card-tips { background: #0A1F12 !important; border-color: #166534 !important; border-left-color: #16A34A !important; }
        .rg-card-tips .rg-card-label { color: #86EFAC !important; }
        .rg-tip-item { color: #DCFCE7 !important; border-bottom-color: #14532D !important; }
        .rg-map-tip { background: rgba(37,99,235,0.12) !important; border-color: rgba(37,99,235,0.35) !important; border-left-color: #3B82F6 !important; color: #93C5FD !important; }
        .rg-map-tip strong { color: #93C5FD !important; }
        .rg-map-tip-icon svg { stroke: #93C5FD !important; }
        .rg-map-pin-card { background: #1E293B !important; border-color: #2D3748 !important; }
        .rg-map-pin-card:hover { border-color: #3B82F6 !important; }
        .rg-map-pin-name { color: #F1F5F9 !important; }
        .rg-map-pin-full { color: #94A3B8 !important; }
        .rg-map-pin-coords { color: #64748B !important; }
        .rg-badge-blue { background: rgba(37,99,235,0.18) !important; border-color: rgba(59,130,246,0.35) !important; color: #93C5FD !important; }
        .rg-badge-red { background: rgba(220,38,38,0.15) !important; border-color: rgba(248,113,113,0.35) !important; color: #FCA5A5 !important; }
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


def _repair_unescaped_quotes(json_like: str) -> str:
    """
    Repairs common malformed JSON where quotes inside string values are not escaped.
    Heuristic: when inside a string, a quote is treated as closing only if the next
    non-space character is a valid JSON delimiter (: , } ]).
    """
    result = []
    in_string = False
    escaped = False
    length = len(json_like)

    for i, char in enumerate(json_like):
        if not in_string:
            result.append(char)
            if char == '"':
                in_string = True
                escaped = False
            continue

        if escaped:
            result.append(char)
            escaped = False
            continue

        if char == "\\":
            result.append(char)
            escaped = True
            continue

        if char == '"':
            j = i + 1
            while j < length and json_like[j].isspace():
                j += 1

            next_char = json_like[j] if j < length else ""
            if next_char in [":", ",", "}", "]", ""]:
                result.append(char)
                in_string = False
            else:
                result.append('\\"')
            continue

        if char in ["\n", "\r"]:
            result.append("\\n")
            continue

        result.append(char)

    return "".join(result)


def _extract_json_object(raw_text: str) -> str:
    """Extracts the first top-level JSON object from mixed model text."""
    text = re.sub(r"```json|```", "", raw_text or "", flags=re.IGNORECASE).strip()
    text = re.sub(r"^\s*assistant\s*avatar\s*", "", text, flags=re.IGNORECASE)

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1].strip()
    return text


def _try_parse_json_candidate(candidate: str):
    if not isinstance(candidate, str):
        return None

    candidate = candidate.strip()
    if not candidate:
        return None

    try:
        parsed = json.loads(candidate)
    except Exception:
        parsed = None

    if isinstance(parsed, dict):
        return parsed

    if isinstance(parsed, str):
        nested = _extract_json_object(parsed)
        try:
            nested_parsed = json.loads(nested)
            if isinstance(nested_parsed, dict):
                return nested_parsed
        except Exception:
            pass

    decoder = json.JSONDecoder()
    for index, char in enumerate(candidate):
        if char not in ["{", "["]:
            continue
        try:
            parsed_obj, _ = decoder.raw_decode(candidate[index:])
            if isinstance(parsed_obj, dict):
                return parsed_obj
            if isinstance(parsed_obj, str):
                nested = _extract_json_object(parsed_obj)
                nested_parsed = _try_parse_json_candidate(nested)
                if isinstance(nested_parsed, dict):
                    return nested_parsed
        except Exception:
            continue

    return None


def _extract_route_object_from_text(raw_text: str):
    text = raw_text or ""
    if "route" not in text.lower():
        return None

    def _field(name: str):
        pattern = rf'"{name}"\s*:\s*"(.*?)"'
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""

    route_type = _field("type")
    if route_type and route_type.lower() != "route":
        return None

    steps_match = re.search(r'"steps"\s*:\s*\[(.*?)\]', text, flags=re.IGNORECASE | re.DOTALL)
    steps = []
    if steps_match:
        raw_steps = steps_match.group(1)
        steps = [m.strip() for m in re.findall(r'"((?:\\.|[^"\\])*)"', raw_steps)]
        steps = [s.replace('\\"', '"') for s in steps if s.strip()]

    tips_match = re.search(r'"tips"\s*:\s*\[(.*?)\]', text, flags=re.IGNORECASE | re.DOTALL)
    tips = []
    if tips_match:
        raw_tips = tips_match.group(1)
        tips = [m.strip() for m in re.findall(r'"((?:\\.|[^"\\])*)"', raw_tips)]
        tips = [t.replace('\\"', '"') for t in tips if t.strip()]

    route_obj = {
        "type": "route",
        "route_code": _field("route_code"),
        "route_name": _field("route_name"),
        "origin": _field("origin"),
        "destination": _field("destination"),
        "boarding": _field("boarding"),
        "steps": steps,
        "fare": _field("fare"),
        "fare_note": _field("fare_note"),
        "dropoff": _field("dropoff"),
        "tips": tips,
    }

    has_core_content = bool(route_obj["steps"] or route_obj["origin"] or route_obj["destination"] or route_obj["route_name"])
    return route_obj if has_core_content else None


def _parse_llm_json(raw_text: str):
    """Attempts strict parse first, then lenient repair for malformed JSON."""
    candidate = _extract_json_object(raw_text)
    parsed = _try_parse_json_candidate(candidate)
    if isinstance(parsed, dict):
        return parsed

    repaired = _repair_unescaped_quotes(candidate)
    repaired = re.sub(r",\s*([}\]])", r"\1", repaired)
    parsed_repaired = _try_parse_json_candidate(repaired)
    if isinstance(parsed_repaired, dict):
        return parsed_repaired

    heuristic_route = _extract_route_object_from_text(raw_text)
    if isinstance(heuristic_route, dict):
        return heuristic_route

    return None


def format_response(text: str) -> str:
    """
    Parses JSON from the LLM and renders structured route cards.
    Falls back to plain text with bold badges if JSON is absent/malformed.
    All HTML is built with zero leading whitespace — st.markdown() turns
    4-space-indented lines into code blocks.
    """
    data = _parse_llm_json(text)
    if data is None:
        clean_fallback = _extract_json_object(text)
        clean_fallback = re.sub(r"^\s*assistant\s*avatar\s*", "", clean_fallback, flags=re.IGNORECASE)
        return "<div class='rg-response-body'>" + _badge(clean_fallback).replace("\n", "<br>") + "</div>"

    if not isinstance(data, dict):
        return "<div class='rg-response-body'>" + _badge(str(data)).replace("\n", "<br>") + "</div>"

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

    def _clean_step_text(step_text: str) -> str:
        cleaned = (step_text or "").strip()
        cleaned = re.sub(r"^\s*\d+\s*[\)\].:,-]?\s*", "", cleaned)
        cleaned = re.sub(r"^\s*step\s*\d+\s*[\)\].:,-]?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^\s*[\-–—:]+\s*", "", cleaned)
        cleaned = re.sub(r"\s+[\-–—]{2,}\s+", " — ", cleaned)
        return cleaned

    cleaned_steps = [_clean_step_text(s) for s in steps]
    cleaned_steps = [s for s in cleaned_steps if s and not re.fullmatch(r"\d+", s)]

    # Numbered steps
    steps_html = "".join(
        '<div class="rg-step">'
        + f'<div class="rg-step-num">{i}</div>'
        + f'<div class="rg-step-content"><div class="rg-step-label">Step {i}</div><div class="rg-step-text">{_badge(s)}</div></div>'
        + '</div>'
        for i, s in enumerate(cleaned_steps, 1)
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
       + (f'<span class="jeep-code rg-route-code">{route_code}</span> ' if route_code else '')
        + header
        + '</div>'
        + '<div class="rg-route-subtitle">Follow these passenger directions</div>'
        + '<div class="rg-steps-label">DIRECTIONS</div>'
        + f'<div class="rg-steps">{steps_html}</div>'
        + fare_block
        + dropoff_block
        + tips_block
        + '</div>'
    )