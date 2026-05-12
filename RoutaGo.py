import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os, json, sys, base64, re, urllib.parse
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.helpers import load_css, render_sidebar, format_response, page_loader, parse_agent_response
from utils.agent import run_agent

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


def parse_route_query(text: str):
    text = text.strip().lower()
    patterns = [
        r'from\s+(.+?)\s+to\s+(.+)',
        r'(.+?)\s+to\s+(.+)',
        r'gikan sa\s+(.+?)\s+padulong\s+(.+)',
        r'(.+?)\s+padulong\s+(.+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            origin = match.group(1).strip(' .?')
            destination = match.group(2).strip(' .?')
            if origin and destination:
                return origin, destination

    return None, None


def build_route_map_html(user_prompt: str):
    origin, destination = parse_route_query(user_prompt)
    if not origin or not destination:
        return ""

    origin_q = urllib.parse.quote(f"{origin}, Cebu City")
    destination_q = urllib.parse.quote(f"{destination}, Cebu City")
    embed_url = f"https://www.google.com/maps?q={origin_q}+to+{destination_q}&output=embed"
    map_url = f"https://www.google.com/maps/dir/{origin_q}/{destination_q}"

    return f"""
<div style=\"margin-top: 1rem; border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 8px 24px rgba(0,0,0,0.15);\">
    <iframe width=\"100%\" height=\"320\" frameborder=\"0\" style=\"border:0; min-height:320px;\" src=\"{embed_url}\"></iframe>
</div>
<div style=\"margin-top: 0.75rem; text-align: right;\">
    <a href=\"{map_url}\" target=\"_blank\" style=\"color: #60A5FA; font-size: 0.9rem; text-decoration: none;\">↗ Open full directions on Google Maps</a>
</div>
"""

load_css("assets/styles/main.css")
load_css("assets/styles/chat.css")
load_css("assets/styles/cards.css")
render_sidebar()

with open("routes.json", "r", encoding="utf-8") as f:
    ROUTES = json.load(f)

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
        <p>Tell me where you're starting and where you need to go. I'll give you clear, landmark-based jeepney directions with fares and routes.</p>
        <div class="rg-chips">
            <span class="rg-chip">💡 Parkmall to CIT-U</span>
            <span class="rg-chip">🗺️ SM City to Colon</span>
            <span class="rg-chip">🚌 Student discount routes</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🚌" if msg["role"] == "assistant" else "🧑"):
        if msg["role"] == "assistant":
            st.markdown(format_response(msg["content"]), unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

if prompt := st.chat_input("🚌 Ask about jeepney routes... (e.g., 'Parkmall to CIT-U', 'SM City to Colon')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🚌"):
        with st.spinner("🤖 RoutaGo is thinking..."):
            try:
                # Run the agent loop - it handles tool calling internally
                reply = run_agent(
                    user_message=prompt,
                    routes=ROUTES,
                    client=client,
                    max_steps=3
                )

                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.markdown(format_response(reply), unsafe_allow_html=True)

                map_html = build_route_map_html(prompt)
                if map_html:
                    st.markdown(map_html, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")