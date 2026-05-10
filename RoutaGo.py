import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os, json, sys, base64, re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.helpers import load_css, render_sidebar, format_response, calculate_exact_route, page_loader

load_dotenv()

from PIL import Image

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
2. If the JSON says "type": "transfer", explain that they need to take TWO jeepneys. 
   - Tell them to take the first jeepney (**first_jeep**) until **transfer_at**.
   - Then tell them to transfer to the second jeepney (**second_jeep**) to reach their destination.
3. DO NOT add any jeepney codes, stops, or landmarks that are not explicitly written in the JSON.
4. Start with a friendly Cebuano greeting and acknowledge where they want to go.
5. Use bold text for the jeepney codes (e.g., **01K**).
6. List the 'stops_passed' (or leg stops) exactly as they appear in the data.
7. When telling the user to alight or transfer, tell them to say "Lugar lang!".
8. Using your internal knowledge of Cebu geography, ESTIMATE the driving distance in kilometers between the user's origin and destination.
9. Calculate the fare using this strict formula: ₱13.00 for the first 4km, plus ₱1.80 for every succeeding kilometer. State BOTH the estimated distance and the exact calculated fare amount directly in your response! (For transfers, remember to calculate the total fare for BOTH rides)."""

api_key = os.getenv("GROQ_API_KEY")

if not api_key or api_key == "your_actual_api_key_here":
    st.error("🔑 **Groq API Key Missing!** Please add your `GROQ_API_KEY` to the `.env` file.")
    st.stop()

client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

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

# Chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🚌" if msg["role"] == "assistant" else "🧑"):
        if msg["role"] == "assistant":
            st.markdown(format_response(msg["content"]), unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

# Input
# Input
if prompt := st.chat_input("Ask about jeepney routes in Cebu... (e.g., 'Parkmall to CIT-U')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🚌"):
        with st.spinner("Calculating route..."):
            
            lower_prompt = prompt.lower()
            
            clean_prompt = lower_prompt.replace("how do i go ", "").replace("how to go ", "").replace("commute ", "").replace("route for ", "")
            
            match = re.search(r"from\s+(.+?)\s+to\s+(.+)", clean_prompt)
            
            if match:
                origin = match.group(1).strip()
                destination = match.group(2).replace("?", "").strip()
            elif " to " in clean_prompt:
                # 3. THE FIX: If no "from", take the ENTIRE left side of " to " as the origin!
                parts = clean_prompt.rsplit(" to ", 1)
                origin = parts[0].strip()
                destination = parts[1].replace("?", "").strip()
            else:
                origin, destination = None, None

            if origin and destination:
                exact_route = calculate_exact_route(origin, destination, ROUTES)
                
                # DEBUG PRINT: Verify what Python actually extracted!
                print(f"\n--- EXTRACTED: Origin='{origin}', Dest='{destination}' ---")
                print(json.dumps(exact_route, indent=2))
                print("-----------------------------------------------------------\n")
            else:
                exact_route = {"type": "none", "message": "General query or unformatted route request."}

            # FEED ONLY THE MATH RESULT TO THE LLM
            system_prompt = build_system_prompt(exact_route)

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                temperature=0.0,
            )
            reply = response.choices[0].message.content

            if exact_route.get("type") != "none" and origin and destination:
                safe_origin = origin.replace(" ", "+")
                safe_dest = destination.replace(" ", "+")
                map_url = f"https://www.google.com/maps/dir/?api=1&origin={safe_origin},+Cebu&destination={safe_dest},+Cebu&travelmode=transit"
                embed_url = f"https://maps.google.com/maps?saddr={safe_origin},+Cebu&daddr={safe_dest},+Cebu&output=embed"
                
                reply += f"\n\n[🗺️ **Open Full Map**]({map_url})"
                reply += f"""
<div style="margin-top: 1.5rem; border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 8px 24px rgba(0,0,0,0.3);">
    <iframe width="100%" height="320" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="{embed_url}"></iframe>
</div>
"""

            formatted_reply = format_response(reply)
            st.markdown(formatted_reply, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": reply})