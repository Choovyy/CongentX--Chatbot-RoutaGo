import streamlit as st
import re # <-- ADD THIS IMPORT

def load_css(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

def render_sidebar():
    with st.sidebar:
        st.markdown("### 🚌 RoutaGo")
        st.markdown("Your Cebu Jeepney Guide")

def format_response(text):
    return text

def calculate_exact_route(origin_query: str, dest_query: str, routes_data: dict) -> dict:
    
    def clean_text(text):
        cleaned = text.lower().strip().replace("-", "").replace(".", "")
        import re
        return re.sub(r'\s+', ' ', cleaned).strip()

    origin = clean_text(origin_query)
    dest = clean_text(dest_query)

    # NEW: Added 'exact_match' parameter. Default is False for user input.
    def get_stop_index(keyword, stops_array, exact_match=False):
        for idx, stop in enumerate(stops_array):
            clean_stop_name = clean_text(stop["name"])
            
            if exact_match:
                # STRICT match for database-to-database transfers
                if keyword == clean_stop_name:
                    return idx, stop["name"]
            else:
                # FUZZY match for user input (e.g. "citu" in "cebu institute... (citu)")
                if keyword in clean_stop_name:
                    return idx, stop["name"]
        return -1, None

    def get_stops_passed(stops, idx1, idx2):
        if idx1 < idx2:
            return [f"{i+1}. {s['name']}" for i, s in enumerate(stops[idx1:idx2+1])]
        else:
            return [f"{i+1}. {s['name']}" for i, s in enumerate(stops[idx2:idx1+1][::-1])]

    # 1. Search for Direct Routes
    for code, data in routes_data.items():
        stops = data.get("stops", [])
        orig_idx, orig_name = get_stop_index(origin, stops, exact_match=False)
        dest_idx, dest_name = get_stop_index(dest, stops, exact_match=False)

        if orig_idx != -1 and dest_idx != -1 and orig_idx != dest_idx:
            return {
                "type": "direct",
                "code": code,
                "name": data.get("name"),
                "board_at": orig_name,
                "alight_at": dest_name,
                "stops_passed": get_stops_passed(stops, orig_idx, dest_idx)
            }

    # 2. Search for 1-Transfer Routes
    for code_A, data_A in routes_data.items():
        stops_A = data_A.get("stops", [])
        orig_idx_A, orig_name = get_stop_index(origin, stops_A, exact_match=False)
        if orig_idx_A == -1: continue

        for code_B, data_B in routes_data.items():
            if code_A == code_B: continue
            stops_B = data_B.get("stops", [])
            dest_idx_B, dest_name = get_stop_index(dest, stops_B, exact_match=False)
            if dest_idx_B == -1: continue

            for idx_A, stop_A in enumerate(stops_A):
                if idx_A == orig_idx_A: continue 
                
                transfer_candidate = clean_text(stop_A["name"])
                
                # THE FIX: Force exact_match=True so SWU does not equal SWU Basak!
                trans_idx_B, exact_trans_name = get_stop_index(transfer_candidate, stops_B, exact_match=True)

                if trans_idx_B != -1 and trans_idx_B != dest_idx_B:
                    return {
                        "type": "transfer",
                        "leg1_code": code_A,
                        "leg1_name": data_A.get("name"),
                        "leg1_board": orig_name,
                        "transfer_point": exact_trans_name,
                        "leg1_stops_passed": get_stops_passed(stops_A, orig_idx_A, idx_A),
                        "leg2_code": code_B,
                        "leg2_name": data_B.get("name"),
                        "leg2_board": exact_trans_name,
                        "alight_at": dest_name,
                        "leg2_stops_passed": get_stops_passed(stops_B, trans_idx_B, dest_idx_B)
                    }

    return {"type": "none"}