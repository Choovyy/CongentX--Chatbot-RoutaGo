import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os, json, sys, urllib.parse
from datetime import datetime

# Add root to path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import load_css, render_sidebar, format_response, calculate_exact_route, page_loader

load_dotenv()

from PIL import Image

try:
    logo_img = Image.open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo.png"))
except Exception:
    logo_img = "🗺️"

if "recent_routes" not in st.session_state:
    st.session_state.recent_routes = []

st.set_page_config(page_title="Plan Route — RoutaGo", page_icon=logo_img, layout="wide", initial_sidebar_state="expanded")
page_loader()
load_css("assets/styles/main.css")
load_css("assets/styles/plan.css")
render_sidebar()

if "recent_routes" not in st.session_state:
    st.session_state.recent_routes = []

# Load the database once
with open("routes.json", "r", encoding="utf-8") as f:
    ROUTES = json.load(f)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# THE FUNCTION DEFINITION
def build_plan_prompt(route_data: dict) -> str:
    return f"""You are RoutaGo, a friendly Cebu jeepney guide.
The backend system has mathematically calculated the ONLY correct route. 
You MUST format this EXACT JSON data into a friendly response. 

SYSTEM ROUTE DATA:
{json.dumps(route_data, indent=2)}

STRICT RULES:
1. If the JSON says "type": "none", reply EXACTLY with: "Sorry bai, I don't have a route covering that trip yet."
2. If the JSON says "type": "transfer", explain that they need to take TWO jeepneys. 
   - Tell them to take the first jeepney (**first_jeep**) until **transfer_at**.
   - Then tell them to transfer to the second jeepney (**second_jeep**) to reach their destination.
   - For transfers, PROVIDE A FARE BREAKDOWN (e.g., "Ride 1: ₱13.00, Ride 2: ₱13.00, Total: ₱26.00").
3. Mention the Jeepney Codes in **bold**.
4. List the stops EXACTLY as they appear in the JSON.
5. Using your internal knowledge of Cebu geography, ESTIMATE the driving distance in kilometers between the origin and destination.
6. Calculate the fare using this strict formula: ₱13.00 for the first 4km, plus ₱1.80 for every succeeding kilometer. State BOTH the estimated distance and the exact calculated fare amount directly in your response! (For transfers, remember to calculate the total fare for BOTH rides).
7. FORMAT YOUR RESPONSE CLEARLY:
   - Start with a friendly greeting and route explanation
   - **Distance:** Show the estimated distance on a separate line
   - **Fare:** Show the calculated fare on a separate line  
   - **Route:** Show the jeepney codes and transfer info
   - **Stops:** List the stops clearly
   - End with helpful tips
Use light Cebuano flavor (e.g., "Lugar lang!")."""

# UI Header
st.markdown("""
<div class="rg-page-header">
    <h1>🗺️ <span class="rg-gradient-text">Plan My Route</span></h1>
    <p>Professional Cebu jeepney navigation and route planning.</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 Plan Your Route", "🕒 Recent Routes"])

with tab1:
    st.markdown("<div class='rg-form-card'>", unsafe_allow_html=True)
    with st.form("route_form", clear_on_submit=False):
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
            origin = st.text_input("Current Location", placeholder="e.g., Parkmall", key="origin_input")
        with col2:
            destination = st.text_input("Where to?", placeholder="e.g., CIT-U", key="dest_input")

        submitted = st.form_submit_button("Find Best Route →", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        if not origin or not destination:
            st.warning("Please fill in both fields to plan your commute.")
        else:
            # Clean up entities
            def clean_entity(text):
                if not text: return text
                import re
                text = re.sub(r'^(gikan|sa|from|to|padulong|padung|adto)\b\s*', '', text, flags=re.IGNORECASE)
                text = re.sub(r'\s*\b(sa|to|padulong|padung|adto)\b$', '', text, flags=re.IGNORECASE)
                text = re.sub(r'\bcit-u\b', 'citu', text, flags=re.IGNORECASE)
                return text.strip()

            origin = clean_entity(origin)
            destination = clean_entity(destination)

            with st.spinner("Calculating route mathematically..."):
                
                # 1. PYTHON DOES THE MATH
                exact_route = calculate_exact_route(origin, destination, ROUTES)
                
                # 2. LLM JUST FORMATS THE PYTHON RESULT
                system_prompt = build_plan_prompt(exact_route)

                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"How do I go from {origin} to {destination}?"}
                    ],
                    temperature=0.1,
                )
                
                result = response.choices[0].message.content or ""

                map_html = ""
                if exact_route.get("type") != "none" and origin and destination and origin.lower() != "none" and destination.lower() != "none":
                    o_q = urllib.parse.quote(f"{origin}, Cebu City")
                    d_q = urllib.parse.quote(f"{destination}, Cebu City")
                    map_url = f"https://www.google.com/maps/dir/?api=1&origin={o_q}&destination={d_q}"
                    embed_url = f"https://www.google.com/maps?q={o_q}+to+{d_q}&output=embed"
                    
                    result += f"\n\n[🗺️ **Open Full Map**]({map_url})"
                    map_html = f"""
<div class="plan-map-card">
    <iframe width="100%" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="{embed_url}"></iframe>
    <div class="plan-map-actions">
        <a href="https://www.google.com/maps/dir/{o_q}/{d_q}" target="_blank">↗ Open full directions on Google Maps</a>
    </div>
</div>
"""

                formatted_result = format_response(result)

                # Store in history
                st.session_state.recent_routes.insert(0, {
                    "origin": origin,
                    "destination": destination,
                    "result": formatted_result,
                    "time": datetime.now().strftime("%I:%M %p")
                })
                st.session_state.recent_routes = st.session_state.recent_routes[:10]

                st.markdown(formatted_result, unsafe_allow_html=True)
                if map_html:
                    st.markdown(map_html, unsafe_allow_html=True)

with tab2:
    if not st.session_state.recent_routes:
        st.info("No recent routes yet. Start planning to see your history here!")
    else:
        st.markdown("<div class='recent-container'>", unsafe_allow_html=True)
        for route in st.session_state.recent_routes:
            with st.expander(f"📍 {route['origin']} → {route['destination']} ({route['time']})"):
                st.markdown(f"<div class='rg-result' style='margin-top:0;'>{route['result']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)