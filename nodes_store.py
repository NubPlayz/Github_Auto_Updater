import json
import os

NODES_FILE = "nodes.json"

def load_nodes():
    if not os.path.exists(NODES_FILE):
        return []
    with open(NODES_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return []

def save_nodes(nodes):
    with open(NODES_FILE, "w") as f:
        json.dump(nodes, f, indent=2)
