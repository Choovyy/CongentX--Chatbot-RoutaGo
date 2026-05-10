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
<div class="rg-result" style="margin-top: 0; padding: 2rem;">
<div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
<span class="jeep-code" style="font-size: 1.5rem; padding: 5px 12px;">{selected_code}</span>
<h3 style="margin:0;">{route_data['name'].split('-', 1)[-1].strip()}</h3>
</div>
<p style="font-size: 0.95rem; line-height: 1.6; margin-bottom: 1.5rem;">{route_data.get('description', '')}</p>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; border-top: 1px solid rgba(128,128,128,0.1); padding-top: 1.5rem;">
<div>
<h4 style="color: #A78BFA; margin-bottom: 0.5rem; font-size: 1rem;">🚦 Terminals</h4>
<p style="margin: 0;"><strong>Origin:</strong> {origin_term}</p>
<p style="margin: 0;"><strong>Destination:</strong> {dest_term}</p>
</div>
<div>
<h4 style="color: #60A5FA; margin-bottom: 0.5rem; font-size: 1rem;">💳 Est. Fare</h4>
<p style="margin: 0;"><strong>Base:</strong> ₱{fare.get('base_fare', 13)}.00</p>
<p style="margin: 0; font-size: 0.8rem; color: #64748B;">{fare.get('note', '₱13 first 4km')}</p>
</div>
</div>
</div>
""", unsafe_allow_html=True)

        # Map Section with Fallback Link
        st.markdown(f"""
<div class="rg-result" style="margin-top: 1.5rem; padding: 0; overflow: hidden; height: 350px;">
<iframe
width="100%"
height="350"
frameborder="0"
style="border:0"
src="https://www.google.com/maps?q={origin_q}+to+{dest_q}&output=embed"
allowfullscreen>
</iframe>
</div>
<div style="margin-top: 10px; text-align: right;">
<a href="https://www.google.com/maps/dir/{origin_q}/{dest_q}" target="_blank" style="color: #60A5FA; font-size: 0.85rem; text-decoration: none;">↗ View full directions on Google Maps</a>
</div>
""", unsafe_allow_html=True)
