import streamlit as st
import os

def load_css(filepath: str):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base, filepath)
    with open(full_path, "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sb-brand">
            <div class="sb-icon">🚌</div>
            <div class="sb-brand-text">
                <span class="sb-name">RoutaGo</span>
                <span class="sb-sub">Cebu Jeepney Guide</span>
            </div>
        </div>
        <div class="sb-sep"></div>
        <div class="sb-section-label">MENU</div>
        """, unsafe_allow_html=True)

        st.page_link("RoutaGo.py",               label="💬  Chat Assistant")
        st.page_link("pages/1_Plan_My_Route.py", label="🗺️  Plan My Route")
        st.page_link("pages/2_Safety_Tips.py",   label="🛡️  Safety Tips")
        st.page_link("pages/3_Saved_Routes.py",  label="❤️  Saved Routes")

        st.markdown("""
        <div class="sb-sep"></div>
        <div class="sb-section-label">INFO</div>
        <div class="sb-info-item">📍 Cebu City, PH</div>
        <div class="sb-info-item">🚌 Route 01K available</div>
        <div class="sb-ver">RoutaGo v1.0.0</div>
        """, unsafe_allow_html=True)
