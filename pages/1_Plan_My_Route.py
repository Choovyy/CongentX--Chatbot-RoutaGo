import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os, json, sys, re, base64, requests
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# --- CUSTOM MODULES ---
# helpers module contains shared UI components and response formatting logic
from utils.helpers import load_css, render_sidebar, format_response, inject_dark_mode

load_dotenv()

st.set_page_config(page_title="Plan Route — RoutaGo", page_icon="assets/logo.png", layout="wide", initial_sidebar_state="expanded")
load_css("assets/styles/main.css")
load_css("assets/styles/plan.css")
render_sidebar()
inject_dark_mode()

# Initialize session state for recent routes
if "recent_routes" not in st.session_state:
    st.session_state.recent_routes = []
if "last_plan" not in st.session_state:
    st.session_state.last_plan = None

# Known Cebu landmarks with fixed coordinates (Nominatim-proof)
_CEBU_LANDMARKS = {
    # ── 01K Route stops (Urgello → Parkmall, in order) ───────────────────
    "urgello st": (10.2938, 123.8958),
    "urgello street": (10.2938, 123.8958),
    "urgello": (10.2938, 123.8958),
    "sacred heart hospital": (10.2951, 123.8965),
    "southwestern university": (10.2942, 123.8957),
    "swu": (10.2942, 123.8957),
    "elizabeth mall": (10.2933, 123.8971),
    "emall": (10.2933, 123.8971),
    "e-mall": (10.2933, 123.8971),
    "leon kilat st": (10.2978, 123.8989),
    "leon kilat": (10.2978, 123.8989),
    "colon st": (10.2940, 123.8985),
    "colon street": (10.2940, 123.8985),
    "colon": (10.2940, 123.8985),
    "metro gaisano colon": (10.2959, 123.9003),
    "gaisano colon": (10.2959, 123.9003),
    "colonnade supermarket": (10.2967, 123.9012),
    "colonnade": (10.2967, 123.9012),
    "university of the visayas": (10.2968, 123.9014),
    "uv": (10.2968, 123.9014),
    "uv urgello": (10.2968, 123.9014),
    "gaisano main": (10.2985, 123.9023),
    "brgy. parian": (10.3002, 123.9033),
    "brgy parian": (10.3002, 123.9033),
    "parian": (10.3002, 123.9033),
    "zulueta st": (10.3043, 123.9040),
    "zulueta": (10.3043, 123.9040),
    "m.j. cuenco ave": (10.3095, 123.9048),
    "mj cuenco": (10.3095, 123.9048),
    "cuenco ave": (10.3095, 123.9048),
    "nso": (10.3112, 123.9053),
    "national statistics office": (10.3112, 123.9053),
    "general maxilom ave": (10.3135, 123.9055),
    "maxilom": (10.3135, 123.9055),
    "a. soriano ave": (10.3152, 123.9053),
    "soriano ave": (10.3152, 123.9053),
    "sm city cebu": (10.3176, 123.9053),
    "sm cebu": (10.3176, 123.9053),
    "sm hypermarket": (10.3187, 123.9058),
    "north bus terminal": (10.3213, 123.9069),
    "north terminal": (10.3213, 123.9069),
    "cebu north terminal": (10.3213, 123.9069),
    "cebu doctors university": (10.3249, 123.9112),
    "cebu doctors": (10.3249, 123.9112),
    "cicc": (10.3288, 123.9172),
    "cebu international convention center": (10.3288, 123.9172),
    "parkmall": (10.3354, 123.9348),
    "parkmall puj terminal": (10.3354, 123.9348),
    "parkmall terminal": (10.3354, 123.9348),
    # ── Other common Cebu landmarks ───────────────────────────────────────
    "carbon market": (10.2939, 123.9008),
    "carbon": (10.2939, 123.9008),
    "fuente osmena": (10.3060, 123.8930),
    "fuente osmeña": (10.3060, 123.8930),
    "fuente": (10.3060, 123.8930),
    "ayala center cebu": (10.3183, 123.9049),
    "ayala": (10.3183, 123.9049),
    "it park": (10.3310, 123.9055),
    "cebu it park": (10.3310, 123.9055),
    "capitol": (10.3175, 123.8915),
    "cebu capitol": (10.3175, 123.8915),
    "robinsons galleria": (10.3025, 123.8937),
    "robinson": (10.3025, 123.8937),
    "pier": (10.2913, 123.9017),
    "cebu port": (10.2913, 123.9017),
    "mactan": (10.3108, 123.9791),
    "lahug": (10.3289, 123.9006),
}

