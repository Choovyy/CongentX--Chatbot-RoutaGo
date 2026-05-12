import math
from utils.helpers import calculate_exact_route


def tool_find_route(origin: str, destination: str, routes: dict) -> dict:
    """Finds the best jeepney route between two locations."""
    result = calculate_exact_route(origin, destination, routes)
    return result


def tool_calculate_fare(distance_km: float, passenger_type: str = "Regular") -> dict:
    """Calculates the jeepney fare given a distance and passenger type."""
    base_fare = 13.00
    per_km = 1.80
    if distance_km <= 4:
        total = base_fare
    else:
        extra = math.ceil(distance_km - 4)
        total = base_fare + (extra * per_km)

    if passenger_type in ["Student", "Senior Citizen", "PWD"]:
        total *= 0.80
        discounted = True
    else:
        discounted = False

    return {
        "distance_km": distance_km,
        "passenger_type": passenger_type,
        "total_fare": round(total, 2),
        "discounted": discounted
    }


def tool_list_routes_through_landmark(landmark: str, routes: dict) -> dict:
    """Lists all jeepney routes that pass through a given landmark or stop."""
    landmark_lower = landmark.lower().strip()
    matches = {}

    for code, data in routes.items():
        stops = [s["name"].lower() for s in data.get("stops", [])]
        for stop in stops:
            if landmark_lower in stop or stop in landmark_lower:
                matches[code] = {
                    "name": data["name"],
                    "terminals": data["terminals"],
                    "first_stop": data.get("stops", [{}])[0].get("name", "Unknown")
                }
                break

    return {"landmark": landmark, "matching_routes": matches, "route_count": len(matches)}


def tool_get_route_details(route_code: str, routes: dict) -> dict:
    """Returns full details of a specific jeepney route by its code."""
    route_code = route_code.upper().strip()
    if route_code in routes:
        data = routes[route_code]
        return {
            "code": route_code,
            "name": data["name"],
            "terminals": data["terminals"],
            "stops": [s["name"] for s in data.get("stops", [])],
            "description": data.get("description", ""),
            "stop_count": len(data.get("stops", []))
        }
    return {"error": f"Route {route_code} not found."}


# Tool schema definitions for the agent to understand available tools
TOOL_SCHEMAS = [
    {
        "name": "find_route",
        "description": "Find the best jeepney route between an origin and destination in Cebu City. Returns direct routes or 1-transfer options. Use this when the user asks how to get from one place to another.",
        "parameters": {
            "origin": "string — the starting location (e.g., 'Parkmall', 'SM City', 'Colon')",
            "destination": "string — the destination location (e.g., 'CIT-U', 'University of San Carlos', 'Airport')"
        }
    },
    {
        "name": "calculate_fare",
        "description": "Calculate the jeepney fare for a given distance and passenger type. Use this when the user asks about cost, price, or fare.",
        "parameters": {
            "distance_km": "float — estimated distance in kilometers (required)",
            "passenger_type": "string — one of: Regular, Student, Senior Citizen, PWD (optional, defaults to Regular)"
        }
    },
    {
        "name": "list_routes_through_landmark",
        "description": "List all jeepney routes that pass through a specific landmark, street, or stop. Use when the user asks which jeepneys pass through or serve a location.",
        "parameters": {
            "landmark": "string — the landmark, area, or stop name to search (e.g., 'Fuente Osmeña', 'Colon', 'IT Park')"
        }
    },
    {
        "name": "get_route_details",
        "description": "Get the full stop list and details of a specific jeepney route by its code. Use when the user asks about a specific route (e.g., '01K', '13B', 'N1').",
        "parameters": {
            "route_code": "string — the jeepney route code (e.g., '01K', '13B', 'N1')"
        }
    }
]
