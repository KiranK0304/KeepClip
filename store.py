import json
import os
import time
import hashlib

DATA_DIR = os.path.expanduser("~/.local/share/clipboard-history")
DATA_FILE = os.path.join(DATA_DIR, "history.json")
MAX_ITEMS = 100

def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_data():
    _ensure_dir()
    if not os.path.exists(DATA_FILE):
        return {"pinned": [], "history": []}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {"pinned": [], "history": []}
            data.setdefault("pinned", [])
            data.setdefault("history", [])
            return data
    except Exception:
        return {"pinned": [], "history": []}

def save_data(data):
    _ensure_dir()
    tmp_file = DATA_FILE + ".tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_file, DATA_FILE)

def make_id(text):
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:12]

def add_entry(text):
    if not text or not text.strip():
        return
    text = text.rstrip("\r\n")
    data = load_data()
    item_id = make_id(text)
    
    # If already in pinned, do nothing
    for item in data["pinned"]:
        if item["text"] == text:
            return
            
    # If in history, remove old occurrence
    data["history"] = [item for item in data["history"] if item["text"] != text]
    
    # Prepend new item
    new_entry = {
        "id": item_id,
        "text": text,
        "timestamp": int(time.time()),
        "pinned": False
    }
    data["history"].insert(0, new_entry)
    
    # Limit history size
    if len(data["history"]) > MAX_ITEMS:
        data["history"] = data["history"][:MAX_ITEMS]
        
    save_data(data)

def toggle_pin(item_id):
    data = load_data()
    # Check if in pinned
    for i, item in enumerate(data["pinned"]):
        if item["id"] == item_id:
            item["pinned"] = False
            item["timestamp"] = int(time.time())
            data["pinned"].pop(i)
            data["history"].insert(0, item)
            save_data(data)
            return
            
    # Check if in history
    for i, item in enumerate(data["history"]):
        if item["id"] == item_id:
            item["pinned"] = True
            data["history"].pop(i)
            data["pinned"].insert(0, item)
            save_data(data)
            return

def delete_entry(item_id):
    data = load_data()
    data["pinned"] = [x for x in data["pinned"] if x["id"] != item_id]
    data["history"] = [x for x in data["history"] if x["id"] != item_id]
    save_data(data)

def clear_history():
    data = load_data()
    data["history"] = []
    save_data(data)

def get_all_entries(query=""):
    data = load_data()
    all_items = []
    for item in data.get("pinned", []):
        it = dict(item)
        it["pinned"] = True
        all_items.append(it)
    for item in data.get("history", []):
        it = dict(item)
        it["pinned"] = False
        all_items.append(it)
        
    if query:
        q = query.lower()
        all_items = [x for x in all_items if q in x["text"].lower()]
    return all_items
