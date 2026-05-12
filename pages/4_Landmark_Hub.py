import streamlit as st
import os, sys, json
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import load_css, render_sidebar, page_loader

try:
    logo_img = Image.open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo.png"))
except Exception:
    logo_img = "🏢"

st.set_page_config(page_title="Landmark Hub — RoutaGo", page_icon=logo_img, layout="wide", initial_sidebar_state="expanded")
page_loader()
load_css("assets/styles/main.css")
load_css("assets/styles/plan.css")
render_sidebar()

st.markdown("""
<div class="rg-page-header">
    <h1>🏢 <span class="rg-gradient-text">Landmark Hub</span></h1>
    <p>Select a popular Cebu destination to instantly see every jeepney route that passes through it.</p>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def load_landmark_data():
    with open("routes.json", "r", encoding="utf-8") as f:
        routes = json.load(f)
        
    landmarks = {}
    for code, data in routes.items():
        for stop in data.get('stops', []):
            name = stop['name']
            if name not in landmarks:
                landmarks[name] = []
            if code not in landmarks[name]:
                landmarks[name].append(code)
                
    sorted_landmarks = dict(sorted(landmarks.items()))
    return routes, sorted_landmarks

routes, landmarks = load_landmark_data()

selected_landmark = st.selectbox("Search for a Destination, Mall, or Street", list(landmarks.keys()))

if selected_landmark:
    with st.spinner(f"Finding jeepneys for {selected_landmark}..."):
        passing_jeeps = landmarks[selected_landmark]
        
        st.markdown(f"""
<div style="margin-top: 2rem; margin-bottom: 1.5rem;">
<h3 style="margin: 0; font-weight: 600;">
Found <span style="color: #A78BFA; font-weight: 800;">{len(passing_jeeps)}</span> jeepney{'s' if len(passing_jeeps)>1 else ''} passing through <span style="color: #60A5FA;">{selected_landmark}</span>
</h3>
</div>
""", unsafe_allow_html=True)
        
        cols = st.columns(2)
        for i, code in enumerate(passing_jeeps):
            route_name = routes[code]['name'].split('-', 1)[-1].strip()
            with cols[i % 2]:
                st.markdown(f"""
<div class="rg-result" style="margin-top: 0; margin-bottom: 1rem; padding: 1.5rem;">
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
<span class="jeep-code" style="font-size: 1.1rem;">{code}</span>
</div>
<p style="margin: 0; font-size: 0.95rem; font-weight: 500;">{route_name}</p>
<p style="margin: 8px 0 0 0; color: #64748B; font-size: 0.8rem;">
Origin: {routes[code]['terminals'][0]}<br>
Destination: {routes[code]['terminals'][1]}
</p>
</div>
""", unsafe_allow_html=True)
