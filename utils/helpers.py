import streamlit as st
import re
import time
import os

def page_loader():
    # A lightweight, non-blocking CSS-only loader
    loader_html = """
    <div class="bus-loader-container">
        <div class="bus-loader-track">
            <div class="bus-loader-icon">🚌</div>
            <div class="bus-loader-road"></div>
        </div>
        <p class="bus-loader-text">ROUTAGO IS ON THE WAY...</p>
    </div>
    <style>
        .bus-loader-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: #0B0F19;
            z-index: 999999;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            pointer-events: none;
            animation: fade-out 0.3s forwards;
            animation-delay: 1s;
        }
        .bus-loader-track {
            position: relative;
            width: 260px;
            height: 80px;
            overflow: hidden;
            border-bottom: 2px solid rgba(255,255,255,0.05);
        }
        .bus-loader-icon {
            position: absolute;
            bottom: 5px;
            left: -60px;
            font-size: 3rem;
            animation: drive 1.2s infinite linear;
        }
        .bus-loader-road {
            position: absolute;
            bottom: 0;
            width: 100%;
            height: 2px;
            background: repeating-linear-gradient(90deg, #FDE047 0, #FDE047 15px, transparent 15px, transparent 30px);
            animation: road 0.3s infinite linear;
        }
        .bus-loader-text {
            color: #F8FAFC;
            margin-top: 1rem;
            font-family: sans-serif;
            font-weight: 600;
            letter-spacing: 1px;
            font-size: 0.9rem;
            opacity: 0.8;
        }
        @keyframes drive {
            0% { left: -60px; }
            100% { left: 260px; }
        }
        @keyframes road {
            from { background-position: 0 0; }
            to { background-position: -30px 0; }
        }
        @keyframes fade-out {
            0% { opacity: 1; visibility: visible; }
            99% { opacity: 0; visibility: visible; }
            100% { opacity: 0; visibility: hidden; }
        }
    </style>
    """
    st.markdown(loader_html, unsafe_allow_html=True)

def load_css(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

def render_sidebar():
    with st.sidebar:
        if "theme" not in st.session_state:
            st.session_state.theme = "Light Mode"
            
        is_dark = st.session_state.theme == "Dark Mode"
        new_theme = st.toggle(" ", value=is_dark)
        
        if new_theme != is_dark:
            st.session_state.theme = "Dark Mode" if new_theme else "Light Mode"
            st.rerun()

    if st.session_state.get("theme") == "Light Mode":
        load_css("assets/styles/light.css")

def format_response(text):
    formatted = re.sub(r'(\b\d+[A-Z]\b)', r'**\1**', text)
    return formatted

def calculate_exact_route(origin_query: str, dest_query: str, routes_data: dict) -> dict:
    o_q = origin_query.lower().strip()
    d_q = dest_query.lower().strip()
    
    # Expanded fuzzy mapping
    landmark_map = {
        "citu": "cebu institute of technology university",
        "cit": "cebu institute of technology university",
        "usc": "university of san carlos",
        "uv": "university of visayas",
        "uc": "university of cebu",
        "ctu": "cebu technological university",
        "sm": "sm city cebu",
        "ayala": "ayala center cebu",
        "emall": "elizabeth mall",
        "csbt": "south bus terminal",
        "colon": "colon",
        "carbon": "carbon public market",
        "it park": "it park",
        "bulacao": "bulacao"
    }
    
    for key, val in landmark_map.items():
        if o_q == key: o_q = val
        if d_q == key: d_q = val

    def is_match(query, target):
        q = query.lower()
        t = target.lower()
        # Basic contains or common word match
        if q in t or t in q: return True
        
        # Intersection match for major hubs
        hubs = ["colon", "sm city", "ayala", "parkmall", "it park", "taboan", "carbon", "pier"]
        for hub in hubs:
            if hub in q and hub in t: return True
        return False

    # 1. DIRECT ROUTES
    for code, data in routes_data.items():
        stops = [s["name"] for s in data.get("stops", [])]
        o_idx, d_idx = -1, -1
        for i, s in enumerate(stops):
            if is_match(o_q, s): o_idx = i
            if is_match(d_q, s): d_idx = i
        
        if o_idx != -1 and d_idx != -1:
            if o_idx < d_idx:
                return {"type": "direct", "jeepney_code": code, "stops_passed": stops[o_idx:d_idx+1]}
            else:
                return {"type": "direct_reverse", "jeepney_code": code, "stops_passed": stops[d_idx:o_idx+1][::-1]}

    # 2. 1-TRANSFER ROUTES
    for code1, data1 in routes_data.items():
        stops1 = [s["name"] for s in data1.get("stops", [])]
        o_idx = -1
        for i, s in enumerate(stops1):
            if is_match(o_q, s): o_idx = i; break
        
        if o_idx != -1:
            for t_idx, stop_info in enumerate(data1.get("stops", [])):
                if t_idx == o_idx: continue
                transfer_point = stop_info["name"]
                
                for code2, data2 in routes_data.items():
                    if code1 == code2: continue
                    stops2 = [s["name"] for s in data2.get("stops", [])]
                    
                    t_idx2, d_idx2 = -1, -1
                    for i, s in enumerate(stops2):
                        if is_match(transfer_point, s): t_idx2 = i
                        if is_match(d_q, s): d_idx2 = i
                    
                    if t_idx2 != -1 and d_idx2 != -1:
                        leg1 = stops1[o_idx:t_idx+1] if o_idx < t_idx else stops1[t_idx:o_idx+1][::-1]
                        leg2 = stops2[t_idx2:d_idx2+1] if t_idx2 < d_idx2 else stops2[d_idx2:t_idx2+1][::-1]
                        return {
                            "type": "transfer",
                            "first_jeep": code1,
                            "transfer_at": transfer_point,
                            "second_jeep": code2,
                            "first_leg_stops": leg1,
                            "second_leg_stops": leg2
                        }

    return {"type": "none"}