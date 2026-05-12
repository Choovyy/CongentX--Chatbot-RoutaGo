import streamlit as st
import os, sys, json, urllib.parse
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import load_css, render_sidebar, page_loader

try:
    logo_img = Image.open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo.png"))
except Exception:
    logo_img = "🧭"

st.set_page_config(page_title="Route Explorer — RoutaGo", page_icon=logo_img, layout="wide", initial_sidebar_state="expanded")
page_loader()
load_css("assets/styles/main.css")
load_css("assets/styles/plan.css")
render_sidebar()

st.markdown("""
<div class="rg-page-header">
    <h1>🧭 <span class="rg-gradient-text">Route Explorer</span></h1>
    <p>Browse the complete directory of Cebu Jeepney routes, terminals, and designated stops.</p>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def load_routes():
    with open("routes.json", "r", encoding="utf-8") as f:
        return json.load(f)

ROUTES = load_routes()

col1, col2 = st.columns([1, 2])
with col1:
    route_keys = list(ROUTES.keys())
    selected_code = st.selectbox("Search Jeepney Code", route_keys)

if selected_code:
    with st.spinner(f"Loading details for {selected_code}..."):
        route_data = ROUTES[selected_code]
        origin_term = route_data['terminals'][0]
        dest_term = route_data['terminals'][1]
        fare = route_data.get('fare_estimate', {})
        
        # Build Safe Search Queries
        origin_q = urllib.parse.quote(f"{origin_term}, Cebu City")
        dest_q = urllib.parse.quote(f"{dest_term}, Cebu City")
        
        with col2:
            st.markdown(f"""
<div class="plan-result-card">
    <div style="display: flex; flex-wrap: wrap; gap: 1.5rem; align-items: flex-start;">
        <div style="flex: 1 1 320px; min-width: 320px;">
            <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem;">
                <span class="jeep-code" style="font-size: 1.4rem; padding: 6px 14px;">{selected_code}</span>
                <h3 style="margin:0; font-size: 1.3rem;">{route_data['name'].split('-', 1)[-1].strip()}</h3>
            </div>
            <p style="font-size: 0.95rem; line-height: 1.75; margin-bottom: 1.4rem;">{route_data.get('description', '')}</p>
        </div>
        <div style="flex: 0 0 280px; min-width: 240px; display: grid; gap: 1rem;">
            <div>
                <h4 style="color: #A78BFA; margin-bottom: 0.6rem; font-size: 1rem;">🚦 Terminals</h4>
                <p style="margin: 0;"><strong>Origin:</strong> {origin_term}</p>
                <p style="margin: 0;"><strong>Destination:</strong> {dest_term}</p>
            </div>
            <div>
                <h4 style="color: #60A5FA; margin-bottom: 0.6rem; font-size: 1rem;">💳 Est. Fare</h4>
                <p style="margin: 0;"><strong>Base:</strong> ₱{fare.get('base_fare', 13)}.00</p>
                <p style="margin: 0; font-size: 0.88rem; color: #94A3B8;">{fare.get('note', '₱13 first 4km')}</p>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

        # Map Section with Fallback Link
        st.markdown(f"""
<div class="plan-map-card">
    <iframe
        src="https://www.google.com/maps?q={origin_q}+to+{dest_q}&output=embed"
        allowfullscreen>
    </iframe>
    <div class="plan-map-actions">
        <a href="https://www.google.com/maps/dir/{origin_q}/{dest_q}" target="_blank">↗ View full directions on Google Maps</a>
    </div>
</div>
""", unsafe_allow_html=True)
