import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os, json, sys, base64
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.helpers import load_css, render_sidebar, format_response, page_loader
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

load_css("assets/styles/main.css")
load_css("assets/styles/chat.css")
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
        with st.spinner("🤖 Agent is thinking..."):
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
            except Exception as e:
                st.error(f"Error: {e}")