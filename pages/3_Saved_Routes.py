import streamlit as st

st.set_page_config(page_title="Saved Routes – RoutaGo", page_icon="❤️", layout="centered")

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
.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    background: #f9fafb;
    border: 2px dashed #e5e7eb;
    border-radius: 16px;
    margin-bottom: 1.5rem;
}
.empty-state .icon { font-size: 3rem; margin-bottom: 0.75rem; }
.empty-state h3 { color: #374151; font-size: 1.1rem; margin: 0 0 6px 0; }
.empty-state p { color: #9ca3af; font-size: 0.875rem; margin: 0; }
.route-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.route-card h4 { margin: 0 0 4px 0; font-size: 1rem; font-weight: 600; color: #1B3A6B; }
.route-card p { margin: 0; font-size: 0.85rem; color: #6b7280; }
.how-to-card {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 14px;
    padding: 20px 22px;
    margin-top: 1rem;
}
.how-to-card h4 { color: #1B3A6B; margin: 0 0 12px 0; font-size: 0.95rem; font-weight: 600; }
.how-to-card ol { margin: 0; padding-left: 1.2rem; color: #374151; font-size: 0.875rem; line-height: 2; }
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

if "saved_routes" not in st.session_state:
    st.session_state.saved_routes = []

st.markdown("""
<div class='page-header'>
    <h1>❤️ Saved Routes</h1>
    <p>Your frequently used routes saved for quick access.</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.saved_routes:
    st.markdown("""
    <div class='empty-state'>
        <div class='icon'>🤍</div>
        <h3>No Saved Routes Yet</h3>
        <p>Start using the route planner to save your favorite routes and access them quickly.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for i, route in enumerate(st.session_state.saved_routes):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
            <div class='route-card'>
                <h4>📍 {route['from']} → {route['to']}</h4>
                <p>{route.get('details', 'Saved route')}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{i}"):
                st.session_state.saved_routes.pop(i)
                st.rerun()

st.markdown("""
<div class='how-to-card'>
    <h4>📖 How to Save Routes</h4>
    <ol>
        <li>Plan a route using the <strong>Plan My Route</strong> page</li>
        <li>Click the heart icon on the route result</li>
        <li>Access your saved routes anytime from this section</li>
    </ol>
</div>
""", unsafe_allow_html=True)