def _clean_place(name: str) -> str:
    """Strip parenthetical abbreviations and transit suffixes."""
    name = re.sub(r'\s*\([^)]*\)', '', name).strip()
    for suffix in ["puj terminal", "terminal", "jeepney stop", "stop", "station"]:
        if name.lower().endswith(suffix):
            name = name[: -len(suffix)].strip(" ,-")
    return name

def _forward_geocode(place: str):
    """Return (lat, lng) for a place in Cebu, or None."""
    key = place.lower().strip()
    if key in _CEBU_LANDMARKS:
        return _CEBU_LANDMARKS[key]
    cleaned = _clean_place(place)
    if cleaned.lower() in _CEBU_LANDMARKS:
        return _CEBU_LANDMARKS[cleaned.lower()]

    def _nominatim(q):
        try:
            r = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": q + ", Cebu, Philippines", "format": "json",
                        "limit": 1, "countrycodes": "ph"},
                headers={"User-Agent": "RoutaGo-Streamlit-App/1.0"},
                timeout=5,
            )
            if r.ok and r.json():
                res = r.json()[0]
                return float(res["lat"]), float(res["lon"])
        except Exception:
            pass
        return None

    result = _nominatim(place)
    if result:
        return result
    if cleaned != place:
        result = _nominatim(cleaned)
        if result:
            return result
    return None

with open("routes.json", "r", encoding="utf-8") as f:
    ROUTES = json.load(f)

try:
    api_key = st.secrets.get("GROQ_API_KEY")
except Exception:
    api_key = None
api_key = api_key or os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

