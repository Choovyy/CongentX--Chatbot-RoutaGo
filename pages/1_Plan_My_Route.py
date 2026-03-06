import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os, json, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import load_css, render_sidebar

load_dotenv()

st.set_page_config(page_title="Plan Route — RoutaGo", page_icon="🗺️", layout="wide", initial_sidebar_state="expanded")
load_css("assets/styles/main.css")
load_css("assets/styles/plan.css")
render_sidebar()

with open("routes.json", "r", encoding="utf-8") as f:
    ROUTES = json.load(f)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.markdown("""
<div class="rg-page-header">
    <h1>🗺️ Plan My Route</h1>
    <p>Enter your start and destination for step-by-step jeepney directions.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='rg-form-card'>", unsafe_allow_html=True)
with st.form("route_form"):
    col1, col2 = st.columns(2, gap="large")
    with col1:
        origin = st.text_input("From", placeholder="e.g., SM City Cebu")
    with col2:
        destination = st.text_input("To", placeholder="e.g., Colon")
    submitted = st.form_submit_button("Find Route →", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

if submitted:
    if not origin or not destination:
        st.warning("Please fill in both fields.")
    else:
        with st.spinner("Finding your route..."):
            route_context = json.dumps(ROUTES, indent=2)
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are RoutaGo, a Cebu jeepney route guide. Always respond in English.
Only use routes from this database. NEVER invent stops or routes.
User is a PASSENGER — NEVER say Turn left/right/Continue onto. Describe landmarks they SEE out the window.
Always include: bold jeepney CODE, boarding spot, numbered landmark steps, drop-off cue with Lugar lang, fare (P13/4km then P3.25/km).
ROUTE DATABASE:\n{route_context}"""
                    },
                    {"role": "user", "content": f"How do I commute from {origin} to {destination} by jeepney in Cebu?"}
                ],
                temperature=0.5,
            )
            result = response.choices[0].message.content
            st.markdown(f"<div class='rg-result'>{result}</div>", unsafe_allow_html=True)
