import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os, json, sys, re
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# --- CUSTOM MODULES ---
# helpers module contains shared UI components and response formatting logic
from utils.helpers import load_css, render_sidebar, format_response, inject_dark_mode

load_dotenv()

st.set_page_config(page_title="Plan Route — RoutaGo", page_icon="🗺️", layout="wide", initial_sidebar_state="expanded")
load_css("assets/styles/main.css")
load_css("assets/styles/plan.css")
render_sidebar()
inject_dark_mode()

# Initialize session state for recent routes
if "recent_routes" not in st.session_state:
    st.session_state.recent_routes = []

with open("routes.json", "r", encoding="utf-8") as f:
    ROUTES = json.load(f)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.markdown("""
<div class="rg-page-header">
    <h1>Plan My Route</h1>
    <p>Plan your Cebu commute with clear, practical, stop-by-stop guidance.</p>
</div>
""", unsafe_allow_html=True)

# TABBED UI: separates the interactive planning tool from history
tab1, tab2 = st.tabs(["Plan Your Route", "Recent Routes"])

with tab1:
    # Card-style container for the route search form
    st.markdown("<div class='rg-form-card'>", unsafe_allow_html=True)
    with st.form("route_form", clear_on_submit=False):
        st.markdown("""
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
                
                st.markdown(f"<div class='rg-result'>{formatted_result}</div>", unsafe_allow_html=True)

with tab2:
    if not st.session_state.recent_routes:
        st.info("No recent routes yet. Start planning to see your history here!")
    else:
        st.markdown("<div class='recent-container'>", unsafe_allow_html=True)
        for i, route in enumerate(st.session_state.recent_routes):
            with st.expander(f"📍 {route['origin']} → {route['destination']} ({route['time']})"):
                st.markdown(f"<div class='rg-result' style='margin-top:0;'>{route['result']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)