st.markdown("""
<div class="rg-page-header">
    <div class="rg-page-header-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" y1="3" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="21"/></svg>
    </div>
    <div class="rg-page-header-text">
        <h1>Plan My Route</h1>
        <p>Plan your Cebu commute with clear, practical, stop-by-stop guidance.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Load logo for bus flag animation
_logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo.png")
with open(_logo_path, "rb") as _lf:
    _logo_b64 = base64.b64encode(_lf.read()).decode("utf-8")

# TABBED UI: separates the interactive planning tool from history
tab1, tab2 = st.tabs(["Plan Your Route", "Recent Routes"])

with tab1:
    # Card-style container for the route search form
    st.markdown("<div class='rg-form-card'>", unsafe_allow_html=True)
    with st.form("route_form", clear_on_submit=False):
        st.markdown(f"""
        <div class="route-lane" aria-hidden="true">
            <div class="route-lane-markings"></div>
            <div class="route-bus-wrap">
                <span class="route-smoke route-smoke-1"></span>
                <span class="route-smoke route-smoke-2"></span>
                <span class="route-smoke route-smoke-3"></span>
                <div class="route-bus-shell">
                    <span class="route-window route-window-1"></span>
                    <span class="route-window route-window-2"></span>
                    <span class="route-window route-window-3"></span>
                    <span class="route-headlight"></span>
                    <span class="route-brake route-brake-top"></span>
                    <span class="route-brake route-brake-bottom"></span>
                </div>
                <span class="route-wheel route-wheel-front"></span>
                <span class="route-wheel route-wheel-rear"></span>
                <img src="data:image/png;base64,{_logo_b64}" class="route-flag-logo" alt="RoutaGo" />
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2, gap="large")
        with col1:
            origin = st.text_input("Current Location", placeholder="e.g., SM City Cebu", key="origin_input")
        with col2:
            destination = st.text_input("Where to?", placeholder="e.g., Colon Street", key="dest_input")
        
        submitted = st.form_submit_button("Find Best Route", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        if not origin or not destination:
            st.warning("Please fill in both fields to plan your commute.")
        else:
            with st.spinner("Calculating the most efficient jeepney route..."):
                route_context = json.dumps(ROUTES, indent=2)
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": f"""You are RoutaGo, a Cebu jeepney route guide. Always respond in English.
Only use routes and stops from this database. NEVER invent stops or routes.
NO EMOJIS anywhere in your response.
User is a PASSENGER — NEVER say Turn left, Turn right, or Continue onto.

FARE: Base fare P15.00 for first 4km, then P1.80 per km after. Estimate based on number of stops.

ROUTE DATABASE:
{route_context}

CRITICAL OUTPUT RULE: Respond with a single valid JSON object only. No text before or after. No markdown fences. Pure raw JSON.

For route questions (do not include travel_time):
{{"type":"route","route_code":"CODE","route_name":"route name","origin":"origin","destination":"destination","boarding":"boarding spot + nearby landmark","steps":["Step 1 — go to boarding point at LANDMARK","Step 2 — board **CODE** (route name)","Step 3 — you will pass LANDMARK","...one step per stop between origin and destination in sequence order"],"fare":"P15.00","fare_note":"Standard fare (approx. Xkm, X stops)","dropoff":"Tell the driver \"Lugar lang!\" when you see LANDMARK. Tap a coin on the rail to signal stop.","tips":["copy each tip from the route tips array exactly as written"]}}

STEPS RULE: Use the sequence numbers in the stops array. Include one step per stop between origin and destination. Never skip stops.

If not found: {{"type":"text","message":"Sorry bai, I don't have that route yet!"}}"""
                        },
                        {"role": "user", "content": f"How do I commute from {origin} to {destination} by jeepney in Cebu?"}
                    ],
                    temperature=0.5,
                )
                result = response.choices[0].message.content
                formatted_result = format_response(result)
                
                # Save the planned route to history for the current session
                st.session_state.recent_routes.insert(0, {
                    "origin": origin,
                    "destination": destination,
                    "result": formatted_result,
                    "time": datetime.now().strftime("%I:%M %p")
                })
                # Maintain only the most recent 10 searches to keep UI clean
                st.session_state.recent_routes = st.session_state.recent_routes[:10]
                
                st.session_state.last_plan = {
                    "origin": origin,
                    "destination": destination,
                    "result": formatted_result,
                }

    # Always show the most recent plan result
    if st.session_state.last_plan:
        plan = st.session_state.last_plan
        st.markdown(f"<div class='rg-result'>{plan['result']}</div>", unsafe_allow_html=True)
        if st.button("View on Map", key="plan_view_map", icon=":material/location_on:"):
            with st.spinner("Locating places on map…"):
                cur_coords  = _forward_geocode(plan["origin"])
                dest_coords = _forward_geocode(plan["destination"])
            if cur_coords:
                st.session_state.current_loc = {
                    "lat": cur_coords[0], "lng": cur_coords[1], "address": plan["origin"]}
            if dest_coords:
                st.session_state.dest_loc = {
                    "lat": dest_coords[0], "lng": dest_coords[1], "address": plan["destination"]}
            st.session_state.pop("road_coords", None)
            st.switch_page("pages/3_Cebu_Map.py")

with tab2:
    if not st.session_state.recent_routes:
        st.info("No recent routes yet. Start planning to see your history here!")
    else:
        st.markdown("<div class='recent-container'>", unsafe_allow_html=True)
        for i, route in enumerate(st.session_state.recent_routes):
            with st.expander(f"{route['origin']} → {route['destination']} ({route['time']})"):
                st.markdown(f"<div class='rg-result' style='margin-top:0;'>{route['result']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)