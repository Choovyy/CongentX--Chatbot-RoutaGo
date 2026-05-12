import json
import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from utils.helpers import calculate_exact_route

with open("routes.json", "r", encoding="utf-8") as f:
    ROUTES = json.load(f)

# Test the exact same case as the user
origin = "Parkmall"
destination = "Citu"

res = calculate_exact_route(origin, destination, ROUTES)
print(f"Result for {origin} to {destination}: {res}")
