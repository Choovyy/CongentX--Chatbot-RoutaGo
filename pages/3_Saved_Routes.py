import streamlit as st
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import load_css, render_sidebar, inject_dark_mode

st.set_page_config(page_title="Saved Routes — RoutaGo", page_icon="❤️", layout="wide", initial_sidebar_state="expanded")
load_css("assets/styles/main.css")
load_css("assets/styles/saved.css")
render_sidebar()
inject_dark_mode()

if "saved_routes" not in st.session_state:
    st.session_state.saved_routes = []

st.markdown("""
<div class="rg-page-header">
    <h1>❤️ Saved Routes</h1>
    <p>Your frequently used jeepney routes for quick access.</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.saved_routes:
    st.markdown("""
    <div class="rg-empty">
        <div class="rg-empty-icon">🤍</div>
        <h3>No saved routes yet</h3>
        <p>Find a route using Chat or Plan My Route, then save it here for quick access on your next commute.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for i, route in enumerate(st.session_state.saved_routes):
        col1, col2 = st.columns([9, 1])
        with col1:
            st.markdown(f"""
            <div class="rg-route-card">
                <h4>📍 {route['from']} → {route['to']}</h4>
                <p>{route.get('details', 'Saved jeepney route')}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{i}"):
                st.session_state.saved_routes.pop(i)
                st.rerun()

st.markdown("""
<div class="rg-howto">
    <h4>How to save routes</h4>
    <ol>
        <li>Find a route via <strong>Chat</strong> or <strong>Plan My Route</strong></li>
        <li>Click the ❤️ icon on the result</li>
        <li>It appears here instantly for next time</li>
    </ol>
</div>
""", unsafe_allow_html=True)
