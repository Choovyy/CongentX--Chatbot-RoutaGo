import json
import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = "chroma_store"
COLLECTION_NAME = "cebu_routes"

def build_route_document(code: str, data: dict, direction: str = "forward") -> str:
    # Extract stops
    stops = [s["name"] for s in data.get("stops", [])]
    
    # Reverse the array if it's the return trip
    if direction == "reverse":
        stops = stops[::-1]
        
    terminals = data.get("terminals", [])
    if direction == "reverse" and len(terminals) >= 2:
        terminals = terminals[::-1]
        
    stops_str = " -> ".join(stops)
    terminals_str = " to ".join(terminals)
    description = data.get("description", "")
    name = data.get("name", "")
    
    return f"Route {code} ({direction} direction): {name}. Description: {description} Terminals: {terminals_str}. Stop Sequence: {stops_str}."

def get_or_build_collection(routes_path: str = "routes.json"):
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        collection = client.get_collection(name=COLLECTION_NAME, embedding_function=embedding_fn)
        if collection.count() > 0:
            return collection
        
        # FIX: Only delete the collection if it actually exists (but happens to be empty)
        client.delete_collection(COLLECTION_NAME)
        
    with open(routes_path, "r", encoding="utf-8") as f:
        routes = json.load(f)
        
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn
    )
    
    documents, ids, metadatas = [], [], []
    for code, data in routes.items():
        # Index Forward Route
        documents.append(build_route_document(code, data, "forward"))
        ids.append(f"{code}_forward")
        metadatas.append({"code": code, "direction": "forward", "name": data.get("name", "")})
        
        # Index Reverse Route
        documents.append(build_route_document(code, data, "reverse"))
        ids.append(f"{code}_reverse")
        metadatas.append({"code": code, "direction": "reverse", "name": data.get("name", "")})
        
    collection.add(documents=documents, ids=ids, metadatas=metadatas)
    return collection

def retrieve_relevant_routes(query: str, routes: dict, top_k: int = 5) -> dict:
    collection = get_or_build_collection()
    # Pull extra results because we have 2x the documents now
    results = collection.query(query_texts=[query], n_results=top_k * 2)
    
    filtered = {}
    for item_id, meta in zip(results["ids"][0], results["metadatas"][0]):
        code = meta.get("code")
        direction = meta.get("direction")
        
        if f"{code}_{direction}" not in filtered and code in routes:
            # Create a deep copy so we don't accidentally mutate the main ROUTES dictionary
            import copy
            data = copy.deepcopy(routes[code])
            data["_rag_direction"] = direction 
            
            # THE FIX: If ChromaDB matched the 'reverse' route, actually reverse the stops array!
            if direction == "reverse" and "stops" in data:
                data["stops"] = data["stops"][::-1]
                
            filtered[f"{code}_{direction}"] = data
            
        if len(filtered) >= top_k:
            break
            
    return filtered

