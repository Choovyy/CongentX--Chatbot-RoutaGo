import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os, json, sys, re
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# --- ENHANCED ROUTE PLANNER ---
# Implemented a tabbed UI to separate the Planning Form from Recent History
# Added session-state based history tracking for the last 10 routes
# Integrated centralized format_response for professional jeepney code styling
from utils.helpers import load_css, render_sidebar, format_response

load_dotenv()

st.set_page_config(page_title="Plan Route — RoutaGo", page_icon="🗺️", layout="wide", initial_sidebar_state="expanded")
load_css("assets/styles/main.css")
load_css("assets/styles/plan.css")
render_sidebar()

# Initialize session state for recent routes
if "recent_routes" not in st.session_state:
    st.session_state.recent_routes = []

with open("routes.json", "r", encoding="utf-8") as f:
    ROUTES = json.load(f)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.markdown("""
<div class="rg-page-header">
    <h1>🗺️ Plan My Route</h1>
    <p>Professional Cebu jeepney navigation and route planning.</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 Plan Your Route", "🕒 Recent Routes"])

with tab1:
    st.markdown("<div class='rg-form-card'>", unsafe_allow_html=True)
    with st.form("route_form", clear_on_submit=False):
        # Smoking Jeepney Highway Animation
        st.markdown("""
        <div class="highway-bar">
            <div class="highway-line"></div>
            <div class="jeep-wrapper">
                <div class="smoke-emitter">
                    <span class="smoke"></span>
                    <span class="smoke"></span>
                    <span class="smoke"></span>
                </div>
                <div class="jeep-icon">🚌</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2, gap="large")
        with col1:
            origin = st.text_input("Current Location", placeholder="e.g., SM City Cebu", key="origin_input")
        with col2:
            destination = st.text_input("Where to?", placeholder="e.g., Colon Street", key="dest_input")
        
        submitted = st.form_submit_button("Find Best Route →", use_container_width=True)
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
Only use routes from this database. NEVER invent stops or routes.
User is a PASSENGER — NEVER say Turn left/right/Continue onto. Describe landmarks they SEE out the window.
Always include: bold jeepney CODE (e.g. **01K**), boarding spot, numbered landmark steps, drop-off cue with 'Lugar lang', fare (P13/4km then P3.25/km).
ROUTE DATABASE:\n{route_context}"""
                        },
                        {"role": "user", "content": f"How do I commute from {origin} to {destination} by jeepney in Cebu?"}
                    ],
                    temperature=0.5,
                )
                result = response.choices[0].message.content
                formatted_result = format_response(result)
                
                # Store in recent routes
                st.session_state.recent_routes.insert(0, {
                    "origin": origin,
                    "destination": destination,
                    "result": formatted_result,
                    "time": datetime.now().strftime("%I:%M %p")
                })
                # Keep only last 10
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

