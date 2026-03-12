import streamlit as st
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import load_css, render_sidebar, inject_dark_mode

st.set_page_config(page_title="Traffic Rules — RoutaGo", page_icon="🚦", layout="wide", initial_sidebar_state="expanded")
load_css("assets/styles/main.css")
load_css("assets/styles/signage.css")
render_sidebar()
inject_dark_mode()

st.markdown("""
<div class="rg-page-header">
    <h1>🚦 Traffic Rules</h1>
    <p>Key road signs and traffic-light rules every jeepney passenger should know.</p>
</div>
""", unsafe_allow_html=True)

signages = [
    ("🚏", "Bus/Jeepney Stop", "Board and wait only at designated stops to avoid unsafe boarding in traffic."),
    ("🚶", "Pedestrian / Walking Area", "Use pedestrian lanes or marked walkways when crossing near terminals and busy roads."),
    ("🛑", "Stop Sign", "Vehicles must fully stop. Be extra careful before crossing, even if a driver slows down."),
    ("⛔", "No Entry", "Do not board or ask to stop in roads marked no entry for the current direction."),
    ("🚫", "No Loading / Unloading", "Do not get on or off where loading and unloading is prohibited by signage."),
    ("↔️", "One Way", "Make sure your route direction matches the road flow before boarding a jeepney."),
    ("⚠️", "Pedestrian Crossing Ahead", "Slow down and stay alert; these areas have frequent foot traffic."),
    ("🅿️", "No Parking Zone", "Expect fewer legal stop points; move to proper loading zones instead."),
    ("🔴", "Traffic Light — Red", "Stop completely. Do not cross or board in moving lanes while the red light is active."),
    ("🟡", "Traffic Light — Yellow", "Prepare to stop. Avoid rushing to cross or stepping into the lane during yellow light."),
    ("🟢", "Traffic Light — Green", "Vehicles may proceed. Cross only on marked pedestrian areas and stay alert before stepping out."),
]

modal_blocks = []

for idx, (icon, title, description) in enumerate(signages):
    st.markdown(f"""
    <a class="sg-card-link" href="#sg-modal-{idx}" aria-label="View {title} full image and meaning">
        <div class="sg-card" role="button" tabindex="0">
            <div class="sg-thumb-btn" aria-hidden="true">
                <div class="sg-icon">{icon}</div>
            </div>
            <div class="sg-body">
                <h4>{title}</h4>
                <p>{description}</p>
            </div>
        </div>
    </a>
    """, unsafe_allow_html=True)

    modal_blocks.append(f"""
    <div id="sg-modal-{idx}" class="sg-modal" aria-hidden="true">
        <a class="sg-modal-backdrop" href="#" aria-label="Close"></a>
        <div class="sg-modal-box" role="dialog" aria-modal="true" aria-label="Traffic rule full view">
            <a class="sg-modal-close" href="#" aria-label="Close">&times;</a>
            <div class="sg-modal-icon">{icon}</div>
            <div class="sg-modal-title">{title}</div>
            <div class="sg-modal-meaning">{description}</div>
        </div>
    </div>
    """)

st.markdown("\n".join(modal_blocks), unsafe_allow_html=True)
