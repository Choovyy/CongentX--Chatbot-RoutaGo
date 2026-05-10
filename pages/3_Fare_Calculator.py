import streamlit as st
import os, sys
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import load_css, render_sidebar, page_loader

from PIL import Image

try:
    logo_img = Image.open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo.png"))
except Exception:
    logo_img = "💳"

st.set_page_config(page_title="Fare Calculator — RoutaGo", page_icon=logo_img, layout="wide", initial_sidebar_state="expanded")
page_loader()
load_css("assets/styles/main.css")
load_css("assets/styles/plan.css")
render_sidebar()

st.markdown("""
<div class="rg-page-header">
    <h1>💳 <span class="rg-gradient-text">Jeepney Fare Calculator</span></h1>
    <p>Dynamically estimate your travel fare based on standard LTFRB rates and discounts.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="rg-form-card">', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    distance = st.number_input("Estimated Travel Distance (in kilometers)", min_value=1.0, max_value=100.0, value=4.0, step=0.5, format="%.1f")
with col2:
    passenger_type = st.selectbox("Passenger Category", ["Regular", "Student", "Senior Citizen", "PWD"])

st.markdown("</div>", unsafe_allow_html=True)

# 2024 Base standard fare rates for Traditional Jeepneys
# (Note: Modern jeepneys are slightly higher, but this is a solid baseline)
base_fare = 13.00
per_km_rate = 1.80

if distance <= 4:
    total_fare = base_fare
else:
    # Charge for the extra distance beyond the first 4km
    extra_distance = math.ceil(distance - 4) # Fares usually round up per succeeding km
    total_fare = base_fare + (extra_distance * per_km_rate)

# Apply 20% Discount
is_discounted = passenger_type in ["Student", "Senior Citizen", "PWD"]
if is_discounted:
    total_fare = total_fare * 0.80

st.markdown(f"""
<div class="rg-result" style="text-align: center; margin-top: 2rem; padding: 3rem;">
    <h3 style="color: #64748B; font-size: 1.2rem; margin-bottom: 0;">Estimated Total Fare</h3>
    <h1 style="background: linear-gradient(to right, #3B82F6, #8B5CF6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 5rem; margin: 10px 0;">₱{total_fare:.2f}</h1>
    <p style="font-size: 1.2rem; color: #94A3B8;">
        {'<span style="color:#10B981; font-weight: 600;">✓ 20% Discount Applied</span>' if is_discounted else 'Standard Regular Rate'}
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="rg-howto" style="margin-top: 2rem;">
    <h4>How Fares are Computed</h4>
    <ul>
        <li><strong>Base Fare:</strong> ₱13.00 for the first 4 kilometers of the trip.</li>
        <li><strong>Succeeding Kilometers:</strong> ₱1.80 per additional kilometer (rounded up).</li>
        <li><strong>Mandated Discount:</strong> 20% off the total fare for Students, Senior Citizens, and PWDs as mandated by the LTFRB.</li>
    </ul>
    <p style="font-size: 0.85rem; color: #64748B; margin-top: 15px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 10px;">
        *Disclaimer: This calculator provides an estimate based on traditional jeepney baseline rates. Modern jeepneys (e-jeeps) have a slightly higher base fare (₱15.00) and succeeding rate (₱2.20). Actual fare collected may vary slightly per route depending on approved LTFRB fare matrices.
    </p>
</div>
""", unsafe_allow_html=True)
