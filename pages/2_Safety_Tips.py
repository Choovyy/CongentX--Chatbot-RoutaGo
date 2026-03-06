import streamlit as st

st.set_page_config(page_title="Safety Tips – RoutaGo", page_icon="🛡️", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, header, footer { visibility: hidden; }
.main .block-container { padding-top: 2rem; max-width: 780px; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #1B3A6B 0%, #142d54 100%); }
[data-testid="stSidebar"] * { color: #ffffff !important; }
.page-header h1 { color: #1B3A6B; font-size: 1.8rem; font-weight: 700; margin-bottom: 0; }
.page-header p { color: #6b7280; font-size: 0.9rem; margin-top: 4px; margin-bottom: 1.5rem; }
.tip-card {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    transition: box-shadow 0.2s;
}
.tip-card:hover { box-shadow: 0 4px 18px rgba(27,58,107,0.1); }
.tip-icon {
    font-size: 1.6rem;
    background: #eff6ff;
    border-radius: 10px;
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.tip-content h4 { margin: 0 0 4px 0; font-size: 1rem; font-weight: 600; color: #1B3A6B; }
.tip-content p { margin: 0; font-size: 0.88rem; color: #6b7280; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 1.5rem 0;'>
        <div style='font-size:1.6rem; font-weight:700;'>🚌 RoutaGo</div>
        <div style='font-size:0.78rem; opacity:0.7; margin-top:2px;'>Cebu Jeepney Route Expert</div>
    </div>
    <hr style='border-color: rgba(255,255,255,0.15); margin-bottom:1rem;'/>
    """, unsafe_allow_html=True)
    st.page_link("app.py", label="💬  Chat Assistant")
    st.page_link("pages/1_Plan_My_Route.py", label="🗺️  Plan My Route")
    st.page_link("pages/2_Safety_Tips.py", label="🛡️  Safety Tips")
    st.page_link("pages/3_Saved_Routes.py", label="❤️  Saved Routes")

st.markdown("""
<div class='page-header'>
    <h1>🛡️ Safety Tips</h1>
    <p>Follow these guidelines to ensure a safe and comfortable journey on Cebu jeepneys.</p>
</div>
""", unsafe_allow_html=True)

tips = [
    ("👜", "Keep Valuables Secure", "Hold bags in front of you. Avoid displaying expensive items like phones or jewelry."),
    ("💵", "Have Exact Fare Ready", "Prepare small bills or coins to speed up payment and avoid inconvenience."),
    ("📣", "Confirm Your Route", "Ask the driver if the jeepney passes your destination before boarding."),
    ("📍", "Know When to Drop Off", "Say \"Lugar lang\" (stop here) or tap a coin on the rail to signal your stop."),
    ("⚠️", "Be Aware of Your Surroundings", "Stay alert, especially in crowded areas or during peak hours."),
    ("🌧️", "Prepare for the Weather", "Bring an umbrella — Cebu rain can be sudden. Wait under covered areas at stops."),
]

for icon, title, desc in tips:
    st.markdown(f"""
    <div class='tip-card'>
        <div class='tip-icon'>{icon}</div>
        <div class='tip-content'>
            <h4>{title}</h4>
            <p>{desc}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
