import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os, json, sys, base64, re, urllib.parse
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.helpers import load_css, render_sidebar, format_response, calculate_exact_route, page_loader

load_dotenv()

try:
    logo_img = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png"))
except Exception:
    logo_img = "🚌"

st.set_page_config(
    page_title="RoutaGo",
    page_icon=logo_img,
    layout="wide",
    initial_sidebar_state="expanded"
)

page_loader()

def get_logo_b64(path="assets/logo.png"):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return ""

logo_b64 = get_logo_b64()

load_css("assets/styles/main.css")
load_css("assets/styles/chat.css")
render_sidebar()

with open("routes.json", "r", encoding="utf-8") as f:
    ROUTES = json.load(f)

def build_system_prompt(route_data: dict) -> str:
    return f"""You are RoutaGo, a friendly, helpful, and highly accurate Cebuano jeepney guide.
Your personality is warm and local. You naturally use light Cebuano expressions like "Maayong adlaw bai!", "amping", and "Lugar lang!".

However, when giving route directions, you are STRICTLY BOUND by the backend JSON data provided below. 
You cannot calculate routes yourself. You must translate the JSON into a friendly guide.

BACKEND JSON DATA:
{json.dumps(route_data, indent=2)}

STRICT RULES:
1. If the JSON says "type": "none", reply EXACTLY with: "Sorry bai, I don't have a route covering that trip yet."
2. If the JSON says "type": "full_route", explain the WHOLE route of this jeepney. Mention its terminals and major stops.
3. If the JSON says "type": "transfer", explain that they need to take TWO jeepneys. 
   - Tell them to take the first jeepney (**first_jeep**) until **transfer_at**.
   - Then tell them to transfer to the second jeepney (**second_jeep**) to reach their destination.
4. DO NOT add any jeepney codes, stops, or landmarks that are not explicitly written in the JSON.
5. Start with a friendly Cebuano greeting and acknowledge where they want to go.
6. Use bold text for the jeepney codes (e.g., **01K**).
7. List the 'stops_passed' (or leg stops) exactly as they appear in the data.
8. When telling the user to alight or transfer, tell them to say "Lugar lang!".
9. Using your internal knowledge of Cebu geography, ESTIMATE the driving distance in kilometers.
10. Calculate the fare using this strict formula: ₱13.00 for the first 4km, plus ₱1.80 for every succeeding kilometer. State BOTH the estimated distance and the exact calculated fare amount directly in your response!"""

api_key = os.getenv("GROQ_API_KEY")

if not api_key or api_key == "your_actual_api_key_here":
    st.error("🔑 **Groq API Key Missing!** Please add your `GROQ_API_KEY` to the `.env` file.")
    st.stop()

client = Groq(api_key=api_key)

# Header
st.markdown(f"""
<div class="rg-page-header">
    <img src="data:image/png;base64,{logo_b64}" class="rg-header-logo" style="width: 50px; height: 50px;" />
    <div>
        <h1><span class="rg-gradient-text">RoutaGo</span></h1>
        <p>Ask me anything about getting around Cebu by jeepney.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Welcome state
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.markdown("""
    <div class="rg-welcome">
        <span class="rg-welcome-logo">🚌</span>
        <h2>How can I help you commute?</h2>
        <p>Tell me where you're starting and where you need to go. I'll give you clear, landmark-based jeepney directions.</p>
        <div class="rg-chips">
            <span class="rg-chip">💡 from Parkmall to CIT-U</span>
            <span class="rg-chip">🗺️ from SM City to Colon</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🚌" if msg["role"] == "assistant" else "🧑"):
        if msg["role"] == "assistant":
            st.markdown(format_response(msg["content"]), unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

if prompt := st.chat_input("Ask about jeepney routes in Cebu... (e.g., 'Parkmall to CIT-U')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🚌"):
        with st.spinner("Searching..."):
            lower_prompt = prompt.lower()
            
            # Check for direct Jeepney Code (e.g., "01K")
            code_match = re.search(r"\b(\d{1,2}[A-Z])\b", prompt.upper())
            
            origin, destination, exact_route = None, None, {"type": "none"}
            
            if code_match:
                code = code_match.group(1)
                if code in ROUTES:
                    route_data = ROUTES[code]
                    origin = route_data['terminals'][0]
                    destination = route_data['terminals'][1]
                    exact_route = {
                        "type": "full_route",
                        "jeepney_code": code,
                        "description": route_data.get('description', ''),
                        "terminals": route_data['terminals'],
                        "stops_passed": [s['name'] for s in route_data.get('stops', [])]
                    }
            
            # If not a direct code, try from/to logic
            if exact_route["type"] == "none":
                clean_prompt = lower_prompt.replace("how do i go ", "").replace("how to go ", "").replace("commute ", "").replace("route for ", "")
                match = re.search(r"from\s+(.+?)\s+to\s+(.+)", clean_prompt)
                
                if match:
                    origin = match.group(1).strip()
                    destination = match.group(2).replace("?", "").strip()
                elif " to " in clean_prompt:
                    parts = clean_prompt.rsplit(" to ", 1)
                    origin = parts[0].strip()
                    destination = parts[1].replace("?", "").strip()
                
                if origin and destination:
                    exact_route = calculate_exact_route(origin, destination, ROUTES)

            system_prompt = build_system_prompt(exact_route)
            
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                    temperature=0.0,
                )
                reply = response.choices[0].message.content
                
                if exact_route.get("type") != "none" and origin and destination:
                    o_q = urllib.parse.quote(f"{origin}, Cebu City")
                    d_q = urllib.parse.quote(f"{destination}, Cebu City")
                    map_url = f"https://www.google.com/maps/dir/?api=1&origin={o_q}&destination={d_q}"
                    embed_url = f"https://www.google.com/maps?saddr={o_q}&daddr={d_q}&output=embed"
                    
                    reply += f"\n\n[🗺️ **Open Full Directions**]({map_url})"
                    reply += f"""
<div style="margin-top: 1.5rem; border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 8px 24px rgba(0,0,0,0.3);">
    <iframe width="100%" height="320" frameborder="0" scrolling="no" src="{embed_url}"></iframe>
</div>
"""
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.markdown(format_response(reply), unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")