import streamlit as st
import re
import json
from typing import Any, Dict, List, Optional, cast

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
    # Remove tool call JSON in various formats
    # Pattern 1: Complete JSON tool calls {"tool": "...", "params": {...}}
    # Uses a more robust brace-matching approach for nested objects
    def remove_json_toolcalls(s):
        result = []
        i = 0
        while i < len(s):
            if s[i] == '{':
                # Try to extract a complete JSON object
                brace_count = 0
                start = i
                for j in range(i, len(s)):
                    if s[j] == '{':
                        brace_count += 1
                    elif s[j] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_str = s[start:j+1]
                            try:
                                obj = json.loads(json_str)
                                if "tool" in obj and "params" in obj:
                                    # Skip this tool call
                                    i = j + 1
                                    break
                                else:
                                    result.append(s[i])
                                    i += 1
                            except:
                                result.append(s[i])
                                i += 1
                            break
                else:
                    result.append(s[i])
                    i += 1
            else:
                result.append(s[i])
                i += 1
        return ''.join(result)

    text = remove_json_toolcalls(text)

    # Remove ALL HTML tags from LLM response (both opening and closing)
    text = re.sub(r'<[^>]+>', '', text)

    # Bold route codes like 01K, 13B, etc.
    formatted = re.sub(r'(\b\d+[A-Z]\b)', r'**\1**', text)

    # Add line breaks after sentences
    formatted = re.sub(r'([.!?])\s+([A-Z])', r'\1\n\n\2', formatted)

    # Convert numbered lists to markdown bullets
    formatted = re.sub(r'^\s*(\d+)[.)]\s+', r'- ', formatted, flags=re.MULTILINE)

    # Clean up extra whitespace
    formatted = re.sub(r'\n\s*\n\s*\n+', '\n\n', formatted)
    formatted = re.sub(r'^\s+|\s+$', '', formatted, flags=re.MULTILINE)

    return formatted.strip()

def parse_agent_response(text: str) -> Dict[str, Any]:
    """Parse agent response to extract structured route and fare data."""
    data: Dict[str, Any] = {
        "text": text,
        "route_info": None,
        "fare_info": None,
        "distance": None,
        "stops": []
    }

    # Extract route codes (like 01K, 13B)
    route_codes = re.findall(r'\b(\d+[A-Z])\b', text)
    if route_codes:
        data["route_info"] = {"codes": list(set(route_codes))}  # Unique codes

    # Extract fare amounts (PHP XXX.XX or PHP XX)
    fare_match = re.search(r'PHP\s*([\d,]+\.?\d*)', text)
    if fare_match:
        fare_amount = fare_match.group(1).replace(',', '')
        data["fare_info"] = {"amount": float(fare_amount)}

    # Extract distance (X kilometers or X km)
    distance_match = re.search(r'([\d.]+)\s*(?:kilometers|km)', text)
    if distance_match:
        data["distance"] = f"{distance_match.group(1)} km"

    # Extract transfer point if mentioned
    transfer_match = re.search(r'[Tt]ransfer\s+(?:at|to)\s+([^\n,.]+)', text)
    if transfer_match:
        if data["route_info"] is None:
            data["route_info"] = {}
        if isinstance(data["route_info"], dict):
            transfer_location = transfer_match.group(1).strip()
            # Clean up any stray HTML tags
            transfer_location = re.sub(r'</?\w+[^>]*>', '', transfer_location)
            data["route_info"]["transfer_at"] = transfer_location

    # Extract stops from numbered lists
    stop_lines: List[str] = re.findall(r'^\s*\d+\.\s+([^\n]+)', text, re.MULTILINE)
    if stop_lines:
        # Clean up stray HTML tags from stops
        cleaned_stops = []
        for s in stop_lines:
            s_clean = s.strip()
            s_clean = re.sub(r'</?\w+[^>]*>', '', s_clean)
            if len(s_clean) > 2:
                cleaned_stops.append(s_clean)
        data["stops"] = cast(List[Any], cleaned_stops)

    return data

