import streamlit as st
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import load_css, render_sidebar

st.set_page_config(page_title="Safety Tips — RoutaGo", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")
load_css("assets/styles/main.css")
load_css("assets/styles/safety.css")
render_sidebar()

st.markdown("""
<div class="rg-page-header">
    <h1>🛡️ Safety Tips</h1>
    <p>Guidelines for a safe and comfortable jeepney ride in Cebu.</p>
</div>
""", unsafe_allow_html=True)

tips = [
    ("👜", "Secure Your Valuables", "Hold your bag in front of you. Never display expensive phones, jewelry, or large amounts of cash inside a jeepney or at terminals."),
    ("💵", "Prepare Exact Fare", "Have small bills or coins ready before boarding. Pass your fare forward to the driver — this is standard practice in Cebu jeepneys."),
    ("📣", "Confirm Route Before Boarding", "Ask the driver 'Mo-abot ba ka sa [place]?' Use a landmark, not just a street name."),
    ("📍", "Know Your Drop-Off Signal", "Watch for your landmark. Say \"Lugar lang!\" loudly or tap a coin on the metal handrail to signal your stop."),
    ("⚠️", "Stay Alert During Peak Hours", "Be extra careful with belongings 7–9AM and 5–7PM on weekdays, and in busy areas like Carbon, Colon, and Fuente Osmeña."),
    ("🌧️", "Prepare for Sudden Rain", "Cebu rain is fast and heavy. Always carry a compact umbrella and locate covered waiting spots before your stop."),
    ("🔋", "Keep Your Phone Charged", "A charged phone lets you use RoutaGo, stay in touch, and check your location. Bring a powerbank for long commutes."),
    ("🕐", "Avoid Peak Congestion", "Cebu traffic is worst 7–9AM and 5–7PM weekdays. Commuting outside these windows saves significant time."),
]

for icon, title, desc in tips:
    st.markdown(f"""
    <div class="tip-card">
        <div class="tip-icon">{icon}</div>
        <div class="tip-body">
            <h4>{title}</h4>
            <p>{desc}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
