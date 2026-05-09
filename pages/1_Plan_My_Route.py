import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os, json, sys
from datetime import datetime

# Add root to path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# IMPORT THE NEW CALCULATOR HERE
from utils.helpers import load_css, render_sidebar, format_response, calculate_exact_route

load_dotenv()

st.set_page_config(page_title="Plan Route — RoutaGo", page_icon="🗺️", layout="wide", initial_sidebar_state="expanded")
load_css("assets/styles/main.css")
load_css("assets/styles/plan.css")
render_sidebar()

if "recent_routes" not in st.session_state:
    st.session_state.recent_routes = []

# Load the database once
with open("routes.json", "r", encoding="utf-8") as f:
    ROUTES = json.load(f)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# STRIPPED DOWN PROMPT: The LLM is now just a friendly formatter
# ... (Keep your imports, including calculate_exact_route from utils.helpers)

def build_system_prompt(route_data: dict) -> str:
    return f"""You are RoutaGo, a friendly Cebu jeepney guide.
The backend system has mathematically calculated the ONLY correct route. 
You MUST format this EXACT JSON data into a friendly response. 
DO NOT invent routes. DO NOT add stops not listed in the JSON. DO NOT look at any other database.

SYSTEM ROUTE DATA:
{json.dumps(route_data, indent=2)}

If the type is "none", just say: "Sorry bai, I don't have a route covering that trip yet."

Otherwise, format it nicely:
1. Mention the Jeepney Codes in **bold**.
2. List the "stops_passed" EXACTLY as they appear in the JSON. Do not add or remove any.
3. Mention the standard fare (₱13 first 4km).
Use light Cebuano flavor (e.g., "Lugar lang!")."""

# ... (Scroll down to your chat input logic)

if prompt := st.chat_input("Ask about jeepney routes in Cebu..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🚌"):
        with st.spinner(""):
            
            # Simple keyword extraction to detect "A to B" queries
            lower_prompt = prompt.lower()
            if " to " in lower_prompt:
                parts = lower_prompt.split(" to ")
                origin = parts[0].split()[-1] if len(parts[0].split()) > 0 else parts[0]
                destination = parts[1]
                
                # PYTHON DOES THE MATH
                exact_route = calculate_exact_route(origin, destination, ROUTES)
            else:
                exact_route = {"type": "none", "message": "General query"}

            # FEED ONLY THE MATH RESULT TO THE LLM
            system_prompt = build_system_prompt(exact_route)

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
                temperature=0.1, # Extremely low temperature prevents hallucination
            )
            reply = response.choices[0].message.content
            formatted_reply = format_response(reply)
            st.markdown(formatted_reply, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    
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
            with st.spinner("Calculating route mathematically..."):
                
                # 1. PYTHON DOES THE MATH DETERMINISTICALLY
                exact_route = calculate_exact_route(origin, destination, ROUTES)
                
                # 2. LLM JUST FORMATS THE PYTHON RESULT
                system_prompt = build_plan_prompt(exact_route)

                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"How do I go from {origin} to {destination}?"}
                    ],
                    temperature=0.1, # Extremely low temp so it does not guess or hallucinate
                )
                
                result = response.choices[0].message.content
                formatted_result = format_response(result)

                st.session_state.recent_routes.insert(0, {
                    "origin": origin,
                    "destination": destination,
                    "result": formatted_result,
                    "time": datetime.now().strftime("%I:%M %p")
                })
                st.session_state.recent_routes = st.session_state.recent_routes[:10]

                st.markdown(f"<div class='rg-result'>{formatted_result}</div>", unsafe_allow_html=True)

with tab2:
    if not st.session_state.recent_routes:
        st.info("No recent routes yet. Start planning to see your history here!")
    else:
        st.markdown("<div class='recent-container'>", unsafe_allow_html=True)
        for route in st.session_state.recent_routes:
            with st.expander(f"📍 {route['origin']} → {route['destination']} ({route['time']})"):
                st.markdown(f"<div class='rg-result' style='margin-top:0;'>{route['result']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)