def calculate_exact_route(origin_query: str, dest_query: str, routes_data: dict) -> dict:
    o_q = origin_query.lower().strip()
    d_q = dest_query.lower().strip()
    
    def normalize(s):
        if not s: return ""
        # Remove common stop words for better matching
        s = s.lower()
        s = re.sub(r'\b(mall|university|campus|public|market|street|st|ave|avenue|road|rd|hub|terminal)\b', '', s)
        return re.sub(r'[^a-z0-9]', '', s)

    landmark_map = {
        # Schools
        "citu": "cebu institute of technology university",
        "cit": "cebu institute of technology university",
        "cit-u": "cebu institute of technology university",
        "usc": "university of san carlos",
        "usc main": "university of san carlos main campus",
        "usc north": "university of san carlos north campus",
        "usc south": "university of san carlos south campus",
        "uv": "university of visayas",
        "uc": "university of cebu",
        "ctu": "cebu technological university",
        "usjr": "university of san jose recoletos",
        "uspf": "university of southern philippines foundation",
        "swu": "southwestern university",
        "up": "university of the philippines",
        "ctu": "cebu technological university",
        "cim": "cebu institute of medicine",
        "stc": "st theresa's college",
        "cicu": "colegio de la inmaculada concepcion",
        "sti": "sti college",
        
        # Malls & Markets
        "sm": "sm city cebu",
        "sm cebu": "sm city cebu",
        "sm seaside": "sm seaside city cebu",
        "ayala": "ayala center cebu",
        "ayala cebu": "ayala center cebu",
        "emall": "elizabeth mall",
        "e-mall": "elizabeth mall",
        "country mall": "gaisano country mall",
        "g-mall": "gaisano grand mall",
        "grand mall": "gaisano grand mall",
        "jy": "jy square mall",
        "jy square": "jy square mall",
        "j centre": "j centre mall",
        "pacific mall": "pacific mall",
        "marina mall": "mactan marina mall",
        "btc": "banilad town center",
        "parkmall": "parkmall",
        "carbon": "carbon public market",
        "taboan": "taboan public market",
        "pasil": "pasil fish market",
        "colonnade": "colonnade supermarket",
        "gaisano main": "gaisano main",
        "metro colon": "metro colon",
        "metro gaisano": "metro gaisano",
        
        # Terminals & Transport
        "csbt": "south bus terminal",
        "south bus": "south bus terminal",
        "north bus": "north bus terminal",
        "pier 1": "pier 1",
        "pier 2": "pier 2",
        "pier 3": "pier 3",
        "pier 4": "pier 4",
        "airport": "mactan cebu international airport",
        "mcia": "mactan cebu international airport",
        "it park": "it park",
        "it-park": "it park",
        "pueblo verde": "pueblo verde terminal",
        "tamiya": "tamiya terminal",
        "tintay": "tintay jeepney terminal",
        
        # Government & Public
        "bir": "bureau of internal revenue",
        "dfa": "department of foreign affairs",
        "sss": "social security system",
        "pldt": "pldt",
        "prc": "professional regulations commission",
        "coa": "commission on audit",
        "sec": "securities and exchange commission",
        "capitol": "cebu provincial capitol",
        "city hall": "cebu city hall",
        "hall of justice": "hall of justice",
        
        # Hospitals
        "votto": "vicente sotto hospital",
        "vsmmc": "vicente sotto memorial medical center",
        "chong hua": "chong hua hospital",
        "cebu doc": "cebu doctors university hospital",
        "miller": "miller hospital",
        "ccmc": "cebu city medical center",
        
        # Major Hubs / Areas
        "colon": "colon",
        "guadalupe": "guadalupe",
        "labangon": "labangon",
        "banawa": "banawa",
        "lahug": "lahug",
        "mabolo": "mabolo",
        "talamban": "talamban",
        "bulacao": "bulacao",
        "pardo": "pardo",
        "quiot": "quiot",
        "tisa": "tisa",
        "apas": "apas",
        "busay": "busay",
        "pitos": "pitos",
        "mandaue": "mandaue",
        "lapu-lapu": "lapu-lapu city",
        "cordova": "cordova"
    }
    
    # Fuzzy match for landmark map
    o_norm = normalize(o_q)
    d_norm = normalize(d_q)
    
    for key, val in landmark_map.items():
        if o_norm == normalize(key): o_q = val
        if d_norm == normalize(key): d_q = val

    def is_match(query, target):
        q_norm = normalize(query)
        t_norm = normalize(target)
        if not q_norm or not t_norm: return False
        
        # Basic normalized match
        if q_norm in t_norm or t_norm in q_norm: return True
        
        # Intersection match for major hubs
        hubs = ["colon", "smcity", "ayala", "parkmall", "itpark", "taboan", "carbon", "pier", "citu", "cit"]
        for hub in hubs:
            h_norm = normalize(hub)
            if h_norm in q_norm and h_norm in t_norm: return True
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