import json
import os

STATE_FILE = "last_seen.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"youtube": {}, "podcasts": {}}

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
