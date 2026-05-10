import json
import re

def normalize(s):
    if not s: return ""
    s = s.lower()
    s = re.sub(r'\b(mall|university|campus|public|market|street|st|ave|avenue|road|rd|hub|terminal)\b', '', s)
    return re.sub(r'[^a-z0-9]', '', s)

def is_match(query, target):
    q_norm = normalize(query)
    t_norm = normalize(target)
    if not q_norm or not t_norm: return False
    if q_norm in t_norm or t_norm in q_norm: return True
    hubs = ["colon", "smcity", "ayala", "parkmall", "itpark", "taboan", "carbon", "pier", "citu", "cit"]
    for hub in hubs:
        h_norm = normalize(hub)
        if h_norm in q_norm and h_norm in t_norm: return True
    return False

def calculate_exact_route(origin_query: str, dest_query: str, routes_data: dict) -> dict:
    o_q = origin_query.lower().strip()
    d_q = dest_query.lower().strip()
    
    landmark_map = {
        "citu": "cebu institute of technology university",
        "cit": "cebu institute of technology university",
        "cit-u": "cebu institute of technology university",
        "sm": "sm city cebu",
        "parkmall": "parkmall",
        "colon": "colon"
    }
    
    o_norm = normalize(o_q)
    d_norm = normalize(d_q)
    for key, val in landmark_map.items():
        if o_norm == normalize(key): o_q = val
        if d_norm == normalize(key): d_q = val

    # 1. DIRECT ROUTES
    for code, data in routes_data.items():
        stops = [s["name"] for s in data.get("stops", [])]
        o_idx, d_idx = -1, -1
        for i, s in enumerate(stops):
            if is_match(o_q, s): o_idx = i
            if is_match(d_q, s): d_idx = i
        
        if o_idx != -1 and d_idx != -1:
            if o_idx < d_idx:
                return {"type": "direct", "jeepney_code": code}
            else:
                return {"type": "direct_reverse", "jeepney_code": code}

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
                        return {
                            "type": "transfer",
                            "first_jeep": code1,
                            "transfer_at": transfer_point,
                            "second_jeep": code2
                        }
    return {"type": "none"}

with open("routes.json", "r", encoding="utf-8") as f:
    ROUTES = json.load(f)

res = calculate_exact_route("Parkmall", "Citu", ROUTES)
print(f"Result for Parkmall to Citu: {res}")
