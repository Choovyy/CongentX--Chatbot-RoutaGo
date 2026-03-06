import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

st.set_page_config(page_title="Plan My Route – RoutaGo", page_icon="🗺️", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, header, footer { visibility: hidden; }
.main .block-container { padding-top: 2rem; max-width: 780px; }
.page-header h1 { color: #1B3A6B; font-size: 1.8rem; font-weight: 700; margin-bottom: 0; }
.page-header p { color: #6b7280; font-size: 0.9rem; margin-top: 4px; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #1B3A6B 0%, #142d54 100%); }
[data-testid="stSidebar"] * { color: #ffffff !important; }
div[data-testid="stForm"] {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}
.stTextInput input {
    border-radius: 10px !important;
    border: 1.5px solid #d1d5db !important;
    padding: 0.65rem 1rem !important;
    font-size: 0.95rem !important;
}
.stTextInput input:focus {
    border-color: #1B3A6B !important;
    box-shadow: 0 0 0 3px rgba(27,58,107,0.1) !important;
}
.stFormSubmitButton button {
    background: linear-gradient(135deg, #1B3A6B, #2563eb) !important;
    color: white !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.5rem !important;
    border: none !important;
    font-size: 0.95rem !important;
    transition: opacity 0.2s;
}
.stFormSubmitButton button:hover { opacity: 0.9; }
.result-box {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-left: 4px solid #1B3A6B;
    border-radius: 12px;
    padding: 1.5rem 1.8rem;
    margin-top: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 1.5rem 0;'>
        <div style='font-size:1.6rem; font-weight:700;'>🚌 RoutaGo</div>
        <div style='font-size:0.78rem; opacity:0.7; margin-top:2px;'>Cebu Jeepney Route Expert</div>
    </div>
    <hr style='border-color: rgba(255,255,255,0.15); margin-bottom:1rem;'/>
    """, unsafe_allow_html=True)
    st.page_link("app.py", label="💬  Chat Assistant")
    st.page_link("pages/1_Plan_My_Route.py", label="🗺️  Plan My Route")
    st.page_link("pages/2_Safety_Tips.py", label="🛡️  Safety Tips")
    st.page_link("pages/3_Saved_Routes.py", label="❤️  Saved Routes")

with open("routes.json", "r") as f:
    ROUTES = json.load(f)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.markdown("""
<div class='page-header'>
    <h1>🗺️ Plan My Route</h1>
    <p>Enter your starting point and destination to get jeepney directions.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

with st.form("route_form"):
    origin = st.text_input("📍 From", placeholder="e.g., SM City Cebu")
    destination = st.text_input("🏁 To", placeholder="e.g., Colon")
    submitted = st.form_submit_button("🔍 Find Route", use_container_width=True)

if submitted:
    if not origin or not destination:
        st.warning("Please fill in both fields, bai! 😊")
    else:
        with st.spinner("Finding your route..."):
            route_context = json.dumps(ROUTES, indent=2)
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are RoutaGo, a Cebu jeepney route guide. Always respond in English.
Only use the routes in this database. Do not invent stops or routes.
If the route is unknown, say so honestly.

The user is a PASSENGER riding a jeepney — NEVER use driving directions like "Turn left", "Turn right", or "Continue onto".
Describe what landmarks they will see out the window as they ride.

When giving directions always include:
1. Which jeepney CODE to ride and its name
2. Where exactly to board it (with a nearby landmark)
3. Numbered steps listing landmarks the user will SEE as they pass by
4. Which landmark to watch for when getting off, and to say 'Lugar lang' or tap the rail
5. Fare estimate (₱13 first 4km, ₱3.25 per km after)

ROUTE DATABASE:
{route_context}"""
                    },
                    {
                        "role": "user",
                        "content": f"How do I get from {origin} to {destination} via Cebu jeepney?"
                    }
                ],
                temperature=0.5,
            )
            result = response.choices[0].message.content
            st.markdown(f"<div class='result-box'>{result}</div>", unsafe_allow_html=True)
